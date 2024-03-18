# pylint: disable=too-many-branches

"""
Unit test file.
"""


import traceback
import unittest
from pathlib import Path
from warnings import warn

from youtube_html_parser.parser import YtPage, parse_yt_page

ENABLE_FETCH_UP_NEXT_VIDEOS = False

HERE = Path(__file__).parent
SEARCH_HTML = HERE / "data" / "error"
assert SEARCH_HTML.exists()

TEST_HTML = list(SEARCH_HTML.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]


class ParseErrorsTester(unittest.TestCase):
    """Main tester class."""

    # @unittest.skip("Skip while we concentrate on one file.")
    def test_all_data_files(self) -> None:
        """Just test the first element in the list."""
        bad: list[str] = []
        for test_html in TEST_HTML:
            print(f"Testing {test_html.name}")
            html = test_html.read_text(encoding="utf-8")
            try:
                _: YtPage = parse_yt_page(html)
            except Exception as exc:  # pylint: disable=broad-except
                warn(f"Failed to parse {test_html.name}: {exc}")
                traceback.print_exc()
                bad.append(test_html.name)
        if bad:
            self.fail(f"Failed to parse {len(bad)} files: {bad}")

    @unittest.skip("Problematic html sources are tested manually here.")
    def test_one_bad_file(self) -> None:
        """Test one bad file."""
        bad_file = SEARCH_HTML / "yt_2022-09-21_926.html"
        html = bad_file.read_text(encoding="utf-8")
        _: YtPage = parse_yt_page(html)


if __name__ == "__main__":
    unittest.main()
