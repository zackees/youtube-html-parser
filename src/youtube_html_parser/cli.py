"""
Main entry point.
"""

import sys
import time
from argparse import ArgumentParser

# import gunzip
from gzip import GzipFile
from pathlib import Path
from tempfile import TemporaryDirectory

from youtube_html_parser.parser import (
    YtPage,
    YtPageSearch,
    parse_yt_page,
    parse_yt_page_seach,
)


def extract_html(infile: Path) -> str:
    """Extract the HTML from the file."""
    if infile.suffix == ".html":
        return infile.read_text(encoding="utf-8")
    if infile.suffix == ".gz":
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            temp_file = temp_dir_path / "temp.html"
            with GzipFile(infile, "r") as gzfile:
                data = gzfile.read()
                temp_file.write_text(data.decode("utf-8"), encoding="utf-8")
            return temp_file.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported file type: {infile.suffix} in {infile}.")


def main() -> int:
    """Main entry point for the template_python_cmd package."""
    parser = ArgumentParser()
    parser.add_argument("--input-html", help="The HTML file to parse.", required=True)
    parser.add_argument("--output-json", help="The output json.", required=True)
    parser.add_argument("--search", help="Parse a search page.", action="store_true")
    args = parser.parse_args()
    infile = Path(args.input_html)
    outfile = Path(args.output_json)
    html = extract_html(infile)
    start_time = time.time()
    parsed: YtPage | YtPageSearch
    if args.search:
        parsed = parse_yt_page_seach(html)
    else:
        parsed = parse_yt_page(html)
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time:.2f} seconds.")
    parsed.write_json(outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
