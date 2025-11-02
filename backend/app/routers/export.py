from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import StreamingResponse
from io import BytesIO
import json
import base64
from zipfile import BadZipFile
from typing import Optional

from ..models.schemas import ExportPdfRequest, ExportDocxRequest
from ..services.export_pdf import render_pdf, render_pdf_from_docx
from ..services.export_docx import render_docx


router = APIRouter(prefix="", tags=["export"])


@router.post("/export/pdf")
async def export_pdf(payload: ExportPdfRequest):
    try:
        pdf_bytes = render_pdf(payload)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=compare.pdf"},
        )
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="PDF export not implemented yet")
    except Exception as e:
        # Surface error details in development to help diagnose native lib issues
        raise HTTPException(status_code=500, detail=f"PDF export error: {type(e).__name__}: {e}")


@router.post("/export/docx")
async def export_docx(
    original: UploadFile = File(...),
    payload: str = Form(...),
):
    try:
        if not (original.filename or "").lower().endswith(".docx"):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Original must be a .docx file for Word export")

        data = await original.read()
        # Accept the same JSON structure as before inside the multipart field "payload"
        payload_obj = ExportDocxRequest(**json.loads(payload))
        docx_bytes = render_docx(payload_obj, base_docx_bytes=data)
        return StreamingResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=compare.docx"},
        )
    except BadZipFile:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Original file is not a valid .docx (BadZipFile)")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="DOCX export not implemented yet")


@router.post("/export/pdf-from-docx")
async def export_pdf_from_docx(
    docx_bytes_b64: str = Body(..., embed=True),
    options: Optional[str] = Body("{}", embed=True),
):
    """Export PDF from a revision-tracked DOCX (OOXML mode).
    
    Accepts base64-encoded DOCX bytes and converts to PDF using
    LibreOffice → Aspose → Word automation fallback chain.
    """
    try:
        opts = json.loads(options or "{}")
        docx_bytes = base64.b64decode(docx_bytes_b64)
        pdf_bytes = render_pdf_from_docx(docx_bytes, opts)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=compare.pdf"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF export error: {type(e).__name__}: {e}"
        )


@router.post("/export/docx-from-ooxml")
async def export_docx_from_ooxml(
    docx_bytes_b64: str = Body(..., embed=True),
):
    """Export DOCX directly from OOXML comparison result.
    
    Accepts base64-encoded DOCX bytes (from DiffResponseOOXML)
    and returns as downloadable file.
    """
    try:
        docx_bytes = base64.b64decode(docx_bytes_b64)
        return StreamingResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=redline.docx"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DOCX export error: {type(e).__name__}: {e}"
        )


