# pylint: disable=too-many-branches

import json
import re
import warnings

# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound

from youtube_html_parser.types import ChannelId, VideoId
from youtube_html_parser.ytpage import YtPage
from youtube_html_parser.ytpagesearch import YtPageSearch

RE_PATTERN_WATCHABLE_LINKS = re.compile(r"watch\?v=[\w-]+")


def parse_out_self_video_ids(soup: BeautifulSoup) -> list[VideoId]:
    """Parse out the video URL from a self post."""
    content_div = soup.find("div", {"id": "content"}, class_="ytd-app")
    assert (
        content_div is not None
    ), "Could not find content div while looking for self video id."
    video_ids: list[VideoId] = []
    ytwatch_flexy = content_div.find("ytd-watch-flexy")
    assert (
        ytwatch_flexy is not None
    ), "Could not find ytwatch flexy while looking for self video id."
    for script in ytwatch_flexy.find_all("script", type="application/ld+json"):
        json_data = json.loads(script.get_text())
        embed_url = json_data.get("embedUrl")
        video_id = embed_url.split("/")[-1]
        # remove ? and evertyhing after it
        video_id = video_id.split("?")[0]
        video_ids.append(VideoId(video_id))
    if not video_ids:
        raise AssertionError("Could not find video ID from embedUrl.")
    return video_ids


def parse_out_up_next_videos_subtype1(
    soup: BeautifulSoup, verbose=True
) -> list[VideoId]:
    """Parse out the video URL from the up next videos."""
    # This parser was known to work with modern videos.
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
                if verbose:
                    warnings.warn(f"Error: {e}")
                raise e
            except FeatureNotFound as e:
                if verbose:
                    warnings.warn(f"Error: {e}")
            except KeyError as e:
                if verbose:
                    warnings.warn(f"Error: {e}")
            except AttributeError as e:
                if verbose:
                    warnings.warn(f"Error: {e}")
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            except Exception as e:  # pylint: disable=broad-except
                if verbose:
                    warnings.warn(f"Error: {e}")
    except AssertionError as e:
        if verbose:
            warnings.warn(f"Error: {e}")
        raise e
    except FeatureNotFound as e:  # pylint: disable=broad-except
        if verbose:
            warnings.warn(f"Error: {e}")
    except AttributeError as e:
        if verbose:
            warnings.warn(f"Error: {e}")
    except KeyError as e:
        if verbose:
            warnings.warn(f"Error: {e}")
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass

    return video_ids


def parse_out_up_next_videos_subtype2(
    soup: BeautifulSoup, verbose=True
) -> list[VideoId]:
    """Used for older videos circa 2022"""
    video_ids: list[VideoId] = []
    try:
        content_divs = soup.find_all(
            "ytd-rich-grid-row", class_="ytd-rich-grid-renderer"
        )
        assert content_divs is not None, "Could not find content divs."
        for content_div in content_divs:
            a_hrefs = content_div.find_all("a", class_="yt-simple-endpoint")
            assert a_hrefs is not None, "Could not find hrefs."
            for a in a_hrefs:
                href = a.get("href")
                if href is None:
                    continue
                clean_link = RE_PATTERN_WATCHABLE_LINKS.search(a.get("href"))
                if clean_link:
                    video_ids.append(VideoId(clean_link.group(0)))
        return video_ids
    except AssertionError as e:
        if verbose:
            warnings.warn(f"Error: {e}")
        raise e


def unique_video_ids(video_ids: list[VideoId]) -> list[VideoId]:
    """Make the video IDs unique."""
    video_ids_set = set([])
    unique_video_ids_out = []
    for video_id in video_ids:
        if video_id not in video_ids_set:
            video_ids_set.add(video_id)
            unique_video_ids_out.append(video_id)
    return unique_video_ids_out


def parse_out_up_next_videos(soup: BeautifulSoup, html: str) -> list[VideoId]:
    """Parse out the video URL from the up next videos using different methods."""
    parsers = [
        lambda: parse_out_up_next_videos_subtype1(soup, verbose=False),
        lambda: parse_out_up_next_videos_subtype2(soup, verbose=False),
        lambda: parse_all_watchable_links(html),  # last resort
    ]
    errors = []
    for parser in parsers:
        try:
            out = parser()
            out = unique_video_ids(out)
            return out
        except AssertionError as e:
            errors.append(e)
        except FeatureNotFound as e:
            errors.append(e)
    raise AssertionError(f"Could not parse up next videos: {errors}")


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
    try:
        title_div = soup.find("player-microformat-renderer")
        assert title_div is not None, "Could not find title div."
        # <script type="application/ld+json">
        script = title_div.find("script", type="application/ld+json")
        assert script is not None, "Could not find script tag."
        json_data = json.loads(script.get_text())
        title = json_data.get("name")
        assert title is not None, "Could not find title."
        return title
    except AssertionError:
        # could not find the title from the json, therefore try to find the title
        # from the <title> tag and remove the " - YouTube" from the end.
        title = soup.title.string
        assert title is not None, "Could not find title."
        return title.replace(" - YouTube", "")
    except AttributeError as e:
        warnings.warn(f"Error: {e}")
        raise e


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
    try:
        video_ids = parse_out_self_video_ids(soup)
    except AssertionError as e:
        warnings.warn(f"Error: {e}")
        video_ids = []
    try:
        up_next_video_ids = parse_out_up_next_videos(soup, html)
    except AssertionError as e:
        warnings.warn(f"Error: {e}")
        raise
    channel_id = parse_channel_url(html)
    return YtPage(
        video_id=video_ids[0] if video_ids else None,
        title=title,
        channel_id=channel_id,
        up_next_videos=up_next_video_ids,
    )


def parse_all_watchable_links(html: str) -> list[VideoId]:
    """Parse out all the hrefs from the HTML."""
    # parse out all the hrefs of the vorm watch?v=VIDEO_ID
    hrefs = re.findall(RE_PATTERN_WATCHABLE_LINKS, html)
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
    return YtPageSearch(search_results=[VideoId(video_id) for video_id in video_ids])
