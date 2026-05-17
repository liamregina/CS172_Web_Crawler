from __future__ import annotations
import hashlib
from scrapy.dupefilters import RFPDupeFilter
from .url_utils import normalizeUrl


class CanonicalURLDupeFilter(RFPDupeFilter):
    """
    Stronger request duplicate filter using normalized URLs.

    It treats URLs that only differ by anchors, default ports, tracking parameters,
    or trailing slashes as the same crawl target.
    """

    def requestFingerprint(self, request) -> str:
        canonicalUrl = normalizeUrl(request.url) or request.url
        return hashlib.sha1(canonicalUrl.encode("utf-8", errors="ignore")).hexdigest()

    def requestSeen(self, request) -> bool:
        fingerprint = self.requestFingerprint(request)
        if fingerprint in self.fingerprints:
            return True
        self.fingerprints.add(fingerprint)
        if self.file:
            self.file.write(fingerprint + "\n")
        return False
    
    # Keeping this consistent with camel casing
    def request_seen(self, request) -> bool:
        return self.requestSeen(request)
