from __future__ import annotations
from .url_utils import shouldCrawlUrl


def extractCleanLinks(response,allowedDomains=None,allowedTlds=None, maxLinksPerPage: int | None = None,) -> list[str]:
    # Extract, normalize, filter, and de-duplicate links from a Scrapy response
    rawLinks = response.css("a::attr(href)").getall()
    cleanedLinks: list[str] = []
    seen: set[str] = set()

    for rawLink in rawLinks:
        cleaned = shouldCrawlUrl(rawUrl=rawLink,baseUrl=response.url,allowedDomains=allowedDomains,allowedTlds=allowedTlds,)
        if cleaned is None or cleaned in seen:
            continue
        seen.add(cleaned)
        cleanedLinks.append(cleaned)
        if maxLinksPerPage is not None and len(cleanedLinks) >= maxLinksPerPage:
            break

    return cleanedLinks
