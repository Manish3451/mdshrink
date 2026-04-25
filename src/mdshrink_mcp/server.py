import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import pdf as pdf_module
from . import image as image_module
from . import cache
from . import tokens as tokens_module

mcp = FastMCP("mdshrink")


def _resolve_path(path: str) -> Path:
    return Path(path).resolve()


@mcp.tool()
def compress_pdf(path: str, mode: str = "fast") -> dict:
    """URGENT: ALWAYS call this FIRST before reading any .pdf file with the Read tool. This converts PDFs to compact Markdown saving 5-10x tokens. Returns {md_path} - read that file instead of the original PDF. Skip ONLY if user explicitly wants original PDF preserved. This saves significant tokens and reduces cost."""
    path_obj = _resolve_path(path)
    
    if not path_obj.exists():
        return {"error": f"File not found: {path}"}
    
    cached = cache.get_cache_entry(str(path_obj), mode)
    if cached:
        original = tokens_module.estimate_pdf_tokens(str(path_obj), 1)
        compressed = tokens_module.count_md_tokens(str(cached))
        return {
            "md_path": str(cached),
            "original_tokens": original,
            "compressed_tokens": compressed,
            "ratio": tokens_module.get_token_ratio(original, compressed),
            "pages": 1,
            "cached": True,
        }
    
    md_content, num_pages = pdf_module.convert_pdf(str(path_obj), mode)
    
    md_path = cache.save_cache_entry(
        str(path_obj),
        md_content,
        mode,
        {"type": "pdf", "pages": num_pages}
    )
    
    original = tokens_module.estimate_pdf_tokens(str(path_obj), num_pages)
    compressed = tokens_module.count_md_tokens(str(md_path))
    
    return {
        "md_path": str(md_path),
        "original_tokens": original,
        "compressed_tokens": compressed,
        "ratio": tokens_module.get_token_ratio(original, compressed),
        "pages": num_pages,
        "cached": False,
    }


@mcp.tool()
def compress_image(path: str) -> dict:
    """URGENT: ALWAYS call this FIRST before reading any image file (.png, .jpg, .jpeg, .webp) that contains text - screenshots of code, errors, docs, UIs, terminal output. This extracts text via OCR saving massive tokens. Returns {md_path} - read that file. Skip for photos/diagrams where visual IS content."""
    path_obj = _resolve_path(path)
    
    if not path_obj.exists():
        return {"error": f"File not found: {path}"}
    
    cached = cache.get_cache_entry(str(path_obj), "ocr")
    if cached:
        original = tokens_module.estimate_image_tokens(str(path_obj))
        compressed = tokens_module.count_md_tokens(str(cached))
        return {
            "md_path": str(cached),
            "original_tokens": original,
            "compressed_tokens": compressed,
            "ratio": tokens_module.get_token_ratio(original, compressed),
            "ocr_confidence": 1.0,
            "cached": True,
        }
    
    md_content, conf = image_module.convert_image(str(path_obj))
    
    md_path = cache.save_cache_entry(
        str(path_obj),
        md_content,
        "ocr",
        {"type": "image", "ocr_confidence": conf}
    )
    
    original = tokens_module.estimate_image_tokens(str(path_obj))
    compressed = tokens_module.count_md_tokens(str(md_path))
    
    return {
        "md_path": str(md_path),
        "original_tokens": original,
        "compressed_tokens": compressed,
        "ratio": tokens_module.get_token_ratio(original, compressed),
        "ocr_confidence": conf,
        "cached": False,
    }


@mcp.tool()
def get_compressed(original_path: str) -> dict:
    """Cheap cache check. Call this first if you suspect the file has been converted before."""
    path_obj = _resolve_path(original_path)
    
    if not path_obj.exists():
        return {"cached": False, "error": f"File not found: {original_path}"}
    
    pdf_hit = cache.get_cache_entry(str(path_obj), "fast")
    if pdf_hit:
        return {"md_path": str(pdf_hit), "cached": True}
    
    ocr_hit = cache.get_cache_entry(str(path_obj), "ocr")
    if ocr_hit:
        return {"md_path": str(ocr_hit), "cached": True}
    
    return {"cached": False}


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()