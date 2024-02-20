"""
Unit test file.
"""
from pathlib import Path
import unittest

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))




class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_loading(self) -> None:
        """Test command line interface (CLI)."""
        data: dict[Path, str] = {}
        for test_html in TEST_HTML:
            data[test_html] = test_html.read_text(encoding="utf-8")
        self.assertTrue(data)
            


if __name__ == "__main__":
    unittest.main()