# JetBrainsLxgwNerdMono

[English](README.md) | [中文](README_zh.md)

JetBrains Mono NerdFont + LXGW 文楷等宽 = 2:1 中英文等宽字体

## 特性

- 英文字符来自 JetBrains Mono NerdFont
- 中日韩 (CJK) 字符来自 LXGW 文楷等宽 (GB Screen 版本)
- 保留 NerdFont 图标
- 完美 2:1 宽度比例 (中文 1200, 英文 600 FUnit)
- 字重: Regular, Medium, Italic, MediumItalic

## 快速开始

### 使用 uv (推荐)

```bash
# 安装依赖
uv sync

# 构建所有字重
uv run python build.py

# 构建指定字重
uv run python build.py --styles Regular,Medium
```

### 使用 Docker

```bash
# 构建镜像
docker build -t jetbrains-lxgw-nerd-mono .

# 运行构建
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    jetbrains-lxgw-nerd-mono

# 构建指定字重
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    jetbrains-lxgw-nerd-mono --styles Regular,Medium
```

## 源字体

请将以下字体文件放置在 `fonts/` 目录:

### JetBrains Mono NerdFont (v3.4.0)

从 [Nerd Fonts 发布页面](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.zip) 下载,解压后放置以下文件:

- `JetBrainsMonoNLNerdFontMono-Regular.ttf`
- `JetBrainsMonoNLNerdFontMono-Medium.ttf`
- `JetBrainsMonoNLNerdFontMono-Italic.ttf`
- `JetBrainsMonoNLNerdFontMono-MediumItalic.ttf`

### LXGW 文楷等宽 GB Screen (v1.521)

直接下载: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.521/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf`

## 输出

生成的字体文件保存在 `output/` 目录:

- `JetBrainsLxgwNerdMono-Regular.ttf`
- `JetBrainsLxgwNerdMono-Medium.ttf`
- `JetBrainsLxgwNerdMono-Italic.ttf`
- `JetBrainsLxgwNerdMono-MediumItalic.ttf`

## 2:1 比例验证

构建字体后,在浏览器中打开 `verify-2-1.html` 即可验证中英文字符的完美 2:1 宽度比例。

![2:1 比例验证](resources/2-1.png)

竖线 (`|`) 应该在所有行之间完美对齐,展示每个中文字符的宽度恰好是英文字符的两倍。

## 命令行选项

```
用法: build.py [-h] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]
                [--cn-font CN_FONT]

选项:
  --styles STYLES       逗号分隔的字重列表 (默认: 全部)
  --fonts-dir FONTS_DIR 源字体目录 (默认: fonts/)
  --output-dir OUTPUT_DIR
                        输出目录 (默认: output/)
  --parallel PARALLEL   并行工作进程数 (默认: 1)
  --cn-font CN_FONT     中文字体文件名
```

## 项目结构

```
.
├── fonts/                  # 源字体
├── output/                 # 生成的字体
├── src/
│   ├── __init__.py
│   ├── config.py           # 字体配置
│   ├── merge.py            # 核心合并逻辑
│   └── utils.py            # 工具函数
├── build.py                # 主构建脚本
├── pyproject.toml          # Python 项目配置
├── Dockerfile              # Docker 构建
└── README.md
```

## 致谢

本项目的实现方案参考了 [maple-font](https://github.com/subframe7536/maple-font) 项目。

## 许可证

本项目仅供个人使用。请查看源字体的许可证:

- JetBrains Mono: OFL-1.1
- LXGW WenKai: OFL-1.1
- Nerd Fonts: MIT
