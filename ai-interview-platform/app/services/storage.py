from __future__ import annotations

import mimetypes
import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import get_settings
from app.core.security import create_scoped_token, decode_scoped_token

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:  # pragma: no cover - optional dependency in local mode
    boto3 = None
    ClientError = Exception

UPLOAD_ACTION = "upload"
DOWNLOAD_ACTION = "download"


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = (self.settings.STORAGE_PROVIDER or "local").strip().lower()
        self.local_root = Path(self.settings.STORAGE_LOCAL_ROOT).resolve()
        self.local_root.mkdir(parents=True, exist_ok=True)

    def max_file_size_bytes(self) -> int:
        return int(self.settings.STORAGE_MAX_FILE_SIZE_MB) * 1024 * 1024

    def provider_name(self) -> str:
        return self.provider

    def bucket_name(self) -> str | None:
        return self.settings.STORAGE_S3_BUCKET if self.provider == "s3" else None

    def initialize(self) -> None:
        if self.provider == "s3":
            self.ensure_bucket_exists()

    def sanitize_filename(self, filename: str) -> str:
        # Keep only the real file name and remove any path traversal fragments.
        # Example: "../My Resume.pdf" -> "My_Resume.pdf".
        raw_name = (filename or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_name)
        while ".." in cleaned:
            cleaned = cleaned.replace("..", ".")
        cleaned = cleaned.lstrip("._-")
        return cleaned[:180] or "resume.bin"

    def normalize_content_type(self, content_type: str | None, filename: str) -> str:
        if content_type:
            return content_type
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "application/octet-stream"

    def generate_object_key(self, owner_id: str, filename: str) -> str:
        safe = self.sanitize_filename(filename)
        return f"resumes/{owner_id}/{uuid.uuid4().hex}-{safe}"

    def create_upload_url(self, *, base_url: str, object_key: str, filename: str, content_type: str) -> str:
        token = create_scoped_token(
            {
                "scope": "storage",
                "act": UPLOAD_ACTION,
                "key": object_key,
                "filename": self.sanitize_filename(filename),
                "content_type": content_type,
                "provider": self.provider,
            },
            expires_in_seconds=int(self.settings.STORAGE_SIGNED_URL_EXPIRES_SECONDS),
        )
        return f"{base_url.rstrip('/')}/api/v1/resumes/storage/upload/{token}"

    def create_download_url(self, *, base_url: str, object_key: str, filename: str) -> str:
        token = create_scoped_token(
            {
                "scope": "storage",
                "act": DOWNLOAD_ACTION,
                "key": object_key,
                "filename": self.sanitize_filename(filename),
                "provider": self.provider,
            },
            expires_in_seconds=int(self.settings.STORAGE_SIGNED_URL_EXPIRES_SECONDS),
        )
        return f"{base_url.rstrip('/')}/api/v1/resumes/storage/download/{token}"

    def object_exists(self, object_key: str) -> bool:
        if self.provider == "s3":
            client = self._get_s3_client()
            if client is None:
                return False
            try:
                self.ensure_bucket_exists(client=client)
                client.head_object(Bucket=self.settings.STORAGE_S3_BUCKET, Key=object_key)
                return True
            except Exception:
                return False
        return self._local_path(object_key).exists()

    def object_size(self, object_key: str) -> int:
        if self.provider == "s3":
            client = self._get_s3_client()
            if client is None:
                return 0
            try:
                self.ensure_bucket_exists(client=client)
                head = client.head_object(Bucket=self.settings.STORAGE_S3_BUCKET, Key=object_key)
                return int(head.get("ContentLength") or 0)
            except Exception:
                return 0
        path = self._local_path(object_key)
        return path.stat().st_size if path.exists() else 0

    def save_upload(self, token: str, payload: bytes, content_type: str | None) -> dict[str, Any]:
        data = decode_scoped_token(token)
        if not data or data.get("scope") != "storage" or data.get("act") != UPLOAD_ACTION:
            raise HTTPException(status_code=403, detail="Invalid upload token")

        object_key = str(data.get("key") or "")
        if not object_key:
            raise HTTPException(status_code=400, detail="Missing object key")

        if len(payload) > self.max_file_size_bytes():
            raise HTTPException(status_code=413, detail="File is too large")

        resolved_content_type = content_type or data.get("content_type") or "application/octet-stream"

        if self.provider == "s3":
            client = self._get_s3_client()
            if client is None:
                raise HTTPException(status_code=500, detail="S3/MinIO client is not available")
            try:
                self.ensure_bucket_exists(client=client)
                client.put_object(
                    Bucket=self.settings.STORAGE_S3_BUCKET,
                    Key=object_key,
                    Body=payload,
                    ContentType=resolved_content_type,
                )
            except Exception as exc:  # pragma: no cover - network/backend dependent
                raise HTTPException(status_code=502, detail=f"Failed to upload file to MinIO: {exc}") from exc
            return {
                "object_key": object_key,
                "size_bytes": len(payload),
                "content_type": resolved_content_type,
                "provider": "s3",
            }

        path = self._local_path(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return {
            "object_key": object_key,
            "size_bytes": len(payload),
            "content_type": resolved_content_type,
            "provider": "local",
        }

    def build_download_response(self, token: str):
        data = decode_scoped_token(token)
        if not data or data.get("scope") != "storage" or data.get("act") != DOWNLOAD_ACTION:
            raise HTTPException(status_code=403, detail="Invalid download token")

        object_key = str(data.get("key") or "")
        filename = str(data.get("filename") or "resume.bin")
        if not object_key:
            raise HTTPException(status_code=400, detail="Missing object key")

        if self.provider == "s3":
            client = self._get_s3_client()
            if client is None:
                raise HTTPException(status_code=500, detail="S3/MinIO client is not available")
            try:
                self.ensure_bucket_exists(client=client)
                response = client.get_object(Bucket=self.settings.STORAGE_S3_BUCKET, Key=object_key)
                body = response["Body"].read()
                media_type = response.get("ContentType") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
                headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
                return StreamingResponse(BytesIO(body), media_type=media_type, headers=headers)
            except ClientError as exc:
                code = getattr(exc, "response", {}).get("Error", {}).get("Code")
                if code in {"NoSuchKey", "404", "NotFound"}:
                    raise HTTPException(status_code=404, detail="File not found") from exc
                raise HTTPException(status_code=502, detail=f"Failed to download file from MinIO: {exc}") from exc
            except Exception as exc:  # pragma: no cover - network/backend dependent
                raise HTTPException(status_code=502, detail=f"Failed to download file from MinIO: {exc}") from exc

        path = self._local_path(object_key)
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return FileResponse(path, media_type=media_type, filename=filename)

    def ensure_bucket_exists(self, client=None) -> None:
        if self.provider != "s3":
            return
        client = client or self._get_s3_client()
        if client is None:
            raise HTTPException(status_code=500, detail="S3/MinIO client is not available")
        bucket = self.settings.STORAGE_S3_BUCKET
        try:
            client.head_bucket(Bucket=bucket)
        except Exception:
            create_kwargs = {"Bucket": bucket}
            region = (self.settings.STORAGE_S3_REGION or "").strip()
            if region and region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
            client.create_bucket(**create_kwargs)

    def _local_path(self, object_key: str) -> Path:
        relative = Path(*[part for part in object_key.split("/") if part not in {"", ".", ".."}])
        return self.local_root / relative

    def _get_s3_client(self):
        if boto3 is None:
            return None
        return boto3.client(
            "s3",
            endpoint_url=self.settings.STORAGE_S3_ENDPOINT_URL,
            region_name=self.settings.STORAGE_S3_REGION,
            aws_access_key_id=self.settings.STORAGE_S3_ACCESS_KEY,
            aws_secret_access_key=self.settings.STORAGE_S3_SECRET_KEY,
        )
