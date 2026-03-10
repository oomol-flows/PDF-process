#region generated meta
import typing
class Inputs(typing.TypedDict):
    md_content: str
    title: str | None
    font_size: typing.Literal[10, 11, 12, 14, 16]
    color_scheme: typing.Literal["elegant_blue", "warm_earth", "modern_dark", "classic_serif", "minimal_gray"]
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import markdown
from xml.etree import ElementTree
import os
import re

# Color schemes with design sense
COLOR_SCHEMES = {
    "elegant_blue": {
        "primary": "#1a365d",      # Deep blue
        "secondary": "#2c5282",    # Medium blue
        "accent": "#3182ce",       # Bright blue
        "text": "#1a202c",         # Dark gray
        "light_bg": "#ebf8ff",     # Light blue bg
        "code_bg": "#f7fafc",      # Code background
        "border": "#bee3f8",       # Border color
    },
    "warm_earth": {
        "primary": "#744210",      # Brown
        "secondary": "#975a16",    # Dark gold
        "accent": "#d69e2e",       # Gold
        "text": "#1a202c",         # Dark gray
        "light_bg": "#fffaf0",     # Warm white
        "code_bg": "#fef3c7",      # Light amber
        "border": "#f6e05e",       # Yellow border
    },
    "modern_dark": {
        "primary": "#e2e8f0",      # Light gray
        "secondary": "#a0aec0",    # Medium gray
        "accent": "#63b3ed",       # Blue accent
        "text": "#e2e8f0",         # Light text
        "light_bg": "#2d3748",     # Dark bg
        "code_bg": "#1a202c",      # Darker code bg
        "border": "#4a5568",       # Border
    },
    "classic_serif": {
        "primary": "#2d3748",      # Dark slate
        "secondary": "#4a5568",    # Slate
        "accent": "#718096",       # Gray
        "text": "#1a202c",         # Near black
        "light_bg": "#f7f7f7",     # Off white
        "code_bg": "#f0f0f0",      # Light gray
        "border": "#cbd5e0",       # Light border
    },
    "minimal_gray": {
        "primary": "#1a202c",      # Dark
        "secondary": "#4a5568",    # Medium
        "accent": "#718096",       # Light accent
        "text": "#2d3748",         # Text
        "light_bg": "#ffffff",     # White
        "code_bg": "#f7fafc",      # Near white
        "border": "#e2e8f0",       # Very light
    },
}


