"""Utility functions for font manipulation."""

from typing import List, Tuple, Optional

from fontTools.ttLib import TTFont


def set_font_name(
    font: TTFont,
    name: str,
    name_id: int,
    mac: bool = True,
    lang_id: int = 0x409
) -> None:
    """Set font name entry.

    Args:
        font: TTFont object
        name: Name string to set
        name_id: Name table ID
        mac: Whether to also set Mac platform entry (default True for macOS compatibility)
        lang_id: Language ID (default 0x409 for US English)
    """
    name_table = font["name"]

    # Only remove existing entries if we are setting English (default)
    # This allows adding multiple languages for the same NameID
    if lang_id == 0x409:
        name_table.removeNames(nameID=name_id)

    # Windows platform (platformID=3, platEncID=1 = Unicode BMP)
    name_table.setName(
        name, nameID=name_id, platformID=3, platEncID=1, langID=lang_id
    )

    # Mac platform (platformID=1, platEncID=0 = Roman, langID=0 = English)
    # Only set for English
    if mac and lang_id == 0x409:
        name_table.setName(
            name, nameID=name_id, platformID=1, platEncID=0, langID=0x0
        )


def update_font_names(
    font: TTFont,
    family_name: str,
    style_name: str,
    full_name: str,
    postscript_name: str,
    version_str: str,
    author: str = "",
    copyright_str: str = "",
    description: str = "",
    url: str = "",
    license_desc: str = "",
    license_url: str = "",
) -> None:
    """Update font metadata names.

    Args:
        font: TTFont object
        family_name: Font family name (NameID 1)
        style_name: Font subfamily/style name (NameID 2)
        full_name: Full font name (NameID 4)
        postscript_name: PostScript name (NameID 6)
        version_str: Version string (NameID 5)
        author: Author/designer name (NameID 8, 9)
        copyright_str: Copyright notice (NameID 0)
        description: Font description (NameID 10)
        url: Vendor/Designer URL (NameID 11, 12)
        license_desc: License description (NameID 13)
        license_url: License URL (NameID 14)
    """
    unique_id = f"{version_str};JBLXGW;{postscript_name}"

    # English names (Language ID 0x409)
    # NameID 0: Copyright
    if copyright_str:
        set_font_name(font, copyright_str, 0)
    # NameID 1: Family name
    set_font_name(font, family_name, 1)
    # NameID 2: Subfamily name
    set_font_name(font, style_name, 2)
    # NameID 3: Unique ID
    set_font_name(font, unique_id, 3)
    # NameID 4: Full name
    set_font_name(font, full_name, 4)
    # NameID 5: Version string
    set_font_name(font, version_str, 5)
    # NameID 6: PostScript name
    set_font_name(font, postscript_name, 6)
    # NameID 7: Trademark (clear it)
    set_font_name(font, "", 7)
    # NameID 8: Manufacturer
    if author:
        set_font_name(font, author, 8)
    # NameID 9: Designer
    if author:
        set_font_name(font, author, 9)
    # NameID 10: Description
    if description:
        set_font_name(font, description, 10)
    # NameID 11: Vendor URL
    if url:
        set_font_name(font, url, 11)
    # NameID 12: Designer URL
    if url:
        set_font_name(font, url, 12)
    # NameID 13: License description
    if license_desc:
        set_font_name(font, license_desc, 13)
    # NameID 14: License URL
    if license_url:
        set_font_name(font, license_url, 14)

    # Set Preferred family/style (NameID 16, 17) for better Windows compatibility
    set_font_name(font, family_name, 16)  # Preferred Family
    set_font_name(font, style_name, 17)  # Preferred Subfamily

    # Add Chinese names (Language ID 0x804) for better Windows CJK compatibility
    # Using the same names as English for now, but registering them under zh-CN
    # This helps Excel recognize the font as supporting Chinese regions
    cn_lang_id = 0x804
    set_font_name(font, family_name, 1, mac=False, lang_id=cn_lang_id)
    set_font_name(font, style_name, 2, mac=False, lang_id=cn_lang_id)
    set_font_name(font, full_name, 4, mac=False, lang_id=cn_lang_id)
    set_font_name(font, family_name, 16, mac=False, lang_id=cn_lang_id)
    set_font_name(font, style_name, 17, mac=False, lang_id=cn_lang_id)


def merge_os2_ranges(target_font: TTFont, source_font: TTFont) -> None:
    """Merge OS/2 table ranges (Unicode ranges and Code Page ranges).

    This is critical for Windows applications (like Excel) to recognize
    Chinese character support.

    Args:
        target_font: The font to update
        source_font: The source font (usually the CJK font)
    """
    if "OS/2" not in target_font or "OS/2" not in source_font:
        return

    target_os2 = target_font["OS/2"]
    source_os2 = source_font["OS/2"]

    # Merge Unicode Ranges (ulUnicodeRange1-4)
    # These are bit fields indicating supported Unicode blocks
    if hasattr(target_os2, "ulUnicodeRange1") and hasattr(source_os2, "ulUnicodeRange1"):
        target_os2.ulUnicodeRange1 |= source_os2.ulUnicodeRange1
        target_os2.ulUnicodeRange2 |= source_os2.ulUnicodeRange2
        target_os2.ulUnicodeRange3 |= source_os2.ulUnicodeRange3
        target_os2.ulUnicodeRange4 |= source_os2.ulUnicodeRange4
        print("  Merged OS/2 Unicode Ranges")

    # Merge Code Page Ranges (ulCodePageRange1-2)
    # These are bit fields indicating supported code pages (e.g. 936 for GBK)
    if hasattr(target_os2, "ulCodePageRange1") and hasattr(source_os2, "ulCodePageRange1"):
        target_os2.ulCodePageRange1 |= source_os2.ulCodePageRange1
        target_os2.ulCodePageRange2 |= source_os2.ulCodePageRange2
        print("  Merged OS/2 Code Page Ranges")


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
