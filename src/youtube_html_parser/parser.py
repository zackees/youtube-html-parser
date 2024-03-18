# pylint: disable=too-many-branches

import json
import re
import warnings

# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound

from youtube_html_parser.types import ChannelId, VideoId
from youtube_html_parser.ytpage import YtPage
from youtube_html_parser.ytpagesearch import YtPageSearch


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


def parse_yt_page(html: str) -> YtPage:
    """Parse the YouTube page."""
    soup = create_soup(html)
    title: str | None = None
    try:
        title = parse_title(soup)
    except AssertionError as e:
        warnings.warn(f"Error: {e}")
        title = "Unknown title."
    video_ids = parse_out_self_video_ids(soup)
    up_next_video_ids = parse_out_up_next_videos(soup)
    channel_id = parse_channel_url(html)
    assert channel_id is not None, "Could not find channel id."
    # assert title is not None, "Could not find title."
    up_next_videos: dict[VideoId, ChannelId | None] = {
        video_id: None for video_id in up_next_video_ids
    }
    return YtPage(
        video_id=video_ids[0],
        title=title,
        channel_id=channel_id,
        up_next_videos=up_next_videos,
    )


def parse_all_watchable_links(html: str) -> list[VideoId]:
    """Parse out all the hrefs from the HTML."""
    # parse out all the hrefs of the vorm watch?v=VIDEO_ID
    hrefs = re.findall(r"watch\?v=[\w-]+", html)
    href_set = set([])
    hrefs_out = []
    for href in hrefs:
        if href not in href_set:
            href_set.add(href)
            hrefs_out.append(href)

    # now remove all watch?v= from the hrefs
    hrefs_out = [href.replace("watch?v=", "") for href in hrefs_out]
    # make unique
    hrefs_set = set([])
    unique_href_out = []
    for href in hrefs_out:
        if href not in hrefs_set:
            hrefs_set.add(href)
            unique_href_out.append(href)
    return [VideoId(video_id) for video_id in unique_href_out]


def parse_yt_page_seach(html: str) -> YtPageSearch:
    """Parse the YouTube page."""
    video_ids = parse_all_watchable_links(html)
    return YtPageSearch(videos=[VideoId(video_id) for video_id in video_ids])
