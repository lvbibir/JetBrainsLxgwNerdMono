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

# Build specific styles
uv run python build.py --styles Regular,Medium
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

Built fonts are saved to `output/`:

- `JetBrainsLxgwNerdMono-Regular.ttf`
- `JetBrainsLxgwNerdMono-Medium.ttf`
- `JetBrainsLxgwNerdMono-Italic.ttf`
- `JetBrainsLxgwNerdMono-MediumItalic.ttf`

## 2:1 Ratio Verification

To verify the perfect 2:1 width ratio between CJK and English characters, open `verify-2-1.html` in your browser after building the fonts.

![2:1 Ratio Verification](resources/2-1.png)

The vertical bars (`|`) should align perfectly across all lines, demonstrating that each CJK character occupies exactly twice the width of an English character.

## Command Line Options

```
usage: build.py [-h] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]
                [--cn-font CN_FONT]

options:
  --styles STYLES       Comma-separated styles (default: all)
  --fonts-dir FONTS_DIR Source fonts directory (default: fonts/)
  --output-dir OUTPUT_DIR
                        Output directory (default: output/)
  --parallel PARALLEL   Parallel workers (default: 1)
  --cn-font CN_FONT     Chinese font filename
```

## Project Structure

```
.
├── fonts/                  # Source fonts
├── output/                 # Built fonts
├── src/
│   ├── __init__.py
│   ├── config.py           # Font configuration
│   ├── merge.py            # Core merge logic
│   └── utils.py            # Utility functions
├── build.py                # Main build script
├── pyproject.toml          # Python project config
├── Dockerfile              # Docker build
└── README.md
```

## Acknowledgments

This project was inspired by and references the implementation approach from [maple-font](https://github.com/subframe7536/maple-font).

## License

This project is for personal use. Please check the licenses of the source fonts:

- JetBrains Mono: OFL-1.1
- LXGW WenKai: OFL-1.1
- Nerd Fonts: MIT
