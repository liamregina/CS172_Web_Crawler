import re
from html import unescape
from pathlib import Path


def clean_text(text):
    if not text:
        return ""
    text = unescape(str(text))
    text = re.sub(r"\s+", " ", text)      # collapse whitespace
    text = re.sub(r'\.+', '.', text)       # collapse multiple periods
    text = re.sub(r'\s+\.', '.', text)     # remove space before periods
    return text.strip()


def remove_script_and_style(html):
    # Removing script, style, and noscript sections from raw HTML.

    html = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style.*?>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<noscript.*?>.*?</noscript>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def extract_tag_text(html, tag):

    # Extracting text from a specific tag, ex: like title, h1, h2, h3.

    pattern = rf"<{tag}.*?>(.*?)</{tag}>"
    matches = re.findall(pattern, html, flags=re.DOTALL | re.IGNORECASE)

    cleaned_matches = []
    for match in matches:
        text = remove_html_tags(match)
        text = clean_text(text)
        if text:
            cleaned_matches.append(text)

    return " ".join(cleaned_matches)


def remove_html_tags(html):
    
    # Removing all HTML tags and keep only text.

    return re.sub(r"<.*?>", " ", html, flags=re.DOTALL)


def parse_html_string(html):

    # Parsing raw HTML and return title, headers, and body.
  
    if not html:
        return {
            "title": "",
            "headers": "",
            "body": "",
        }
    html = remove_script_and_style(html)

    title = extract_tag_text(html, "title")

    headers = " ".join([
        extract_tag_text(html, "h1"),
        extract_tag_text(html, "h2"),
        extract_tag_text(html, "h3"),
    ])

    body_html = extract_tag_text(html, "body")

    # So if body tag is missing, use all page text as fallback.
    if not body_html:
        body_html = remove_html_tags(html)

    return {
        "title": clean_text(title),
        "headers": clean_text(headers),
        "body": clean_text(body_html),
    }

def replace_block_tags_with_periods(html):
    # Replace closing block-level tags with periods so they become sentence boundaries
    block_tags = r'</(p|br|div|tr|td|li|h1|h2|h3|h4|h5|h6)>'
    html = re.sub(block_tags, '. ', html, flags=re.IGNORECASE)
    return html

def parse_html_file(html_file):

    # Read an HTML file and parse it.

    path = Path(html_file)

    if not path.exists():
        return {
            "title": "",
            "headers": "",
            "body": "",
        }

    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {
            "title": "",
            "headers": "",
            "body": "",
        }
        html = replace_block_tags_with_periods(html) # convert block tags to sentence boundaries
    return parse_html_string(html)