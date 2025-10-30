from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Stats(BaseModel):
    insertions: int
    deletions: int
    moves: int
    total: int


class ParagraphHtml(BaseModel):
    html: str


class DiffResponse(BaseModel):
    paragraphs: List[ParagraphHtml]
    stats: Stats
    meta: Dict[str, Any]


class ExportPdfRequest(BaseModel):
    diffHtmlByParagraph: List[str]
    stats: Stats
    meta: Dict[str, Any]


class ExportDocxRequest(BaseModel):
    diffHtmlByParagraph: Optional[List[str]] = None
    # Placeholder for a future richer structure mapping runs with styles
    diffRunsByParagraph: Optional[List[Dict[str, Any]]] = None
    stats: Stats
    meta: Dict[str, Any]


