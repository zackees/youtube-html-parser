"""
Unit test file.
"""

import unittest

from youtube_html_parser.types import VideoId
from youtube_html_parser.ytdlp import (
    fetch_channel_url_ytdlp,
    fetch_videos_from_youtube_channel,
)


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

    @unittest.skip("SLOW")
    def test_fetch_videos_from_channel(self) -> None:
        """Test command line interface (CLI)."""
        zachs_channel_id = "UCiuTGTCkYrjVknhvMAICFjA"
        videos = fetch_videos_from_youtube_channel(zachs_channel_id)
        self.assertIsInstance(videos, list)
        self.assertTrue(len(videos) > 0)
        expected_video_ids: set[VideoId] = set(
            [
                VideoId("iTtFge_ZhJ0"),
                VideoId("w_QWrzjKC9I"),
                VideoId("627MtKeLvxU"),
                VideoId("p8sauzU-ZVY"),
                VideoId("9b9fV0xkU5M"),
                VideoId("2cKHc0NTgIQ"),
                VideoId("iXIy915c8tg"),
                VideoId("bDud_2vCSDs"),
                VideoId("k-JJXheCNYQ"),
                VideoId("7ER3T7CQVss"),
            ]
        )
        for video in videos:
            self.assertIn(video, expected_video_ids)


if __name__ == "__main__":
    unittest.main()
