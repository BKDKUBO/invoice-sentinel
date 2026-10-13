"""Case persistence (Firestore or JSON via db.py) + invoice image storage."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

from db import BlobStore, backend_name, collection, data_dir

MANILA = ZoneInfo("Asia/Manila")


def _default_data_dir() -> Path:  # kept for older imports
    return data_dir()


def _raw_seed_cases() -> list[dict]:
    for p in (data_dir() / "seed-cases.json", Path(__file__).resolve().parent / "seed" / "seed-cases.json"):
        if p.exists():
            return json.loads(p.read_text("utf-8") or "[]")
    return []


def _seed_cases(today: date | None = None) -> list[dict]:
    """Seed cases re-dated relative to today (Asia/Manila): newest seed 1 day ago, spread over the last 1-6 days.
    Each case keeps its time of day and the spacing of its audit events, so the 14-day risk chart never goes empty."""
    seeds = _raw_seed_cases()
    if not seeds:
        return seeds
    today = today or datetime.now(MANILA).date()

    def parse(v: str) -> datetime:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return (d if d.tzinfo else d.replace(tzinfo=MANILA)).astimezone(MANILA)

    order = sorted(range(len(seeds)), key=lambda i: parse(seeds[i]["created_at"]), reverse=True)
    for rank, i in enumerate(order):
        c = seeds[i]
        created = parse(c["created_at"])
        days_ago = min(1 + rank, 6)
        target = datetime.combine(today - timedelta(days=days_ago), created.timetz())
        delta = target - created
        for k in ("created_at", "updated_at"):
            if c.get(k):
                c[k] = (parse(c[k]) + delta).isoformat()
        for ev in c.get("audit_log") or []:
            if ev.get("at"):
                ev["at"] = (parse(ev["at"]) + delta).isoformat()
    return seeds


class CaseStore:
    def __init__(self) -> None:
        self.col = collection("cases", "id")
        self.blobs = BlobStore()
        self.backend = backend_name()
        if not self.col.exists():
            self.reset_from_seed()

    def list_cases(self) -> list[dict[str, Any]]:
        cases = self.col.all()
        cases.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        return cases

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        return self.col.get(case_id)

    def upsert_case(self, case: dict[str, Any]) -> dict[str, Any]:
        return self.col.put(case)

    def reset_from_seed(self) -> int:
        seeds = _seed_cases()
        self.col.replace_all(seeds)
        return len(seeds)

    def save_upload(self, case_id: str, filename: str, content: bytes, mime: str = "application/octet-stream") -> str:
        safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in filename)
        return self.blobs.save(f"{case_id}_{safe}", content, mime)

    def load_upload(self, case: dict[str, Any]) -> bytes | None:
        ref = case.get("upload_ref")
        if not ref:
            safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in case.get("filename", ""))
            ref = str(self.blobs.local / f"{case.get('id')}_{safe}")
        return self.blobs.load(ref)
