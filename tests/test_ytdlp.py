"""
Unit test file.
"""

import unittest

from youtube_html_parser.ytdlp import fetch_channel_url_ytdlp


class TestYtDlp(unittest.TestCase):
    """Main tester class."""

    def test_fetch_channel_url_ytdlp(self) -> None:
        """Test command line interface (CLI)."""
        url = "https://www.youtube.com/watch?v=bW0PAutJkQQ"
        url = fetch_channel_url_ytdlp(url)
        self.assertIsInstance(url, str)
        self.assertEqual(
            url, "https://www.youtube.com/channel/UCJqYySus8eH79ehAr7gGj3g"
        )


if __name__ == "__main__":
    unittest.main()
