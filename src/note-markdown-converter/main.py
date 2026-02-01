from typing import Optional
from pathlib import Path
from .fetcher import NoteApiV3Fetcher
from .converter import NoteHtmlToMarkdownConverter
from .saver import FileSaver

class NoteDownloader:
    def __init__(self):
        self.fetcher = NoteApiV3Fetcher()
        self.converter = NoteHtmlToMarkdownConverter()
        # Default output dir, can be configured
        self.saver = FileSaver(Path.cwd() / "downloads")

    def process_url(self, url: str):
        print(f"Starting process for: {url}")

        # 1. Fetch
        article = self.fetcher.fetch(url)
        if not article:
            print("Failed to fetch article.")
            return

        # 2. Convert
        markdown, image_urls = self.converter.convert(article)

        # 3. Save (download images included)
        result = self.saver.save(article, markdown, image_urls)

        print(f"Successfully saved to: {result.saved_path}")
        print(f"Downloaded {len(result.image_paths)} images.")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m note_downloader.main <note_url>")
        return

    downloader = NoteDownloader()
    for url in sys.argv[1:]:
        downloader.process_url(url)

if __name__ == "__main__":
    main()
