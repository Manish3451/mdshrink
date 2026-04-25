import re
from pathlib import Path
from typing import Tuple

from rapidocr_onnxruntime import RapidOCR


def convert_image(file_path: str) -> Tuple[str, float]:
    Rapid = RapidOCR()
    result, elapse = Rapid(file_path)
    
    if not result:
        return "# No text detected\n\n> [No text found in image]", 0.0
    
    blocks_by_row = _group_by_rows(result)
    
    conf = sum(r[1] for r in result) / len(result) if result else 0.0
    
    md_lines = []
    
    for row in blocks_by_row:
        blocks = sorted(row["blocks"], key=lambda x: x[0])
        line_text = " ".join(b[3] for b in blocks)
        
        if _is_code_like(line_text):
            md_lines.append(f"```\n{line_text}\n```")
        else:
            md_lines.append(line_text)
    
    md_content = "\n".join(md_lines)
    md_content = _clean_text(md_content)
    
    header = "# Extracted Text\n\n"
    md_content = header + md_content
    
    return md_content, conf


def _group_by_rows(results, row_threshold=20):
    if not results:
        return []
    
    results_sorted = sorted(results, key=lambda x: x[0][1])
    
    rows = []
    current_y = None
    current_row = []
    
    for box, conf, text in results_sorted:
        y = box[1]
        
        if current_y is None:
            current_y = y
            current_row.append((box, conf, text))
        elif abs(y - current_y) <= row_threshold:
            current_row.append((box, conf, text))
        else:
            rows.append({"y": current_y, "blocks": current_row})
            current_y = y
            current_row = [(box, conf, text)]
    
    if current_row:
        rows.append({"y": current_y, "blocks": current_row})
    
    return rows


def _is_code_like(text):
    if not text:
        return False
    
    indent_chars = sum(1 for c in text if c in " \t")
    if indent_chars > len(text) * 0.1:
        return True
    
    code_indicators = ["{", "}", "()", "->", "=>", "def ", "class ", "import ", "function", "const ", "let ", "var "]
    if any(ind in text for ind in code_indicators):
        return True
    
    char_variance = _compute_char_variance(text)
    if char_variance > 3:
        return True
    
    return False


def _compute_char_variance(text):
    if len(text) < 4:
        return 0
    
    widths = []
    for c in text:
        if c.isalnum():
            widths.append(1)
    
    if not widths:
        return 0
    
    avg = sum(widths) / len(widths)
    variance = sum((w - avg) ** 2 for w in widths) / len(widths)
    return variance ** 0.5


def _clean_text(text):
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n +", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip() + "\n"