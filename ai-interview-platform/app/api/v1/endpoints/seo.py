from __future__ import annotations

from datetime import date
from html import escape

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from app.core.config import get_settings

router = APIRouter()

INDEXABLE_ROUTES = [
    {"path": "/", "priority": "1.0", "changefreq": "weekly"},
    {"path": "/ai", "priority": "0.8", "changefreq": "weekly"},
    {"path": "/directions", "priority": "0.8", "changefreq": "weekly"},
    {"path": "/resources", "priority": "0.8", "changefreq": "daily"},
    {"path": "/about", "priority": "0.6", "changefreq": "monthly"},
]

PRIVATE_ROUTES = ["/login", "/register", "/profile", "/resume", "/interview", "/admin"]


@router.get("/robots.txt", include_in_schema=False, response_class=PlainTextResponse)
def robots_txt() -> str:
    settings = get_settings()
    site_url = settings.PUBLIC_SITE_URL.rstrip("/")
    disallow_lines = "\n".join(f"Disallow: {path}" for path in PRIVATE_ROUTES)
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"{disallow_lines}\n"
        f"Sitemap: {site_url}/sitemap.xml\n"
    )


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml() -> Response:
    settings = get_settings()
    site_url = settings.PUBLIC_SITE_URL.rstrip("/")
    today = date.today().isoformat()
    urls = []
    for route in INDEXABLE_ROUTES:
        loc = escape(f"{site_url}{route['path']}")
        urls.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{route['changefreq']}</changefreq>\n"
            f"    <priority>{route['priority']}</priority>\n"
            "  </url>"
        )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")
