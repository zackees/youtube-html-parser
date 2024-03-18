# pylint: disable=too-many-branches

"""
Unit test file.
"""


import unittest
from pathlib import Path
from warnings import warn

from youtube_html_parser.parser import YtPageSearch, parse_yt_page_seach

ENABLE_FETCH_UP_NEXT_VIDEOS = False

HERE = Path(__file__).parent
SEARCH_HTML = HERE / "data" / "search_html"
assert SEARCH_HTML.exists()

TEST_HTML = list(SEARCH_HTML.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]


class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_all_data_files(self) -> None:
        """Just test the first element in the list."""
        bad: list[str] = []
        for test_html in TEST_HTML:
            print(f"Testing {test_html.name}")
            html = test_html.read_text(encoding="utf-8")
            try:
                _: YtPageSearch = parse_yt_page_seach(html)
            except Exception as exc:  # pylint: disable=broad-except
                warn(f"Failed to parse {test_html.name}: {exc}")
                bad.append(test_html.name)
        if bad:
            self.fail(f"Failed to parse {len(bad)} files: {bad}")


if __name__ == "__main__":
    unittest.main()
