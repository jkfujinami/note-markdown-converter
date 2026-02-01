from pathlib import Path
import os
import urllib.request
import hashlib
from typing import List
try:
    from .models import NoteArticle, ProcessingResult
except ImportError:
    from models import NoteArticle, ProcessingResult

class FileSaver:
    def __init__(self, base_output_dir: Path):
        self.base_output_dir = Path(base_output_dir)

    def save(self, article: NoteArticle, markdown_content: str, image_urls: List[str]) -> ProcessingResult:
        # Sanitize title for directory name
        safe_title = "".join([c for c in article.name if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not safe_title:
            safe_title = article.key

        article_dir = self.base_output_dir / safe_title
        images_dir = article_dir / "images"

        article_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)

        saved_images = []
        final_markdown = markdown_content

        # Download images and update markdown links
        for url in image_urls:
            local_filename = self._download_image(url, images_dir)
            if local_filename:
                saved_path = images_dir / local_filename
                saved_images.append(saved_path)

                # Replace remote URL with relative local path in Markdown
                # Note: This simple Replace might be risky if URL appears in text not as image.
                # A more robust way would be to do this during conversion or use regex.
                # For now, simplistic replacement.
                rel_path = f"images/{local_filename}"
                final_markdown = final_markdown.replace(url, rel_path)

        # Save Markdown
        md_filename = f"{safe_title}.md"
        md_path = article_dir / md_filename
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)

        return ProcessingResult(
            article=article,
            markdown_content=final_markdown,
            saved_path=md_path,
            image_paths=saved_images
        )

    def _download_image(self, url: str, save_dir: Path) -> str:
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
            filename = f"{url_hash}{ext}"
            save_path = save_dir / filename

            if not save_path.exists():
                print(f"Downloading: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    with open(save_path, 'wb') as f:
                        f.write(response.read())

            return filename
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return ""
