import pytest

from tests.conftest import register_and_login


pytestmark = pytest.mark.integration


def test_user_can_create_upload_target_and_list_own_resume(client):
    register_and_login(client, prefix="seed-admin")
    user = register_and_login(client, prefix="resume-owner")

    payload = {
        "title": "Backend Python Resume",
        "filename": "turpal_resume.pdf",
        "content_type": "application/pdf",
        "size_bytes": 2048,
        "grade": "junior",
        "skills": ["Python", "FastAPI"],
        "summary": "Candidate resume for AI interview preparation",
    }
    upload_response = client.post("/api/v1/resumes/upload-url", json=payload, headers=user["headers"])

    assert upload_response.status_code == 201, upload_response.text
    upload_body = upload_response.json()
    assert upload_body["upload_method"] == "PUT"
    assert upload_body["resume"]["status"] == "pending_upload"
    assert "FastAPI" in upload_body["resume"]["skills"]

    list_response = client.get("/api/v1/resumes/?search=backend&grade=junior&page=1&page_size=5", headers=user["headers"])
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["title"] == "Backend Python Resume"


def test_oversized_resume_upload_is_rejected(client):
    register_and_login(client, prefix="seed-admin")
    user = register_and_login(client, prefix="resume-owner")

    response = client.post(
        "/api/v1/resumes/upload-url",
        json={
            "title": "Too large",
            "filename": "large.pdf",
            "content_type": "application/pdf",
            "size_bytes": 50 * 1024 * 1024,
            "grade": "middle",
            "skills": ["Python"],
        },
        headers=user["headers"],
    )

    assert response.status_code == 413


def test_user_cannot_see_another_users_resume(client):
    register_and_login(client, prefix="seed-admin")
    owner = register_and_login(client, prefix="owner")
    stranger = register_and_login(client, prefix="stranger")

    client.post(
        "/api/v1/resumes/upload-url",
        json={
            "title": "Private Resume",
            "filename": "private.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
            "grade": "junior",
            "skills": ["SQL"],
        },
        headers=owner["headers"],
    )

    response = client.get("/api/v1/resumes/?search=Private", headers=stranger["headers"])

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_anonymous_user_cannot_list_resumes(client):
    response = client.get("/api/v1/resumes/")

    assert response.status_code == 401
