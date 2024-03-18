# pylint: disable=too-many-branches

"""
Unit test file.
"""


import unittest
from pathlib import Path

from youtube_html_parser.parser import YtPage, parse_yt_page

ENABLE_FETCH_UP_NEXT_VIDEOS = False

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()


class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_one_bad_file(self) -> None:
        bad_file = "yt_2022-09-01_1.html"
        test_html = DATA_DIR / bad_file
        print(f"Testing {test_html.name}")
        html = test_html.read_text(encoding="utf-8")
        _: YtPage = parse_yt_page(html)
        print(f"Successfully parsed {test_html.name}")


if __name__ == "__main__":
    unittest.main()
