"""Utility functions for font manipulation."""

from typing import List, Tuple

from fontTools.ttLib import TTFont


def set_font_name(font: TTFont, name: str, name_id: int, mac: bool = False) -> None:
    """Set font name entry.

    Args:
        font: TTFont object
        name: Name string to set
        name_id: Name table ID
        mac: Whether to also set Mac platform entry
    """
    # Windows platform
    font["name"].setName(
        name, nameID=name_id, platformID=3, platEncID=1, langID=0x409
    )
    # Mac platform (optional)
    if mac:
        font["name"].setName(
            name, nameID=name_id, platformID=1, platEncID=0, langID=0x0
        )


def update_font_names(
    font: TTFont,
    family_name: str,
    style_name: str,
    full_name: str,
    postscript_name: str,
    version_str: str,
) -> None:
    """Update font metadata names.

    Args:
        font: TTFont object
        family_name: Font family name (NameID 1)
        style_name: Font subfamily/style name (NameID 2)
        full_name: Full font name (NameID 4)
        postscript_name: PostScript name (NameID 6)
        version_str: Version string (NameID 5)
    """
    unique_id = f"{version_str};JBLXGW;{postscript_name}"

    set_font_name(font, family_name, 1)  # Family name
    set_font_name(font, style_name, 2)  # Subfamily name
    set_font_name(font, unique_id, 3)  # Unique ID
    set_font_name(font, full_name, 4)  # Full name
    set_font_name(font, version_str, 5)  # Version string
    set_font_name(font, postscript_name, 6)  # PostScript name

    # Preferred family/style (NameID 16, 17) for non-standard styles
    if style_name not in ("Regular", "Bold", "Italic", "Bold Italic"):
        base_style = style_name.replace(" Italic", "")
        set_font_name(font, family_name.replace(f" {base_style}", ""), 16)
        set_font_name(font, style_name, 17)


def is_cjk_codepoint(
    codepoint: int, cjk_ranges: Tuple[Tuple[int, int], ...]
) -> bool:
    """Check if a Unicode codepoint is in CJK ranges.

    Args:
        codepoint: Unicode codepoint
        cjk_ranges: Tuple of (start, end) ranges

    Returns:
        True if codepoint is in CJK ranges
    """
    for start, end in cjk_ranges:
        if start <= codepoint <= end:
            return True
    return False


def verify_glyph_width(
    font: TTFont, expected_widths: List[int], file_name: str | None = None
) -> None:
    """Verify all glyph widths are in expected values.

    Args:
        font: TTFont object
        expected_widths: List of valid advance widths
        file_name: Optional file name for error messages

    Raises:
        ValueError: If glyphs with unexpected widths are found
    """
    unexpected = []
    hmtx = font["hmtx"]

    for name in font.getGlyphOrder():
        width, _ = hmtx[name]
        if width not in expected_widths and width != 0:
            unexpected.append((name, width))

    if not unexpected:
        print(f"Verified glyph widths in {file_name or 'font'}")
        return

    # Show first 10 unexpected glyphs
    sample = unexpected[:10]
    sample_str = "\n".join(f"  {name}: {width}" for name, width in sample)
    raise ValueError(
        f"Found {len(unexpected)} glyphs with unexpected widths "
        f"(expected {expected_widths}):\n{sample_str}"
    )
