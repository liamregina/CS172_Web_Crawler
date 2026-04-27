from __future__ import annotations
import posixpath
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

try:
    from w3lib.url import canonicalize_url
except Exception:  # fallback for simple unit tests if w3lib is unavailable
    def canonicalize_url(url: str) -> str:
        return url

# File types that are not useful for the Part A HTML crawler.
BLOCKEDEXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp", ".tif", ".tiff",
    ".pdf", ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
    ".mp3", ".wav", ".flac", ".aac", ".ogg",
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm",
    ".css", ".js", ".xml", ".json", ".rss",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".exe", ".bin", ".iso", ".dmg",
}

TRACKINGQUERYPREFIXES = ("utm_",)
TRACKINGQUERYKEYS = {
    "fbclid", "gclid", "mc_cid", "mc_eid", "igshid", "ref", "ref_src", "spm", "source",
}

BADSCHEMES = ("mailto:", "javascript:", "tel:", "data:", "ftp:", "file:")


def normalizeList(values: Iterable[str] | str | None) -> list[str]:
    """Accepts either a comma-separated string or a list/tuple of strings."""
    if values is None:
        return []
    if isinstance(values, str):
        return [v.strip().lower() for v in values.split(",") if v.strip()]
    return [str(v).strip().lower() for v in values if str(v).strip()]


def normalizeUrl(rawUrl: str | None, baseUrl: str | None = None) -> str | None:
    """
    Convert a raw extracted link into a canonical crawlable URL.

    Handles relative URLs, fragments, default ports, tracking query params, path cleanup,
    blocked file extensions, and invalid schemes.
    """
    if not rawUrl or not isinstance(rawUrl, str):
        return None

    rawUrl = rawUrl.strip()
    if not rawUrl:
        return None

    if rawUrl.lower().startswith(BADSCHEMES):
        return None

    absoluteUrl = urljoin(baseUrl, rawUrl) if baseUrl else rawUrl
    parts = urlsplit(absoluteUrl)

    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"}:
        return None

    netloc = parts.netloc.lower()
    if not netloc:
        return None

    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]

    path = parts.path or "/"
    path = posixpath.normpath(path)
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    if hasBlockedExtension(path):
        return None

    queryPairs: list[tuple[str, str]] = []
    for key, value in parse_qsl(parts.query, keep_blank_values=False):
        lowerKey = key.lower()
        if lowerKey in TRACKINGQUERYKEYS:
            continue
        if lowerKey.startswith(TRACKINGQUERYPREFIXES):
            continue
        queryPairs.append((key, value))

    query = urlencode(sorted(queryPairs), doseq=True)
    cleaned = urlunsplit((scheme, netloc, path, query, ""))

    try:
        return canonicalize_url(cleaned)
    except Exception:
        return cleaned


def hasBlockedExtension(pathOrUrl: str | None) -> bool:
    if not pathOrUrl:
        return False
    path = urlsplit(pathOrUrl).path if "://" in pathOrUrl else pathOrUrl
    lowerPath = path.lower()
    return any(lowerPath.endswith(ext) for ext in BLOCKEDEXTENSIONS)


def getDomain(url: str) -> str:
    return urlsplit(url).netloc.lower()


def isAllowedDomain(url: str, allowedDomains: Iterable[str] | str | None) -> bool:
    allowed = normalizeList(allowedDomains)
    if not allowed:
        return True

    domain = getDomain(url)
    for allowedDomain in allowed:
        if domain == allowedDomain or domain.endswith("." + allowedDomain):
            return True
    return False


def isAllowedTld(url: str, allowedTlds: Iterable[str] | str | None) -> bool:
    allowed = normalizeList(allowedTlds)
    if not allowed:
        return True

    domain = getDomain(url)
    for tld in allowed:
        tld = tld if tld.startswith(".") else "." + tld
        if domain.endswith(tld):
            return True
    return False


def shouldCrawlUrl(rawUrl: str | None,baseUrl: str | None = None,allowedDomains: Iterable[str] | str | None = None
                     ,allowedTlds: Iterable[str] | str | None = None,) -> str | None:
    
    """Return cleaned URL if it should be crawled, otherwise None."""
    cleaned = normalizeUrl(rawUrl, baseUrl)
    if cleaned is None:
        return None
    if not isAllowedDomain(cleaned, allowedDomains):
        return None
    if not isAllowedTld(cleaned, allowedTlds):
        return None
    return cleaned
