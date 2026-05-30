from urllib.parse import urljoin, urlparse


NON_HTML_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm",
    ".mp3", ".wav", ".flac", ".aac", ".ogg",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".bin", ".iso", ".dmg",
    ".css", ".js", ".xml", ".json",
}


def filter_link(url):
    """Return True if the URL should be crawled by the basic crawler."""
    if not is_valid_url(url):
        return False
    if not is_crawlable_scheme(url):
        return False
    if not is_html_resource(url):
        return False
    return True


def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def is_crawlable_scheme(url):
    try:
        scheme = urlparse(url).scheme.lower()
        return scheme in ("http", "https")
    except Exception:
        return False


def is_html_resource(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        return not any(path.endswith(ext) for ext in NON_HTML_EXTENSIONS)
    except Exception:
        return False


def get_domain(url):
    return (urlparse(url).hostname or "").lower()


def is_allowed_domain(url, allowed_domains=None):
    if not allowed_domains:
        return True

    domain = get_domain(url)
    for allowed in allowed_domains:
        allowed = str(allowed).lower().strip()
        if domain == allowed or domain.endswith("." + allowed):
            return True
    return False


def get_valid_links(response, allowed_domains=None, max_links_per_page=None):
    raw_links = response.css("a::attr(href)").getall()
    valid_links = []
    seen = set()

    for raw_link in raw_links:
        absolute_link = response.urljoin(raw_link) if hasattr(response, "urljoin") else urljoin(response.url, raw_link)

        if not filter_link(absolute_link):
            continue
        if not is_allowed_domain(absolute_link, allowed_domains):
            continue
        if absolute_link in seen:
            continue

        seen.add(absolute_link)
        valid_links.append(absolute_link)

        if max_links_per_page is not None and len(valid_links) >= max_links_per_page:
            break

    return valid_links
