# Link filtering responsibilities:
# - reject non-crawlable links such as mailto: and javascript:
# - skip links to non-HTML resources like PDFs and image files
# - reject empty, malformed, or otherwise invalid links

from urllib.parse import urlparse

def filter_link(url):
    """
    Filter a link and determine if it should be crawled.
    
    Args:
        url: The URL string to filter
        
    Returns:
        bool: True if the link should be crawled, False otherwise
    """
    # Check if URL is empty or malformed
    if not is_valid_url(url):
        return False
    
    # Check if the scheme is crawlable (http/https)
    if not is_crawlable_scheme(url):
        return False
    
    # Check if it's an HTML resource
    if not is_html_resource(url):
        return False
    
    return True

def is_valid_url(url):
    """
    Check if a URL is valid and well-formed.
    
    Args:
        url: The URL string to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        # A valid URL should have at least a scheme or netloc
        return bool(result.scheme or result.netloc)
    except Exception:
        return False


def is_crawlable_scheme(url):
    """
    Check if the URL has a crawlable scheme (http/https).
    Reject non-crawlable schemes like mailto:, javascript:, ftp:, etc.
    
    Args:
        url: The URL string to check
        
    Returns:
        bool: True if the scheme is crawlable, False otherwise
    """
    try:
        scheme = urlparse(url).scheme.lower()
        return scheme in ('http', 'https')
    except Exception:
        return False


def is_html_resource(url):
    """
    Check if the URL points to an HTML resource.
    Skip links to non-HTML resources like PDFs, images, etc.
    
    Args:
        url: The URL string to check
        
    Returns:
        bool: True if it's likely an HTML resource, False otherwise
    """
    # Non-HTML file extensions to skip
    non_html_extensions = {
        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv',
        '.mp3', '.wav', '.flac', '.aac',
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.exe', '.bin', '.iso', '.dmg',
        '.css', '.js',
    }
    
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check if path has a non-HTML extension
        for ext in non_html_extensions:
            if path.endswith(ext):
                return False
        
        return True
    except Exception:
        return True  # Default to allowing if we can't parse


def get_valid_links(response):
    raw_links = response.css("a::attr(href)").getall()
    return [link for link in raw_links if filter_link(link)]