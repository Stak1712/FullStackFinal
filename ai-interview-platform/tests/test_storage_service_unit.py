import pytest

from app.services.storage import StorageService


pytestmark = pytest.mark.unit


def test_storage_service_sanitizes_filename_and_generates_scoped_urls():
    storage = StorageService()

    safe_name = storage.sanitize_filename("../My Resume 2026!.pdf")
    object_key = storage.generate_object_key("user-1", "../My Resume 2026!.pdf")
    upload_url = storage.create_upload_url(
        base_url="http://testserver",
        object_key=object_key,
        filename=safe_name,
        content_type="application/pdf",
    )

    assert ".." not in safe_name
    assert safe_name.endswith(".pdf")
    assert object_key.startswith("resumes/user-1/")
    assert upload_url.startswith("http://testserver/api/v1/resumes/storage/upload/")


def test_storage_service_saves_local_upload_and_reports_size():
    storage = StorageService()
    object_key = storage.generate_object_key("user-2", "resume.txt")
    result = storage.save_upload(
        token=storage.create_upload_url(
            base_url="http://testserver",
            object_key=object_key,
            filename="resume.txt",
            content_type="text/plain",
        ).rsplit("/", 1)[-1],
        payload=b"hello",
        content_type="text/plain",
    )

    assert result["provider"] == "local"
    assert result["size_bytes"] == 5
    assert storage.object_exists(object_key)
    assert storage.object_size(object_key) == 5
