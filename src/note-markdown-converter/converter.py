from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, Tag
from typing import List, Tuple

try:
    from .models import NoteArticle
except ImportError:
    from models import NoteArticle


class ContentConverter(ABC):
    @abstractmethod
    def convert(self, article: NoteArticle) -> Tuple[str, List[str]]:
        """Returns parsed markdown and list of image URLs found"""
        pass


import functools
from typing import Optional, List, Tuple

# --- Tag Handlers ---


def handle_paragraph(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    text = element.get_text(separator="\n").strip()
    return (text if text else ""), None


def handle_header(
    element: Tag, image_urls: List[str], level: int
) -> Tuple[str, Optional[Tuple[int, str]]]:
    text = element.get_text(strip=True)
    header_info = (level, text)
    return f"{'#' * level} {text}", header_info


def handle_ul(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    items = [
        f"* {li.get_text(separator=' ', strip=True)}" for li in element.find_all("li")
    ]
    return "\n".join(items), None


def handle_ol(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    start = int(element.get("data-start", 1))
    items = [
        f"{i}. {li.get_text(separator=' ', strip=True)}"
        for i, li in enumerate(element.find_all("li"), start=start)
    ]
    return "\n".join(items), None


def handle_pre(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    code = element.get_text(strip=True)
    return f"```\n{code}\n```", None


def handle_hr(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    return "---", None


def handle_toc_placeholder(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    return "<!-- TOC_PLACEHOLDER -->", None


def handle_figure(
    element: Tag, image_urls: List[str]
) -> Tuple[str, Optional[Tuple[int, str]]]:
    # Blockquote
    blockquote = element.find("blockquote")
    if blockquote:
        text = blockquote.get_text(separator="\n", strip=True)
        return "\n".join([f"> {line}" for line in text.splitlines()]), None

    # Image
    img = element.find("img")
    if img:
        alt = img.get("alt", "")
        src = img.get("src", "")
        if src:
            image_urls.append(src)
            # Return placeholder to be replaced by Saver with local path
            return f"![{alt}]({src})", None

    # Embed
    if element.get("embedded-service"):
        a_tag = element.find("a")
        if a_tag:
            return f"[{a_tag.get_text(strip=True)}]({a_tag.get('href')})", None
        iframe = element.find("iframe")
        if iframe:
            return f"Embed: {iframe.get('src')}", None

    return "", None


TAG_HANDLERS = {
    "p": handle_paragraph,
    "h2": functools.partial(handle_header, level=2),
    "h3": functools.partial(handle_header, level=3),
    "ul": handle_ul,
    "ol": handle_ol,
    "pre": handle_pre,
    "figure": handle_figure,
    "hr": handle_hr,
    "table-of-contents": handle_toc_placeholder,
}


class NoteHtmlToMarkdownConverter(ContentConverter):
    def convert(self, article: NoteArticle) -> Tuple[str, List[str]]:
        soup = BeautifulSoup(article.body_html, "html.parser")
        markdown_blocks = []
        image_urls = []
        headers = []  # Tuples of (level, text, anchor_slug)

        # Eyecatch Image
        if article.eyecatch_url:
            image_urls.append(article.eyecatch_url)
            markdown_blocks.append(f"![Header Image]({article.eyecatch_url})")

        # Title
        markdown_blocks.append(f"# {article.name}")

        for element in soup.children:
            converted_text, detected_header = self._parse_element(element, image_urls)
            if converted_text:
                markdown_blocks.append(converted_text)
            if detected_header:
                headers.append(detected_header)

        # Generate TOC
        toc_lines = []
        if headers:
            toc_lines.append("")
            toc_lines.append("**目次**")
            for level, text in headers:
                indent = "  " * (level - 2) if level >= 2 else ""
                # Simple TOC, no links for now as Markdown links require anchors which are tricky to guarantee across viewers
                # But we can try just list items.
                toc_lines.append(f"{indent}- {text}")
            toc_lines.append("")

        toc_content = "\n".join(toc_lines)

        # Replace Placeholder
        final_blocks = []
        for block in markdown_blocks:
            if block == "<!-- TOC_PLACEHOLDER -->":
                if toc_content:
                    final_blocks.append(toc_content)
            else:
                final_blocks.append(block)

        return "\n\n".join(final_blocks), image_urls

    def _parse_element(
        self, element, image_urls: List[str]
    ) -> Tuple[str, Optional[Tuple[int, str]]]:
        if not isinstance(element, Tag):
            # Handle plain text nodes if any (usually soup.children are tags but can be NavigableString)
            return "", None

        handler = TAG_HANDLERS.get(element.name)
        if handler:
            return handler(element, image_urls)

        return "", None
