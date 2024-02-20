"""
Main entry point.
"""

import sys
from argparse import ArgumentParser
from pathlib import Path

from youtube_html_parser.parser import parse_yt_page


def main() -> int:
    """Main entry point for the template_python_cmd package."""
    parser = ArgumentParser()
    parser.add_argument("--input-html", help="The HTML file to parse.")
    parser.add_argument("--output-json", help="The output json.")
    args = parser.parse_args()
    infile = Path(args.input_html)
    outfile = Path(args.output_json)
    html = infile.read_text(encoding="utf-8")
    parsed = parse_yt_page(html)
    parsed.write_json(outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
