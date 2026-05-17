import { useEffect } from "react";
import { useLocation } from "react-router-dom";

type JsonLd = Record<string, unknown>;

type SeoProps = {
  title: string;
  description: string;
  canonicalPath?: string;
  noIndex?: boolean;
  ogType?: "website" | "article";
  jsonLd?: JsonLd;
};

const siteName = "AI Interview Platform";
const siteUrl = (import.meta.env.VITE_PUBLIC_SITE_URL ?? window.location.origin).replace(/\/$/, "");

function upsertMeta(selector: string, attrs: Record<string, string>) {
  let element = document.head.querySelector<HTMLMetaElement>(selector);
  if (!element) {
    element = document.createElement("meta");
    document.head.appendChild(element);
  }
  Object.entries(attrs).forEach(([key, value]) => element?.setAttribute(key, value));
}

function upsertLink(rel: string, href: string) {
  let element = document.head.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`);
  if (!element) {
    element = document.createElement("link");
    element.rel = rel;
    document.head.appendChild(element);
  }
  element.href = href;
}

function upsertJsonLd(jsonLd?: JsonLd) {
  const id = "page-json-ld";
  const existing = document.getElementById(id);
  if (!jsonLd) {
    existing?.remove();
    return;
  }

  const script = existing ?? document.createElement("script");
  script.id = id;
  script.setAttribute("type", "application/ld+json");
  script.textContent = JSON.stringify(jsonLd);
  if (!existing) {
    document.head.appendChild(script);
  }
}

export default function Seo({
  title,
  description,
  canonicalPath,
  noIndex = false,
  ogType = "website",
  jsonLd,
}: SeoProps) {
  const location = useLocation();

  useEffect(() => {
    const canonicalUrl = `${siteUrl}${canonicalPath ?? location.pathname}`;
    const fullTitle = title.includes(siteName) ? title : `${title} | ${siteName}`;

    document.title = fullTitle;
    upsertMeta('meta[name="description"]', { name: "description", content: description });
    upsertMeta('meta[name="robots"]', { name: "robots", content: noIndex ? "noindex,nofollow" : "index,follow" });
    upsertMeta('meta[property="og:title"]', { property: "og:title", content: fullTitle });
    upsertMeta('meta[property="og:description"]', { property: "og:description", content: description });
    upsertMeta('meta[property="og:type"]', { property: "og:type", content: ogType });
    upsertMeta('meta[property="og:url"]', { property: "og:url", content: canonicalUrl });
    upsertMeta('meta[property="og:site_name"]', { property: "og:site_name", content: siteName });
    upsertLink("canonical", canonicalUrl);
    upsertJsonLd(jsonLd);
  }, [title, description, canonicalPath, location.pathname, noIndex, ogType, jsonLd]);

  return null;
}
