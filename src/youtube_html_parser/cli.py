"""
Main entry point.
"""

import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from youtube_html_parser.parser import parse_yt_page


def main() -> int:
    """Main entry point for the template_python_cmd package."""
    parser = ArgumentParser()
    parser.add_argument("--input-html", help="The HTML file to parse.", required=True)
    parser.add_argument("--output-json", help="The output json.", required=True)
    args = parser.parse_args()
    infile = Path(args.input_html)
    outfile = Path(args.output_json)
    html = infile.read_text(encoding="utf-8")
    start_time = time.time()
    parsed = parse_yt_page(html)
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time:.2f} seconds.")
    parsed.write_json(outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
