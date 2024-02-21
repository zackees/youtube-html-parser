#!/bin/bash
. ./activate.sh
pip install nuitka==2.0.3
python -m nuitka --standalone --follow-imports --onefile --mingw --lto=yes --python-flag=-OO src/youtube_html_parser/web.py