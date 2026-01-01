"""Core font merging logic for JetBrainsLxgwNerdMono."""

from typing import Set

from fontTools.ttLib import TTFont

from .config import FontConfig
from .utils import is_cjk_codepoint


def get_cjk_glyphs(font: TTFont, config: FontConfig) -> Set[str]:
    """Get all CJK glyph names from a font.

    Args:
        font: TTFont object
        config: FontConfig with CJK ranges

    Returns:
        Set of glyph names that are CJK characters
    """
    cjk_glyphs = set()
    cmap = font["cmap"].getBestCmap()

    if cmap:
        for codepoint, glyph_name in cmap.items():
            if is_cjk_codepoint(codepoint, config.cjk_ranges):
                cjk_glyphs.add(glyph_name)

    return cjk_glyphs


def get_cjk_cmap_entries(font: TTFont, config: FontConfig) -> dict:
    """Get cmap entries for CJK codepoints.

    Args:
        font: TTFont object
        config: FontConfig with CJK ranges

    Returns:
        Dict mapping codepoint -> glyph_name for CJK characters
    """
    entries = {}
    cmap = font["cmap"].getBestCmap()

    if cmap:
        for codepoint, glyph_name in cmap.items():
            if is_cjk_codepoint(codepoint, config.cjk_ranges):
                entries[codepoint] = glyph_name

    return entries


def merge_fonts(
    base_font_path: str,
    cn_font_path: str,
    config: FontConfig,
) -> TTFont:
    """Merge CJK glyphs from cn_font into base_font.

    The base font (JetBrains Mono NerdFont) provides:
    - English characters
    - NerdFont icons

    The CN font (LXGW WenKai Mono) provides:
    - CJK characters

    Args:
        base_font_path: Path to JetBrains Mono NerdFont
        cn_font_path: Path to LXGW WenKai Mono
        config: FontConfig object

    Returns:
        Merged TTFont object
    """
    print(f"  Loading base font: {base_font_path}")
    base_font = TTFont(base_font_path)
    print(f"  Loading CN font: {cn_font_path}")
    cn_font = TTFont(cn_font_path)

    # Get existing glyphs in base font (to avoid overwriting)
    base_glyph_names = set(base_font.getGlyphOrder())

    # Get CJK glyphs and cmap entries from CN font
    cjk_glyphs = get_cjk_glyphs(cn_font, config)
    cjk_cmap = get_cjk_cmap_entries(cn_font, config)

    print(f"  Found {len(cjk_glyphs)} CJK glyphs in CN font")

    # Get font tables
    base_glyf = base_font["glyf"]
    cn_glyf = cn_font["glyf"]
    base_hmtx = base_font["hmtx"]
    cn_hmtx = cn_font["hmtx"]
    base_cmap = base_font["cmap"].getBestCmap()

    # Check unitsPerEm for scaling
    base_upm = base_font["head"].unitsPerEm
    cn_upm = cn_font["head"].unitsPerEm
    scale_factor = base_upm / cn_upm if base_upm != cn_upm else 1.0

    if scale_factor != 1.0:
        print(f"  Scaling CN glyphs by {scale_factor:.4f} (UPM: {cn_upm} -> {base_upm})")

    glyphs_added = []

    for glyph_name in cjk_glyphs:
        # Skip if glyph already exists in base font
        if glyph_name in base_glyph_names:
            continue

        # Skip if glyph doesn't exist in cn font's glyf table
        if glyph_name not in cn_glyf.glyphs:
            continue

        # Copy glyph outline
        glyph = cn_glyf.glyphs[glyph_name]
        base_glyf.glyphs[glyph_name] = glyph

        # Scale glyph if needed
        if scale_factor != 1.0 and hasattr(glyph, "coordinates") and glyph.numberOfContours > 0:
            glyph.coordinates.scale((scale_factor, scale_factor))
            glyph.recalcBounds(base_glyf)

        # Set advance width to cn_width (1200) for 2:1 ratio
        if glyph_name in cn_hmtx.metrics:
            _, lsb = cn_hmtx.metrics[glyph_name]
            # Scale LSB if needed
            if scale_factor != 1.0:
                lsb = int(round(lsb * scale_factor))
            base_hmtx.metrics[glyph_name] = (config.cn_width, lsb)
        else:
            base_hmtx.metrics[glyph_name] = (config.cn_width, 0)

        glyphs_added.append(glyph_name)

    print(f"  Added {len(glyphs_added)} new glyphs")

    if not glyphs_added:
        cn_font.close()
        return base_font

    # Update glyph order
    new_glyph_order = base_font.getGlyphOrder() + glyphs_added
    base_font.setGlyphOrder(new_glyph_order)
    base_font["maxp"].numGlyphs = len(new_glyph_order)

    # Update cmap with new glyphs
    for codepoint, glyph_name in cjk_cmap.items():
        if glyph_name in glyphs_added and codepoint not in base_cmap:
            base_cmap[codepoint] = glyph_name

    # Update hhea table
    if "hhea" in base_font:
        base_font["hhea"].advanceWidthMax = max(
            base_font["hhea"].advanceWidthMax, config.cn_width
        )
        base_font["hhea"].numberOfHMetrics = len(base_hmtx.metrics)

    cn_font.close()
    return base_font


def center_cjk_glyphs(font: TTFont, config: FontConfig) -> None:
    """Center CJK glyphs within their advance width.

    This ensures glyphs are visually centered in the 1200-unit space.

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cjk_glyphs = get_cjk_glyphs(font, config)

    for glyph_name in cjk_glyphs:
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        width, lsb = hmtx[glyph_name]
        if width != config.cn_width:
            continue

        # Calculate glyph bounds
        if not hasattr(glyph, "xMin") or glyph.xMin is None:
            glyph.recalcBounds(glyf)

        if glyph.xMin is None or glyph.xMax is None:
            continue

        glyph_width = glyph.xMax - glyph.xMin
        # Calculate centering offset
        ideal_lsb = (config.cn_width - glyph_width) // 2
        delta = ideal_lsb - glyph.xMin

        if abs(delta) > 1:  # Only adjust if significant
            glyph.coordinates.translate((delta, 0))
            glyph.recalcBounds(glyf)
            hmtx[glyph_name] = (config.cn_width, ideal_lsb)
