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
