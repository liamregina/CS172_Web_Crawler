def is_valid_link(link):
    """
    Return True if the link should be followed by the crawler.
    Return False otherwise.
    """
    pass


def get_valid_links(response):
    """
    Extract all links from the response and return only the valid ones.
    """
    links = response.css("a::attr(href)").getall()
    return [link for link in links if is_valid_link(link)]