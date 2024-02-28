# pylint: disable=too-many-branches,import-outside-toplevel


import traceback
import warnings

import requests

from youtube_html_parser.types import ChannelId, VideoId, video_to_url
from youtube_html_parser.ytdlp import fetch_channel_url_ytdlp

FetchError = requests.HTTPError


def __fetch_channel_id(vidid: VideoId) -> ChannelId | None:
    """Fetches the channel url from the video id, raises HTTPError if http error."""
    from youtube_html_parser.parser import (  # pylint: disable=cyclic-import
        parse_channel_id2,
    )

    try:
        url = video_to_url(vidid)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        out = parse_channel_id2(response.text)
        return out
    except FetchError as http_err:
        channel_id_str = fetch_channel_url_ytdlp(url)
        if channel_id_str is None:
            raise FetchError(f"HTTP error occurred: {http_err}")
        return ChannelId(channel_id_str)


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
