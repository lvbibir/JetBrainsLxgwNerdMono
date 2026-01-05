# JetBrainsLxgwNerdMono

[English](README.md) | [中文](README_zh.md)

JetBrains Mono NerdFont + LXGW WenKai Mono = 2:1 中英文等宽字体

## 特性

- 英文字符来自 JetBrains Mono NerdFont
- 中日韩 (CJK) 字符来自霞鹜文楷屏幕阅读版等宽 GB (Regular/Medium) 和霞鹜臻楷 GB (Bold)
- 保留 NerdFont 图标并缩放至与中文等宽
  - Powerline 符号 (U+E0A0-U+E0DF) 保持原始垂直边界, 确保终端中正确对齐
  - 普通图标缩放 1.4 倍并垂直居中
- 完美 2:1 宽度比例 (中文 1200, 英文 600 FUnit)
- 字重: Regular, Medium, Italic, MediumItalic, Bold, BoldItalic
- 支持 YAML 配置文件, 可通过命令行覆盖
- 支持多字重中文字体映射 (可选)

## 快速开始

### 使用 uv (推荐)

```bash
# 安装依赖
uv sync

# 构建所有字重
uv run python build.py

# 字体分包 (Web 字体)
# 默认读取 output/fonts 目录下的字体, 并输出到 output/split 目录
uv run python split.py
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
- `JetBrainsMonoNLNerdFontMono-Bold.ttf`
- `JetBrainsMonoNLNerdFontMono-BoldItalic.ttf`

### 霞鹜文楷屏幕阅读版等宽 GB (v1.521)

直接下载: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.521/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf` - 用于 Regular/Italic/Medium/MediumItalic 字重

### 霞鹜臻楷 GB (用于 Bold 字重)

