"""
PDF generation utilities — professional report styling.
Produces reports that match the ISRI sample document format:
  - Barrier Analysis: cover page, executive summary, per-barrier Root Causes/Impact/Recommendations
  - Strategic Roadmap: cover page, per-barrier 4-section format with tables
"""
import re
import markdown2
from weasyprint import HTML, CSS
from typing import Optional, Dict

# ── Shared base CSS ─────────────────────────────────────────────────────────

_BASE_CSS = """
@page {
    size: A4;
    margin: 2cm 2.2cm 2cm 2.2cm;
    @bottom-left {
        content: "Indian SME Readiness Index (ISRI)  |  Confidential";
        font-size: 7.5pt;
        color: #888;
        border-top: 1px solid #ccc;
        padding-top: 5pt;
    }
    @bottom-right {
        content: "Page " counter(page);
        font-size: 7.5pt;
        color: #888;
        border-top: 1px solid #ccc;
        padding-top: 5pt;
    }
}

body {
    font-family: 'Calibri', 'Arial', sans-serif;
    font-size: 10.5pt;
    line-height: 1.58;
    color: #1a1a2e;
}

/* ── Headings ───────────────────────────────────────── */
h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #1F4E79;
    margin: 1.3em 0 0.3em;
    border-bottom: 3px solid #1F4E79;
    padding-bottom: 6pt;
    page-break-before: auto;
    page-break-after: avoid;
}
h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1F4E79;
    margin: 1.2em 0 0.4em;
    border-bottom: 2px solid #2E75B6;
    padding-bottom: 4pt;
    page-break-after: avoid;
}
h3 {
    font-size: 12pt;
    font-weight: 700;
    color: #2E75B6;
    margin: 1em 0 0.3em;
    page-break-after: avoid;
}
h4 {
    font-size: 11pt;
    font-weight: 700;
    color: #1F4E79;
    margin: 0.7em 0 0.2em;
}

/* ── Body text ─────────────────────────────────────── */
p {
    margin-bottom: 0.65em;
    text-align: justify;
}
strong {
    color: #1F4E79;
}
em {
    color: #444;
    font-style: italic;
}

/* ── Lists ─────────────────────────────────────────── */
ul, ol {
    margin-left: 1.6em;
    margin-bottom: 0.8em;
}
li {
    margin-bottom: 0.35em;
}
ul li ul {
    margin-top: 0.2em;
}

/* ── Tables ────────────────────────────────────────── */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8em 0 1.3em;
    font-size: 9.5pt;
    page-break-inside: avoid;
}
th {
    background-color: #1F4E79;
    color: #ffffff;
    font-weight: 700;
    padding: 7pt 10pt;
    text-align: left;
    border: 1px solid #1F4E79;
    font-size: 9.5pt;
}
td {
    border: 1px solid #BDD7EE;
    padding: 6pt 10pt;
    vertical-align: top;
    line-height: 1.5;
    white-space: pre-line;
}
tr:nth-child(even) td {
    background-color: #EBF3FB;
}

/* ── Horizontal rule ───────────────────────────────── */
hr {
    border: none;
    border-top: 2px solid #BDD7EE;
    margin: 1.4em 0;
}

/* ── Blockquote (used for highlighted summary boxes) ─ */
blockquote {
    border-left: 5px solid #2E75B6;
    margin: 0.6em 0;
    padding: 0.6em 1em;
    background-color: #EBF3FB;
    color: #1a1a2e;
    font-size: 10pt;
    border-radius: 0 4pt 4pt 0;
}

/* ── Score / Severity highlights ──────────────────── */
.score-line {
    display: inline-block;
    background-color: #FFF176;
    border: 1px solid #F9A825;
    padding: 2pt 7pt;
    border-radius: 3pt;
    font-weight: bold;
    color: #333;
    font-size: 10pt;
}
mark {
    background-color: #FFF176;
    color: #333;
    padding: 1pt 3pt;
    border-radius: 2pt;
}
"""

_COVER_CSS = """
/* ── Cover page ────────────────────────────────────── */
.cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 240mm;
    text-align: center;
    padding: 40pt 30pt;
    background: linear-gradient(160deg, #1F4E79 0%, #2E75B6 100%);
    color: white;
    margin: -2cm -2.2cm -2cm -2.2cm;
}
.cover-logo-line {
    font-size: 9pt;
    letter-spacing: 3pt;
    text-transform: uppercase;
    opacity: 0.75;
    margin-bottom: 24pt;
}
.cover-report-type {
    font-size: 11pt;
    letter-spacing: 2pt;
    text-transform: uppercase;
    background-color: rgba(255,255,255,0.15);
    padding: 4pt 16pt;
    border-radius: 3pt;
    margin-bottom: 20pt;
    display: inline-block;
}
.cover-title {
    font-size: 28pt;
    font-weight: 900;
    line-height: 1.2;
    margin-bottom: 8pt;
    color: white;
}
.cover-subtitle {
    font-size: 13pt;
    opacity: 0.9;
    margin-bottom: 40pt;
}
.cover-divider {
    width: 80pt;
    height: 3pt;
    background-color: rgba(255,255,255,0.5);
    margin: 0 auto 36pt;
}
.cover-meta-table {
    width: auto;
    border-collapse: collapse;
    margin: 0 auto;
    font-size: 10pt;
    color: white;
}
.cover-meta-table td {
    border: none;
    padding: 4pt 10pt;
    background: transparent;
    color: white;
    text-align: left;
}
.cover-meta-label {
    opacity: 0.7;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 1pt;
    padding-right: 16pt;
}
.cover-meta-value {
    font-weight: 700;
    font-size: 10.5pt;
}
.cover-footer {
    margin-top: 48pt;
    font-size: 8pt;
    opacity: 0.55;
    letter-spacing: 1pt;
}
"""


