import os
import csv
import json
from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.celery_app import celery_app
from app.core.s3_client import s3_service
from app.crud.dataset import dataset_crud, dataset_file_crud
from app.models.dataset import DatasetFile


@celery_app.task(bind=True)
def validate_dataset_upload(self, dataset_id: int, file_key: str, file_name: str, file_type: str):
    db: Session = SessionLocal()
    try:
        self.update_state(state="PROGRESS", meta={"step": "downloading", "progress": 10})
        dataset = dataset_crud.get(db, id=dataset_id)
        if not dataset:
            return {"error": "Dataset not found"}

        local_path = f"/tmp/{file_key.replace('/', '_')}"
        try:
            s3_service.client.download_file(s3_service.bucket, file_key, local_path)
        except Exception as exc:
            return {"error": f"Failed to download file: {exc}"}

        self.update_state(state="PROGRESS", meta={"step": "magic_bytes", "progress": 30})
        magic = _check_magic_bytes(local_path, file_type)
        if not magic["valid"]:
            return {"error": f"Magic bytes mismatch: expected {file_type}, got {magic['detected']}"}

        self.update_state(state="PROGRESS", meta={"step": "virus_scan", "progress": 50})
        virus_scan = _scan_file(local_path)
        if not virus_scan["clean"]:
            return {"error": "Virus scan failed", "threats": virus_scan["threats"]}

        self.update_state(state="PROGRESS", meta={"step": "shape_analysis", "progress": 70})
        shape = _analyze_shape(local_path, file_type)

        self.update_state(state="PROGRESS", meta={"step": "saving_metadata", "progress": 90})
        file_size = os.path.getsize(local_path)
        db_file = DatasetFile(
            dataset_id=dataset_id,
            file_name=file_name,
            storage_path_url=f"{s3_service.client.meta.endpoint_url}/{s3_service.bucket}/{file_key}",
            file_size_bytes=file_size,
            file_type=file_type,
        )
        db.add(db_file)

        dataset.status = "Active"
        db.add(dataset)
        db.commit()

        try:
            os.remove(local_path)
        except Exception:
            pass

        self.update_state(state="SUCCESS", meta={"progress": 100})
        return {
            "dataset_id": dataset_id,
            "file_name": file_name,
            "shape": shape,
            "file_size_bytes": file_size,
        }
    finally:
        db.close()


def _check_magic_bytes(path: str, declared_type: str) -> dict:
    with open(path, "rb") as f:
        header = f.read(8)
    magic_map = {
        "csv": [b"\xef\xbb\xbf", b""],
        "json": [b"\x7b", b"\x5b"],
        "zip": [b"PK"],
    }
    declared = declared_type.lower()
    expected = magic_map.get(declared, [])
    valid = any(header.startswith(e) for e in expected) if expected else True
    detected = "unknown"
    if header.startswith(b"PK"):
        detected = "zip"
    elif header.startswith(b"{") or header.startswith(b"["):
        detected = "json"
    elif header[:3] == b"\xef\xbb\xbf" or header[:1].isascii():
        detected = "csv"
    return {"valid": valid, "detected": detected}


def _scan_file(path: str) -> dict:
    # Placeholder for ClamAV or cloud AV integration
    return {"clean": True, "threats": []}


def _analyze_shape(path: str, file_type: str) -> dict:
    ft = file_type.lower()
    if ft == "csv":
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                cols = len(header) if header else 0
                rows = sum(1 for _ in reader)
                return {"rows": rows, "columns": cols}
        except Exception:
            return {"rows": None, "columns": None}
    elif ft == "json":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return {"rows": len(data), "columns": len(data[0]) if data else 0}
            return {"rows": 1, "columns": len(data)}
        except Exception:
            return {"rows": None, "columns": None}
    return {"rows": None, "columns": None}
