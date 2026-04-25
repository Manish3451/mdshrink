import re
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import fitz


def convert_pdf(file_path: str, mode: str = "fast") -> Tuple[str, int]:
    doc = fitz.open(file_path)
    num_pages = len(doc)
    
    if num_pages == 0:
        doc.close()
        return "# Empty Document\n", 0
    
    font_sizes = _collect_font_sizes(doc)
    thresholds = _compute_heading_thresholds(font_sizes)
    
    title = _extract_title(doc)
    header_footer = _detect_header_footer(doc)
    
    pages_content = []
    
    for page_num, page in enumerate(doc):
        content = _extract_page_content(page, thresholds, header_footer, page_num)
        pages_content.append(content)
    
    md_content = _build_markdown(title, pages_content, num_pages)
    
    doc.close()
    return md_content, num_pages


def _collect_font_sizes(doc):
    font_area = defaultdict(float)
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    size = span.get("size", 12)
                    char_count = len(text)
                    area = size * char_count
                    font_area[size] += area
    
    return dict(font_area)


def _compute_heading_thresholds(font_area):
    if not font_area:
        return {"h1": 1.5, "h2": 1.3, "h3": 1.15}
    
    body_size = max(font_area.items(), key=lambda x: x[1])[0]
    
    return {
        "h1": body_size * 1.5,
        "h2": body_size * 1.3,
        "h3": body_size * 1.15,
    }


def _extract_title(doc):
    first_page = doc[0]
    text = first_page.get_text().strip()
    lines = text.split("\n")[:10]
    
    for line in lines:
        line = line.strip()
        if len(line) > 3:
            return line[:200]
    
    if doc.metadata.get("title"):
        return doc.metadata.get("title", "Untitled")[:200]
    
    return "Untitled Document"


def _detect_header_footer(doc):
    if len(doc) < 3:
        return None
    
    line_counts = defaultdict(lambda: defaultdict(int))
    
    for page in doc[:min(5, len(doc))]:
        text = page.get_text()
        lines = text.split("\n")
        
        if lines:
            first_lines = [l.strip() for l in lines[:3] if l.strip()]
            for i, l in enumerate(first_lines):
                line_counts[i][l] += 1
        
        if len(lines) > 3:
            last_lines = [l.strip() for l in lines[-3:] if l.strip()]
            for i, l in enumerate(last_lines):
                line_counts[f"last_{i}"][l] += 1
    
    header_footer = {}
    
    for key, counts in line_counts.items():
        for text, count in counts.items():
            if count > len(doc) * 0.5 and len(text) < 100:
                header_footer[text] = True
    
    return header_footer if header_footer else None


def _extract_page_content(page, thresholds, header_footer, page_num):
    blocks = page.get_text("dict")["blocks"]
    
    lines_by_y = []
    
    for block in blocks:
        if block.get("type") != 0:
            continue
        
        for line in block.get("lines", []):
            line_text = ""
            font_size = None
            
            for span in line.get("spans", []):
                text = span.get("text", "")
                if font_size is None:
                    font_size = span.get("size", 12)
                line_text += text
            
            line_text = line_text.strip()
            if not line_text:
                continue
            
            if header_footer and line_text in header_footer:
                continue
            
            y = line.get("bbox", [0, 0, 0, 0])[1]
            
            level = "body"
            if font_size:
                if font_size >= thresholds.get("h1", 999):
                    level = "h1"
                elif font_size >= thresholds.get("h2", 999):
                    level = "h2"
                elif font_size >= thresholds.get("h3", 999):
                    level = "h3"
            
            lines_by_y.append((y, level, line_text))
    
    lines_by_y.sort(key=lambda x: x[0])
    
    return lines_by_y


def _build_markdown(title, pages_content, num_pages):
    lines = [f"# {title}\n"]
    
    current_section = None
    
    for page_num, content in enumerate(pages_content):
        lines.append(f"\n---\n\n## Page {page_num + 1}\n")
        
        for y, level, text in content:
            if level == "h1":
                lines.append(f"\n### {text}\n\n")
                current_section = "h1"
            elif level == "h2":
                lines.append(f"\n#### {text}\n\n")
                current_section = "h2"
            elif level == "h3":
                lines.append(f"##### {text}\n\n")
                current_section = "h3"
            else:
                if _is_list_item(text):
                    lines.append(f"{text}\n")
                elif _is_table_row(text):
                    lines.append(f"{text}\n")
                else:
                    if current_section == "body" and lines and lines[-1].strip() and not lines[-1].startswith("#"):
                        lines.append(f"{text} ")
                    else:
                        lines.append(f"{text}\n")
    
    md = "".join(lines)
    md = _clean_paragraphs(md)
    
    return md


def _is_list_item(text):
    patterns = [
        r"^[\s]*[•\-\*\u2022\u2023\u2043]\s+",
        r"^[\s]*\d+[.\)]\s+",
        r"^[\s]*\([a-zA-Z]\)\s+",
    ]
    return any(re.match(p, text) for p in patterns)


def _is_table_row(text):
    if "|" in text:
        parts = text.split("|")
        return len(parts) >= 3
    return False


def _clean_paragraphs(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n +", "\n", text)
    
    return text.strip() + "\n"