def register_fonts():
    """Register Chinese fonts for PDF generation"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_paths[0]))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_paths[1]))
        pdfmetrics.registerFont(TTFont('DejaVuSansMono', font_paths[2]))
        return True
    except Exception:
        return False


def create_styles(color_scheme: str, base_font_size: int) -> dict:
    """Create custom paragraph styles based on color scheme"""
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant_blue"])
    
    styles = getSampleStyleSheet()
    custom_styles = {}
    
    # Base font name
    font_name = "DejaVuSans" if register_fonts() else "Helvetica"
    font_bold = "DejaVuSans-Bold" if register_fonts() else "Helvetica-Bold"
    font_mono = "DejaVuSansMono" if register_fonts() else "Courier"
    
    # Title style
    custom_styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=font_bold,
        fontSize=base_font_size * 2,
        textColor=HexColor(colors['primary']),
        spaceAfter=20 * mm,
        alignment=TA_CENTER,
    )
    
    # Heading styles
    for i in range(1, 7):
        size_factor = 2.2 - (i - 1) * 0.25
        custom_styles[f'heading{i}'] = ParagraphStyle(
            f'CustomHeading{i}',
            parent=styles[f'Heading{i}'],
            fontName=font_bold,
            fontSize=int(base_font_size * size_factor),
            textColor=HexColor(colors['primary']),
            spaceBefore=12 * mm if i <= 2 else 8 * mm,
            spaceAfter=4 * mm,
            borderPadding=2 * mm,
        )
    
    # Body text
    custom_styles['body'] = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=base_font_size,
        textColor=HexColor(colors['text']),
        leading=base_font_size * 1.6,
        alignment=TA_JUSTIFY,
        spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    )
    
    # Code style - for syntax highlighted code blocks
    # NOTE: backColor prevents <font color> from working, so we use borderPadding for visual separation
    custom_styles['code'] = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontName=font_mono,
        fontSize=base_font_size * 0.85,
        textColor=HexColor('#2d3748'),  # Dark gray for default text
        backColor=None,  # MUST be None to allow <font color> tags to work
        borderColor=HexColor('#e2e8f0'),
        borderWidth=1,
        borderPadding=12,
        spaceBefore=4 * mm,
        spaceAfter=4 * mm,
        leftIndent=4 * mm,
        rightIndent=4 * mm,
        leading=base_font_size * 1.5,
        allowWidows=0,
        allowOrphans=0,
    )
    
    # Inline code style
    custom_styles['inline_code'] = ParagraphStyle(
        'InlineCode',
        parent=styles['Normal'],
        fontName=font_mono,
        fontSize=base_font_size * 0.9,
        textColor=HexColor(colors['accent']),
        backColor=HexColor(colors['code_bg']),
        borderPadding=2,
    )
    
    # Blockquote style
    custom_styles['blockquote'] = ParagraphStyle(
        'CustomBlockquote',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=base_font_size,
        textColor=HexColor(colors['secondary']),
        leftIndent=10 * mm,
        rightIndent=10 * mm,
        spaceBefore=4 * mm,
        spaceAfter=4 * mm,
        borderPadding=4 * mm,
        borderColor=HexColor(colors['accent']),
        borderWidth=2,
        borderRadius=2,
    )
    
    # Link style
    custom_styles['link'] = ParagraphStyle(
        'CustomLink',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=base_font_size,
        textColor=HexColor(colors['accent']),
        underline=True,
    )
    
    return custom_styles


def highlight_code(code: str) -> str:
    """Format code for PDF display

    Note: Reportlab's Paragraph class has limited support for inline color formatting.
    This function formats code with proper escaping and line breaks, but uses a
    monochrome style. For full syntax highlighting, consider using WeasyPrint or
    other HTML-to-PDF libraries in the future.
    """
    # Escape XML special characters
    safe_code = (code
                 .replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;')
                 .replace('"', '&quot;'))

    # Convert newlines to <br/> and preserve indentation
    formatted = safe_code.replace('\n', '<br/>')
    formatted = formatted.replace('  ', '&nbsp;&nbsp;')

    # Wrap in monospace font
    formatted = f'<font face="DejaVuSansMono">{formatted}</font>'

    return formatted


def parse_markdown_element(element, styles: dict, colors: dict) -> list:
    """Parse a single markdown element and return reportlab flowables"""
    flowables = []
    tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
    
    if tag == 'h1':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading1']))
    elif tag == 'h2':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading2']))
    elif tag == 'h3':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading3']))
    elif tag == 'h4':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading4']))
    elif tag == 'h5':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading5']))
    elif tag == 'h6':
        text = element.text or ''
        flowables.append(Paragraph(text, styles['heading6']))
    elif tag == 'p':
        # Handle inline formatting
        text = process_inline_formatting(element, styles)
        if text.strip():
            flowables.append(Paragraph(text, styles['body']))
    elif tag == 'pre':
        code_elem = element.find('.//code') if element.find('.//code') is not None else element
        code_text = code_elem.text or ''

        if not code_text:
            # Try to get text from child elements
            code_text = ''.join(code_elem.itertext()) if code_elem is not None else ''

        # Apply code formatting (monochrome due to Reportlab limitations)
        highlighted_code = highlight_code(code_text)

        # Create paragraph with formatted code
        code_para = Paragraph(
            highlighted_code,
            styles['code']
        )
        flowables.append(code_para)
    elif tag == 'code':
        # Inline code
        code_text = element.text or ''
        code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        flowables.append(Paragraph(f'<font face="DejaVuSansMono" size="10" color="{colors["text"]}">{code_text}</font>', styles['body']))
    elif tag == 'blockquote':
        text = process_inline_formatting(element, styles)
        flowables.append(Paragraph(text, styles['blockquote']))
    elif tag == 'ul':
        items = []
        for li in element.findall('.//li'):
            li_text = process_inline_formatting(li, styles)
            items.append(ListItem(Paragraph(li_text, styles['body']), bulletColor=HexColor(colors['accent'])))
        if items:
            flowables.append(ListFlowable(items, bulletType='bullet', start='•'))
    elif tag == 'ol':
        items = []
        for li in element.findall('.//li'):
            li_text = process_inline_formatting(li, styles)
            items.append(ListItem(Paragraph(li_text, styles['body'])))
        if items:
            flowables.append(ListFlowable(items, bulletType='1', start=1))
    elif tag == 'hr':
        flowables.append(Spacer(1, 5 * mm))
    elif tag == 'a':
        href = element.get('href', '')
        text = element.text or href
        link_text = f'<link href="{href}" color="{colors["accent"]}">{text}</link>'
        flowables.append(Paragraph(link_text, styles['body']))
    elif tag == 'img':
        # For images, we just add a placeholder text
        alt = element.get('alt', 'Image')
        src = element.get('src', '')
        flowables.append(Paragraph(f'[Image: {alt}] ({src})', styles['body']))
    elif tag == 'table':
        # Simplified table handling - just render as text
        rows = []
        for tr in element.findall('.//tr'):
            cells = []
            for td in tr.findall('.//td') + tr.findall('.//th'):
                cells.append(td.text or '')
            rows.append(' | '.join(cells))
        if rows:
            table_text = '<br/>'.join(rows)
            flowables.append(Paragraph(table_text, styles['code']))
    else:
        # Handle other elements recursively
        if element.text and element.text.strip():
            flowables.append(Paragraph(element.text, styles['body']))
        for child in element:
            flowables.extend(parse_markdown_element(child, styles, colors))
        if element.tail and element.tail.strip():
            flowables.append(Paragraph(element.tail, styles['body']))
    
    return flowables


def process_inline_formatting(element, styles: dict) -> str:
    """Process inline formatting like bold, italic, code, links"""
    result = element.text or ''
    
    for child in element:
        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        
        if child_tag == 'strong' or child_tag == 'b':
            result += f'<b>{child.text or ""}</b>'
        elif child_tag == 'em' or child_tag == 'i':
            result += f'<i>{child.text or ""}</i>'
        elif child_tag == 'code':
            code_text = child.text or ''
            code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            result += f'<font face="DejaVuSansMono" size="10">{code_text}</font>'
        elif child_tag == 'a':
            href = child.get('href', '')
            text = child.text or href
            result += f'<link href="{href}">{text}</link>'
        else:
            result += child.text or ''
        
        result += child.tail or ''
    
    return result


def markdown_to_flowables(md_content: str, styles: dict, colors: dict) -> list:
    """Convert markdown content to reportlab flowables"""
    # Configure markdown extension
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'toc',
        'nl2br',
    ])
    
    # Convert markdown to HTML
    html_content = md.convert(md_content)
    
    # Parse HTML
    try:
        root = ElementTree.fromstring(f'<root>{html_content}</root>')
    except ElementTree.ParseError:
        # Fallback: treat as plain text
        return [Paragraph(md_content.replace('\n', '<br/>'), styles['body'])]
    
    flowables = []
    for element in root:
        flowables.extend(parse_markdown_element(element, styles, colors))
    
    return flowables


def add_page_decorations(canvas, doc, colors: dict):
    """Add page header and footer decorations"""
    canvas.saveState()
    
    page_width, page_height = A4
    
    # Header line
    canvas.setStrokeColor(HexColor(colors['border']))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, page_height - 15 * mm, page_width - 20 * mm, page_height - 15 * mm)
    
    # Footer line
    canvas.line(20 * mm, 15 * mm, page_width - 20 * mm, 15 * mm)
    
    # Page number
    canvas.setFont('DejaVuSans' if register_fonts() else 'Helvetica', 9)
    canvas.setFillColor(HexColor(colors['secondary']))
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(page_width / 2, 8 * mm, f"— {page_num} —")
    
    canvas.restoreState()


async def main(params: Inputs, context: Context) -> Outputs:
    """Main function to convert markdown to PDF"""
    md_content = params.get("md_content", "")
    if not md_content:
        raise ValueError("md_content is required")
    
    title = params.get("title", "")
    font_size = params.get("font_size", 11)
    color_scheme = params.get("color_scheme", "elegant_blue")
    output_path = params.get("output_path") or context.session_dir
    
    # Ensure output path ends with .pdf
    if not output_path.endswith('.pdf'):
        output_path = os.path.join(output_path, "output.pdf")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Get color scheme
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant_blue"])
    
    # Create styles
    styles = create_styles(color_scheme, font_size)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )
    
    # Build flowables
    story = []
    
    # Add title if provided
    if title:
        story.append(Paragraph(title, styles['title']))
        story.append(Spacer(1, 10 * mm))
    
    # Convert markdown to flowables
    flowables = markdown_to_flowables(md_content, styles, colors)
    story.extend(flowables)
    
    # Build PDF with decorations
    doc.build(
        story,
        onFirstPage=lambda c, d: add_page_decorations(c, d, colors),
        onLaterPages=lambda c, d: add_page_decorations(c, d, colors),
    )
    
    return {"pdf_path": output_path}