#!/usr/bin/env python3
"""
JetBrainsLxgwNerdMono Font Builder

Build merged font with:
- English characters from JetBrains Mono NerdFont
- CJK characters from LXGW WenKai Mono
- NerdFont icons preserved
- 2:1 width ratio (CJK 1200, English 600)

Usage:
    uv run python build.py
    uv run python build.py --styles Regular,Medium
    uv run python build.py --fonts-dir ./fonts --output-dir ./output
"""

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import FontConfig
from src.merge import merge_fonts, center_cjk_glyphs
from src.utils import update_font_names, verify_glyph_width


def build_single_font(
    style: str,
    jb_font_path: Path,
    cn_font_path: Path,
    output_dir: Path,
    config: FontConfig,
) -> str:
    """Build a single font variant.

    Args:
        style: Font style (Regular, Medium, Italic, MediumItalic)
        jb_font_path: Path to JetBrains Mono NerdFont
        cn_font_path: Path to LXGW WenKai Mono
        output_dir: Output directory
        config: FontConfig object

    Returns:
        Output file path
    """
    print(f"\nBuilding {config.family_name_compact}-{style}...")

    # Merge fonts
    merged_font = merge_fonts(
        base_font_path=str(jb_font_path),
        cn_font_path=str(cn_font_path),
        config=config,
    )

    # Center CJK glyphs
    print("  Centering CJK glyphs...")
    center_cjk_glyphs(merged_font, config)

    # Update font names
    style_display = config.weight_mapping[style][1]
    postscript_name = f"{config.family_name_compact}-{style}"

    print("  Updating font metadata...")
    update_font_names(
        font=merged_font,
        family_name=config.family_name,
        style_name=style_display,
        full_name=f"{config.family_name} {style_display}",
        postscript_name=postscript_name,
        version_str=f"Version {config.version}",
    )

    # Verify glyph widths
    print("  Verifying glyph widths...")
    try:
        verify_glyph_width(
            font=merged_font,
            expected_widths=[0, config.en_width, config.cn_width],
            file_name=postscript_name,
        )
    except ValueError as e:
        print(f"  Warning: {e}")

    # Save font
    output_path = output_dir / f"{postscript_name}.ttf"
    merged_font.save(str(output_path))
    merged_font.close()

    print(f"  Saved: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Build JetBrainsLxgwNerdMono font",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python build.py
  uv run python build.py --styles Regular,Medium
  uv run python build.py --fonts-dir ./fonts --output-dir ./output
        """,
    )
    parser.add_argument(
        "--styles",
        type=str,
        default="Regular,Medium,Italic,MediumItalic",
        help="Comma-separated styles to build (default: all)",
    )
    parser.add_argument(
        "--fonts-dir",
        type=Path,
        default=Path("fonts"),
        help="Directory containing source fonts (default: fonts/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers (default: 1)",
    )
    parser.add_argument(
        "--cn-font",
        type=str,
        default="LXGWWenKaiMonoGBScreen.ttf",
        help="Chinese font filename (default: LXGWWenKaiMonoGBScreen.ttf)",
    )

    args = parser.parse_args()

    # Initialize config
    config = FontConfig()

    # Parse styles
    styles = [s.strip() for s in args.styles.split(",")]
    valid_styles = list(config.weight_mapping.keys())

    for style in styles:
        if style not in valid_styles:
            print(f"Error: Invalid style '{style}'. Valid styles: {valid_styles}")
            sys.exit(1)

    # Check source fonts exist
    cn_font_path = args.fonts_dir / args.cn_font
    if not cn_font_path.exists():
        print(f"Error: CN font not found: {cn_font_path}")
        sys.exit(1)

    for style in styles:
        jb_font_file = config.weight_mapping[style][0]
        jb_font_path = args.fonts_dir / jb_font_file
        if not jb_font_path.exists():
            print(f"Error: JetBrains font not found: {jb_font_path}")
            sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building {config.family_name} v{config.version}")
    print(f"Styles: {', '.join(styles)}")
    print(f"Source: {args.fonts_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Width ratio: {config.cn_width}:{config.en_width} (2:1)")

    # Build fonts
    if args.parallel <= 1:
        # Sequential build
        for style in styles:
            jb_font_path = args.fonts_dir / config.weight_mapping[style][0]
            build_single_font(style, jb_font_path, cn_font_path, args.output_dir, config)
    else:
        # Parallel build
        with ProcessPoolExecutor(max_workers=args.parallel) as executor:
            futures = {}
            for style in styles:
                jb_font_path = args.fonts_dir / config.weight_mapping[style][0]
                future = executor.submit(
                    build_single_font,
                    style,
                    jb_font_path,
                    cn_font_path,
                    args.output_dir,
                    config,
                )
                futures[future] = style

            for future in as_completed(futures):
                style = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error building {style}: {e}")
                    raise

    print(f"\nBuild complete! Fonts saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
