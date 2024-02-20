#!/bin/bash
. ./activate.sh
pip install nuitka==2.0.3
python -m nuitka --standalone --follow-imports --onefile --mingw --lto=yes src/youtube_html_parser/cli.py