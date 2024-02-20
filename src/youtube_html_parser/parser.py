# pylint: disable=too-many-branches

import json
import warnings
from dataclasses import dataclass

# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound


@dataclass
class ParsedYtPage:
    """Dataclass to hold the parsed data."""

    video_id: str
    up_next_video_ids: list[str]


def parse_out_self_video_ids(soup: BeautifulSoup) -> list[str]:
    """Parse out the video URL from a self post."""
    content_div = soup.find("div", {"id": "content"}, class_="ytd-app")
    video_ids: list[str] = []
    ytwatch_flexy = content_div.find("ytd-watch-flexy")
    for script in ytwatch_flexy.find_all("script", type="application/ld+json"):
        json_data = json.loads(script.get_text())
        embed_url = json_data.get("embedUrl")
        video_id = embed_url.split("/")[-1]
        video_ids.append(video_id)
    return video_ids


def parse_out_up_next_videos(soup: BeautifulSoup) -> list[str]:
    """Parse out the video URL from the up next videos."""
    video_ids: list[str] = []
    try:
        secondary_div = soup.find(
            "div", {"id": "secondary", "class": "ytd-watch-flexy"}
        )
        # now within this is div id="related"
        related_div = secondary_div.find("div", {"id": "related"})
        # ytd-watch-next-secondary-results-renderer
        ytd_watch_container = related_div.find(
            "ytd-watch-next-secondary-results-renderer"
        )
        items = ytd_watch_container.find_all("ytd-compact-video-renderer")
        for item in items:
            try:
                a_tag = item.find("a", {"id": "thumbnail"})
                href = a_tag["href"]
                video_id = href.split("=")[-1]
                if video_id is not None:
                    video_ids.append(video_id)
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


def create_soup(html: str) -> BeautifulSoup:
    """Create a soup object."""
    return BeautifulSoup(html, "lxml")


def parse_yt_page(html: str) -> ParsedYtPage:
    """Parse the YouTube page."""
    soup = create_soup(html)
    video_ids = parse_out_self_video_ids(soup)
    up_next_video_ids = parse_out_up_next_videos(soup)
    return ParsedYtPage(video_ids[0], up_next_video_ids)
