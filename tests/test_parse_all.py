# pylint: disable=too-many-branches

"""
Unit test file.
"""


import unittest
from pathlib import Path
from warnings import warn

from youtube_html_parser.parser import YtPage, parse_yt_page

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
                bad.append(test_html.name)
        if bad:
            self.fail(f"Failed to parse {len(bad)} files: {bad}")


if __name__ == "__main__":
    unittest.main()
