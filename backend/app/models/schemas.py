from typing import List, Optional, Dict, Any, Literal
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


class CompareOptions(BaseModel):
    """Configuration options for document comparison."""
    mode: Literal["legacy_html", "docx_ooxml"] = "docx_ooxml"
    shingle_size: int = 5
    jaccard_threshold: float = 0.85
    min_move_span_tokens: int = 12
    force_brand_colors: bool = False
    use_word_automation: bool = False
    # Legacy options
    includeFormatting: bool = True
    ocr: bool = True
    diffGranularity: str = "word"


class DiffResponseOOXML(BaseModel):
    """Response for OOXML-native comparison."""
    document_bytes: bytes  # Base64 encoded revision-tracked DOCX
    stats: Stats
    meta: Dict[str, Any]  # Alignment pairs, move mappings, etc.


