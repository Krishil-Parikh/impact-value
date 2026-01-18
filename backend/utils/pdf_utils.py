"""
PDF generation utilities
"""
import markdown2
from weasyprint import HTML, CSS
from typing import Optional


def create_pdf_from_markdown(markdown_content: str, report_title: str, css_style: Optional[str] = None) -> bytes:
    """
    Converts a markdown string into a styled PDF document in memory.
    
    Args:
        markdown_content: The markdown text to convert
        report_title: Title for the PDF document
        css_style: Optional custom CSS. If not provided, uses default styling.
    
    Returns:
        PDF document as bytes
    """
    # Convert markdown to HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=["tables", "fenced-code-blocks", "header-ids"]
    )
    
    # Default CSS if not provided
    if css_style is None:
        css_style = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }
        h1, h2, h3, h4 {
            font-family: 'Arial', sans-serif;
            color: #2c3e50;
            line-height: 1.3;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        h1 { 
            font-size: 24pt;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.3em;
        }
        h2 { 
            font-size: 20pt;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 0.2em;
        }
        h3 { 
            font-size: 16pt;
            font-weight: bold;
        }
        h4 { 
            font-size: 14pt;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1em;
            margin-bottom: 1em;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #ecf0f1;
        }
        p {
            margin-bottom: 0.8em;
            text-align: justify;
        }
        ul, ol {
            margin-left: 1.5em;
            margin-bottom: 1em;
        }
        li {
            margin-bottom: 0.3em;
        }
        strong {
            color: #2c3e50;
        }
        code {
            background-color: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        """
    
    # Build complete HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{report_title}</title>
    </head>
    <body>
        <h1>{report_title}</h1>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    html_doc = HTML(string=full_html)
    css_doc = CSS(string=css_style)
    pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
    
    return pdf_bytes
