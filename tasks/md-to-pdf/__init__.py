#region generated meta
import typing
class Inputs(typing.TypedDict):
    md_content: str
    title: str | None
    font_size: typing.Literal[10, 11, 12, 14, 16]
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
import markdown
import os

# Color schemes with design sense
COLOR_SCHEMES = {
    "elegant_blue": {
        "primary": "#1a365d",
        "secondary": "#2c5282",
        "accent": "#3182ce",
        "text": "#1a202c",
        "light_bg": "#ebf8ff",
        "code_bg": "#f7fafc",
        "border": "#bee3f8",
        "background": "#ffffff",
    },
    "warm_earth": {
        "primary": "#744210",
        "secondary": "#975a16",
        "accent": "#d69e2e",
        "text": "#1a202c",
        "light_bg": "#fffaf0",
        "code_bg": "#fef3c7",
        "border": "#f6e05e",
        "background": "#fffaf0",
    },
    "modern_dark": {
        "primary": "#e2e8f0",
        "secondary": "#a0aec0",
        "accent": "#63b3ed",
        "text": "#e2e8f0",
        "light_bg": "#2d3748",
        "code_bg": "#1a202c",
        "border": "#4a5568",
        "background": "#1a202c",
    },
    "classic_serif": {
        "primary": "#2d3748",
        "secondary": "#4a5568",
        "accent": "#718096",
        "text": "#1a202c",
        "light_bg": "#f7f7f7",
        "code_bg": "#f0f0f0",
        "border": "#cbd5e0",
        "background": "#ffffff",
    },
    "minimal_gray": {
        "primary": "#1a202c",
        "secondary": "#4a5568",
        "accent": "#718096",
        "text": "#2d3748",
        "light_bg": "#ffffff",
        "code_bg": "#f7fafc",
        "border": "#e2e8f0",
        "background": "#ffffff",
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
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant_blue"])
    
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
        line-height: 1.6;
        color: {colors['text']};
        background-color: {colors['background']};
    }}
    
    h1 {{
        font-size: {font_size * 2}pt;
        color: {colors['primary']};
        margin-top: 0.8em;
        margin-bottom: 0.4em;
        padding-bottom: 0.2em;
        border-bottom: 2px solid {colors['accent']};
        page-break-after: avoid;
    }}
    
    h2 {{
        font-size: {int(font_size * 1.6)}pt;
        color: {colors['primary']};
        margin-top: 0.8em;
        margin-bottom: 0.3em;
        page-break-after: avoid;
    }}
    
    h3 {{
        font-size: {int(font_size * 1.3)}pt;
        color: {colors['secondary']};
        margin-top: 0.6em;
        margin-bottom: 0.2em;
        page-break-after: avoid;
    }}
    
    h4, h5, h6 {{
        font-size: {font_size}pt;
        color: {colors['secondary']};
        margin-top: 0.5em;
        margin-bottom: 0.2em;
        page-break-after: avoid;
    }}
    
    p {{
        margin: 0.5em 0;
        text-align: justify;
    }}
    
    a {{
        color: {colors['accent']};
        text-decoration: none;
    }}
    
    a:hover {{
        text-decoration: underline;
    }}
    
    code {{
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        font-size: {int(font_size * 0.9)}pt;
        background-color: {colors['code_bg']};
        padding: 0.1em 0.3em;
        border-radius: 3px;
    }}
    
    pre {{
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        font-size: {int(font_size * 0.85)}pt;
        background-color: {colors['code_bg']};
        padding: 0.8em;
        border: 1px solid {colors['border']};
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
        border-left: 4px solid {colors['accent']};
        margin: 0.8em 0;
        padding: 0.5em 1em;
        background-color: {colors['light_bg']};
        color: {colors['secondary']};
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
        border: 1px solid {colors['border']};
        padding: 0.5em 0.8em;
        text-align: left;
    }}
    
    th {{
        background-color: {colors['light_bg']};
        font-weight: bold;
        color: {colors['primary']};
    }}
    
    tr:nth-child(even) {{
        background-color: {colors['light_bg']};
    }}
    
    img {{
        max-width: 100%;
        height: auto;
    }}
    
    hr {{
        border: none;
        border-top: 1px solid {colors['border']};
        margin: 1em 0;
    }}
    
    /* Syntax highlighting colors */
    .highlight .hll {{ background-color: {colors['code_bg']} }}
    .highlight .c {{ color: #60a0b0; font-style: italic }}
    .highlight .err {{ color: #a00000 }}
    .highlight .k {{ color: #007020; font-weight: bold }}
    .highlight .o {{ color: #666666 }}
    .highlight .cm {{ color: #60a0b0; font-style: italic }}
    .highlight .cp {{ color: #007020 }}
    .highlight .c1 {{ color: #60a0b0; font-style: italic }}
    .highlight .cs {{ color: #60a0b0; background-color: #fff0f0 }}
    .highlight .gd {{ color: #a00000 }}
    .highlight .ge {{ font-style: italic }}
    .highlight .gr {{ color: #ff0000 }}
    .highlight .gh {{ color: #000080; font-weight: bold }}
    .highlight .gi {{ color: #00a000 }}
    .highlight .go {{ color: #888888 }}
    .highlight .gp {{ color: #c65d09; font-weight: bold }}
    .highlight .gs {{ font-weight: bold }}
    .highlight .gu {{ color: #800080; font-weight: bold }}
    .highlight .gt {{ color: #0044dd }}
    .highlight .kc {{ color: #007020; font-weight: bold }}
    .highlight .kd {{ color: #007020; font-weight: bold }}
    .highlight .kn {{ color: #007020; font-weight: bold }}
    .highlight .kp {{ color: #007020 }}
    .highlight .kr {{ color: #007020; font-weight: bold }}
    .highlight .kt {{ color: #902000 }}
    .highlight .m {{ color: #40a070 }}
    .highlight .s {{ color: #4070a0 }}
    .highlight .na {{ color: #4070a0 }}
    .highlight .nb {{ color: #007020 }}
    .highlight .nc {{ color: #0e84b5; font-weight: bold }}
    .highlight .no {{ color: #60add5 }}
    .highlight .nd {{ color: #555555; font-weight: bold }}
    .highlight .ni {{ color: #d55537; font-weight: bold }}
    .highlight .ne {{ color: #007020; font-weight: bold }}
    .highlight .nf {{ color: #06287e }}
    .highlight .nl {{ color: #002070; font-weight: bold }}
    .highlight .nn {{ color: #0e84b5; font-weight: bold }}
    .highlight .nt {{ color: #062875; font-weight: bold }}
    .highlight .nv {{ color: #bb60d5 }}
    .highlight .ow {{ color: #007020; font-weight: bold }}
    .highlight .w {{ color: #bbbbbb }}
    .highlight .mf {{ color: #40a070 }}
    .highlight .mh {{ color: #40a070 }}
    .highlight .mi {{ color: #40a070 }}
    .highlight .mo {{ color: #40a070 }}
    .highlight .sb {{ color: #4070a0 }}
    .highlight .sc {{ color: #4070a0 }}
    .highlight .sd {{ color: #4070a0; font-style: italic }}
    .highlight .s2 {{ color: #4070a0 }}
    .highlight .se {{ color: #4070a0; font-weight: bold }}
    .highlight .sh {{ color: #4070a0 }}
    .highlight .si {{ color: #70a0d0; font-style: italic }}
    .highlight .sx {{ color: #c65d09 }}
    .highlight .sr {{ color: #235388 }}
    .highlight .s1 {{ color: #4070a0 }}
    .highlight .ss {{ color: #517918 }}
    .highlight .bp {{ color: #007020 }}
    .highlight .vc {{ color: #bb60d5 }}
    .highlight .vg {{ color: #bb60d5 }}
    .highlight .vi {{ color: #bb60d5 }}
    .highlight .il {{ color: #40a070 }}
    """


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Convert Markdown content to PDF using WeasyPrint.
    """
    md_content = params.get("md_content")
    if not md_content:
        raise ValueError("md_content is required")

    # Get parameters
    title = params.get("title") or "Document"
    font_size = params.get("font_size", 11)
    color_scheme = params.get("color_scheme", "elegant_blue")

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

    # Generate CSS
    css_content = generate_css(color_scheme, font_size, font_path)

    # Convert Markdown to HTML with syntax highlighting
    md_converter = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "attr_list",
            "def_list",
            "abbr",
            "footnotes",
            "admonition",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
                "guess_lang": True,
            }
        }
    )
    html_body = md_converter.convert(md_content)

    # Build complete HTML document
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    {css_content}
    </style>
</head>
<body data-title="{title}">
    <h1>{title}</h1>
    {html_body}
</body>
</html>"""

    # Convert HTML to PDF using WeasyPrint
    from weasyprint import HTML, CSS
    
    html = HTML(string=html_content, base_url="/")
    css = CSS(string=css_content)
    html.write_pdf(output_path, stylesheets=[css])

    return {"pdf_path": output_path}
