# pylint: disable=too-many-branches,import-outside-toplevel,cyclic-import

import traceback
import warnings
from typing import TypeAlias

import requests

from youtube_html_parser.types import ChannelId, VideoId, video_to_url

FetchError: TypeAlias = requests.HTTPError


def __fetch_channel_id(vidid: VideoId) -> ChannelId | None:
    """Fetches the channel url from the video id, raises HTTPError if http error."""
    from youtube_html_parser.parser import parse_channel_id2  # avoid circular import

    url = video_to_url(vidid)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    out = parse_channel_id2(response.text)
    return out


def resolve_channel_ids(
    data: dict[VideoId, ChannelId | None]
) -> dict[VideoId, ChannelId | None]:
    """Resolve the channel ids for a list of video ids."""
    out = data.copy()
    for vidid in data.keys():
        try:
            channel_id = __fetch_channel_id(vidid)
        except FetchError as fetch_err:
            traceback_str = traceback.format_exc()
            warnings.warn(f"HTTP error occurred: {fetch_err}\n\n{traceback_str}")
            channel_id = None
        out[vidid] = channel_id
    return out
