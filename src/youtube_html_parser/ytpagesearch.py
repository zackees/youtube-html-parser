# pylint: disable=import-outside-toplevel

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from youtube_html_parser.types import VideoId, video_to_url


@dataclass
class YtPageSearch:
    """Dataclass to hold the parsed data."""

    search_results: list[VideoId]

    def video_urls(self) -> list[str]:
        """Return the video URL."""
        # return f"https://www.youtube.com/watch?v={self.video_id}"
        return [video_to_url(video_id) for video_id in self.search_results]

    def serialize(self) -> str:
        """Serialize the data."""
        out: dict[str, Any] = {
            "search_results": self.search_results,
        }
        return json.dumps(out, indent=2)

    def write_json(self, outfile: Path) -> None:
        """Write the data to a JSON file."""
        outfile.write_text(self.serialize(), encoding="utf-8")
