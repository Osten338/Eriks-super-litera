from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO

from ..models.schemas import ExportPdfRequest, ExportDocxRequest
from ..services.export_pdf import render_pdf
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


@router.post("/export/docx")
async def export_docx(payload: ExportDocxRequest):
    try:
        docx_bytes = render_docx(payload)
        return StreamingResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=compare.docx"},
        )
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="DOCX export not implemented yet")


