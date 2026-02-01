from abc import ABC, abstractmethod
from typing import Optional
import urllib.request
import json
import re
from .models import NoteArticle

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
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                note_data = data.get('data', {})

                return NoteArticle(
                    key=note_data.get('key', key),
                    name=note_data.get('name', 'Untitled'),
                    body_html=note_data.get('body', ''),
                    slug=note_data.get('slug', ''),
                    publish_at=note_data.get('publish_at'),
                    user_nickname=note_data.get('user', {}).get('nickname'),
                    tags=note_data.get('hashtag_notes', []), # Note: this might need adjustment based on exact API response
                    raw_data=note_data
                )
        except Exception as e:
            print(f"Fetcher error: {e}")
            return None

    def _extract_key(self, url: str) -> Optional[str]:
        # Handle full URL or just key
        if "note.com" in url:
            match = re.search(r'/n/([a-zA-Z0-9]+)', url)
            return match.group(1) if match else None
        return url # Assume it's a key if not a URL
