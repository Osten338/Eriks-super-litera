from typing import Any, Dict, List
from fastapi import UploadFile
import io
import os
import mimetypes

from docx import Document
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from PIL import Image

from ..utils.ocr import ocr_image


def _guess_type(filename: str, content_type: str | None) -> str:
    if content_type:
        return content_type
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def _extract_docx_paragraphs(data: bytes) -> List[Dict[str, str]]:
    with io.BytesIO(data) as bio:
        document = Document(bio)
    paras: List[Dict[str, str]] = []
    for p in document.paragraphs:
        text = p.text or ""
        # Keep empty paragraphs to preserve structure
        paras.append({"text": text})
    if not paras:
        paras.append({"text": ""})
    return paras


def _page_text_density(text: str) -> float:
    total = len(text)
    if total == 0:
        return 0.0
    # crude density metric: ratio of alnum chars
    alnum = sum(c.isalnum() for c in text)
    return alnum / total


def _extract_pdf_with_pymupdf(data: bytes, ocr: bool) -> List[str]:
    texts: List[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            text = page.get_text("text") or ""
            density = _page_text_density(text)
            if ocr and density < 0.05:
                # Render and OCR
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = ocr_image(img)
            texts.append(text)
    return texts


def _extract_pdf_paragraphs(data: bytes, use_ocr: bool) -> List[Dict[str, str]]:
    texts: List[str] = []
    try:
        texts = _extract_pdf_with_pymupdf(data, ocr=use_ocr)
    except Exception:
        # Fallback to pdfminer full text
        try:
            with io.BytesIO(data) as bio:
                text_all = pdfminer_extract_text(bio)
            texts = text_all.split("\n\f\n") if text_all else [""]
        except Exception:
            texts = [""]

    # Turn pages into paragraphs, splitting on double newlines to keep structure
    paragraphs: List[Dict[str, str]] = []
    for page_text in texts:
        if not page_text:
            paragraphs.append({"text": ""})
            continue
        chunks = [seg for seg in page_text.split("\n\n")]
        for seg in chunks:
            paragraphs.append({"text": seg})
    if not paragraphs:
        paragraphs.append({"text": ""})
    return paragraphs


async def extract_to_paragraphs(file: UploadFile, options: Dict[str, Any]) -> List[Dict[str, str]]:
    data = await file.read()
    filename = file.filename or "file"
    ctype = _guess_type(filename, getattr(file, "content_type", None))

    use_ocr = bool(options.get("ocr", True))

    if filename.lower().endswith(".docx") or ctype in {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        return _extract_docx_paragraphs(data)
    if filename.lower().endswith(".pdf") or ctype in {"application/pdf"}:
        return _extract_pdf_paragraphs(data, use_ocr)

    # Fallback: treat as text
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    if not text:
        text = filename
    return [{"text": seg} for seg in text.splitlines() or [""]]