直接下载: [LXGWZhenKaiGB-Regular.ttf](https://github.com/lxgw/LxgwZhenKai/releases)

- `LXGWZhenKaiGB-Regular.ttf` - 用于 Bold/BoldItalic 字重, 提供更粗的中文笔画

## 输出

- 生成的字体文件保存在 `output/fonts/` 目录。
- 分包后的 Web 字体保存在 `output/split/` 目录。

## 字体分包 (Web 字体)

项目包含一个 `split.py` 脚本, 使用 [cn-font-split](https://github.com/KonghaYao/cn-font-split) 将字体分割为 woff2 子集, 用于 Web 分发:

```bash
# 安装 cn-font-split (需要 Node.js)
npm install -g cn-font-split

# 运行分包脚本 (自动处理 output/fonts 下的所有字体)
uv run python split.py

# 自定义目录
uv run python split.py --input-dir my_fonts --output-dir my_split_fonts
```

输出结构:

```
output/split/
├── all.css                  # 合并所有字体的 CSS 引用
├── JetBrainsLxgwNerdMono-Regular/
│   ├── result.css           # 单个字体的 CSS
│   ├── index.html           # 测试页面 (包含分包验证报告)
│   └── *.woff2              # 字体子集
└── ...
```

分包完成后，您可以直接打开 `output/split/<FontName>/index.html` 查看该字体的分包验证报告和预览效果。

> **注意**: 由于浏览器跨域安全策略 (CORS)，直接双击打开 `index.html` 可能无法正常加载字体文件或 JSON 报告。请使用本地 HTTP 服务器查看:
>
> ```bash
> uv run python -m http.server 8000
> # 访问 http://localhost:8000/output/split/<FontName>/index.html
> ```

## 2:1 比例验证

验证中英文字符的完美 2:1 宽度比例:

```bash
# 启动本地 HTTP 服务器打开验证页面
uv run python -m http.server 8000
# 然后访问 http://localhost:8000/verify-2-1.html
```

验证页面现已支持通过下拉菜单切换不同的字重。

对于分包后的 Web 字体，请访问 `http://localhost:8000/verify-2-1-split.html` 进行验证。

或者构建字体后直接在浏览器中打开 `verify-2-1.html`。

![2:1 比例验证](resources/2-1.png)

竖线 (`|`) 应该在所有行之间完美对齐,展示每个中文字符的宽度恰好是英文字符的两倍。

## 命令行选项

### 构建脚本 (build.py)

```
用法: build.py [-h] [--config CONFIG] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]

选项:
  --config CONFIG         配置文件路径 (默认: config.yaml)
  --styles STYLES         逗号分隔的字重列表 (默认: 从配置文件读取)
  --fonts-dir FONTS_DIR   源字体目录 (默认: fonts/)
  --output-dir OUTPUT_DIR 输出目录 (默认: output/fonts/)
  --parallel PARALLEL     并行工作进程数 (默认: 1)
```

配置优先级: 命令行参数 > config.yaml > 默认值

## 配置文件

`config.yaml` 文件提供集中式的构建配置:

```yaml
# 字体元数据
font:
  family_name: "JetBrainsLxgwNerdMono"
  version: "1.1"
  author: "lvbibir"
  copyright: "Copyright (c) 2024 lvbibir"
  description: "JetBrains Mono NerdFont + LXGW WenKai Mono merged font with 2:1 CJK ratio."
  url: "https://github.com/lvbibir/JetBrainsLxgwNerdMono"
  license: "This font is licensed under the SIL Open Font License, Version 1.1."
  license_url: "https://openfontlicense.org"

# 源字体目录
fonts_dir: "fonts"

# 字重配置
# 每个字重需要指定:
#   en_font: 英文字体文件名 (位于 fonts_dir)
#   cn_font: 中文字体文件名 (位于 fonts_dir)
#   display_name: 字体元数据中显示的样式名称
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Regular"
  Italic:
    en_font: "JetBrainsMonoNLNerdFontMono-Italic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Italic"
  Medium:
    en_font: "JetBrainsMonoNLNerdFontMono-Medium.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Medium"
  MediumItalic:
    en_font: "JetBrainsMonoNLNerdFontMono-MediumItalic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Medium Italic"
  Bold:
    en_font: "JetBrainsMonoNLNerdFontMono-Bold.ttf"
    cn_font: "LXGWZhenKaiGB-Regular.ttf"  # 使用较粗的中文字体
    display_name: "Bold"
  BoldItalic:
    en_font: "JetBrainsMonoNLNerdFontMono-BoldItalic.ttf"
    cn_font: "LXGWZhenKaiGB-Regular.ttf"
    display_name: "Bold Italic"

# 构建选项
build:
  styles: "Regular,Medium,Italic,MediumItalic,Bold,BoldItalic"
  output_dir: "output/fonts"
  parallel: 6

# 字形宽度配置 (2:1 比例)
width:
  en_width: 600
  cn_width: 1200
```

### 多字重中文字体示例

如果中文字体有多个字重, 为每个样式指定不同的 `cn_font`:

```yaml
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Regular.ttf"
    display_name: "Regular"
  Medium:
    en_font: "JetBrainsMonoNLNerdFontMono-Medium.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Medium.ttf"
    display_name: "Medium"
  Bold:
    en_font: "JetBrainsMonoNLNerdFontMono-Bold.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Medium.ttf"  # 回退到 Medium
    display_name: "Bold"
```

### 分包脚本 (split.py)

```
用法: split.py [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]

选项:
  --input-dir INPUT_DIR   包含字体文件的输入目录 (默认: output/fonts)
  --output-dir OUTPUT_DIR 分包字体的输出目录 (默认: output/split)
```

## 项目结构

```
.
├── fonts/                  # 源字体
├── output/                 # 输出目录
│   ├── fonts/              # 生成的 TTF 字体
│   │   └── fonts-manifest.json  # 字体元数据(用于验证页面)
│   └── split/              # 生成的 Web 字体 (WOFF2)
├── src/
│   ├── __init__.py
│   ├── config.py           # 字体配置
│   ├── merge.py            # 核心合并逻辑
│   └── utils.py            # 工具函数
├── build.py                # 主构建脚本
├── split.py                # 字体分包脚本
├── config.yaml             # 构建配置
├── pyproject.toml          # Python 项目配置
├── Dockerfile              # Docker 构建
└── README.md
```

## 致谢

- [maple-font](https://github.com/subframe7536/maple-font): 本项目的实现方案参考来源
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts): 提供了丰富的开发者图标
- [霞鹜文楷](https://github.com/lxgw/LxgwWenKai): 优秀的开源中文字体
- [霞鹜臻楷](https://github.com/lxgw/LxgwZhenKai): 霞鹜文楷的粗体版本
- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono): 优秀的编程等宽字体
- [cn-font-split](https://github.com/KonghaYao/cn-font-split): 强大的 Web 字体分包工具

## 许可证

本项目仅供个人使用。请查看源字体的许可证:

- JetBrains Mono: OFL-1.1
- 霞鹜文楷: OFL-1.1
- 霞鹜臻楷: OFL-1.1
- Nerd Fonts: MIT
