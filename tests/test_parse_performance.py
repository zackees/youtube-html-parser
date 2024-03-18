# pylint: disable=too-many-branches

"""
Unit test file.
"""

import time
import unittest
from pathlib import Path

from youtube_html_parser.parser import parse_yt_page

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

    def test_parse_performance(self) -> None:
        """Test the performance of parsing."""
        print("Testing performance of parsing.")
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        start = time.time()
        for _ in range(10):
            _ = invoke_parse_py(test_html)
        # print(parsed_json)
        dif = time.time() - start
        print(f"Time taken: {dif}")


if __name__ == "__main__":
    unittest.main()
