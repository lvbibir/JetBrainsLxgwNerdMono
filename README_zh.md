# JetBrainsLxgwNerdMono

[English](README.md) | [中文](README_zh.md)

JetBrains Mono NerdFont + LXGW WenKai Mono = 2:1 中英文等宽字体

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

### LXGW 文楷等宽 GB Screen (v1.521)

直接下载: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.521/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf`

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
│   ├── index.html           # 测试页面
│   └── *.woff2              # 字体子集
└── ...
```

## 2:1 比例验证

验证中英文字符的完美 2:1 宽度比例:

```bash
# 启动本地 HTTP 服务器打开验证页面
uv run python -m http.server 8000
# 然后访问 http://localhost:8000/verify-2-1.html
```

或者构建字体后直接在浏览器中打开 `verify-2-1.html`。

![2:1 比例验证](resources/2-1.png)

竖线 (`|`) 应该在所有行之间完美对齐,展示每个中文字符的宽度恰好是英文字符的两倍。

## 命令行选项

### 构建脚本 (build.py)

```
用法: build.py [-h] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]
                [--cn-font CN_FONT]

选项:
  --styles STYLES         逗号分隔的字重列表 (默认: 全部)
  --fonts-dir FONTS_DIR   源字体目录 (默认: fonts/)
  --output-dir OUTPUT_DIR 输出目录 (默认: output/fonts/)
  --parallel PARALLEL     并行工作进程数 (默认: 1)
  --cn-font CN_FONT       中文字体文件名
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
│   └── split/              # 生成的 Web 字体 (WOFF2)
├── src/
│   ├── __init__.py
│   ├── config.py           # 字体配置
│   ├── merge.py            # 核心合并逻辑
│   └── utils.py            # 工具函数
├── build.py                # 主构建脚本
├── split.py                # 字体分包脚本
├── pyproject.toml          # Python 项目配置
├── Dockerfile              # Docker 构建
└── README.md
```

## 致谢

- [maple-font](https://github.com/subframe7536/maple-font): 本项目的实现方案参考来源
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts): 提供了丰富的开发者图标
- [LXGW WenKai](https://github.com/lxgw/LxgwWenKai): 优秀的开源中文字体
- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono): 优秀的编程等宽字体
- [cn-font-split](https://github.com/KonghaYao/cn-font-split): 强大的 Web 字体分包工具

## 许可证

本项目仅供个人使用。请查看源字体的许可证:

- JetBrains Mono: OFL-1.1
- LXGW WenKai: OFL-1.1
- Nerd Fonts: MIT
