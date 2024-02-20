"""
Unit test file.
"""
from pathlib import Path
from bs4 import BeautifulSoup
# import beautiful soup exceptions
from bs4 import FeatureNotFound
import unittest
import json
import warnings

import re
HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]

def parse_out_self_video_ids(soup: BeautifulSoup) -> list[str]:
    """Parse out the video URL from a self post."""
    content_div = soup.find("div", {"id": "content"}, class_="ytd-app")
    video_ids: list[str] = []
    ytwatch_flexy = content_div.find("ytd-watch-flexy")
    for script in ytwatch_flexy.find_all("script", type="application/ld+json"):
        json_data = json.loads(script.get_text())
        embed_url = json_data.get("embedUrl")
        video_id = embed_url.split("/")[-1]
        video_ids.append(video_id)
    return video_ids


def parse_out_up_next_videos(soup: BeautifulSoup) -> list[str]:
    """Parse out the video URL from the up next videos."""
    video_ids: list[str] = []
    try:
        # div id="secondary"
        secondary_div = soup.find("div", {"id": "secondary", "class": "ytd-watch-flexy"})
        # now within this is div id="related"
        related_div = secondary_div.find("div", {"id": "related"})
        # ytd-watch-next-secondary-results-renderer
        ytd_watch_container = related_div.find("ytd-watch-next-secondary-results-renderer")
        # print(ytd_watch)
        items = ytd_watch_container.find_all("ytd-compact-video-renderer")
        for item in items:
            try:
                # get the <a id="thumbnail"
                a_tag = item.find("a", {"id": "thumbnail"})
                href = a_tag["href"]
                video_id = href.split("=")[-1]
                video_ids.append(video_id)
            except FeatureNotFound as e:  # pylint: disable=broad-except
                warnings.warn(f"Error: {e}")

        # now within this is div id="related"
        #related_div = secondary_div.find("div", {"id": "related"})
        #print(related_div)
        # ytd-watch-next-secondary-results-renderer
        #ytd_watch = secondary_div.find("ytd-watch-next-secondary-results-renderer")
        #print(ytd_watch)
    except FeatureNotFound as e:  # pylint: disable=broad-except
        warnings.warn(f"Error: {e}")
    return video_ids

class ParseTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skip("Not implemented yet.")
    def test_get_self_video_id(self) -> None:
        """Just test the first element in the list."""
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        soup = BeautifulSoup(test_html, "html.parser")
        video_ids = parse_out_self_video_ids(soup)
        self.assertEqual(len(video_ids), 1)
        print(f"Found video id: {video_ids[0]}")
        print(video_ids[0])

    def test_get_up_next_videos(self) -> None:
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        soup = BeautifulSoup(test_html, "html.parser")
        video_ids = parse_out_up_next_videos(soup)
        print(f"Found {len(video_ids)} video ids.")
        print(video_ids)



if __name__ == "__main__":
    unittest.main()
