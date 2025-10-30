from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json

from ..models.schemas import DiffResponse
from ..services.extract import extract_to_paragraphs
from ..services.compare_engine import run_compare


router = APIRouter(prefix="", tags=["compare"])


@router.post("/compare", response_model=DiffResponse)
async def compare(
    original: UploadFile = File(...),
    modified: UploadFile = File(...),
    options: Optional[str] = Form("{}"),
):
    opts = json.loads(options or "{}")
    original_paragraphs = await extract_to_paragraphs(original, opts)
    modified_paragraphs = await extract_to_paragraphs(modified, opts)
    diff = run_compare(original_paragraphs, modified_paragraphs, opts)
    return diff


