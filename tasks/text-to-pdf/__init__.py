#region generated meta
import typing
class Inputs(typing.TypedDict):
    text_content: str
    title: str | None
    font_size: typing.Literal[10, 11, 12, 14, 16]
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
import os
import re

# Color schemes with design-focused palettes
COLOR_SCHEMES = {
    "elegant-blue": {
        "primary": "#1E3A5F",
        "secondary": "#4A90A4",
        "accent": "#E8F4F8",
        "text": "#2C3E50",
        "title": "#1E3A5F",
        "background": "#FFFFFF",
        "header_bg": "#E8F4F8",
    },
    "warm-earth": {
        "primary": "#8B4513",
        "secondary": "#D2691E",
        "accent": "#FFF8DC",
        "text": "#3E2723",
        "title": "#5D4037",
        "background": "#FFFAF0",
        "header_bg": "#FFF8DC",
    },
    "modern-dark": {
        "primary": "#00BCD4",
        "secondary": "#78909C",
        "accent": "#263238",
        "text": "#ECEFF1",
        "title": "#00BCD4",
        "background": "#1A1A2E",
        "header_bg": "#16213E",
    },
    "classic-serif": {
        "primary": "#2C3E50",
        "secondary": "#7F8C8D",
        "accent": "#F5F5F5",
        "text": "#333333",
        "title": "#2C3E50",
        "background": "#FFFFFF",
        "header_bg": "#F5F5F5",
    },
    "minimal-gray": {
        "primary": "#212121",
        "secondary": "#757575",
        "accent": "#FAFAFA",
        "text": "#424242",
        "title": "#212121",
        "background": "#FFFFFF",
        "header_bg": "#F5F5F5",
    },
}


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


def generate_css(color_scheme: str, font_size: int, font_path: str) -> str:
    """Generate CSS styles based on color scheme."""
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant-blue"])
    
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
        @top-center {{
            content: attr(data-title);
            font-size: 9pt;
            color: {colors['secondary']};
        }}
        @bottom-center {{
            content: counter(page);
            font-size: 9pt;
            color: {colors['secondary']};
        }}
    }}
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: 'SourceHanSans', 'Noto Sans SC', 'WenQuanYi Micro Hei', sans-serif;
        font-size: {font_size}pt;
        line-height: 1.8;
        color: {colors['text']};
        background-color: {colors['background']};
    }}
    
    .document-title {{
        font-size: {font_size + 8}pt;
        color: {colors['title']};
        text-align: center;
        margin-bottom: 1.5em;
        padding-bottom: 0.5em;
        border-bottom: 2px solid {colors['primary']};
    }}
    
    .heading {{
        font-size: {font_size + 4}pt;
        color: {colors['primary']};
        margin-top: 1.2em;
        margin-bottom: 0.6em;
        padding-bottom: 0.2em;
        border-bottom: 1px solid {colors['header_bg']};
        page-break-after: avoid;
    }}
    
    .subheading {{
        font-size: {font_size + 2}pt;
        color: {colors['secondary']};
        margin-top: 1em;
        margin-bottom: 0.4em;
        page-break-after: avoid;
    }}
    
    .paragraph {{
        margin: 0.6em 0;
        text-align: justify;
    }}
    
    .quote {{
        border-left: 4px solid {colors['primary']};
        margin: 1em 0;
        padding: 0.5em 1em;
        background-color: {colors['accent']};
        color: {colors['secondary']};
        font-style: italic;
    }}
    
    .bullet-item {{
        margin: 0.3em 0;
        padding-left: 1.5em;
        position: relative;
    }}
    
    .bullet-item::before {{
        content: "•";
        position: absolute;
        left: 0.5em;
        color: {colors['primary']};
    }}
    
    .caption {{
        font-size: {font_size - 1}pt;
        color: {colors['secondary']};
        text-align: center;
        margin: 0.5em 0;
    }}
    """


def parse_text_structure(text: str) -> list:
    """Parse text into structured elements."""
    elements = []
    lines = text.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect headings
        if line.startswith("# "):
            elements.append(("heading", line[2:]))
        elif line.startswith("## "):
            elements.append(("subheading", line[3:]))
        elif line.startswith("> "):
            elements.append(("quote", line[2:]))
        elif line.startswith("- ") or line.startswith("* "):
            elements.append(("bullet", line[2:]))
        elif re.match(r"^[A-Z][A-Z\s]+:$", line):
            elements.append(("heading", line.rstrip(":")))
        else:
            elements.append(("paragraph", line))
    
    return elements


def build_html(elements: list, title: str, color_scheme: str, font_size: int, font_path: str) -> str:
    """Build HTML document from parsed elements."""
    css = generate_css(color_scheme, font_size, font_path)
    
    body_parts = []
    
    # Add title
    if title:
        body_parts.append(f'<div class="document-title">{title}</div>')
    
    for elem_type, content in elements:
        if elem_type == "heading":
            body_parts.append(f'<div class="heading">{content}</div>')
        elif elem_type == "subheading":
            body_parts.append(f'<div class="subheading">{content}</div>')
        elif elem_type == "quote":
            body_parts.append(f'<div class="quote">{content}</div>')
        elif elem_type == "bullet":
            body_parts.append(f'<div class="bullet-item">{content}</div>')
        else:
            body_parts.append(f'<div class="paragraph">{content}</div>')
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    {css}
    </style>
</head>
<body data-title="{title}">
    {''.join(body_parts)}
</body>
</html>"""


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Convert plain text to PDF using WeasyPrint.
    """
    text = params.get("text_content")
    if not text:
        raise ValueError("text is required")

    # Get parameters
    title = params.get("title") or "Document"
    font_size = params.get("font_size", 11)
    color_scheme = params.get("color_scheme", "elegant-blue")

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

    # Parse text and build HTML
    elements = parse_text_structure(text)
    html_content = build_html(elements, title, color_scheme, font_size, font_path)

    # Convert HTML to PDF using WeasyPrint
    from weasyprint import HTML, CSS
    
    css = generate_css(color_scheme, font_size, font_path)
    html = HTML(string=html_content, base_url="/")
    stylesheet = CSS(string=css)
    html.write_pdf(output_path, stylesheets=[stylesheet])

    return {"pdf_path": output_path}
