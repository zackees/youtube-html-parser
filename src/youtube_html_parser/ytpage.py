import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from youtube_html_parser.fetch import resolve_channel_ids
from youtube_html_parser.types import ChannelId, VideoId, channel_to_url, video_to_url


@dataclass
class YtPage:
    """Dataclass to hold the parsed data."""

    video_id: VideoId
    title: str
    channel_id: ChannelId
    up_next_videos: dict[VideoId, ChannelId | None]

    def video_url(self) -> str:
        """Return the video URL."""
        # return f"https://www.youtube.com/watch?v={self.video_id}"
        return video_to_url(self.video_id)

    def channel_url(self) -> str:
        """Return the channel URL."""
        # return f"https://www.youtube.com/channel/{self.channel_id}"
        return channel_to_url(self.channel_id)

    def up_next_videos_urls(self) -> dict[str, str | None]:
        """Return the up next videos."""
        out: dict[str, str | None] = {}
        for video_id, channel_id in self.up_next_videos.items():
            channel_url: str | None = None
            if channel_id is not None:
                # channel_url = f"https://www.youtube.com/channel/{channel_id}"
                channel_url = channel_to_url(channel_id)
            out[f"https://www.youtube.com/watch?v={video_id}"] = channel_url
        return out

    def serialize(self) -> str:
        """Serialize the data."""
        out: dict[str, Any] = {
            "video_id": self.video_id,
            "title": self.title,
            "channel_id": self.channel_id,
            "up_next_video_ids": list(self.up_next_videos.keys()),
        }
        # extend to include the URLs
        out["video_url"] = self.video_url()
        out["channel_url"] = self.channel_url()
        out["up_next_video_urls"] = self.up_next_videos_urls()
        return json.dumps(out, indent=2)

    def write_json(self, outfile: Path) -> None:
        """Write the data to a JSON file."""
        outfile.write_text(self.serialize(), encoding="utf-8")

    def resolve_up_next_video_channels(self) -> None:
        """Fetch the channel id for the parsed video ids."""
        self.up_next_videos = resolve_channel_ids(self.up_next_videos)
