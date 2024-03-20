"""
Unit test file.
"""

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

HTML_GZ = DATA_DIR / "yt-1c2402c189252cad7e3e74fe966b888f-1708156846826.html.gz"

COMMAND = "youtube-html-parser"


class MainTester(unittest.TestCase):
    """Main tester class."""

    def test_imports(self) -> None:
        """Test command line interface (CLI)."""
        inhtml_gz = HTML_GZ.absolute()
        with TemporaryDirectory() as tmpdir:
            outjson = Path(tmpdir) / "test.json"
            cmd = f"{COMMAND} --input-html {inhtml_gz} --output-json {outjson}"
            rtn = os.system(cmd)
            self.assertEqual(0, rtn)
            self.assertTrue(outjson.exists())
            # parses the JSON file
            data_str = outjson.read_text(encoding="utf-8")
            data = json.loads(data_str)
            self.assertIn("video_id", data)
            self.assertIn("title", data)
            self.assertIn("channel_id", data)
            self.assertIn("video_url", data)
            self.assertIn("channel_url", data)
            self.assertIn("up_next_video_urls", data)
            # assert equality
            self.assertEqual("jqiVn9nWiiQ", data["video_id"])
            self.assertEqual(
                "KAMA UNA WIVU UWEZI KUANGALIA NANDY NA BILLNASS WALIVYOLISHANA KEKI!",
                data["title"],
            )
            self.assertEqual("UCu2uabLB7WHhkhdcLV5BcZg", data["channel_id"])


if __name__ == "__main__":
    unittest.main()
