# pylint: disable=too-many-branches

"""
Unit test file.
"""

import unittest
from pathlib import Path

from youtube_html_parser.parser import (
    YtPage,
    create_soup,
    parse_out_self_video_ids,
    parse_out_up_next_videos,
    parse_yt_page,
)

ENABLE_FETCH_UP_NEXT_VIDEOS = False

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]


PROJECT_ROOT = HERE.parent


def invoke_parse_py(html: str) -> str:
    parsed_data = parse_yt_page(html)
    return parsed_data.serialize()


class ParseTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skip("Not implemented yet.")
    def test_get_self_video_id(self) -> None:
        """Just test the first element in the list."""
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        soup = create_soup(test_html)
        video_ids = parse_out_self_video_ids(soup)
        self.assertEqual(len(video_ids), 1)
        print(f"Found video id: {video_ids[0]}")
        print(video_ids[0])

    def test_get_up_next_videos(self) -> None:
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        # soup = BeautifulSoup(test_html, "lxml")
        soup = create_soup(test_html)
        video_ids = parse_out_up_next_videos(soup, test_html)
        print(f"Found {len(video_ids)} video ids.")
        print(video_ids)

    def test_parse(self) -> None:
        """Test the parse_yt_page function."""
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        parsed = parse_yt_page(test_html)
        self.assertIsInstance(parsed, YtPage)
        print(parsed)
        print(parsed.video_url())
        print(parsed.channel_url())
        print()


if __name__ == "__main__":
    unittest.main()
