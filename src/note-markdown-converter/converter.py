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

class NoteHtmlToMarkdownConverter(ContentConverter):
    def convert(self, article: NoteArticle) -> Tuple[str, List[str]]:
        soup = BeautifulSoup(article.body_html, 'html.parser')
        markdown_blocks = []
        image_urls = []

        # Eyecatch Image (Header Image)
        if article.eyecatch_url:
            image_urls.append(article.eyecatch_url)
            markdown_blocks.append(f"![Header Image]({article.eyecatch_url})")

        # Title at the top
        markdown_blocks.append(f"# {article.name}")


        for element in soup.children:
            converted_text = self._parse_element(element, image_urls)
            if converted_text:
                markdown_blocks.append(converted_text)

        # Append TOC if needed (logic can be refined)
        # Note: The original script parsed <table-of-contents> tag.

        # Add generated TOC at the end if placeholder exists or standard practice
        # For this implementation, let's keep it simple: body logic handles specific tags.

        return "\n\n".join(markdown_blocks), image_urls

    def _parse_element(self, element, image_urls: List[str]) -> str:
        if not isinstance(element, Tag):
            return ""

        if element.name == 'p':
            text = element.get_text(separator="\n").strip()
            return text if text else ""

        elif element.name == 'h2':
            return f"## {element.get_text(strip=True)}"

        elif element.name == 'h3':
            # Option to use Bold instead of Header to avoid folding issues as requested
            # return f"**{element.get_text(strip=True)}**"
            # Reverting to standard H3 as per user's last "it's fine" comment
            return f"### {element.get_text(strip=True)}"

        elif element.name == 'ul':
            items = [f"* {li.get_text(separator=' ', strip=True)}" for li in element.find_all('li')]
            return "\n".join(items)

        elif element.name == 'ol':
            start = int(element.get('data-start', 1))
            items = [f"{i}. {li.get_text(separator=' ', strip=True)}" for i, li in enumerate(element.find_all('li'), start=start)]
            return "\n".join(items)

        elif element.name == 'pre':
            # Check for code tag? usually note pre has code inside?
            # Adjust based on observed schema
            code = element.get_text(strip=True)
            return f"```\n{code}\n```"

        elif element.name == 'figure':
            return self._parse_figure(element, image_urls)

        elif element.name == 'hr':
            return "---"

        elif element.name == 'table-of-contents':
            # We can implement dynamic TOC generation here if we want to replace this placeholder later
            # Or generate it right now using collected headers?
            # For simplicity, returning a placeholder.
            return "<!-- TOC -->" # Using HTML comment as placeholder or actual string

        return ""

    def _parse_figure(self, element: Tag, image_urls: List[str]) -> str:
        # Blockquote
        blockquote = element.find('blockquote')
        if blockquote:
            text = blockquote.get_text(separator="\n", strip=True)
            return "\n".join([f"> {line}" for line in text.splitlines()])

        # Image
        img = element.find('img')
        if img:
            alt = img.get('alt', '')
            src = img.get('src', '')
            if src:
                image_urls.append(src)
                # Return placeholder to be replaced by Saver with local path
                return f"![{alt}]({src})"

        # Embed
        if element.get('embedded-service'):
            a_tag = element.find('a')
            if a_tag:
                 return f"[{a_tag.get_text(strip=True)}]({a_tag.get('href')})"
            iframe = element.find('iframe')
            if iframe:
                return f"Embed: {iframe.get('src')}"

        return ""
