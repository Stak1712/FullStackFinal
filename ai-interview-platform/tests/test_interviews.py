import pytest

from tests.conftest import register_and_login


pytestmark = pytest.mark.integration


def test_interview_catalog_supports_search_sort_and_pagination(client):
    admin = register_and_login(client, prefix="admin")

    for title in ["Python Backend", "React Frontend", "SQL Data"]:
        response = client.post(
            "/api/v1/interviews/",
            json={"title": title, "description": f"Questions for {title}", "status": "active"},
            headers=admin["headers"],
        )
        assert response.status_code == 200

    catalog = client.get(
        "/api/v1/interviews/catalog?search=Python&sort_by=title&sort_order=asc&page=1&page_size=2",
        headers=admin["headers"],
    )

    assert catalog.status_code == 200
    body = catalog.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Python Backend"


def test_get_missing_interview_returns_404(client):
    admin = register_and_login(client, prefix="admin")

    response = client.get("/api/v1/interviews/9999", headers=admin["headers"])

    assert response.status_code == 404
