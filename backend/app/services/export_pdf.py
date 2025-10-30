from typing import List

from weasyprint import HTML, CSS

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
    html = _build_html_document(payload.diffHtmlByParagraph, payload.stats.model_dump())
    pdf = HTML(string=html).write_pdf()
    return pdf


