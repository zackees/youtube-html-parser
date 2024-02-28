import subprocess
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]
PROJECT_ROOT = HERE.parent


CLI_EXE = PROJECT_ROOT / "cli.exe"

assert CLI_EXE.exists()


def invoke_parse_cli(html: str) -> str:
    args = [str(CLI_EXE)]
    with tempfile.TemporaryDirectory() as temp_dir:
        cwd = Path(temp_dir)
        inputfile = cwd / "temp.html"
        outfile = cwd / "temp.json"
        inputfile.write_text(html, encoding="utf-8")
        args.extend(["--input-html", "temp.html"])
        args.extend(["--output-json", "temp.json"])
        result = subprocess.run(args, shell=True, cwd=cwd, check=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to run {CLI_EXE} with args: {args}")
        # read the output file
        out = outfile.read_text(encoding="utf-8")
        return out


class ParseTester(unittest.TestCase):
    """Main tester class."""

    def test_cli_parse(self) -> None:
        """Test the CLI parsing."""
        print("Testing CLI parsing.")
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        start = time.time()
        for _ in range(10):
            _ = invoke_parse_cli(test_html)
        # print(parsed_json)
        dif = time.time() - start
        print(f"Time taken: {dif}")


if __name__ == "__main__":
    unittest.main()
