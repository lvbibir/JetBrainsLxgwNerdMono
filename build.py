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
    uv run python build.py --config config.yaml
    uv run python build.py --styles Regular,Medium
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict

import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import FontConfig
from src.merge import merge_fonts, center_cjk_glyphs, scale_nerd_icons
from src.utils import update_font_names, verify_glyph_width


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config.yaml

    Returns:
        Configuration dictionary
    """
    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_config_value(yaml_config: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Get nested value from config dictionary.

    Args:
        yaml_config: Configuration dictionary
        keys: Nested keys to access
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    value = yaml_config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value


def build_single_font(
    style: str,
    en_font_path: Path,
    cn_font_path: Path,
    display_name: str,
    output_dir: Path,
    config: FontConfig,
    metadata: dict,
) -> str:
    """Build a single font variant.

    Args:
        style: Font style (Regular, Medium, Italic, MediumItalic)
        en_font_path: Path to English font (e.g., JetBrains Mono NerdFont)
        cn_font_path: Path to Chinese font (e.g., LXGW WenKai Mono)
        display_name: Display name for the style in font metadata
        output_dir: Output directory
        config: FontConfig object
        metadata: Font metadata dict (author, copyright, description, url, license, license_url)

    Returns:
        Output file path
    """
    print(f"\nBuilding {config.family_name_compact}-{style}...")

    # Merge fonts
    merged_font = merge_fonts(
        base_font_path=str(en_font_path),
        cn_font_path=str(cn_font_path),
        config=config,
    )

    # Scale NerdFont icons to CJK width
    print("  Scaling NerdFont icons...")
    scale_nerd_icons(merged_font, config)

    # Center CJK glyphs
    print("  Centering CJK glyphs...")
    center_cjk_glyphs(merged_font, config)

    # Update font names
    postscript_name = f"{config.family_name_compact}-{style}"

    print("  Updating font metadata...")
    update_font_names(
        font=merged_font,
        family_name=config.family_name,
        style_name=display_name,
        full_name=f"{config.family_name} {display_name}",
        postscript_name=postscript_name,
        version_str=f"Version {config.version}",
        author=metadata.get("author", ""),
        copyright_str=metadata.get("copyright", ""),
        description=metadata.get("description", ""),
        url=metadata.get("url", ""),
        license_desc=metadata.get("license", ""),
        license_url=metadata.get("license_url", ""),
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
    # Default config path
    default_config_path = Path(__file__).parent / "config.yaml"

    parser = argparse.ArgumentParser(
        description="Build JetBrainsLxgwNerdMono font",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python build.py
  uv run python build.py --config config.yaml
  uv run python build.py --styles Regular,Medium

Configuration priority: CLI args > config.yaml > defaults
        """,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path,
        help=f"Path to config.yaml (default: {default_config_path})",
    )
    parser.add_argument(
        "--styles",
        type=str,
        default=None,
        help="Comma-separated styles to build (default: from config or all)",
    )
    parser.add_argument(
        "--fonts-dir",
        type=Path,
        default=None,
        help="Directory containing source fonts (default: from config or fonts/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: from config or output/fonts/)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=None,
        help="Number of parallel workers (default: from config or 1)",
    )

    args = parser.parse_args()

    # Load YAML config
    yaml_config = load_config(args.config)

    # Get styles configuration from YAML
    styles_config = get_config_value(yaml_config, "styles") or {}
    if not styles_config:
        print("Error: No styles defined in config.yaml")
        sys.exit(1)

    # Merge config: CLI args > YAML > defaults
    styles_str = (
        args.styles
        or get_config_value(yaml_config, "build", "styles")
        or ",".join(styles_config.keys())
    )
    fonts_dir = (
        args.fonts_dir
        or Path(get_config_value(yaml_config, "fonts_dir") or "fonts")
    )
    output_dir = (
        args.output_dir
        or Path(get_config_value(yaml_config, "build", "output_dir") or "output/fonts")
    )
    parallel = (
        args.parallel
        if args.parallel is not None
        else get_config_value(yaml_config, "build", "parallel", default=1)
    )

    # Font metadata from config
    family_name = get_config_value(yaml_config, "font", "family_name") or "JetBrainsLxgwNerdMono"
    version = get_config_value(yaml_config, "font", "version") or "1.0"
    en_width = get_config_value(yaml_config, "width", "en_width", default=600)
    cn_width = get_config_value(yaml_config, "width", "cn_width", default=1200)

    # Font metadata for name table
    metadata = {
        "author": get_config_value(yaml_config, "font", "author") or "",
        "copyright": get_config_value(yaml_config, "font", "copyright") or "",
        "description": get_config_value(yaml_config, "font", "description") or "",
        "url": get_config_value(yaml_config, "font", "url") or "",
        "license": get_config_value(yaml_config, "font", "license") or "",
        "license_url": get_config_value(yaml_config, "font", "license_url") or "",
    }

    # Initialize FontConfig
    config = FontConfig(
        family_name=family_name,
        family_name_compact=family_name,
        version=version,
        en_width=en_width,
        cn_width=cn_width,
    )

    # Parse styles to build
    styles = [s.strip() for s in styles_str.split(",")]
    valid_styles = list(styles_config.keys())

    for style in styles:
        if style not in valid_styles:
            print(f"Error: Invalid style '{style}'. Valid styles: {valid_styles}")
            sys.exit(1)

    # Build font paths and validate
    font_paths: Dict[str, Dict[str, Any]] = {}
    for style in styles:
        style_cfg = styles_config[style]
        en_font = style_cfg.get("en_font")
        cn_font = style_cfg.get("cn_font")
        display_name = style_cfg.get("display_name", style)

        if not en_font or not cn_font:
            print(f"Error: Style '{style}' must have both 'en_font' and 'cn_font' defined")
            sys.exit(1)

        en_font_path = fonts_dir / en_font
        cn_font_path = fonts_dir / cn_font

        if not en_font_path.exists():
            print(f"Error: English font not found: {en_font_path}")
            sys.exit(1)
        if not cn_font_path.exists():
            print(f"Error: Chinese font not found: {cn_font_path}")
            sys.exit(1)

        font_paths[style] = {
            "en_font_path": en_font_path,
            "cn_font_path": cn_font_path,
            "display_name": display_name,
        }

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building {config.family_name} v{config.version}")
    print(f"Styles: {', '.join(styles)}")
    print(f"Source: {fonts_dir}")
    print(f"Output: {output_dir}")
    print(f"Width ratio: {config.cn_width}:{config.en_width} (2:1)")
    print("Font mapping:")
    for style in styles:
        paths = font_paths[style]
        print(f"  {style}:")
        print(f"    EN: {paths['en_font_path'].name}")
        print(f"    CN: {paths['cn_font_path'].name}")

    # Build fonts
    if parallel <= 1:
        # Sequential build
        for style in styles:
            paths = font_paths[style]
            build_single_font(
                style,
                paths["en_font_path"],
                paths["cn_font_path"],
                paths["display_name"],
                output_dir,
                config,
                metadata,
            )
    else:
        # Parallel build
        with ProcessPoolExecutor(max_workers=parallel) as executor:
            futures = {}
            for style in styles:
                paths = font_paths[style]
                future = executor.submit(
                    build_single_font,
                    style,
                    paths["en_font_path"],
                    paths["cn_font_path"],
                    paths["display_name"],
                    output_dir,
                    config,
                    metadata,
                )
                futures[future] = style

            for future in as_completed(futures):
                style = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error building {style}: {e}")
                    raise

    # Generate font manifest for HTML verification pages
    manifest = {
        "family_name": config.family_name,
        "version": config.version,
        "fonts": []
    }
    for style in styles:
        display_name = font_paths[style]["display_name"]
        manifest["fonts"].append({
            "style": style,
            "display_name": display_name,
            "filename": f"{config.family_name_compact}-{style}.ttf"
        })

    manifest_path = output_dir / "fonts-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Generated manifest: {manifest_path}")

    print(f"\nBuild complete! Fonts saved to: {output_dir}")


if __name__ == "__main__":
    main()
