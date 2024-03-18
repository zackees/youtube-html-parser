# pylint: disable=import-outside-toplevel

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from youtube_html_parser.types import ChannelId, VideoId, channel_to_url, video_to_url


@dataclass
class YtPage:
    """Dataclass to hold the parsed data."""

    video_id: VideoId | None
    title: str
    channel_id: ChannelId | None
    up_next_videos: list[VideoId]

    def video_url(self) -> str | None:
        """Return the video URL."""
        # return f"https://www.youtube.com/watch?v={self.video_id}"
        return video_to_url(self.video_id) if self.video_id else None

    def channel_url(self) -> str | None:
        """Return the channel URL."""
        # return f"https://www.youtube.com/channel/{self.channel_id}"
        return channel_to_url(self.channel_id) if self.channel_id else None

    def up_next_videos_urls(self) -> list[str]:
        """Return the up next videos."""
        return [video_to_url(video_id) for video_id in self.up_next_videos if video_id]

    def serialize(self) -> str:
        """Serialize the data."""
        out: dict[str, Any] = {
            "video_id": self.video_id,
            "title": self.title,
            "channel_id": self.channel_id,
            "up_next_video_ids": self.up_next_videos,
        }
        # extend to include the URLs
        out["video_url"] = self.video_url()
        out["channel_url"] = self.channel_url()
        out["up_next_video_urls"] = self.up_next_videos_urls()
        return json.dumps(out, indent=2)

    def write_json(self, outfile: Path) -> None:
        """Write the data to a JSON file."""
        outfile.write_text(self.serialize(), encoding="utf-8")
