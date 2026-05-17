import unittest
from filtering import filter_link, is_valid_url, is_crawlable_scheme, is_html_resource


class TestIsValidUrl(unittest.TestCase):
    """Test cases for is_valid_url function"""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL"""
        self.assertTrue(is_valid_url("http://example.com"))
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL"""
        self.assertTrue(is_valid_url("https://example.com"))
    
    def test_valid_url_with_path(self):
        """Test valid URL with path"""
        self.assertTrue(is_valid_url("https://example.com/path/to/page"))
    
    def test_valid_url_with_query(self):
        """Test valid URL with query parameters"""
        self.assertTrue(is_valid_url("https://example.com?param=value"))
    
    def test_empty_string(self):
        """Test empty string"""
        self.assertFalse(is_valid_url(""))
    
    def test_none_value(self):
        """Test None value"""
        self.assertFalse(is_valid_url(None))
    
    def test_non_string_value(self):
        """Test non-string value"""
        self.assertFalse(is_valid_url(123))
        self.assertFalse(is_valid_url([]))
    
    def test_malformed_url(self):
        """Test malformed URL"""
        self.assertFalse(is_valid_url("not a url"))


class TestIsCrawlableScheme(unittest.TestCase):
    """Test cases for is_crawlable_scheme function"""
    
    def test_http_scheme(self):
        """Test HTTP scheme"""
        self.assertTrue(is_crawlable_scheme("http://example.com"))
    
    def test_https_scheme(self):
        """Test HTTPS scheme"""
        self.assertTrue(is_crawlable_scheme("https://example.com"))
    
    def test_ftp_scheme(self):
        """Test FTP scheme (non-crawlable)"""
        self.assertFalse(is_crawlable_scheme("ftp://example.com"))
    
    def test_mailto_scheme(self):
        """Test mailto: scheme (non-crawlable)"""
        self.assertFalse(is_crawlable_scheme("mailto:test@example.com"))
    
    def test_javascript_scheme(self):
        """Test javascript: scheme (non-crawlable)"""
        self.assertFalse(is_crawlable_scheme("javascript:void(0)"))
    
    def test_file_scheme(self):
        """Test file: scheme (non-crawlable)"""
        self.assertFalse(is_crawlable_scheme("file:///path/to/file"))
    
    def test_tel_scheme(self):
        """Test tel: scheme (non-crawlable)"""
        self.assertFalse(is_crawlable_scheme("tel:+1234567890"))
    
    def test_case_insensitive(self):
        """Test case insensitivity"""
        self.assertTrue(is_crawlable_scheme("HTTP://example.com"))
        self.assertTrue(is_crawlable_scheme("HTTPS://example.com"))


class TestIsHtmlResource(unittest.TestCase):
    """Test cases for is_html_resource function"""
    
    def test_html_page(self):
        """Test regular HTML page"""
        self.assertTrue(is_html_resource("https://example.com/page.html"))
    
    def test_no_extension(self):
        """Test URL with no extension"""
        self.assertTrue(is_html_resource("https://example.com/page"))
    
    def test_pdf_file(self):
        """Test PDF file (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/document.pdf"))
    
    def test_image_files(self):
        """Test image files (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/image.jpg"))
        self.assertFalse(is_html_resource("https://example.com/image.png"))
        self.assertFalse(is_html_resource("https://example.com/icon.svg"))
    
    def test_video_files(self):
        """Test video files (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/video.mp4"))
        self.assertFalse(is_html_resource("https://example.com/video.avi"))
    
    def test_audio_files(self):
        """Test audio files (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/audio.mp3"))
        self.assertFalse(is_html_resource("https://example.com/audio.wav"))
    
    def test_document_files(self):
        """Test document files (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/doc.pdf"))
        self.assertFalse(is_html_resource("https://example.com/doc.docx"))
        self.assertFalse(is_html_resource("https://example.com/sheet.xlsx"))
    
    def test_archive_files(self):
        """Test archive files (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/archive.zip"))
        self.assertFalse(is_html_resource("https://example.com/archive.tar.gz"))
    
    def test_css_file(self):
        """Test CSS file (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/style.css"))
    
    def test_javascript_file(self):
        """Test JavaScript file (non-HTML)"""
        self.assertFalse(is_html_resource("https://example.com/script.js"))
    
    def test_case_insensitive_extensions(self):
        """Test case insensitivity of extensions"""
        self.assertFalse(is_html_resource("https://example.com/image.JPG"))
        self.assertFalse(is_html_resource("https://example.com/document.PDF"))


class TestFilterLink(unittest.TestCase):
    """Test cases for filter_link function"""
    
    def test_valid_http_link(self):
        """Test valid HTTP link"""
        self.assertTrue(filter_link("http://example.com"))
    
    def test_valid_https_link(self):
        """Test valid HTTPS link"""
        self.assertTrue(filter_link("https://example.com/page"))
    
    def test_empty_link(self):
        """Test empty link"""
        self.assertFalse(filter_link(""))
    
    def test_none_link(self):
        """Test None link"""
        self.assertFalse(filter_link(None))
    
    def test_mailto_link(self):
        """Test mailto link (should be rejected)"""
        self.assertFalse(filter_link("mailto:test@example.com"))
    
    def test_javascript_link(self):
        """Test javascript link (should be rejected)"""
        self.assertFalse(filter_link("javascript:void(0)"))
    
    def test_pdf_link(self):
        """Test PDF link (should be rejected)"""
        self.assertFalse(filter_link("https://example.com/document.pdf"))
    
    def test_image_link(self):
        """Test image link (should be rejected)"""
        self.assertFalse(filter_link("https://example.com/image.png"))
    
    def test_valid_with_query_params(self):
        """Test valid link with query parameters"""
        self.assertTrue(filter_link("https://example.com/page?id=123&name=test"))
    
    def test_valid_with_fragment(self):
        """Test valid link with fragment"""
        self.assertTrue(filter_link("https://example.com/page#section"))
    
    def test_ftp_link(self):
        """Test FTP link (should be rejected)"""
        self.assertFalse(filter_link("ftp://example.com/file"))
    
    def test_malformed_link(self):
        """Test malformed link"""
        self.assertFalse(filter_link("not a valid link"))


class TestIntegration(unittest.TestCase):
    """Integration tests for realistic scenarios"""
    
    def test_blog_post_should_pass(self):
        """Test that a blog post URL should pass"""
        self.assertTrue(filter_link("https://myblog.com/posts/2024/interesting-article"))
    
    def test_news_article_should_pass(self):
        """Test that a news article URL should pass"""
        self.assertTrue(filter_link("https://news.example.com/world/breaking"))
    
    def test_api_endpoint_should_pass(self):
        """Test that an API endpoint URL should pass (no extension)"""
        self.assertTrue(filter_link("https://api.example.com/data"))
    
    def test_stylesheet_should_fail(self):
        """Test that a stylesheet should be rejected"""
        self.assertFalse(filter_link("https://example.com/css/style.css"))
    
    def test_script_should_fail(self):
        """Test that a script should be rejected"""
        self.assertFalse(filter_link("https://example.com/js/app.js"))
    
    def test_download_link_should_fail(self):
        """Test that a download link should be rejected"""
        self.assertFalse(filter_link("https://example.com/downloads/software.zip"))
    
    def test_relative_link_should_fail(self):
        """Test that a relative link should be rejected"""
        self.assertFalse(filter_link("/relative/path"))
    
    def test_anchor_only_should_fail(self):
        """Test that an anchor-only link should be rejected"""
        self.assertFalse(filter_link("#section"))


if __name__ == '__main__':
    unittest.main()
