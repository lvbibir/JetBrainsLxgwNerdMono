import argparse
import sys
import json
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import FontConfig

logger = logging.getLogger(__name__)


def check_cn_font_split_installed() -> bool:
    """Check if cn-font-split is installed."""
    return shutil.which("cn-font-split") is not None


def split_font(
    font_path: Path,
    output_base_dir: Path,
    config: FontConfig,
    test_html: bool = True,
) -> Path:
    """Split a single font file using cn-font-split.

    Args:
        font_path: Path to the font file
        output_base_dir: Base directory for output (e.g., output/split)
        config: FontConfig object
        test_html: Whether to generate a test HTML file

    Returns:
        Path to the output directory for this font
    """
    if not check_cn_font_split_installed():
        raise RuntimeError(
            "cn-font-split is not installed. Please run 'npm install -g cn-font-split' first."
        )

    font_name = font_path.stem
    output_dir = output_base_dir / font_name

    # Determine font weight and style for CSS
    style_key = None
    # Sort keys by length descending to ensure "MediumItalic" is matched before "Medium"
    sorted_keys = sorted(config.weight_mapping.keys(), key=len, reverse=True)

    for key in sorted_keys:
        if key in font_name:
            style_key = key
            break

    # Default values
    font_weight = "400"
    font_style = "normal"

    if style_key:
        if "Medium" in style_key:
            font_weight = "500"
        if "Italic" in style_key:
            font_style = "italic"

    logger.info(f"Splitting font: {font_path}")
    logger.info(f"Output directory: {output_dir}")

    cmd = [
        "cn-font-split",
        "run",
        "-i", str(font_path),
        "-o", str(output_dir),
        "--css.fontFamily", config.family_name,
        "--css.fontWeight", font_weight,
        "--css.fontStyle", font_style,
        "--css.fontDisplay", "swap",
        "--renameOutputFont", "[index].[ext]",
        "--testHtml", str(test_html).lower(),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully split {font_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to split {font_name}: {e.stderr}")
        raise

    return output_dir


def generate_merged_css(split_dirs: List[Path], output_file: Path) -> None:
    """Generate a merged CSS file that imports all font subsets.

    This function reads the result.css from each split directory and creates a new
    CSS file that imports them.
    """
    logger.info(f"Generating merged CSS: {output_file}")

    import_statements = []

    for split_dir in split_dirs:
        css_file = split_dir / "result.css"
        if not css_file.exists():
            logger.warning(f"CSS file not found: {css_file}")
            continue

        font_name = split_dir.name
        # Use relative path for import
        import_path = f"./{font_name}/result.css"
        import_statements.append(f'@import "{import_path}";')

    output_file.write_text("\n".join(import_statements), encoding="utf-8")
    logger.info("Merged CSS generated successfully")


def split_all_fonts(
    input_dir: Path,
    output_dir: Path,
    config: FontConfig,
) -> None:
    """Split all fonts in the input directory.

    Args:
        input_dir: Directory containing font files (e.g., output/)
        output_dir: Base directory for split output (e.g., output/split/)
        config: FontConfig object
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    font_files = list(input_dir.glob("*.ttf"))
    if not font_files:
        logger.warning(f"No .ttf files found in {input_dir}")
        return

    split_dirs = []
    for font_file in font_files:
        try:
            split_dir = split_font(font_file, output_dir, config)
            split_dirs.append(split_dir)
        except Exception as e:
            logger.error(f"Error processing {font_file}: {e}")

    # Generate merged CSS
    if split_dirs:
        generate_merged_css(split_dirs, output_dir / "all.css")


def main():
    parser = argparse.ArgumentParser(
        description="Split fonts for web use using cn-font-split",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("output/fonts"),
        help="Input directory containing built fonts (default: output/fonts/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/split"),
        help="Output directory for split fonts (default: output/split/)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Initialize config
    config = FontConfig()

    print("\nSplitting fonts for web use...")
    try:
        split_all_fonts(args.input_dir, args.output_dir, config)
        print(f"Fonts split successfully! Output: {args.output_dir}")
    except Exception as e:
        print(f"Error splitting fonts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
