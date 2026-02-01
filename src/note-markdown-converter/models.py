from dataclasses import dataclass, field
from typing import Optional, List, Dict
from pathlib import Path

@dataclass
class NoteArticle:
    key: str
    name: str # Title
    body_html: str
    slug: str
    publish_at: Optional[str] = None
    user_nickname: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)

@dataclass
class ProcessingResult:
    article: NoteArticle
    markdown_content: str
    saved_path: Path
    image_paths: List[Path] = field(default_factory=list)
