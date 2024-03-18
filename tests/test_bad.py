# pylint: disable=too-many-branches

"""
Unit test file.
"""


import unittest
from pathlib import Path

import re

from youtube_html_parser.parser import YtPage, parse_yt_page


# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
BAD_FILE = DATA_DIR / "search_html" / "yt_2022-09-01_1.html"
assert BAD_FILE.exists()


def parse_all_watchable_links(html: str) -> list[str]:
    """Parse out all the hrefs from the HTML."""
    # parse out all the hrefs of the vorm watch?v=VIDEO_ID
    hrefs = re.findall(r'watch\?v=[\w-]+', html)
    href_set = set([])
    hrefs_out = []
    for href in hrefs:
        if href not in href_set:
            href_set.add(href)
            hrefs_out.append(href)
    
    # now remove all watch?v= from the hrefs
    hrefs_out = [href.replace("watch?v=", "") for href in hrefs_out]
    return hrefs_out

def parse_all_image_links(html: str) -> list[str]:
    """Parse out all the image links from the HTML."""
    # parse out all the hrefs of the vorm watch?v=VIDEO_ID
    pattern = r'https://i.ytimg.com/vi/[\w-]+/[\w-]+.jpg'
    hrefs = re.findall(pattern, html)
    href_set = set([])
    hrefs_out = []
    for href in hrefs:
        if href not in href_set:
            href_set.add(href)
            hrefs_out.append(href)
    return hrefs_out


class ParseTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skipIf(True, "disabled for now")
    def test_one_bad_file(self) -> None:
        print(f"Testing {BAD_FILE.name}")
        html = BAD_FILE.read_text(encoding="utf-8")
        _: YtPage = parse_yt_page(html)
        print(f"Successfully parsed {BAD_FILE.name}")

    def test_parse_all_hrefs(self) -> None:
        """Just test the first element in the list."""
        html = BAD_FILE.read_text(encoding="utf-8")
        hrefs = parse_all_watchable_links(html)
        print(f"Found {len(hrefs)} hrefs.")
        print(hrefs)
        hrefs = parse_all_image_links(html)
        print(f"Found {len(hrefs)} image links.")
        print(hrefs)
        print()


if __name__ == "__main__":
    unittest.main()
