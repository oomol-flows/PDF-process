#region generated meta
import typing
class Inputs(typing.TypedDict):
    html_content: str
    title: str | None
    font_size: typing.Literal[10, 11, 12, 14, 16]
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
import os


def get_font_path() -> str:
    """Get the best available Chinese font path."""
    # Prefer OTF font (WeasyPrint supports OTF natively)
    otf_path = "/usr/share/fonts/SourceHanSans/SourceHanSansSC-Normal.otf"
    ttf_path = "/usr/share/fonts/NotoSansSC/NotoSansSC-Regular.ttf"
    
    if os.path.exists(otf_path):
        return otf_path
    elif os.path.exists(ttf_path):
        return ttf_path
    else:
        raise FileNotFoundError("No Chinese font found")


def get_base_css(font_path: str) -> str:
    """Generate base CSS with Chinese font support."""
    return f"""
    @font-face {{
        font-family: 'SourceHanSans';
        src: url('{font_path}');
        font-weight: normal;
        font-style: normal;
    }}
    
    @page {{
        margin: 2cm;
        size: A4;
        @bottom-center {{
            content: counter(page);
            font-size: 9pt;
            color: #718096;
        }}
    }}
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: 'SourceHanSans', 'Noto Sans SC', 'WenQuanYi Micro Hei', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #1a202c;
    }}
    
    h1 {{
        font-size: 22pt;
        color: #1a365d;
        margin-top: 0.8em;
        margin-bottom: 0.4em;
        padding-bottom: 0.2em;
        border-bottom: 2px solid #3182ce;
        page-break-after: avoid;
    }}
    
    h2 {{
        font-size: 16pt;
        color: #1a365d;
        margin-top: 0.8em;
        margin-bottom: 0.3em;
        page-break-after: avoid;
    }}
    
    h3 {{
        font-size: 13pt;
        color: #2c5282;
        margin-top: 0.6em;
        margin-bottom: 0.2em;
        page-break-after: avoid;
    }}
    
    h4, h5, h6 {{
        font-size: 11pt;
        color: #4a5568;
        margin-top: 0.5em;
        margin-bottom: 0.2em;
        page-break-after: avoid;
    }}
    
    p {{
        margin: 0.5em 0;
        text-align: justify;
    }}
    
    a {{
        color: #3182ce;
        text-decoration: none;
    }}
    
    a:hover {{
        text-decoration: underline;
    }}
    
    code {{
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        font-size: 10pt;
        background-color: #f7fafc;
        padding: 0.1em 0.3em;
        border-radius: 3px;
    }}
    
    pre {{
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        font-size: 9pt;
        background-color: #f7fafc;
        padding: 0.8em;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0.8em 0;
        page-break-inside: avoid;
    }}
    
    pre code {{
        background-color: transparent;
        padding: 0;
        border-radius: 0;
    }}
    
    blockquote {{
        border-left: 4px solid #3182ce;
        margin: 0.8em 0;
        padding: 0.5em 1em;
        background-color: #ebf8ff;
        color: #4a5568;
        font-style: italic;
    }}
    
    blockquote p {{
        margin: 0;
    }}
    
    ul, ol {{
        margin: 0.5em 0;
        padding-left: 1.5em;
    }}
    
    li {{
        margin: 0.2em 0;
    }}
    
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 0.8em 0;
        page-break-inside: avoid;
    }}
    
    th, td {{
        border: 1px solid #cbd5e0;
        padding: 0.5em 0.8em;
        text-align: left;
    }}
    
    th {{
        background-color: #edf2f7;
        font-weight: bold;
        color: #1a365d;
    }}
    
    tr:nth-child(even) {{
        background-color: #f7fafc;
    }}
    
    img {{
        max-width: 100%;
        height: auto;
    }}
    
    hr {{
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1em 0;
    }}
    """


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Convert HTML content to PDF using WeasyPrint.
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

    # Get font path
    font_path = get_font_path()
    base_css = get_base_css(font_path)

    # Get title
    title = params.get("title") or "Document"

    # Wrap HTML content with proper structure if not already present
    html_lower = html_content.lower()
    if "<html" not in html_lower:
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            head_close = html_lower.find("</head>")
            if head_close != -1:
                html_content = (
                    html_content[:head_close] + 
                    f"<style>{base_css}</style>" + 
                    html_content[head_close:]
                )

    # Convert HTML to PDF using WeasyPrint
    from weasyprint import HTML, CSS
    
    html = HTML(string=html_content, base_url="/")
    css = CSS(string=base_css)
    html.write_pdf(output_path, stylesheets=[css])

    return {"pdf_path": output_path}