#!/usr/bin/env python3
"""Prepare deterministic one-page web-source evidence for Channel Intelligence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT_SECONDS = float(os.environ.get("WEB_CONTENT_TIMEOUT_SECONDS", "20"))
DEFAULT_MAX_HTML_BYTES = int(os.environ.get("WEB_CONTENT_MAX_HTML_BYTES", "6000000"))
DEFAULT_MAX_IMAGES = int(os.environ.get("WEB_CONTENT_MAX_IMAGES", "16"))
DEFAULT_MAX_IMAGE_BYTES = int(os.environ.get("WEB_CONTENT_MAX_IMAGE_BYTES", "10000000"))
DEFAULT_USER_AGENT = os.environ.get(
    "WEB_CONTENT_USER_AGENT",
    "VideoFactoryContentParser/1.0 (+local evidence capture)",
)
BLOCK_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "li",
    "blockquote",
    "figcaption",
    "caption",
    "td",
    "th",
}
SKIP_TEXT_TAGS = {"script", "style", "noscript", "svg", "canvas", "iframe", "form", "nav", "footer", "aside"}
ARTICLE_TYPES = {"article", "newsarticle", "blogposting", "report", "techarticle", "scholarlyarticle"}


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slug or fallback


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: drop_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value if item is not None]
    return value


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(drop_none(data), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relpath(path: Path | str | None, repo_root: Path) -> str | None:
    if not path:
        return None
    item = Path(path)
    try:
        resolved = item.resolve()
    except OSError:
        return item.as_posix()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        return str(resolved)


def path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def parse_attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key.lower(): value or "" for key, value in attrs}


def parse_srcset(srcset: str, base_url: str) -> list[dict[str, Any]]:
    candidates = []
    for part in srcset.split(","):
        chunk = part.strip()
        if not chunk:
            continue
        pieces = chunk.split()
        url = urllib.parse.urljoin(base_url, pieces[0])
        descriptor = " ".join(pieces[1:]) if len(pieces) > 1 else None
        width = None
        density = None
        if descriptor:
            width_match = re.search(r"(\d+)w\b", descriptor)
            density_match = re.search(r"([0-9.]+)x\b", descriptor)
            if width_match:
                width = int(width_match.group(1))
            if density_match:
                try:
                    density = float(density_match.group(1))
                except ValueError:
                    density = None
        candidates.append(drop_none({
            "url": url,
            "descriptor": descriptor,
            "width": width,
            "density": density,
        }))
    return candidates


class PageHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.in_ld_json = False
        self.ld_json_buffer: list[str] = []
        self.json_ld_raw: list[str] = []
        self.skip_depth = 0
        self.block_stack: list[dict[str, Any]] = []
        self.blocks: list[dict[str, Any]] = []
        self.meta: dict[str, list[str]] = {}
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = parse_attrs(attrs)

        if tag == "title":
            self.in_title = True
            return

        if tag == "script":
            script_type = attr_map.get("type", "").lower()
            if "ld+json" in script_type:
                self.in_ld_json = True
                self.ld_json_buffer = []
            else:
                self.skip_depth += 1
            return

        if tag in SKIP_TEXT_TAGS:
            self.skip_depth += 1
            return

        if tag == "meta":
            key = attr_map.get("property") or attr_map.get("name") or attr_map.get("itemprop")
            content = attr_map.get("content")
            if key and content:
                self.meta.setdefault(key.lower(), []).append(clean_text(content))
            return

        if tag == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href")
            if rel and href:
                self.links.append({
                    "rel": rel,
                    "href": urllib.parse.urljoin(self.base_url, href),
                    "type": attr_map.get("type", ""),
                })
            return

        if tag == "img":
            self._record_image(tag, attr_map)
            return

        if tag == "source" and (attr_map.get("srcset") or attr_map.get("data-srcset")):
            self._record_image(tag, attr_map)
            return

        if tag in BLOCK_TAGS and self.skip_depth == 0:
            self.block_stack.append({
                "tag": tag,
                "attrs": attr_map,
                "text": [],
            })

        if tag == "br":
            self._append_text("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
            return
        if tag == "script":
            if self.in_ld_json:
                self.json_ld_raw.append("".join(self.ld_json_buffer).strip())
                self.ld_json_buffer = []
                self.in_ld_json = False
            elif self.skip_depth:
                self.skip_depth -= 1
            return
        if tag in SKIP_TEXT_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.block_stack and self.block_stack[-1]["tag"] == tag:
            item = self.block_stack.pop()
            text = clean_text("".join(item["text"]))
            if text:
                self.blocks.append({
                    "tag": item["tag"],
                    "text": text,
                })

    def handle_data(self, data: str) -> None:
        if self.in_ld_json:
            self.ld_json_buffer.append(data)
            return
        if self.in_title:
            self.title_parts.append(data)
            return
        if self.skip_depth == 0:
            self._append_text(data)

    def handle_entityref(self, name: str) -> None:
        self.handle_data(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.handle_data(f"&#{name};")

    def _append_text(self, value: str) -> None:
        for block in self.block_stack:
            block["text"].append(value)

    def _record_image(self, tag: str, attrs: dict[str, str]) -> None:
        src = (
            attrs.get("src")
            or attrs.get("data-src")
            or attrs.get("data-original")
            or attrs.get("data-lazy-src")
            or attrs.get("data-url")
        )
        srcset = attrs.get("srcset") or attrs.get("data-srcset")
        candidates = parse_srcset(srcset, self.base_url) if srcset else []
        if src:
            candidates.insert(0, {"url": urllib.parse.urljoin(self.base_url, src), "descriptor": "src"})
        if not candidates:
            return
        self.images.append(drop_none({
            "source_tag": tag,
            "url": candidates[0]["url"],
            "srcset_candidates": candidates,
            "alt": clean_text(attrs.get("alt", "")),
            "title": clean_text(attrs.get("title", "")),
            "width": attrs.get("width"),
            "height": attrs.get("height"),
            "loading": attrs.get("loading"),
        }))


def extract_charset(content_type: str | None, payload: bytes) -> str:
    if content_type:
        match = re.search(r"charset=([^;\s]+)", content_type, re.IGNORECASE)
        if match:
            return match.group(1).strip('"')
    head = payload[:4096].decode("ascii", errors="ignore")
    match = re.search(r"<meta[^>]+charset=[\"']?([^\"'\s/>]+)", head, re.IGNORECASE)
    if match:
        return match.group(1)
    return "utf-8"


def fetch_bytes(
    url: str,
    user_agent: str,
    timeout: float,
    max_bytes: int | None = None,
) -> tuple[bytes, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            chunks = []
            total = 0
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if max_bytes is not None and total > max_bytes:
                    raise ValueError(f"Response exceeded max bytes ({max_bytes}).")
            return b"".join(chunks), {
                "status": getattr(response, "status", None),
                "final_url": response.geturl(),
                "headers": dict(response.headers.items()),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(max_bytes or 65536)
        return body, {
            "status": exc.code,
            "final_url": exc.geturl(),
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "error": str(exc),
        }


def check_robots(url: str, user_agent: str, timeout: float) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"status": "not_applicable", "allowed": True, "reason": "Non-HTTP URL."}
    robots_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    try:
        payload, meta = fetch_bytes(robots_url, user_agent, timeout, max_bytes=500000)
    except Exception as exc:  # noqa: BLE001 - preserve network failure as evidence.
        return {"status": "unknown", "allowed": True, "robots_url": robots_url, "reason": f"Robots check failed: {exc}"}
    status = int(meta.get("status") or 0)
    if 400 <= status < 500:
        return {"status": "unavailable", "allowed": True, "robots_url": robots_url, "http_status": status}
    if status >= 500:
        return {
            "status": "unreachable",
            "allowed": True,
            "robots_url": robots_url,
            "http_status": status,
            "reason": "Robots endpoint returned server error; analysis records limitation.",
        }
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(payload.decode("utf-8", errors="ignore").splitlines())
    allowed = parser.can_fetch(user_agent, url)
    return {"status": "checked", "allowed": allowed, "robots_url": robots_url, "http_status": status}


def canonical_url(links: list[dict[str, str]], fallback_url: str) -> str:
    for link in links:
        rel_values = {item.strip().lower() for item in link.get("rel", "").split()}
        if "canonical" in rel_values and link.get("href"):
            return link["href"]
    return fallback_url


def first_meta(meta: dict[str, list[str]], keys: list[str]) -> str | None:
    for key in keys:
        values = meta.get(key.lower())
        if values:
            return values[0]
    return None


def walk_jsonld(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            found.extend(walk_jsonld(item))
    elif isinstance(value, dict):
        node_type = value.get("@type") or value.get("type")
        type_values = node_type if isinstance(node_type, list) else [node_type]
        normalized = {str(item).lower() for item in type_values if item}
        if normalized & ARTICLE_TYPES:
            found.append(value)
        for key in ("@graph", "mainEntity", "mainEntityOfPage", "itemListElement"):
            if key in value:
                found.extend(walk_jsonld(value[key]))
    return found


def jsonld_text(value: Any) -> str | None:
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        pieces = [jsonld_text(item) for item in value]
        return ", ".join(item for item in pieces if item) or None
    if isinstance(value, dict):
        for key in ("name", "headline", "@id", "url"):
            if value.get(key):
                return jsonld_text(value[key])
    return None


def extract_jsonld_articles(raw_values: list[str]) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for raw in raw_values:
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in walk_jsonld(payload):
            articles.append(item)
    return articles


def build_metadata(parser: PageHTMLParser, page_url: str) -> dict[str, Any]:
    articles = extract_jsonld_articles(parser.json_ld_raw)
    article = articles[0] if articles else {}
    title = (
        first_meta(parser.meta, ["og:title", "twitter:title", "dc.title"])
        or jsonld_text(article.get("headline"))
        or jsonld_text(article.get("name"))
        or clean_text("".join(parser.title_parts))
    )
    description = (
        first_meta(parser.meta, ["og:description", "twitter:description", "description", "dc.description"])
        or jsonld_text(article.get("description"))
    )
    author = (
        first_meta(parser.meta, ["article:author", "author", "dc.creator"])
        or jsonld_text(article.get("author"))
        or jsonld_text(article.get("creator"))
    )
    publisher = (
        first_meta(parser.meta, ["og:site_name", "application-name"])
        or jsonld_text(article.get("publisher"))
    )
    published = (
        first_meta(parser.meta, ["article:published_time", "date", "dc.date", "pubdate"])
        or jsonld_text(article.get("datePublished"))
    )
    modified = (
        first_meta(parser.meta, ["article:modified_time", "dateModified"])
        or jsonld_text(article.get("dateModified"))
    )
    language = first_meta(parser.meta, ["og:locale", "language", "dc.language"])
    return drop_none({
        "title": title,
        "description": description,
        "author": author,
        "publisher": publisher,
        "published_date": published,
        "modified_date": modified,
        "language": language,
        "canonical_url": canonical_url(parser.links, page_url),
        "jsonld_article_count": len(articles),
        "open_graph": {key: values[0] for key, values in parser.meta.items() if key.startswith("og:") and values},
        "twitter_card": {key: values[0] for key, values in parser.meta.items() if key.startswith("twitter:") and values},
    })


def metadata_images(parser: PageHTMLParser, page_url: str) -> list[dict[str, Any]]:
    images = []
    for key in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
        for value in parser.meta.get(key, []):
            images.append({
                "source_tag": "meta",
                "source_key": key,
                "url": urllib.parse.urljoin(page_url, value),
                "srcset_candidates": [{"url": urllib.parse.urljoin(page_url, value), "descriptor": key}],
            })
    return images


def dedupe_images(images: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for image in images:
        candidates = image.get("srcset_candidates") or [{"url": image.get("url")}]
        best = choose_best_image_candidate(candidates)
        url = best.get("url") or image.get("url")
        if not url or url.startswith("data:") or url in seen:
            continue
        seen.add(url)
        deduped.append({**image, "url": url, "selected_candidate": best})
    return deduped


def choose_best_image_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in candidates if item.get("url")]
    if not valid:
        return {}
    return sorted(
        valid,
        key=lambda item: (
            int(item.get("width") or 0),
            float(item.get("density") or 0),
            1 if item.get("descriptor") == "src" else 0,
        ),
        reverse=True,
    )[0]


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [clean_text(item) for item in chunks if len(clean_text(item)) >= 35]


def claim_score(sentence: str) -> int:
    score = 0
    if re.search(r"\b(19|20)\d{2}\b", sentence):
        score += 3
    if re.search(r"\d", sentence):
        score += 2
    if any(token in sentence.lower() for token in ["according to", "reported", "study", "research", "data", "survey"]):
        score += 2
    if any(token in sentence for token in ["%", "$", "€", "£"]):
        score += 2
    if len(sentence) > 220:
        score -= 1
    return score


def build_blocks(raw_blocks: list[dict[str, Any]], max_blocks: int) -> list[dict[str, Any]]:
    blocks = []
    for index, block in enumerate(raw_blocks[:max_blocks], start=1):
        text = block.get("text", "")
        blocks.append({
            "block_id": f"block-{index:03d}",
            "tag": block.get("tag"),
            "text": text,
            "char_count": len(text),
        })
    return blocks


def build_claim_candidates(source_id: str, blocks: list[dict[str, Any]], max_claims: int = 40) -> list[dict[str, Any]]:
    candidates = []
    for block in blocks:
        if block.get("tag") not in {"p", "li", "blockquote", "td", "th"}:
            continue
        for sentence_index, sentence in enumerate(split_sentences(block.get("text", "")), start=1):
            score = claim_score(sentence)
            if score <= 0:
                continue
            candidates.append({
                "claim_id": f"claim-{source_id}-{len(candidates) + 1:03d}",
                "source_id": source_id,
                "block_id": block["block_id"],
                "sentence_index": sentence_index,
                "claim": sentence,
                "support_state": "source_claim_unverified",
                "allowed_use": "needs_review",
                "risk": "unknown",
                "confidence": "medium" if score >= 3 else "low",
                "score": score,
            })
    candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)[:max_claims]
    for item in candidates:
        item.pop("score", None)
    return candidates


def build_annotations(source_id: str, claims: list[dict[str, Any]], images: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotations = []
    for claim in claims:
        annotations.append({
            "annotation_id": f"ann-{claim['claim_id']}",
            "source_id": source_id,
            "motivation": "candidate_script_claim",
            "target": {"selector": claim.get("block_id"), "sentence_index": claim.get("sentence_index")},
            "body": {
                "purpose": "fact_check_before_script_use",
                "text": claim.get("claim"),
                "confidence": claim.get("confidence"),
            },
        })
    for index, image in enumerate(images, start=1):
        annotations.append({
            "annotation_id": f"ann-{source_id}-image-{index:03d}",
            "source_id": source_id,
            "motivation": "visual_evidence_candidate",
            "target": {"source_url": image.get("url")},
            "body": {
                "purpose": "review_rights_and_relevance_before_visual_use",
                "alt": image.get("alt"),
                "title": image.get("title"),
            },
        })
    return annotations


def render_markdown_report(
    source_id: str,
    url: str,
    metadata: dict[str, Any],
    claims: list[dict[str, Any]],
    images: list[dict[str, Any]],
    limitations: list[str],
) -> str:
    lines = [
        f"# Source Report: {metadata.get('title') or source_id}",
        "",
        f"- Source id: `{source_id}`",
        f"- URL: {url}",
        f"- Captured at: {utc_now()}",
    ]
    for key in ("publisher", "author", "published_date", "modified_date", "canonical_url"):
        if metadata.get(key):
            lines.append(f"- {key.replace('_', ' ').title()}: {metadata[key]}")
    lines.extend(["", "## Candidate Claims"])
    if claims:
        for claim in claims[:20]:
            lines.append(f"- `{claim['block_id']}` {claim['claim']}")
    else:
        lines.append("- No high-signal claim candidates were extracted by deterministic heuristics.")
    lines.extend(["", "## Visual Evidence Candidates"])
    if images:
        for index, image in enumerate(images[:20], start=1):
            label = image.get("alt") or image.get("title") or image.get("source_key") or "image"
            lines.append(f"- `image-{index:03d}` {label}: {image.get('url')}")
    else:
        lines.append("- No image candidates were found.")
    lines.extend(["", "## Limitations"])
    if limitations:
        lines.extend(f"- {item}" for item in limitations)
    else:
        lines.append("- No deterministic parser limitations recorded.")
    lines.append("")
    return "\n".join(lines)


def safe_image_extension(url: str, content_type: str | None) -> str:
    parsed_ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if parsed_ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
        return parsed_ext
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/avif": ".avif",
    }
    return mapping.get((content_type or "").split(";")[0].strip().lower(), ".img")


def download_images(
    images: list[dict[str, Any]],
    images_dir: Path,
    repo_root: Path,
    source_id: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[str]]:
    notes = []
    downloaded = []
    images_dir.mkdir(parents=True, exist_ok=True)
    for index, image in enumerate(images[: max(0, args.max_images)], start=1):
        url = image.get("url")
        if not url:
            continue
        try:
            payload, meta = fetch_bytes(url, args.user_agent, args.timeout, max_bytes=args.max_image_bytes)
        except Exception as exc:  # noqa: BLE001 - per-image failures should not abort page analysis.
            notes.append(f"Image download failed for {url}: {exc}")
            continue
        content_type = meta.get("headers", {}).get("Content-Type") or meta.get("headers", {}).get("content-type")
        if content_type and not content_type.lower().startswith("image/"):
            notes.append(f"Skipped non-image response for {url}: {content_type}")
            continue
        digest = hashlib.sha256(payload).hexdigest()[:12]
        ext = safe_image_extension(url, content_type)
        filename = f"{slugify(source_id)}-image-{index:03d}-{digest}{ext}"
        path = images_dir / filename
        path.write_bytes(payload)
        downloaded.append({
            **image,
            "asset_id": f"asset-{slugify(source_id)}-web-image-{index:03d}",
            "local_path": relpath(path, repo_root),
            "content_type": content_type,
            "size_bytes": len(payload),
            "checksum": f"sha256:{hashlib.sha256(payload).hexdigest()}",
        })
    return downloaded, notes


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def append_manifest_assets(manifest_path: Path, assets: list[dict[str, Any]]) -> list[str]:
    manifest = load_manifest(manifest_path)
    if manifest is None:
        return [f"Media asset manifest not found: {manifest_path}"]
    existing_assets = manifest.get("assets", [])
    if not isinstance(existing_assets, list):
        existing_assets = []
    by_id: dict[str, dict[str, Any]] = {
        item.get("asset_id"): item for item in existing_assets if isinstance(item, dict) and item.get("asset_id")
    }
    for asset in assets:
        by_id[asset["asset_id"]] = {**by_id.get(asset["asset_id"], {}), **drop_none(asset)}
    manifest["assets"] = list(by_id.values())
    manifest.setdefault("qa", {})
    manifest["qa"]["status"] = "partial"
    manifest["qa"]["summary"] = "Web source evidence artifacts were updated; review rights before final use."
    write_json(manifest_path, manifest)
    return []


def manifest_assets(
    source_id: str,
    source_url: str,
    repo_root: Path,
    paths: dict[str, Path],
    downloaded_images: list[dict[str, Any]],
    related_contracts: list[str | None],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    source_slug = slugify(source_id)
    contracts = [item for item in related_contracts if item]
    base_rights = {
        "license_summary": args.rights_notes or "Source captured for analysis; reuse rights are not implied.",
        "usage_allowed": False,
        "approval_required": True,
        "attribution_required": None,
        "restrictions": ["Do not reuse copied text or images in final video without rights review."],
    }
    assets = [
        {
            "asset_id": f"asset-{source_slug}-web-raw-html",
            "kind": "web_snapshot",
            "origin": "web_source",
            "status": "loaded",
            "canonical_path": relpath(paths["raw_html"], repo_root),
            "source_url": source_url,
            "title": args.title,
            "owner": args.owner,
            "rights": base_rights,
            "related_contract_paths": contracts,
        },
        {
            "asset_id": f"asset-{source_slug}-web-extracted-json",
            "kind": "metadata",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": relpath(paths["extracted_json"], repo_root),
            "source_url": source_url,
            "derived_from_asset_ids": [f"asset-{source_slug}-web-raw-html"],
            "related_contract_paths": contracts,
        },
        {
            "asset_id": f"asset-{source_slug}-web-report",
            "kind": "source_report",
            "origin": "derived",
            "status": "loaded",
            "canonical_path": relpath(paths["report_md"], repo_root),
            "source_url": source_url,
            "derived_from_asset_ids": [f"asset-{source_slug}-web-raw-html"],
            "related_contract_paths": contracts,
        },
    ]
    for image in downloaded_images:
        assets.append({
            "asset_id": image["asset_id"],
            "kind": "web_image",
            "origin": "web_source",
            "status": "loaded",
            "canonical_path": image.get("local_path"),
            "source_url": image.get("url"),
            "title": image.get("alt") or image.get("title"),
            "rights": base_rights,
            "technical": {
                "checksum": image.get("checksum"),
            },
            "derived_from_asset_ids": [f"asset-{source_slug}-web-raw-html"],
            "related_contract_paths": contracts,
            "evidence_refs": [{
                "evidence_id": f"ev-{source_slug}-image-{len(assets):03d}",
                "description": "Downloaded image candidate from web source.",
                "source_id": source_id,
                "path_or_url": image.get("local_path"),
                "confidence": "medium",
            }],
        })
    return assets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-html")
    parser.add_argument("--kind", default="webpage", choices=["webpage", "blog", "best_practice", "channel_data", "other"])
    parser.add_argument("--analysis-id")
    parser.add_argument("--page-id")
    parser.add_argument("--title")
    parser.add_argument("--owner")
    parser.add_argument("--rights-notes")
    parser.add_argument("--project-id")
    parser.add_argument("--project-path")
    parser.add_argument("--channel-profile-id")
    parser.add_argument("--channel-slug")
    parser.add_argument("--channel-profile-path")
    parser.add_argument("--media-asset-manifest")
    parser.add_argument("--update-media-asset-manifest", action="store_true")
    parser.add_argument("--download-images", action="store_true")
    parser.add_argument("--approved-downloads", action="store_true")
    parser.add_argument("--max-images", type=int, default=DEFAULT_MAX_IMAGES)
    parser.add_argument("--max-image-bytes", type=int, default=DEFAULT_MAX_IMAGE_BYTES)
    parser.add_argument("--max-html-bytes", type=int, default=DEFAULT_MAX_HTML_BYTES)
    parser.add_argument("--max-blocks", type=int, default=250)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--skip-robots-check", action="store_true")
    parser.add_argument("--screenshot-path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    work_dir = Path(args.work_dir)
    if not work_dir.is_absolute():
        work_dir = (Path.cwd() / work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    source_id = args.source_id
    source_slug = slugify(source_id)
    analysis_id = args.analysis_id or f"web-content-analysis-{source_slug}"
    page_id = args.page_id or f"web-page-{source_slug}"
    fetched_at = utc_now()
    limitations: list[str] = []
    robots = {"status": "skipped", "allowed": True, "reason": "Robots check skipped by flag."}

    if not path_is_under(output_path, repo_root):
        limitations.append("Output path is outside repo root; durable contract paths should be repo-relative for project artifacts.")
    if not path_is_under(work_dir, repo_root):
        limitations.append("Work directory is outside repo root; durable sidecar paths should be repo-relative for project artifacts.")

    if args.input_html:
        input_html = Path(args.input_html)
        if not input_html.is_absolute():
            input_html = (Path.cwd() / input_html).resolve()
        html_text = input_html.read_text(encoding="utf-8-sig")
        fetch_meta = {
            "status": "local_file",
            "final_url": args.url,
            "headers": {},
            "input_html_path": relpath(input_html, repo_root),
        }
    else:
        if not args.skip_robots_check:
            robots = check_robots(args.url, args.user_agent, args.timeout)
            if robots.get("status") in {"unknown", "unreachable"}:
                limitations.append(f"Robots check was {robots.get('status')}: {robots.get('reason', 'no detail')}")
            if not robots.get("allowed", True):
                analysis = {
                    "analysis_id": analysis_id,
                    "status": "blocked",
                    "sources": [{
                        "source_id": source_id,
                        "kind": args.kind,
                        "path_or_url": args.url,
                        "title": args.title,
                        "owner": args.owner,
                        "rights_notes": args.rights_notes,
                        "confidence": "unknown",
                    }],
                    "source_ledger": [{
                        "source_id": source_id,
                        "kind": args.kind,
                        "path_or_url": args.url,
                        "title": args.title,
                        "owner": args.owner,
                        "rights_state": "blocked",
                        "reusable_scope": "do_not_use",
                        "why_it_matters": "Robots rules disallow this URL for the configured user agent.",
                        "missing_assets": ["Page was not fetched."],
                        "confidence": "unknown",
                    }],
                    "claim_ledger": [],
                    "reference_beats": [],
                    "findings": {
                        "rights_or_policy_risks": ["Robots rules disallow this URL for the configured user agent."],
                        "evidence_gaps": ["Page was not fetched."],
                        "confidence_notes": [json.dumps(robots)],
                    },
                    "downstream_guidance": {
                        "creative_producer": ["Do not use this source for script claims."],
                        "visual_producer": ["Do not use page media or visual references from this source."],
                        "video_critic": ["Treat any dependency on this blocked source as a provenance failure."],
                    },
                    "invalidation_impact": [{
                        "impact_id": f"impact-{source_slug}-robots-blocked",
                        "change_or_gap": "robots_disallow",
                        "affected_artifacts": ["scenario", "visual_pack", "render", "critique"],
                        "reason": "Source capture was blocked by robots rules.",
                        "owner_agent": "channel-intelligence",
                        "severity": "blocker",
                        "recommended_action": "Use another approved source or obtain explicit user-provided content.",
                    }],
                }
                write_json(output_path, analysis)
                print(output_path)
                return 2
        payload, fetch_meta = fetch_bytes(args.url, args.user_agent, args.timeout, max_bytes=args.max_html_bytes)
        charset = extract_charset(fetch_meta.get("headers", {}).get("Content-Type"), payload)
        html_text = payload.decode(charset, errors="replace")

    raw_html_path = work_dir / "raw.html"
    write_text(raw_html_path, html_text)

    parser_obj = PageHTMLParser(fetch_meta.get("final_url") or args.url)
    parser_obj.feed(html_text)
    parser_obj.close()
    metadata = build_metadata(parser_obj, fetch_meta.get("final_url") or args.url)
    if args.title and not metadata.get("title"):
        metadata["title"] = args.title
    if args.owner and not metadata.get("publisher"):
        metadata["publisher"] = args.owner

    blocks = build_blocks(parser_obj.blocks, max(1, args.max_blocks))
    images = dedupe_images(metadata_images(parser_obj, fetch_meta.get("final_url") or args.url) + parser_obj.images)
    claim_candidates = build_claim_candidates(source_id, blocks)
    annotations = build_annotations(source_id, claim_candidates, images)

    downloaded_images: list[dict[str, Any]] = []
    if args.download_images:
        if args.approved_downloads:
            downloaded_images, image_notes = download_images(images, work_dir / "images", repo_root, source_id, args)
            limitations.extend(image_notes)
        else:
            limitations.append("Image download requested but --approved-downloads was not supplied; image URLs were cataloged only.")

    image_manifest = {
        "source_id": source_id,
        "page_id": page_id,
        "status": "downloaded" if downloaded_images else "cataloged",
        "images": images,
        "downloaded_images": downloaded_images,
    }
    image_manifest_path = work_dir / "images" / "image-manifest.json"
    write_json(image_manifest_path, image_manifest)

    annotations_path = work_dir / "annotations.json"
    write_json(annotations_path, {"source_id": source_id, "annotations": annotations})

    extracted = {
        "source_id": source_id,
        "page_id": page_id,
        "url": args.url,
        "final_url": fetch_meta.get("final_url"),
        "fetched_at": fetched_at,
        "http": {
            "status": fetch_meta.get("status"),
            "content_type": fetch_meta.get("headers", {}).get("Content-Type"),
        },
        "metadata": metadata,
        "blocks": blocks,
        "claim_candidates": claim_candidates,
        "images": images,
        "downloaded_images": downloaded_images,
        "annotations_path": relpath(annotations_path, repo_root),
        "image_manifest_path": relpath(image_manifest_path, repo_root),
        "robots": robots,
        "limitations": limitations,
    }
    extracted_json_path = work_dir / "extracted.json"
    write_json(extracted_json_path, extracted)

    extracted_md_path = work_dir / "extracted.md"
    md_lines = [f"# {metadata.get('title') or source_id}", ""]
    for block in blocks:
        tag = block.get("tag")
        text = block.get("text", "")
        if tag and tag.startswith("h") and len(tag) == 2:
            level = min(int(tag[1]) + 1, 6)
            md_lines.extend([f"{'#' * level} {text}", ""])
        elif tag == "blockquote":
            md_lines.extend([f"> {text}", ""])
        else:
            md_lines.extend([text, ""])
    write_text(extracted_md_path, "\n".join(md_lines).strip() + "\n")

    report_md_path = work_dir / "source-report.md"
    write_text(report_md_path, render_markdown_report(source_id, args.url, metadata, claim_candidates, images, limitations))
    report_json_path = work_dir / "source-report.json"

    evidence_refs = []
    for block in blocks:
        evidence_refs.append({
            "evidence_id": f"ev-{source_slug}-{block['block_id']}",
            "source_id": source_id,
            "description": f"Extracted {block.get('tag')} text block.",
            "path_or_url": f"{args.url}#{block['block_id']}",
            "confidence": "medium",
        })
    for index, image in enumerate(images, start=1):
        evidence_refs.append({
            "evidence_id": f"ev-{source_slug}-image-{index:03d}",
            "source_id": source_id,
            "asset_id": image.get("asset_id"),
            "description": image.get("alt") or image.get("title") or "Image candidate from source page.",
            "path_or_url": image.get("local_path") or image.get("url"),
            "confidence": "medium",
        })

    status = "complete"
    if not blocks:
        status = "partial"
        limitations.append("No article-like text blocks were extracted.")
    if args.download_images and not args.approved_downloads:
        status = "partial"
    if fetch_meta.get("status") not in {200, "local_file"}:
        status = "partial"
        limitations.append(f"Fetch status was {fetch_meta.get('status')}; review extracted evidence.")

    captured_artifacts = [
        {"kind": "web_snapshot", "path": relpath(raw_html_path, repo_root), "notes": "Raw HTML snapshot."},
        {"kind": "metadata", "path": relpath(extracted_json_path, repo_root), "notes": "Extracted text, metadata, images, and claim candidates."},
        {"kind": "text", "path": relpath(extracted_md_path, repo_root), "notes": "Markdown text extraction."},
        {"kind": "metadata", "path": relpath(image_manifest_path, repo_root), "notes": "Image URL/download manifest."},
        {"kind": "metadata", "path": relpath(annotations_path, repo_root), "notes": "Evidence annotations."},
        {"kind": "source_report", "path": relpath(report_md_path, repo_root), "notes": "Human-readable source report."},
    ]
    if args.screenshot_path:
        captured_artifacts.append({
            "kind": "screenshot",
            "path": relpath(args.screenshot_path, repo_root),
            "notes": "Externally captured page screenshot.",
        })

    source_ledger_entry = {
        "source_id": source_id,
        "asset_id": f"asset-{source_slug}-web-raw-html",
        "kind": args.kind,
        "path_or_url": args.url,
        "local_path": relpath(raw_html_path, repo_root),
        "title": metadata.get("title") or args.title,
        "owner": metadata.get("publisher") or args.owner,
        "rights_state": "needs_approval",
        "reusable_scope": "project_only",
        "why_it_matters": "Direct web source parsed for script claims, visual evidence candidates, and critique provenance.",
        "missing_assets": limitations,
        "confidence": "medium" if blocks else "low",
    }
    invalidation_impact = []
    if claim_candidates:
        invalidation_impact.append({
            "impact_id": f"impact-{source_slug}-claims",
            "change_or_gap": "web_claim_candidates_added",
            "affected_artifacts": ["scenario", "producer_criteria", "visual_pack", "critique"],
            "reason": "New parsed claim candidates can affect script wording, source cards, visual evidence choices, and factual review gates.",
            "owner_agent": "channel-intelligence",
            "severity": "minor",
            "recommended_action": "Creative Producer should use claim_ledger entries only after source-support review.",
        })
    if images and not downloaded_images:
        invalidation_impact.append({
            "impact_id": f"impact-{source_slug}-image-approval",
            "change_or_gap": "web_image_candidates_unapproved",
            "affected_artifacts": ["visual_pack", "timeline_sync", "render", "critique"],
            "reason": "Page image URLs were cataloged but not approved as local render media.",
            "owner_agent": "visual-producer",
            "severity": "minor",
            "recommended_action": "Use source-card recreation or request approval before rendering page images.",
        })

    analysis = drop_none({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "analysis_id": analysis_id,
        "project_id": args.project_id,
        "project_path": args.project_path,
        "channel_profile_id": args.channel_profile_id,
        "channel_slug": args.channel_slug,
        "channel_profile_path": args.channel_profile_path,
        "media_asset_manifest_path": args.media_asset_manifest,
        "status": status,
        "processing_runs": [{
            "run_id": f"processing-{source_slug}-local-web-content-parse",
            "mode": "local_deterministic",
            "tool": "parse_web_content.py",
            "status": status,
            "command": sys.argv,
            "inputs": [args.input_html or args.url],
            "outputs": [
                relpath(output_path, repo_root),
                relpath(raw_html_path, repo_root),
                relpath(extracted_json_path, repo_root),
                relpath(extracted_md_path, repo_root),
                relpath(image_manifest_path, repo_root),
                relpath(annotations_path, repo_root),
                relpath(report_md_path, repo_root),
            ],
            "deterministic_evidence": [
                "raw HTML snapshot",
                "HTML metadata extraction",
                "article-like text block extraction",
                "image URL/srcset extraction",
                "claim candidate heuristics",
            ],
            "limitations": limitations,
        }],
        "sources": [{
            "source_id": source_id,
            "asset_id": f"asset-{source_slug}-web-raw-html",
            "kind": args.kind,
            "path_or_url": args.url,
            "local_path": relpath(raw_html_path, repo_root),
            "title": metadata.get("title") or args.title,
            "owner": metadata.get("publisher") or args.owner,
            "date": metadata.get("published_date"),
            "rights_notes": args.rights_notes or "Source captured for analysis; reuse rights are not implied.",
            "summary": metadata.get("description"),
            "confidence": "medium" if blocks else "low",
            "captured_artifacts": captured_artifacts,
        }],
        "source_ledger": [source_ledger_entry],
        "web_pages": [{
            "page_id": page_id,
            "source_id": source_id,
            "url": args.url,
            "final_url": fetch_meta.get("final_url"),
            "captured_at": fetched_at,
            "metadata": metadata,
            "artifacts": {
                "raw_html_path": relpath(raw_html_path, repo_root),
                "extracted_json_path": relpath(extracted_json_path, repo_root),
                "extracted_markdown_path": relpath(extracted_md_path, repo_root),
                "image_manifest_path": relpath(image_manifest_path, repo_root),
                "annotations_path": relpath(annotations_path, repo_root),
                "report_markdown_path": relpath(report_md_path, repo_root),
                "report_json_path": relpath(report_json_path, repo_root),
                "screenshot_path": relpath(args.screenshot_path, repo_root) if args.screenshot_path else None,
            },
            "claim_candidates": claim_candidates,
            "visual_evidence_candidates": images[:40],
            "downloaded_images": downloaded_images,
            "robots": robots,
            "limitations": limitations,
            "confidence": "medium" if blocks else "low",
        }],
        "claim_ledger": [
            {
                "claim_id": item["claim_id"],
                "claim": item["claim"],
                "source_ids": [source_id],
                "support_state": "needs_review",
                "allowed_use": "script_claim_after_review",
                "risk": "factual",
                "confidence": item["confidence"],
                "evidence_refs": [{
                    "evidence_id": f"ev-{source_slug}-{item['block_id']}",
                    "source_id": source_id,
                    "path_or_url": f"{args.url}#{item['block_id']}",
                    "confidence": item["confidence"],
                }],
            }
            for item in claim_candidates
        ],
        "reference_beats": [],
        "findings": {
            "source_claims": [
                {
                    "claim": item["claim"],
                    "source_ids": [source_id],
                    "confidence": item["confidence"],
                }
                for item in claim_candidates[:20]
            ],
            "visual_evidence_opportunities": [
                f"{len(images)} page image candidates cataloged; review rights and relevance before using.",
                f"{len(downloaded_images)} image candidates downloaded after approval." if downloaded_images else None,
            ],
            "story_opportunities": [
                "Use extracted claims as source evidence, then shape the video around a distinct angle rather than summarizing the page."
            ],
            "rights_or_policy_risks": [
                "Page text and images are source evidence only; final reuse needs rights review and attribution decisions.",
                "Do not bypass paywalls, logins, robots disallow rules, or site terms.",
            ],
            "evidence_gaps": limitations,
            "confidence_notes": [
                "Metadata, text blocks, image URLs, and local artifact paths are deterministic parser outputs.",
                "Claim importance, factual correctness, narrative angle, and visual selection still need agent review.",
            ],
        },
        "evidence_refs": evidence_refs,
        "downstream_guidance": {
            "creative_producer": [
                "Use claim_ledger entries only after source-support review; avoid reading the page as the whole video."
            ],
            "visual_producer": [
                "Use visual_evidence_candidates for source-backed visual planning after rights and relevance review."
            ],
            "invideo_ai_generator": [
                "Do not include copied article images or exact text in generation prompts unless rights and usage are approved."
            ],
            "remotion_clip_builder": [
                "Use source cards, redrawn diagrams, or abstracted motion graphics when direct image reuse is not approved."
            ],
            "remotion_video_producer": [
                "Only render local web images when the media asset manifest marks them approved for use."
            ],
            "video_critic": [
                "Check that script claims trace back to claim_ledger/evidence_refs and that unapproved page images are not reused."
            ],
        },
        "invalidation_impact": invalidation_impact,
    })

    paths = {
        "raw_html": raw_html_path,
        "extracted_json": extracted_json_path,
        "report_md": report_md_path,
    }
    related_contracts = [relpath(output_path, repo_root)]
    manifest_action_notes = []
    if args.update_media_asset_manifest:
        if not args.media_asset_manifest:
            manifest_action_notes.append("Manifest update requested but --media-asset-manifest was not supplied.")
        else:
            manifest_path = Path(args.media_asset_manifest)
            if not manifest_path.is_absolute():
                manifest_path = repo_root / manifest_path
            assets = manifest_assets(
                source_id,
                args.url,
                repo_root,
                paths,
                downloaded_images,
                related_contracts,
                args,
            )
            manifest_notes = append_manifest_assets(manifest_path, assets)
            manifest_action_notes.extend(manifest_notes)
            if not manifest_notes:
                analysis["processing_runs"][0].setdefault("outputs", []).append(relpath(manifest_path, repo_root))
                analysis["manifest_actions"] = [
                    {
                        "action": "created",
                        "asset_id": asset["asset_id"],
                        "canonical_path": asset.get("canonical_path"),
                        "rights_state": "needs_approval",
                        "technical_metadata_state": "partial",
                        "reason": "Web source artifact captured for analysis.",
                    }
                    for asset in assets
                ]
    if manifest_action_notes:
        analysis.setdefault("findings", {}).setdefault("evidence_gaps", []).extend(manifest_action_notes)
    if args.download_images and not args.approved_downloads and images:
        analysis.setdefault("manifest_actions", []).append({
            "action": "deferred",
            "asset_id": f"asset-{source_slug}-web-images",
            "canonical_path": relpath(image_manifest_path, repo_root),
            "rights_state": "needs_approval",
            "technical_metadata_state": "partial",
            "reason": "Image URLs were cataloged, but file download requires Director approval.",
        })

    write_json(report_json_path, analysis)
    write_json(output_path, analysis)
    print(output_path)
    return 0 if status != "blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
