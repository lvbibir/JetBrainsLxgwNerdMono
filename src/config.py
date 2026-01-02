"""Font configuration for JetBrainsLxgwNerdMono."""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class FontConfig:
    """Configuration for font building."""

    # Font naming
    family_name: str = "JetBrainsLxgwNerdMono"
    family_name_compact: str = "JetBrainsLxgwNerdMono"
    version: str = "1.0"

    # Glyph width configuration (2:1 ratio)
    en_width: int = 600  # English character width
    cn_width: int = 1200  # CJK character width (2x)

    # CJK Unicode ranges
    cjk_ranges: Tuple[Tuple[int, int], ...] = (
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
        (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
        (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
        (0x30000, 0x3134F),  # CJK Unified Ideographs Extension G
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
        (0x2E80, 0x2EFF),  # CJK Radicals Supplement
        (0x2F00, 0x2FDF),  # Kangxi Radicals
        (0x3100, 0x312F),  # Bopomofo
        (0x31A0, 0x31BF),  # Bopomofo Extended
        (0x31C0, 0x31EF),  # CJK Strokes
        (0x3200, 0x32FF),  # Enclosed CJK Letters and Months
        (0x3300, 0x33FF),  # CJK Compatibility
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
    )

    # Weight mapping: style -> (source_file, display_name)
    weight_mapping: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.weight_mapping:
            self.weight_mapping = {
                "Regular": ("JetBrainsMonoNLNerdFontMono-Regular.ttf", "Regular"),
                "Medium": ("JetBrainsMonoNLNerdFontMono-Medium.ttf", "Medium"),
                "Italic": ("JetBrainsMonoNLNerdFontMono-Italic.ttf", "Italic"),
                "MediumItalic": (
                    "JetBrainsMonoNLNerdFontMono-MediumItalic.ttf",
                    "Medium Italic",
                ),
            }
