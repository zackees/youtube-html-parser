"""
Unit test file.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import unittest

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))




class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_loading(self) -> None:
        """Test command line interface (CLI)."""
        data: dict[Path, BeautifulSoup] = {}
        for test_html in TEST_HTML:
            with open(test_html, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                data[test_html] = soup
        self.assertTrue(data)
            


if __name__ == "__main__":
    unittest.main()
