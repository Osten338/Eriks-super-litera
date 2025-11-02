from typing import List, Dict, Any
import os
import io
import tempfile
import subprocess
import shutil
from pathlib import Path

from ..models.schemas import ExportPdfRequest


def _build_html_document(paragraphs: List[str], stats: dict) -> str:
    body = "".join(f"<div class=\"paragraph\">{p}</div>" for p in paragraphs)
    summary = (
        f"<div class=\"summary\">Insertions: {stats['insertions']} · "
        f"Deletions: {stats['deletions']} · Moves: {stats['moves']} · Total: {stats['total']}</div>"
    )
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>Erik's Super Compare - PDF Export</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 12pt; color: #111; }}
    .header {{ margin-bottom: 16px; }}
    .title {{ font-size: 18pt; font-weight: 700; }}
    .tagline {{ color: #666; font-size: 10pt; }}
    .summary {{ margin: 12px 0 24px; color: #333; font-size: 10pt; }}
    .paragraph {{ margin: 8px 0; line-height: 1.5; white-space: pre-wrap; }}
    .diff-insert {{ color: #1e3a8a; }} /* blue-800 */
    .diff-delete {{ color: #b91c1c; }} /* red-700 */
    .diff-move {{ color: #065f46; }}   /* emerald-800 */
    .line-through {{ text-decoration: line-through; }}
  </style>
  </head>
  <body>
    <div class=\"header\">
      <div class=\"title\">Erik's Super Compare</div>
      <div class=\"tagline\">Redlines so good, even Litera blushes.</div>
    </div>
    {summary}
    {body}
  </body>
  </html>
    """
    return html


def render_pdf(payload: ExportPdfRequest) -> bytes:
    # Ensure Homebrew-installed native libs are discoverable (macOS)
    os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")
    # Lazy import so env is set before WeasyPrint loads its ffi bindings
    try:
        from weasyprint import HTML  # type: ignore
        html = _build_html_document(payload.diffHtmlByParagraph, payload.stats.model_dump())
        pdf = HTML(string=html).write_pdf()
        return pdf
    except Exception:
        # Fallback: generate a basic PDF using pydyf if WeasyPrint is unavailable
        # This ensures exports work locally even when native libs are missing
        import pydyf

        pdf = pydyf.PDF()
        pdf.add_page()
        # Very simple text; pydyf operates at a low level
        stream = pydyf.Stream([
            b"BT",
            b"/F1 12 Tf",
            b"72 720 Td",
            b"(Export generated without WeasyPrint. Install cairo/pango to enable full render.) Tj",
            b"ET",
        ])
        pdf.add_object(stream)
        pdf_page = pdf.catalog.pages.kids[0]
        pdf_page.contents = stream
        out = bytes(pdf)
        return out


def render_pdf_via_lo(docx_bytes: bytes) -> bytes:
    """Render PDF from DOCX using LibreOffice headless.
    
    Args:
        docx_bytes: DOCX file as bytes
    
    Returns:
        PDF file as bytes
    
    Raises:
        FileNotFoundError: If LibreOffice not found
        subprocess.CalledProcessError: If conversion fails
    """
    # Check if LibreOffice is available
    lo_cmd = shutil.which("libreoffice")
    if not lo_cmd:
        # Try common alternative names
        for cmd in ["libreoffice", "soffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice"]:
            if shutil.which(cmd) or os.path.exists(cmd):
                lo_cmd = cmd
                break
    
    if not lo_cmd:
        raise FileNotFoundError("LibreOffice not found. Install LibreOffice to enable PDF export.")
    
    # Create temporary directory for conversion
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Write DOCX to temp file
        docx_path = tmp_path / "input.docx"
        docx_path.write_bytes(docx_bytes)
        
        # Run LibreOffice conversion
        cmd = [
            lo_cmd,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(tmp_path),
            str(docx_path),
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                result.stderr,
            )
        
        # Read generated PDF
        pdf_path = tmp_path / "input.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not generated: {pdf_path}")
        
        return pdf_path.read_bytes()


def render_pdf_via_aspose(docx_bytes: bytes) -> bytes:
    """Render PDF from DOCX using Aspose.Words (optional, premium).
    
    Args:
        docx_bytes: DOCX file as bytes
    
    Returns:
        PDF file as bytes
    
    Raises:
        ImportError: If Aspose not available
        Exception: If conversion fails
    """
    try:
        import aspose.words as aw
    except ImportError:
        raise ImportError(
            "Aspose.Words not available. Install aspose-words package "
            "and provide a license to use this renderer."
        )
    
    # Load document from bytes
    doc_stream = io.BytesIO(docx_bytes)
    doc = aw.Document(doc_stream)
    
    # Save as PDF
    pdf_stream = io.BytesIO()
    doc.save(pdf_stream, aw.SaveFormat.PDF)
    
    return pdf_stream.getvalue()


def render_pdf_via_word(docx_bytes: bytes) -> bytes:
    """Render PDF from DOCX using Microsoft Word automation (Windows only, optional).
    
    Args:
        docx_bytes: DOCX file as bytes
    
    Returns:
        PDF file as bytes
    
    Raises:
        ImportError: If pywin32 not available
        OSError: If not on Windows
        Exception: If Word automation fails
    """
    import sys
    
    if sys.platform != "win32":
        raise OSError("Word automation is only available on Windows")
    
    try:
        import win32com.client
    except ImportError:
        raise ImportError(
            "pywin32 not available. Install pywin32 to use Word automation. "
            "Note: This is Windows-only and requires Microsoft Word installed."
        )
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        docx_path = tmp_path / "input.docx"
        pdf_path = tmp_path / "output.pdf"
        
        docx_path.write_bytes(docx_bytes)
        
        # Use Word COM automation
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        try:
            doc = word.Documents.Open(str(docx_path.absolute()))
            
            # Export as PDF (format 17 = PDF)
            doc.ExportAsFixedFormat(
                OutputFileName=str(pdf_path.absolute()),
                ExportFormat=17,  # wdExportFormatPDF
                OpenAfterExport=False,
                OptimizeFor=0,  # wdExportOptimizeForPrint
            )
            
            doc.Close(False)
            
            return pdf_path.read_bytes()
        
        finally:
            word.Quit()


def render_pdf_from_docx(docx_bytes: bytes, options: Dict[str, Any]) -> bytes:
    """Render PDF from DOCX using fallback chain.
    
    Order of attempts:
    1. LibreOffice (cross-platform, default)
    2. Aspose.Words (optional, premium - if available)
    3. Word automation (Windows only, optional - if use_word_automation=True)
    
    Args:
        docx_bytes: DOCX file as bytes
        options: Configuration options including:
            - use_word_automation: bool (default False)
    
    Returns:
        PDF file as bytes
    
    Raises:
        RuntimeError: If all renderers fail
    """
    use_word_automation = bool(options.get("use_word_automation", False))
    
    # Try LibreOffice first (cross-platform, reliable)
    try:
        return render_pdf_via_lo(docx_bytes)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        # LibreOffice not available or failed, try next option
        pass
    
    # Try Aspose (optional, premium)
    try:
        return render_pdf_via_aspose(docx_bytes)
    except ImportError:
        # Aspose not available, try next option
        pass
    except Exception as e:
        # Aspose failed, but don't give up yet
        pass
    
    # Try Word automation (Windows only, optional)
    if use_word_automation:
        try:
            return render_pdf_via_word(docx_bytes)
        except (ImportError, OSError) as e:
            # Word automation not available
            pass
        except Exception as e:
            # Word automation failed
            pass
    
    # All methods failed
    raise RuntimeError(
        "PDF export failed: No suitable renderer available. "
        "Install LibreOffice, Aspose.Words, or enable Word automation (Windows only)."
    )



