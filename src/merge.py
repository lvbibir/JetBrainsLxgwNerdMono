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

    # Calculate scaling factors
    base_upm = base_font["head"].unitsPerEm
    cn_upm = cn_font["head"].unitsPerEm

    # Strategy:
    # LXGW WenKai Mono glyphs don't fill the entire em square
    # - UPM: 2048
    # - Actual glyph width: ~1724 (average of CJK characters)
    # - After UPM normalization to 1000: ~841
    #
    # We want final glyph width ~809 (like MapleMono, ~67% of 1200 advance)
    # So scale factor: 809 / 841 = 0.962
    #
    # But we need to be conservative to avoid overflow
    # Let's target ~800 width (2/3 of 1200 advance)

    upm_scale = base_upm / cn_upm  # 1000 / 2048 = 0.4883

    # After UPM scale, average LXGW glyph is: 1724 * 0.4883 = 841 units
    # Target: ~860 units (similar to MapleMono's ~809-918 range)
    # Visual scale: 860 / 841 = 1.023
    visual_scale = 1.02

    combined_scale = upm_scale * visual_scale

    print(f"  Scaling CN glyphs by {combined_scale:.4f} (UPM: {cn_upm} -> {base_upm}, visual: {visual_scale:.2f}x)")

    glyphs_added = []

    for glyph_name in cjk_glyphs:
        # Skip if glyph already exists in base font
        if glyph_name in base_glyph_names:
            continue

        # Skip if glyph doesn't exist in cn font's glyf table
        if glyph_name not in cn_glyf.glyphs:
            continue

        # Copy glyph outline (deep copy to avoid modifying source font)
        # IMPORTANT: Use cn_glyf[name] instead of cn_glyf.glyphs[name]
        # The latter returns undecompiled glyph without coordinates attribute
        import copy
        glyph = copy.deepcopy(cn_glyf[glyph_name])
        base_glyf.glyphs[glyph_name] = glyph

        # Scale glyph to fit target width
        if hasattr(glyph, "coordinates") and glyph.numberOfContours > 0:
            # Ensure bounds are calculated before scaling
            if not hasattr(glyph, 'xMin') or glyph.xMin is None:
                glyph.recalcBounds(base_glyf)

            # Apply combined scaling
            glyph.coordinates.scale((combined_scale, combined_scale))
            glyph.recalcBounds(base_glyf)

        # Set advance width to cn_width (1200) for 2:1 ratio
        # LSB will be recalculated in center_cjk_glyphs()
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


def scale_nerd_icons(font: TTFont, config: FontConfig) -> None:
    """Scale NerdFont icons to occupy 2x English character width (same as CJK).

    NerdFont icons are in Private Use Area:
    - U+E000-U+F8FF (BMP Private Use Area)
    - U+F0000-U+FFFFD (Supplementary Private Use Area-A)

    Powerline symbols (U+E0A0-U+E0DF) are handled specially:
    - They must maintain their original vertical bounds to align with text
    - Only horizontal width adjustment is applied, no scaling or vertical shift

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font["cmap"].getBestCmap()

    # NerdFont icon Unicode ranges
    nerd_ranges = [
        (0xE000, 0xF8FF),      # Private Use Area
        (0xF0000, 0xFFFFD),    # Supplementary Private Use Area-A
    ]

    # Powerline symbols range - these need special handling
    # They must span the full line height and not be scaled
    powerline_range = (0xE0A0, 0xE0DF)

    # Build mapping: codepoint -> glyph_name for nerd icons
    nerd_glyph_map = {}  # glyph_name -> codepoint
    for codepoint, glyph_name in cmap.items():
        for start, end in nerd_ranges:
            if start <= codepoint <= end:
                nerd_glyph_map[glyph_name] = codepoint
                break

    if not nerd_glyph_map:
        return

    print(f"  Processing {len(nerd_glyph_map)} NerdFont icons...")

    # Target: scale icons to ~70% of 1200 = 840 units (similar to CJK fill ratio)
    # Original icon width is ~600, so scale factor = 840 / 600 = 1.4
    scale_factor = 1.4

    powerline_count = 0
    scaled_count = 0

    for glyph_name, codepoint in nerd_glyph_map.items():
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        # Get current metrics
        width, lsb = hmtx[glyph_name]
        if width != config.en_width:
            continue  # Skip if not standard English width

        # Check if this is a Powerline symbol
        is_powerline = powerline_range[0] <= codepoint <= powerline_range[1]

        if is_powerline:
            # Powerline symbols: only adjust width, no scaling or vertical shift
            # These symbols need to maintain their original vertical bounds
            if hasattr(glyph, "coordinates"):
                if not hasattr(glyph, 'xMin') or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Only center horizontally, keep vertical position
                if hasattr(glyph, 'xMin') and glyph.xMin is not None:
                    glyph_width = glyph.xMax - glyph.xMin
                    ideal_lsb = (config.cn_width - glyph_width) // 2
                    delta_x = ideal_lsb - glyph.xMin

                    if abs(delta_x) > 1:
                        glyph.coordinates.translate((delta_x, 0))
                        glyph.recalcBounds(glyf)

                    hmtx[glyph_name] = (config.cn_width, ideal_lsb)
                else:
                    hmtx[glyph_name] = (config.cn_width, 0)

            powerline_count += 1
        else:
            # Regular icons: scale and center both horizontally and vertically
            if hasattr(glyph, "coordinates"):
                # Ensure bounds are calculated
                if not hasattr(glyph, 'xMin') or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Scale to 2x size
                glyph.coordinates.scale((scale_factor, scale_factor))
                glyph.recalcBounds(glyf)

            # Update advance width to CJK width (1200)
            # Center the glyph horizontally and vertically
            if hasattr(glyph, 'xMin') and glyph.xMin is not None:
                glyph_width = glyph.xMax - glyph.xMin
                ideal_lsb = (config.cn_width - glyph_width) // 2
                delta_x = ideal_lsb - glyph.xMin

                # Vertical centering: align icon center with CJK center (~360)
                glyph_center_y = (glyph.yMin + glyph.yMax) / 2
                target_center_y = 360  # Similar to CJK vertical center
                delta_y = target_center_y - glyph_center_y

                if abs(delta_x) > 1 or abs(delta_y) > 1:
                    glyph.coordinates.translate((delta_x, delta_y))
                    glyph.recalcBounds(glyf)

                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            else:
                hmtx[glyph_name] = (config.cn_width, 0)

            scaled_count += 1

    print(f"    Powerline symbols (no scaling): {powerline_count}")
    print(f"    Regular icons (scaled 1.4x): {scaled_count}")


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