def _build_cover_html(
    company_name: str,
    industry: str,
    num_employees: int,
    annual_revenue: float,
    report_date: str,
    report_type: str,
    report_title: str,
    report_subtitle: str,
) -> str:
    return f"""
<div class="cover">
  <div class="cover-logo-line">Indian SME Readiness Index</div>
  <div class="cover-report-type">{report_type}</div>
  <h1 class="cover-title" style="color:white; border:none; font-size:28pt; margin:0 0 8pt;">{report_title}</h1>
  <div class="cover-subtitle">{report_subtitle}</div>
  <div class="cover-divider"></div>
  <table class="cover-meta-table">
    <tr>
      <td class="cover-meta-label">Prepared for</td>
      <td class="cover-meta-value">{company_name}</td>
    </tr>
    <tr>
      <td class="cover-meta-label">Industry</td>
      <td class="cover-meta-value">{industry}</td>
    </tr>
    <tr>
      <td class="cover-meta-label">Organisation size</td>
      <td class="cover-meta-value">{num_employees} employees</td>
    </tr>
    <tr>
      <td class="cover-meta-label">Annual revenue</td>
      <td class="cover-meta-value">Rs {annual_revenue} Cr</td>
    </tr>
    <tr>
      <td class="cover-meta-label">Report date</td>
      <td class="cover-meta-value">{report_date}</td>
    </tr>
  </table>
  <div class="cover-footer">ISRI Assessment &nbsp;|&nbsp; Confidential &nbsp;|&nbsp; Impact Value Consulting</div>
</div>
"""


def _post_process_html(html: str) -> str:
    """
    Post-process converted HTML to:
    1. Highlight lines containing score / severity / impact value data with yellow mark tags.
    2. Wrap ✔ characters in styled spans for correct rendering.
    """
    # Highlight score-bearing list items and paragraphs
    score_patterns = [
        r'(Score:\s*[\d.]+\s*/\s*10)',
        r'(Barrier Score:\s*[\d.]+\s*/\s*10)',
        r'(Overall Score:\s*[\d.]+\s*/\s*10)',
        r'(Severity:\s*(?:CRITICALLY HIGH|CRITICAL|HIGH|MODERATE TO HIGH|MODERATE|LOW|VERY LOW)[^<]*)',
        r'(Impact Value[^:]*:\s*[\d.]+)',
    ]
    for pat in score_patterns:
        html = re.sub(pat, r'<mark>\1</mark>', html, flags=re.IGNORECASE)

    # Style checkmarks
    html = html.replace('✔', '<span style="color:#1F7A1F; font-weight:bold;">✔</span>')
    html = html.replace('✓', '<span style="color:#1F7A1F; font-weight:bold;">✓</span>')

    return html


def create_report_pdf(
    markdown_content: str,
    report_title: str,
    report_subtitle: str,
    report_type: str,
    company_details: Optional[Dict] = None,
    report_date: str = "",
) -> bytes:
    """
    Convert markdown report content to a styled, professional PDF.
    Includes a cover page when company_details is supplied.

    Args:
        markdown_content: Full report in Markdown (with tables, headings, etc.)
        report_title: Main title shown on cover and H1
        report_subtitle: Subtitle shown on cover
        report_type: Short label e.g. "Barrier Analysis" or "Strategic Roadmap"
        company_details: dict with company_name, industry, num_employees, annual_revenue
        report_date: Formatted date string

    Returns:
        PDF bytes
    """
    # Convert Markdown → HTML
    body_html = markdown2.markdown(
        markdown_content,
        extras=["tables", "fenced-code-blocks", "header-ids", "strike", "footnotes"],
    )
    body_html = _post_process_html(body_html)

    # Build cover page HTML
    cover_html = ""
    if company_details:
        cover_html = _build_cover_html(
            company_name=company_details.get("company_name", ""),
            industry=company_details.get("industry", ""),
            num_employees=company_details.get("num_employees", 0),
            annual_revenue=company_details.get("annual_revenue", 0),
            report_date=report_date,
            report_type=report_type,
            report_title=report_title,
            report_subtitle=report_subtitle,
        )

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{report_title}</title>
</head>
<body>
{cover_html}
{body_html}
</body>
</html>"""

    css_string = _BASE_CSS + _COVER_CSS
    pdf_bytes = HTML(string=full_html).write_pdf(stylesheets=[CSS(string=css_string)])
    return pdf_bytes


# ── Backwards-compatible wrapper used by existing app.py calls ───────────────

def create_pdf_from_markdown(
    markdown_content: str,
    report_title: str,
    css_style: Optional[str] = None,
    company_details: Optional[Dict] = None,
    report_date: str = "",
) -> bytes:
    """
    Drop-in replacement for the old create_pdf_from_markdown.
    css_style is ignored (new styling is applied automatically).
    """
    # Determine report type from title
    if "roadmap" in report_title.lower():
        rtype = "Strategic Roadmap"
        subtitle = "18-Month IoT Transformation Plan — Top 3 Critical Barriers"
    else:
        rtype = "Barrier Analysis"
        subtitle = "IoT Adoption Readiness Assessment — All 15 Barriers"

    return create_report_pdf(
        markdown_content=markdown_content,
        report_title=report_title,
        report_subtitle=subtitle,
        report_type=rtype,
        company_details=company_details,
        report_date=report_date,
    )
