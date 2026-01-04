# JetBrainsLxgwNerdMono

[English](README.md) | [中文](README_zh.md)

JetBrains Mono NerdFont + LXGW WenKai Mono = 2:1 CJK Monospace Font

## Features

- English characters from JetBrains Mono NerdFont
- CJK characters from LXGW WenKai Mono (GB Screen version)
- NerdFont icons preserved
- Perfect 2:1 width ratio (CJK 1200, English 600 FUnit)
- Styles: Regular, Medium, Italic, MediumItalic

## Quick Start

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Build all styles
uv run python build.py

# Font Splitting (Web Fonts)
# Default input: output/fonts, output: output/split
uv run python split.py
```

### Using Docker

```bash
# Build image
docker build -t jetbrains-lxgw-nerd-mono .

# Run build
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    jetbrains-lxgw-nerd-mono

# Build specific styles
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    jetbrains-lxgw-nerd-mono --styles Regular,Medium
```

## Source Fonts

Place the following fonts in the `fonts/` directory:

### JetBrains Mono NerdFont (v3.4.0)

Download from [Nerd Fonts release](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.zip), extract and place these files:

- `JetBrainsMonoNLNerdFontMono-Regular.ttf`
- `JetBrainsMonoNLNerdFontMono-Medium.ttf`
- `JetBrainsMonoNLNerdFontMono-Italic.ttf`
- `JetBrainsMonoNLNerdFontMono-MediumItalic.ttf`

### LXGW WenKai Mono GB Screen (v1.521)

Download directly: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.521/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf`

## Output

- Generated fonts are saved to `output/fonts/`.
- Split web fonts are saved to `output/split/`.

## Font Splitting (Web Fonts)

The project includes a `split.py` script that uses [cn-font-split](https://github.com/KonghaYao/cn-font-split) to split fonts into woff2 subsets for web delivery:

```bash
# Install cn-font-split (requires Node.js)
npm install -g cn-font-split

# Run split script (processes all fonts in output/fonts)
uv run python split.py

# Custom directories
uv run python split.py --input-dir my_fonts --output-dir my_split_fonts
```

Output structure:

```
output/split/
├── all.css                  # Merged CSS importing all fonts
├── JetBrainsLxgwNerdMono-Regular/
│   ├── result.css           # Single font CSS
│   ├── index.html           # Test page (contains splitting report)
│   └── *.woff2              # Font subsets
└── ...
```

After splitting, you can open `output/split/<FontName>/index.html` to view the splitting report and preview the font.

> **Note**: Due to browser CORS policies, directly opening `index.html` may fail to load font files or JSON reports. Please use a local HTTP server:
>
> ```bash
> uv run python -m http.server 8000
> # Visit http://localhost:8000/output/split/<FontName>/index.html
> ```

## 2:1 Ratio Verification

To verify the perfect 2:1 width ratio between CJK and English characters:

```bash
# Open verification page in browser
uv run python -m http.server 8000
# Then visit http://localhost:8000/verify-2-1.html
```

For split web fonts, please visit `http://localhost:8000/verify-2-1-split.html`.

Or simply open `verify-2-1.html` directly in your browser after building the fonts.

![2:1 Ratio Verification](resources/2-1.png)

The vertical bars (`|`) should align perfectly across all lines, demonstrating that each CJK character occupies exactly twice the width of an English character.

## Command Line Options

### Build Script (build.py)

```
usage: build.py [-h] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]
                [--cn-font CN_FONT]

options:
  --styles STYLES         Comma-separated styles (default: all)
  --fonts-dir FONTS_DIR   Source fonts directory (default: fonts/)
  --output-dir OUTPUT_DIR Output directory (default: output/fonts/)
  --parallel PARALLEL     Parallel workers (default: 1)
  --cn-font CN_FONT       Chinese font filename
```

### Split Script (split.py)

```
usage: split.py [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]

options:
  --input-dir INPUT_DIR   Input directory containing font files (default: output/fonts)
  --output-dir OUTPUT_DIR Output directory for split fonts (default: output/split)
```

## Project Structure

```
.
├── fonts/                  # Source fonts
├── output/                 # Output directory
│   ├── fonts/              # Generated TTF fonts
│   └── split/              # Generated Web fonts (WOFF2)
├── src/
│   ├── __init__.py
│   ├── config.py           # Font configuration
│   ├── merge.py            # Core merge logic
│   └── utils.py            # Utility functions
├── build.py                # Main build script
├── split.py                # Font splitting script
├── pyproject.toml          # Python project config
├── Dockerfile              # Docker build
└── README.md
```

## Acknowledgments

- [maple-font](https://github.com/subframe7536/maple-font): Implementation reference and inspiration
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts): Developer icons
- [LXGW WenKai](https://github.com/lxgw/LxgwWenKai): Source CJK font
- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono): Source English font
- [cn-font-split](https://github.com/KonghaYao/cn-font-split): Web font splitting tool

## License

This project is for personal use. Please check the licenses of the source fonts:

- JetBrains Mono: OFL-1.1
- LXGW WenKai: OFL-1.1
- Nerd Fonts: MIT
