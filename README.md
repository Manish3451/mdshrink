# TokenSaver MCP

A Claude Code MCP server that auto-converts PDFs and screenshots to compact Markdown before they hit the model, cutting token usage 5-10x without losing semantic content.

## Features

- **PDF to Markdown** - Converts text-native PDFs to clean Markdown with heading detection
- **Image OCR** - Extracts text from screenshots using RapidOCR
- **Content-addressed cache** - Converts same file only once
- **Token reporting** - Shows original vs compressed token counts

## Installation

```bash
pip install tokensaver-mcp
```

## Claude Code Setup

```bash
claude mcp add tokensaver -- tokensaver-mcp
```

Then restart Claude Code.

## Usage

Once installed, Claude Code will automatically call the compression tools before reading PDF or image files. The tools exposed are:

- `compress_pdf` - Converts PDF to Markdown
- `compress_image` - Extracts text from images via OCR
- `get_compressed` - Cache lookup

## Token Savings

Each conversion reports:
- `original_tokens` - Estimated tokens for native file
- `compressed_tokens` - Actual tokens in Markdown
- `ratio` - Compression ratio (e.g., "5.2x")

## Cache

Cached files are stored in:
- Linux/macOS: `~/.cache/tokensaver/`
- Windows: `%LOCALAPPDATA%\tokensaver\`

To disable caching: `TOKENSAVER_NO_CACHE=1`

To clear cache:
```python
from tokensaver_mcp import cache
cache.clear_cache()
```

## Requirements

- Python 3.10+
- PyMuPDF (AGPL)
- RapidOCR
- tiktoken

## License

AGPL-3.0 - See LICENSE file for details.

**Note:** PyMuPDF is AGPL-licensed. If you need MIT compatibility, consider `pdfminer.six` as an alternative backend.

## Troubleshooting

### Tool not triggering?

Make sure Claude Code has loaded the MCP server:
```bash
/mcp
```

### Wrong compression ratio?

Token counts are estimates using `cl100k_base` tokenizer. Ratios are meaningful; absolute numbers are approximate.

## Uninstall

```bash
claude mcp remove tokensaver
pip uninstall tokensaver-mcp
```