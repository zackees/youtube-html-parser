# pylint: disable=too-many-branches

"""
Unit test file.
"""

import json
import time
import unittest
import warnings
from pathlib import Path

# import beautiful soup exceptions
from bs4 import BeautifulSoup, FeatureNotFound

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
assert DATA_DIR.exists()

TEST_HTML = list(DATA_DIR.glob("*.html"))
# Filter out *.pretty.html files
TEST_HTML = [file for file in TEST_HTML if not file.name.endswith(".pretty.html")]


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


class ParseTester(unittest.TestCase):
    """Main tester class."""

    @unittest.skip("Not implemented yet.")
    def test_get_self_video_id(self) -> None:
        """Just test the first element in the list."""
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        soup = BeautifulSoup(test_html, "html.parser")
        video_ids = parse_out_self_video_ids(soup)
        self.assertEqual(len(video_ids), 1)
        print(f"Found video id: {video_ids[0]}")
        print(video_ids[0])

    def test_get_up_next_videos(self) -> None:
        test_html = TEST_HTML[0].read_text(encoding="utf-8")
        soup = BeautifulSoup(test_html, "html.parser")
        video_ids = parse_out_up_next_videos(soup)
        print(f"Found {len(video_ids)} video ids.")
        print(video_ids)

    def test_parse_performane(self) -> None:
        """Test the performance of parsing."""
        start = time.time()
        for html_file in TEST_HTML:
            test_html = html_file.read_text(encoding="utf-8")
            soup = BeautifulSoup(test_html, "html.parser")
            _ = parse_out_up_next_videos(soup)
            # print(f"Found {len(video_ids)} video ids.")
            # print(video_ids)
        end = time.time()
        diff = end - start
        # print(f"Time taken: {end - start}")
        # self.assertLess(diff, 5)
        print(f"Time taken: {diff}")


if __name__ == "__main__":
    unittest.main()
