#region generated meta
import typing
class Inputs(typing.TypedDict):
    text: str
    title: str | None
    font_size: typing.Literal[10, 11, 12, 14, 16]
    color_scheme: typing.Literal["elegant-blue", "warm-earth", "modern-dark", "classic-serif", "minimal-gray"]
    output_path: str | None
class Outputs(typing.TypedDict):
    pdf_path: typing.NotRequired[str]
#endregion

from oocana import Context
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import mm, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
import re

# Color schemes with design-focused palettes
COLOR_SCHEMES = {
    "elegant-blue": {
        "primary": "#1E3A5F",        # Deep navy blue
        "secondary": "#4A90A4",     # Steel blue
        "accent": "#E8F4F8",        # Light blue background
        "text": "#2C3E50",          # Dark slate
        "title": "#1E3A5F",         # Same as primary
        "background": "#FFFFFF",
        "header_bg": "#E8F4F8",
    },
    "warm-earth": {
        "primary": "#8B4513",       # Saddle brown
        "secondary": "#D2691E",     # Chocolate
        "accent": "#FFF8DC",        # Cornsilk
        "text": "#3E2723",          # Dark brown
        "title": "#5D4037",         # Brown
        "background": "#FFFAF0",    # Floral white
        "header_bg": "#FFF8DC",
    },
    "modern-dark": {
        "primary": "#00BCD4",       # Cyan accent
        "secondary": "#78909C",     # Blue grey
        "accent": "#263238",        # Dark slate
        "text": "#ECEFF1",          # Light grey
        "title": "#00BCD4",         # Cyan
        "background": "#1A1A2E",    # Dark navy
        "header_bg": "#16213E",
    },
    "classic-serif": {
        "primary": "#2C3E50",       # Dark blue grey
        "secondary": "#7F8C8D",     # Grey
        "accent": "#F5F5F5",        # White smoke
        "text": "#333333",          # Dark grey
        "title": "#2C3E50",         # Dark blue grey
        "background": "#FFFFFF",
        "header_bg": "#F5F5F5",
    },
    "minimal-gray": {
        "primary": "#212121",       # Almost black
        "secondary": "#757575",     # Medium grey
        "accent": "#FAFAFA",        # Almost white
        "text": "#424242",          # Dark grey
        "title": "#212121",         # Almost black
        "background": "#FFFFFF",
        "header_bg": "#F5F5F5",
    },
}


def register_fonts():
    """Register fonts for PDF generation."""
    try:
        # Try to register common fonts
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                font_name = os.path.basename(path).replace(".ttf", "")
                pdfmetrics.registerFont(TTFont(font_name, path))
        
        return True
    except Exception:
        return False


def create_styles(color_scheme: str, font_size: int) -> dict:
    """Create custom paragraph styles based on color scheme."""
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant-blue"])
    
    styles = getSampleStyleSheet()
    custom_styles = {}
    
    # Title style
    custom_styles["title"] = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=font_size + 8,
        textColor=HexColor(colors["title"]),
        spaceAfter=20 * mm,
        spaceBefore=10 * mm,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    
    # Heading style
    custom_styles["heading"] = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=font_size + 4,
        textColor=HexColor(colors["primary"]),
        spaceAfter=10 * mm,
        spaceBefore=15 * mm,
        fontName="Helvetica-Bold",
    )
    
    # Body text style
    custom_styles["body"] = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=font_size,
        textColor=HexColor(colors["text"]),
        spaceAfter=6 * mm,
        spaceBefore=3 * mm,
        alignment=TA_JUSTIFY,
        leading=font_size * 1.5,
        fontName="Helvetica",
    )
    
    # Quote style
    custom_styles["quote"] = ParagraphStyle(
        "CustomQuote",
        parent=styles["Normal"],
        fontSize=font_size - 1,
        textColor=HexColor(colors["secondary"]),
        spaceAfter=8 * mm,
        spaceBefore=8 * mm,
        leftIndent=15 * mm,
        rightIndent=15 * mm,
        fontName="Helvetica-Oblique",
    )
    
    # Caption style
    custom_styles["caption"] = ParagraphStyle(
        "CustomCaption",
        parent=styles["Normal"],
        fontSize=font_size - 2,
        textColor=HexColor(colors["secondary"]),
        spaceAfter=5 * mm,
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique",
    )
    
    return custom_styles


