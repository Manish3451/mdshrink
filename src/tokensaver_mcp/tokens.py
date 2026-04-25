import math
from pathlib import Path

import tiktoken


enc = None


def _get_encoder():
    global enc
    if enc is None:
        enc = tiktoken.get_encoding("cl100k_base")
    return enc


def count_tokens(text: str) -> int:
    if not text:
        return 0
    encoder = _get_encoder()
    return len(encoder.encode(text))


def count_md_tokens(md_path: str) -> int:
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    return count_tokens(text)


def estimate_pdf_tokens(file_path: str, num_pages: int) -> int:
    page_overhead = 150
    overhead = num_pages * page_overhead
    
    try:
        import fitz
        doc = fitz.open(file_path)
        total_chars = sum(len(page.get_text().strip()) for page in doc)
        doc.close()
    except Exception:
        total_chars = 0
    
    tokens = total_chars // 3 + overhead
    return max(tokens, 1)


def estimate_image_tokens(image_path: str) -> int:
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            width, height = img.size
    except Exception:
        width, height = 1920, 1080
    
    base_tokens = 65
    
    aspect = width / height if height > 0 else 1
    if aspect > 1:
        w = min(width, 2048)
        h = int(height * (w / width))
    else:
        h = min(height, 2048)
        w = int(width * (h / height))
    
    tiles = math.ceil(w / 512) * math.ceil(h / 512)
    
    return base_tokens + (tiles - 1) * 85


def get_token_ratio(original: int, compressed: int) -> float:
    if compressed <= 0:
        return 0.0
    return round(original / compressed, 1)