# mdshrink

> Auto-compress PDFs and screenshots to Markdown before they hit Claude Code's context. 5-10x fewer tokens, fully local, one-line install.

[![PyPI Version](https://img.shields.io/pypi/v/mdshrink-mcp)](https://pypi.org/project/mdshrink-mcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/mdshrink-mcp)](https://pypi.org/project/mdshrink-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub Actions CI](https://github.com/Manish3451/mdshrink/actions/workflows/ci.yml/badge.svg)](https://github.com/Manish3451/mdshrink/actions)

## What is mdshrink?

mdshrink is an MCP server that automatically converts PDFs and screenshots to compact Markdown **before** they hit Claude Code's context window. It preserves semantic content while reducing token usage by 5-10x.

### Why?

When you attach a PDF or screenshot in Claude Code:
- A typical 20-page PDF consumes **25k-40k tokens**
- A single screenshot consumes **1.5k-3k tokens** per image

Most of those tokens are visual redundancy - fonts, layout, whitespace - that the model doesn't need. mdshrink extracts the semantic content and discards the bloat.

## Installation

```bash
pip install mdshrink-mcp
claude mcp add mdshrink -- mdshrink
```

Restart Claude Code. That's it.

## Usage

Once installed, Claude Code will automatically call mdshrink tools before reading PDF or image files:

- **`compress_pdf`** - Converts PDFs to compact Markdown
- **`compress_image`** - OCR extracts text from screenshots
- **`get_compressed`** - Cache lookup (fast check)

Each conversion reports:
- `original_tokens` - Estimated tokens for native file
- `compressed_tokens` - Actual tokens in Markdown  
- `ratio` - Compression ratio (e.g., "5.2x")

## What It Compresses Well

| Type | Compression | Notes |
|------|-------------|-------|
| Text-native PDFs | 5-10x | API specs, RFCs, papers, contracts |
| Screenshots of text | 3-5x | Code, error messages, docs, terminal |
| Scanned docs | Varies | Requires OCR (future) |

## What It Doesn't Compress

- Scanned/image-only PDFs (v1.1+)
- Tables with complex merged cells
- Equations and charts
- Photos where visual IS the content
- Diagrams (v1.2+ with VLM)

## Troubleshooting

### Tool not triggering?

```bash
/mcp
```

Should show:
```
✔ Found 1 MCP server
  • mdshrink: connected (3 tools)
```

If not, reinstall:
```bash
claude mcp remove mdshrink
claude mcp add mdshrink -- mdshrink
```

### Permission errors on Windows

Run PowerShell as Administrator, then:
```bash
pip install --force-reinstall mdshrink-mcp
```

### Cache location

- Linux/macOS: `~/.cache/mdshrink/`
- Windows: `%LOCALAPPDATA%\mdshrink\`

Disable caching: `MDSHRINK_NO_CACHE=1`

Clear cache:
```python
from mdshrink_mcp import cache
cache.clear_cache()
```

## Uninstall

```bash
claude mcp remove mdshrink
pip uninstall mdshrink-mcp
```

## License

MIT - See [LICENSE](LICENSE) for details.

## Credits

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF processing
- [RapidOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine
- [Anthropic](https://anthropic.com) - MCP specification