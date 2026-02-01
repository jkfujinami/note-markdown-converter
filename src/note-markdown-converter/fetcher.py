from abc import ABC, abstractmethod
from typing import Optional
import urllib.request
import json
import re

try:
    from .models import NoteArticle
except ImportError:
    from models import NoteArticle


class ContentFetcher(ABC):
    @abstractmethod
    def fetch(self, target: str) -> Optional[NoteArticle]:
        pass


class NoteApiV3Fetcher(ContentFetcher):
    BASE_URL = "https://note.com/api/v3/notes/"

    def fetch(self, url_or_key: str) -> Optional[NoteArticle]:
        key = self._extract_key(url_or_key)
        if not key:
            raise ValueError(f"Could not extract key from: {url_or_key}")

        api_url = f"{self.BASE_URL}{key}"
        print(f"Fetching from: {api_url}")

        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                note_data = data.get("data", {})

                return NoteArticle(
                    key=note_data.get("key", key),
                    name=note_data.get("name", "Untitled"),
                    body_html=note_data.get("body", ""),
                    slug=note_data.get("slug", ""),
                    publish_at=note_data.get("publish_at"),
                    eyecatch_url=note_data.get("eyecatch"),
                    user_nickname=note_data.get("user", {}).get("nickname"),
                    tags=note_data.get(
                        "hashtag_notes", []
                    ),  # Note: this might need adjustment based on exact API response
                    raw_data=note_data,
                )
        except Exception as e:
            print(f"Fetcher error: {e}")
            return None

    def _extract_key(self, url_or_key: str) -> Optional[str]:
        # Clean input
        text = url_or_key.strip()

        # If it looks like a URL
        if "note.com" in text:
            # Match pattern like .../n/n12345678...
            match = re.search(r"/n/([a-zA-Z0-9]+)", text)
            if match:
                return match.group(1)
            # If it's a URL but not a specific note, maybe it's a user profile?
            return None

        # If it's just the key (e.g. na3c861f59d8b)
        if re.match(r"^[a-zA-Z0-9]+$", text):
            return text

        return None


class NoteUserContentsFetcher:
    """Fetches list of contents for a specific user using API v2"""

    BASE_URL = "https://note.com/api/v2/creators/{}/contents?kind=note&page={}"

    def fetch_all_keys(self, user_urlname: str) -> list[str]:
        """Yields article keys one by one from all pages"""
        import time

        page = 1
        all_keys = []

        print(f"Fetching content list for user: {user_urlname}")

        while True:
            url = self.BASE_URL.format(user_urlname, page)
            try:
                # print(f"  Fetching page {page}...", end="\r")
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as res:
                    raw_json = json.loads(res.read())
                    data_block = raw_json.get("data", {})

                    contents = data_block.get("contents", [])
                    is_last_page = data_block.get("isLastPage", False)

                    # Extract keys from this page
                    page_keys = [c.get("key") for c in contents if c.get("key")]
                    all_keys.extend(page_keys)

                    if not contents or is_last_page:
                        break

                    page += 1
                    time.sleep(1)  # Be polite

            except Exception as e:
                print(f"Error fetching user contents page {page}: {e}")
                break

        print(f"Found total {len(all_keys)} articles for {user_urlname}")
        return all_keys
