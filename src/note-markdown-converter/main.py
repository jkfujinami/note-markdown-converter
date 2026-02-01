from typing import Optional
from pathlib import Path

try:
    from .fetcher import NoteApiV3Fetcher, NoteUserContentsFetcher
    from .converter import NoteHtmlToMarkdownConverter
    from .saver import FileSaver
except ImportError:
    import sys
    from pathlib import Path

    # Add current directory to sys.path to resolve sibling modules
    sys.path.append(str(Path(__file__).parent))

    from fetcher import NoteApiV3Fetcher, NoteUserContentsFetcher
    from converter import NoteHtmlToMarkdownConverter
    from saver import FileSaver


class NoteDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.fetcher = NoteApiV3Fetcher()
        self.user_fetcher = NoteUserContentsFetcher()
        self.converter = NoteHtmlToMarkdownConverter()
        # Default output dir, can be configured
        self.saver = FileSaver(Path(output_dir))

    def process_target(self, target: str):
        # Check if target is user URL or ID
        user_id = self._extract_user_id(target)
        if user_id:
            print(f"Target identified as User: {user_id}")
            keys = self.user_fetcher.fetch_all_keys(user_id)
            for i, key in enumerate(keys, 1):
                print(f"[{i}/{len(keys)}] Processing: {key}")
                self._process_single_article(key)
        else:
            # Assume single article
            self._process_single_article(target)

    def _process_single_article(self, url_or_key: str):
        print(f"Starting process for: {url_or_key}")

        # 1. Fetch
        article = self.fetcher.fetch(url_or_key)
        if not article:
            print("Failed to fetch article.")
            return

        # 2. Convert
        markdown, image_urls = self.converter.convert(article)

        # 3. Save (download images included)
        result = self.saver.save(article, markdown, image_urls)

        print(f"Successfully saved to: {result.saved_path}")
        print(f"Downloaded {len(result.image_paths)} images.")

    def _extract_user_id(self, target: str) -> Optional[str]:
        """Tries to extract user ID if target is a user profile URL.
        Also returns target if it looks like a user ID (and not a note key).
        """
        import re

        # https://note.com/user_id
        # https://note.com/user_id/magazines/... (ignore for now, focus on user root)

        target = target.strip()

        # Exact match for User Profile URL
        match = re.search(r"note\.com/([^/]+)/?$", target)
        if match:
            uid = match.group(1)
            if uid not in ("login", "signup", "hashtag"):  # exclude system paths
                return uid

        # If just text (no url), how to distinguish UserID vs NoteKey?
        # NoteKey usually starts with 'n' and is 13 chars? Or just alphanumeric.
        # UserID is customizable.
        # Strategy: If it starts with 'n' and followed by digits/lower, might be key.
        # But UserID can also be that.
        # For safety: Command line arg usually needed.
        # BUT user asked for "smart" detection or "argument".
        # Let's assume if it doesn't match Note Key pattern (n + 12 chars?), it's user?
        # Note Key: n + 12 chars (approx). e.g. na3c861f59d8b (13 chars total)
        # User ID: fuji1080

        # Regex for Note Key (informal): ^n[a-z0-9]{12}$
        if re.match(r"^n[a-z0-9]{12}$", target):
            return None  # It is a Note Key

        # If it looks like a simpler ID (not Note Key), treat as User?
        # Risk: User ID "n123456789012"
        # It's better NOT to guess too aggressively on raw string.
        # Only support User extraction from valid URL for now to be safe.

        return None


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Note.com Markdown Converter")
    parser.add_argument(
        "targets", nargs="*", help="URL or Key to process (auto-detect if no flag used)"
    )
    parser.add_argument("--user", help="Process all notes for specific user ID")
    parser.add_argument("--id", help="Process specific note Key (ID)")
    parser.add_argument("--url", help="Process specific URL (Auto detect User or Note)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory (default: downloads)",
        default="downloads",
    )

    args = parser.parse_args()

    if not (args.targets or args.user or args.id or args.url):
        parser.print_help()
        return

    downloader = NoteDownloader(output_dir=args.output)

    # Priority: Explicit flags -> Positional args

    if args.user:
        print(f"Explicit User mode: {args.user}")
        keys = downloader.user_fetcher.fetch_all_keys(args.user)
        for i, key in enumerate(keys, 1):
            print(f"[{i}/{len(keys)}] Processing: {key}")
            downloader._process_single_article(key)

    if args.id:
        print(f"Explicit ID mode: {args.id}")
        downloader._process_single_article(args.id)

    if args.url:
        print(f"Explicit URL mode: {args.url}")
        downloader.process_target(args.url)

    # Process positional arguments (backwards compatibility / simple usage)
    for target in args.targets:
        downloader.process_target(target)


if __name__ == "__main__":
    main()
