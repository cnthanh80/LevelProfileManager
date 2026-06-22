from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REGULAR_FONT_NAME = "LPMUnicode"
BOLD_FONT_NAME = "LPMUnicode-Bold"

REGULAR_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

BOLD_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

_registered = False


def _first_existing(paths: list[str]) -> str | None:
    for value in paths:
        if Path(value).exists():
            return value
    return None


def register_unicode_fonts() -> tuple[str, str]:
    """Register Unicode TTF fonts for Vietnamese PDF output.

    The Dockerfile installs fonts-dejavu-core. If the font package is not
    available, ReportLab falls back to Helvetica, but Vietnamese output may not
    render correctly. Keeping fallback avoids breaking local/dev environments.
    """
    global _registered
    regular_path = _first_existing(REGULAR_FONT_CANDIDATES)
    bold_path = _first_existing(BOLD_FONT_CANDIDATES)
    if not regular_path:
        return "Helvetica", "Helvetica-Bold"
    if not _registered:
        pdfmetrics.registerFont(TTFont(REGULAR_FONT_NAME, regular_path))
        if bold_path:
            pdfmetrics.registerFont(TTFont(BOLD_FONT_NAME, bold_path))
        else:
            pdfmetrics.registerFont(TTFont(BOLD_FONT_NAME, regular_path))
        _registered = True
    return REGULAR_FONT_NAME, BOLD_FONT_NAME


def apply_unicode_styles(styles):
    regular, bold = register_unicode_fonts()
    for style in styles.byName.values():
        style.fontName = regular
    for name in ("Title", "Heading1", "Heading2", "Heading3", "Heading4"):
        if name in styles.byName:
            styles[name].fontName = bold
    return regular, bold
