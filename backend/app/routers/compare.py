from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional, Union
import json
import base64

from ..models.schemas import DiffResponse, DiffResponseOOXML
from ..services.extract import extract_to_paragraphs
from ..services.compare_engine import run_compare, run_compare_ooxml


router = APIRouter(prefix="", tags=["compare"])


@router.post("/compare")
async def compare(
    original: UploadFile = File(...),
    modified: UploadFile = File(...),
    options: Optional[str] = Form("{}"),
) -> Union[DiffResponse, DiffResponseOOXML]:
    """Compare two documents.
    
    Supports two modes:
    - legacy_html: Returns HTML-based diff (default for non-DOCX files)
    - docx_ooxml: Returns native OOXML revision-tracked DOCX (for DOCX files)
    """
    opts = json.loads(options or "{}")
    mode = opts.get("mode", "docx_ooxml")
    
    # Check if both files are DOCX and mode is docx_ooxml
    orig_is_docx = (original.filename or "").lower().endswith(".docx")
    mod_is_docx = (modified.filename or "").lower().endswith(".docx")
    
    if mode == "docx_ooxml" and orig_is_docx and mod_is_docx:
        # Use OOXML-native comparison
        orig_bytes = await original.read()
        mod_bytes = await modified.read()
        
        result = run_compare_ooxml(orig_bytes, mod_bytes, opts)
        
        # Encode document bytes as base64 for JSON response
        doc_bytes_b64 = base64.b64encode(result["document_bytes"]).decode("utf-8")
        
        return DiffResponseOOXML(
            document_bytes=doc_bytes_b64,
            stats=result["stats"],
            meta=result["meta"],
        )
    else:
        # Use legacy HTML-based comparison
        original_paragraphs = await extract_to_paragraphs(original, opts)
        modified_paragraphs = await extract_to_paragraphs(modified, opts)
        diff = run_compare(original_paragraphs, modified_paragraphs, opts)
        return diff


