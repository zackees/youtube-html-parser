# pylint: disable=too-many-branches

import json
import re
import traceback
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound


class VideoId(str):
    pass


class ChannelId(str):
    pass


def channel_to_url(channel_id: ChannelId) -> str:
    """Convert the channel id to a URL."""
    return f"https://www.youtube.com/channel/{channel_id}"


def video_to_url(video_id: VideoId) -> str:
    """Convert the video id to a URL."""
    return f"https://www.youtube.com/watch?v={video_id}"


@dataclass
class ParsedYtPage:
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

    def fetch_up_next_channels(self) -> None:
        """Fetch the channel id for the parsed video ids."""
        for video_id, channel_id in self.up_next_videos.items():
            if channel_id is not None:
                continue
            try:
                channel_id = fetch_channel_id(video_id)
                self.up_next_videos[video_id] = channel_id
            except requests.HTTPError as http_err:
                traceback_str = traceback.format_exc()
                warnings.warn(f"HTTP error occurred: {http_err}\n\n{traceback_str}")


def parse_out_self_video_ids(soup: BeautifulSoup) -> list[VideoId]:
    """Parse out the video URL from a self post."""
    content_div = soup.find("div", {"id": "content"}, class_="ytd-app")
    video_ids: list[VideoId] = []
    ytwatch_flexy = content_div.find("ytd-watch-flexy")
    for script in ytwatch_flexy.find_all("script", type="application/ld+json"):
        json_data = json.loads(script.get_text())
        embed_url = json_data.get("embedUrl")
        video_id = embed_url.split("/")[-1]
        video_ids.append(VideoId(video_id))
    return video_ids


def parse_out_up_next_videos(soup: BeautifulSoup) -> list[VideoId]:
    """Parse out the video URL from the up next videos."""
    video_ids: list[VideoId] = []
    try:
        secondary_div = soup.find(
            "div", {"id": "secondary", "class": "ytd-watch-flexy"}
        )
        assert secondary_div is not None, "Could not find secondary div."
        # now within this is div id="related"
        related_div = secondary_div.find("div", {"id": "related"})
        assert related_div is not None, "Could not find related div."
        # ytd-watch-next-secondary-results-renderer
        ytd_watch_container = related_div.find(
            "ytd-watch-next-secondary-results-renderer"
        )
        assert ytd_watch_container is not None, "Could not find watch next container."
        items = ytd_watch_container.find_all("ytd-compact-video-renderer")
        assert items is not None, "Could not find items."
        for item in items:
            try:
                a_tag = item.find("a", {"id": "thumbnail"})
                assert a_tag is not None, "Could not find a tag."
                href = a_tag["href"]
                video_id = href.split("=")[-1]
                if video_id is not None:
                    video_ids.append(VideoId(video_id))
            except AssertionError as e:
                warnings.warn(f"Error: {e}")
                raise e
            except FeatureNotFound as e:
                warnings.warn(f"Error: {e}")
            except KeyError as e:
                warnings.warn(f"Error: {e}")
            except AttributeError as e:
                warnings.warn(f"Error: {e}")
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            except Exception as e:  # pylint: disable=broad-except
                warnings.warn(f"Error: {e}")
    except AssertionError as e:
        warnings.warn(f"Error: {e}")
        raise e
    except FeatureNotFound as e:  # pylint: disable=broad-except
        warnings.warn(f"Error: {e}")
    except AttributeError as e:
        warnings.warn(f"Error: {e}")
    except KeyError as e:
        warnings.warn(f"Error: {e}")
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass

    return video_ids


def parse_channel_url(html: str) -> ChannelId | None:
    """Parse the channel URL."""
    # href="/channel/UCu2uabLB7WHhkhdcLV5BcZg/videos"
    match = re.search(r'href="/channel/([^/]+)/about"', html)
    if match:
        out: str = str(match.group(1))
        return ChannelId(out)
    return None


def parse_channel_id2(html: str) -> ChannelId | None:
    match = re.search(r'/channel/([^/">\b]+)/about"', html)
    if match:
        out: str = str(match.group(1))
        return ChannelId(out)
    return None


def fetch_channel_id(vidid: VideoId) -> ChannelId | None:
    """Fetches the channel url from the video id, raises HTTPError if http error."""
    url = video_to_url(vidid)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    # print(response.text)
    dbg_out_file = Path("debug.html")
    dbg_out_file.write_text(response.text, encoding="utf-8")
    out = parse_channel_id2(response.text)
    return out


def parse_title(soup: BeautifulSoup) -> str:
    """Parse the title of the video."""
    title_div = soup.find("player-microformat-renderer")
    assert title_div is not None, "Could not find title div."
    # <script type="application/ld+json">
    script = title_div.find("script", type="application/ld+json")
    assert script is not None, "Could not find script tag."
    json_data = json.loads(script.get_text())
    title = json_data.get("name")
    assert title is not None, "Could not find title."
    return title


def create_soup(html: str) -> BeautifulSoup:
    """Create a soup object."""
    return BeautifulSoup(html, "lxml")


def parse_yt_page(html: str) -> ParsedYtPage:
    """Parse the YouTube page."""
    soup = create_soup(html)
    title = parse_title(soup)
    video_ids = parse_out_self_video_ids(soup)
    up_next_video_ids = parse_out_up_next_videos(soup)
    channel_id = parse_channel_url(html)
    assert channel_id is not None, "Could not find channel id."
    assert title is not None, "Could not find title."
    up_next_videos: dict[VideoId, ChannelId | None] = {
        video_id: None for video_id in up_next_video_ids
    }
    return ParsedYtPage(
        video_id=video_ids[0],
        title=title,
        channel_id=channel_id,
        up_next_videos=up_next_videos,
    )
