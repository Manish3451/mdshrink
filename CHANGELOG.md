# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-25

### Added
- Initial release of mdshrink-mcp
- PDF to Markdown conversion via PyMuPDF
- Image OCR via RapidOCR
- Content-addressed caching with LRU eviction (500MB limit)
- Token reporting (original vs compressed tokens)
- MCP server with 3 tools: compress_pdf, compress_image, get_compressed

[0.1.0]: https://github.com/Manish3451/mdshrink/compare/v0.1.0