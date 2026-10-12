"""Storage abstraction: Firestore (Native) when configured, JSON files otherwise (local dev).

Select with STORAGE_BACKEND=firestore (+ optional FIRESTORE_PROJECT / FIRESTORE_DATABASE).
Invoice images go to a private Cloud Storage bucket when UPLOAD_BUCKET is set, else a local folder.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

_lock = threading.RLock()


def data_dir() -> Path:
    env = os.getenv("DATA_DIR")
    p = Path(env).resolve() if env else Path(__file__).resolve().parent.parent / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def backend_name() -> str:
    return "firestore" if os.getenv("STORAGE_BACKEND", "").lower() == "firestore" else "json"


class JsonCollection:
    def __init__(self, name: str, key: str) -> None:
        self.path = data_dir() / f"{name}.json"
        self.key = key

    def _read(self) -> list[dict]:
        with _lock:
            if not self.path.exists():
                return []
            raw = self.path.read_text("utf-8").strip()
            data = json.loads(raw) if raw else []
            return data if isinstance(data, list) else []

    def _write(self, rows: list[dict]) -> None:
        with _lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False), "utf-8")
            tmp.replace(self.path)

    def exists(self) -> bool:
        return self.path.exists()

    def all(self) -> list[dict]:
        return self._read()

    def get(self, doc_id: str) -> dict | None:
        return next((r for r in self._read() if str(r.get(self.key)) == str(doc_id)), None)

    def put(self, doc: dict) -> dict:
        with _lock:
            rows = [r for r in self._read() if str(r.get(self.key)) != str(doc[self.key])] + [doc]
            self._write(rows)
        return doc

    def delete(self, doc_id: str) -> bool:
        with _lock:
            rows = self._read()
            new = [r for r in rows if str(r.get(self.key)) != str(doc_id)]
            self._write(new)
        return len(new) != len(rows)

    def replace_all(self, docs: list[dict]) -> None:
        self._write(list(docs))


_fs_client = None


def _firestore():
    global _fs_client
    if _fs_client is None:
        from google.cloud import firestore

        _fs_client = firestore.Client(project=os.getenv("FIRESTORE_PROJECT") or None,
                                      database=os.getenv("FIRESTORE_DATABASE", "(default)"))
    return _fs_client


class FirestoreCollection:
    def __init__(self, name: str, key: str) -> None:
        self.col = _firestore().collection(os.getenv("FIRESTORE_PREFIX", "is_") + name)
        self.key = key

    @staticmethod
    def _id(v: Any) -> str:
        return str(v).replace("/", "_")

    def exists(self) -> bool:
        return any(True for _ in self.col.limit(1).stream()) or self.col.document("_meta").get().exists

    def all(self) -> list[dict]:
        return [d.to_dict() for d in self.col.stream() if d.id != "_meta"]

    def get(self, doc_id: str) -> dict | None:
        snap = self.col.document(self._id(doc_id)).get()
        return snap.to_dict() if snap.exists else None

    def put(self, doc: dict) -> dict:
        self.col.document(self._id(doc[self.key])).set(doc)
        return doc

    def delete(self, doc_id: str) -> bool:
        ref = self.col.document(self._id(doc_id))
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    def replace_all(self, docs: list[dict]) -> None:
        db = _firestore()
        batch, n = db.batch(), 0
        for d in self.col.stream():
            batch.delete(d.reference)
            n += 1
            if n % 400 == 0:
                batch.commit(); batch = db.batch()
        batch.set(self.col.document("_meta"), {"seeded": True})
        for d in docs:
            batch.set(self.col.document(self._id(d[self.key])), d)
            n += 1
            if n % 400 == 0:
                batch.commit(); batch = db.batch()
        batch.commit()


def collection(name: str, key: str):
    return FirestoreCollection(name, key) if backend_name() == "firestore" else JsonCollection(name, key)


class BlobStore:
    def __init__(self) -> None:
        self.bucket_name = os.getenv("UPLOAD_BUCKET", "").removeprefix("gs://").strip("/")
        self.local = Path(os.getenv("UPLOAD_DIR", str(data_dir() / "uploads")))
        if not self.bucket_name:
            self.local.mkdir(parents=True, exist_ok=True)
        self._bucket = None

    def _b(self):
        if self._bucket is None:
            from google.cloud import storage

            self._bucket = storage.Client(project=os.getenv("FIRESTORE_PROJECT") or None).bucket(self.bucket_name)
        return self._bucket

    def save(self, name: str, content: bytes, mime: str) -> str:
        if self.bucket_name:
            self._b().blob(f"uploads/{name}").upload_from_string(content, content_type=mime)
            return f"gs://{self.bucket_name}/uploads/{name}"
        (self.local / name).write_bytes(content)
        return str(self.local / name)

    def load(self, ref: str) -> bytes | None:
        try:
            if ref.startswith("gs://"):
                blob = self._b().blob(ref.split("/", 3)[3])
                return blob.download_as_bytes() if blob.exists() else None
            p = Path(ref)
            return p.read_bytes() if p.exists() else None
        except Exception:  # noqa: BLE001
            return None
