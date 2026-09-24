"""JSON-file persistence for local MVP (Firestore-ready shape)."""

from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any

_lock = threading.Lock()


def _default_data_dir() -> Path:
    env = os.getenv("DATA_DIR")
    if env:
        return Path(env).resolve()
    # api/ is sibling of data/
    return Path(__file__).resolve().parent.parent / "data"


class CaseStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or _default_data_dir()
        self.cases_path = self.data_dir / "cases.json"
        self.seed_path = self.data_dir / "seed-cases.json"
        self.upload_dir = Path(os.getenv("UPLOAD_DIR", str(self.data_dir / "uploads")))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        with _lock:
            if self.cases_path.exists():
                return
            if self.seed_path.exists():
                shutil.copy(self.seed_path, self.cases_path)
            else:
                self.cases_path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        with _lock:
            if not self.cases_path.exists():
                return []
            raw = self.cases_path.read_text(encoding="utf-8").strip()
            if not raw:
                return []
            return json.loads(raw)

    def _write(self, cases: list[dict[str, Any]]) -> None:
        with _lock:
            tmp = self.cases_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.cases_path)

    def list_cases(self) -> list[dict[str, Any]]:
        cases = self._read()
        cases.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        return cases

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        for c in self._read():
            if c.get("id") == case_id:
                return c
        return None

    def upsert_case(self, case: dict[str, Any]) -> dict[str, Any]:
        cases = self._read()
        found = False
        for i, c in enumerate(cases):
            if c.get("id") == case["id"]:
                cases[i] = case
                found = True
                break
        if not found:
            cases.append(case)
        self._write(cases)
        return case

    def reset_from_seed(self) -> int:
        if not self.seed_path.exists():
            self._write([])
            return 0
        shutil.copy(self.seed_path, self.cases_path)
        return len(self._read())

    def save_upload(self, case_id: str, filename: str, content: bytes) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in filename)
        dest = self.upload_dir / f"{case_id}_{safe}"
        dest.write_bytes(content)
        return dest