def parse_text_structure(text: str) -> list:
    """Parse text into structured elements (title, headings, paragraphs, quotes)."""
    elements = []
    lines = text.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect headings (lines starting with # or ALL CAPS)
        if line.startswith("# "):
            elements.append(("heading", line[2:]))
        elif line.startswith("## "):
            elements.append(("subheading", line[3:]))
        elif line.startswith("> "):
            elements.append(("quote", line[2:]))
        elif line.startswith("- ") or line.startswith("* "):
            elements.append(("bullet", line[2:]))
        elif re.match(r"^[A-Z][A-Z\s]+:$", line):
            # ALL CAPS heading with colon
            elements.append(("heading", line.rstrip(":")))
        else:
            elements.append(("paragraph", line))
    
    return elements


def build_pdf_content(elements: list, styles: dict, title: str = None) -> list:
    """Build PDF content from parsed elements."""
    story = []
    
    # Add title if provided
    if title:
        story.append(Paragraph(title, styles["title"]))
        story.append(Spacer(1, 10 * mm))
    
    for element_type, content in elements:
        if element_type == "heading":
            story.append(Paragraph(content, styles["heading"]))
        elif element_type == "subheading":
            # Use slightly smaller heading
            story.append(Paragraph(content, styles["heading"]))
        elif element_type == "quote":
            story.append(Paragraph(f'"{content}"', styles["quote"]))
        elif element_type == "bullet":
            story.append(Paragraph(f"• {content}", styles["body"]))
        else:
            story.append(Paragraph(content, styles["body"]))
    
    return story


def add_page_decorations(canvas, doc, colors: dict):
    """Add decorative elements to each page."""
    canvas.saveState()
    
    # Add subtle header line
    canvas.setStrokeColor(HexColor(colors["primary"]))
    canvas.setLineWidth(0.5)
    canvas.line(
        20 * mm, 
        A4[1] - 15 * mm, 
        A4[0] - 20 * mm, 
        A4[1] - 15 * mm
    )
    
    # Add subtle footer line
    canvas.line(
        20 * mm, 
        15 * mm, 
        A4[0] - 20 * mm, 
        15 * mm
    )
    
    # Add page number
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(HexColor(colors["secondary"]))
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(
        A4[0] / 2, 
        10 * mm, 
        f"— {page_num} —"
    )
    
    canvas.restoreState()


async def main(params: Inputs, context: Context) -> Outputs:
    """Main function to convert text to PDF."""
    text = params.get("text", "")
    title = params.get("title", "")
    font_size = params.get("font_size", 11)
    color_scheme = params.get("color_scheme", "elegant-blue")
    output_path = params.get("output_path")
    
    if not text:
        raise ValueError("Text content is required")
    
    # Determine output path
    if not output_path:
        output_path = os.path.join(context.session_dir, "output.pdf")
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Register fonts
    register_fonts()
    
    # Get color scheme
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["elegant-blue"])
    
    # Create styles
    styles = create_styles(color_scheme, font_size)
    
    # Parse text structure
    elements = parse_text_structure(text)
    
    # Build PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )
    
    # Build content
    story = build_pdf_content(elements, styles, title if title else None)
    
    # Build PDF with page decorations
    doc.build(
        story,
        onFirstPage=lambda c, d: add_page_decorations(c, d, colors),
        onLaterPages=lambda c, d: add_page_decorations(c, d, colors),
    )
    
    return {"pdf_path": output_path}