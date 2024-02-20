"""
Unit test file.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import unittest
import json

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


class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_first(self) -> None:
        """Just test the first element in the list."""
        with open(TEST_HTML[0], "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            video_ids = parse_out_self_video_ids(soup)
            self.assertEqual(len(video_ids), 1)
            print(video_ids[0])
            print()
            #urls = parse_urls(soup)
            #self.assertTrue(urls)
            #print(urls)



if __name__ == "__main__":
    unittest.main()
