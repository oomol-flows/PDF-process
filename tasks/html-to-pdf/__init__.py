#region generated meta
import typing
class Inputs(typing.TypedDict):
    html_content: str
    title: str | None
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
import os


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Convert HTML content to PDF using xhtml2pdf.
    """
    html_content = params.get("html_content")
    if not html_content:
        raise ValueError("html_content is required")

    # Determine output path
    output_path = params.get("output_path")
    if not output_path:
        output_path = os.path.join(context.session_dir, "output.pdf")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Import xhtml2pdf
    from xhtml2pdf import pisa
    import io

    # Build base CSS for better default styling
    base_css = """
    @page {
        margin: 2cm;
        size: A4;
    }
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #1a202c;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1a365d;
        margin-top: 1.2em;
        margin-bottom: 0.4em;
        font-weight: bold;
    }
    h1 { font-size: 22pt; }
    h2 { font-size: 16pt; }
    h3 { font-size: 13pt; }
    p {
        margin: 0.4em 0;
        text-align: justify;
    }
    a {
        color: #3182ce;
        text-decoration: underline;
    }
    code {
        font-family: Courier, monospace;
        background-color: #f0f0f0;
        padding: 0.1em 0.3em;
        font-size: 10pt;
    }
    pre {
        background-color: #f0f0f0;
        padding: 0.8em;
        border: 1px solid #ddd;
        font-family: Courier, monospace;
        font-size: 9pt;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 0.8em 0;
    }
    th, td {
        border: 1px solid #cbd5e0;
        padding: 0.4em 0.6em;
        text-align: left;
    }
    th {
        background-color: #edf2f7;
        font-weight: bold;
    }
    img {
        max-width: 100%;
    }
    blockquote {
        border-left: 3px solid #3182ce;
        margin: 0.8em 0;
        padding-left: 0.8em;
        color: #4a5568;
        font-style: italic;
    }
    ul, ol {
        margin: 0.4em 0;
        padding-left: 1.5em;
    }
    li {
        margin: 0.2em 0;
    }
    """

    # Wrap HTML content with proper structure if not already present
    html_lower = html_content.lower()
    if "<html" not in html_lower:
        title = params.get("title") or "Document"
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
    {base_css}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    else:
        # Inject CSS into existing HTML if style tag not present
        if "</style>" not in html_lower and "<style" not in html_lower:
            # Try to inject before </head>
            head_close = html_lower.find("</head>")
            if head_close != -1:
                html_content = (
                    html_content[:head_close] + 
                    f"<style>{base_css}</style>" + 
                    html_content[head_close:]
                )

    # Convert HTML to PDF
    with open(output_path, "wb") as output_file:
        # Convert string to bytes for pisa
        source = io.BytesIO(html_content.encode("utf-8"))
        
        # Convert
        result = pisa.pisaDocument(source, output_file, encoding="utf-8")
        
        if result.err:
            raise RuntimeError(f"PDF conversion failed with {result.err} errors")

    return {"pdf_path": output_path}