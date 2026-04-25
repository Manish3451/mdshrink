import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple

CACHE_DIR_NAME = "tokensaver"
MAX_CACHE_SIZE = 500 * 1024 * 1024


def _get_cache_dir() -> Path:
    if os.name == "nt":
        cache_base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        cache_base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    
    cache_dir = cache_base / CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_cache_key(file_path: str, mode: str = "") -> str:
    with open(file_path, "rb") as f:
        data = f.read()
    key = hashlib.sha256(data).hexdigest()
    if mode:
        key = f"{key}-{mode}"
    return key


def _get_cached_path(cache_key: str) -> Path:
    cache_dir = _get_cache_dir()
    return cache_dir / f"{cache_key}.md"


def get_cache_entry(original_path: str, mode: str = "") -> Optional[Path]:
    cache_key = _get_cache_key(original_path, mode)
    md_path = _get_cached_path(cache_key)
    if md_path.exists():
        return md_path
    return None


def save_cache_entry(original_path: str, md_content: str, mode: str = "", metadata: Optional[dict] = None) -> Path:
    cache_key = _get_cache_key(original_path, mode)
    md_path = _get_cached_path(cache_key)
    
    cache_dir = _get_cache_dir()
    meta_path = cache_dir / f"{cache_key}.meta"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    meta = metadata or {}
    meta["original_path"] = original_path
    meta["cache_key"] = cache_key
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)
    
    _enforce_cache_limit()
    
    return md_path


def lookup_cache(original_path: str) -> Optional[Path]:
    return get_cache_entry(original_path)


def _enforce_cache_limit():
    cache_dir = _get_cache_dir()
    if not cache_dir.exists():
        return
    
    md_files = list(cache_dir.glob("*.md"))
    total_size = sum(f.stat().st_size for f in md_files)
    
    if total_size <= MAX_CACHE_SIZE:
        return
    
    mtimes = [(f, f.stat().st_mtime) for f in md_files]
    mtimes.sort(key=lambda x: x[1])
    
    for f, _ in mtimes:
        if total_size <= MAX_CACHE_SIZE:
            break
        size = f.stat().st_size
        f.unlink()
        meta_file = f.with_suffix(".meta")
        if meta_file.exists():
            meta_file.unlink()
        total_size -= size


def get_cache_stats() -> dict:
    cache_dir = _get_cache_dir()
    if not cache_dir.exists():
        return {"entries": 0, "size_bytes": 0}
    
    md_files = list(cache_dir.glob("*.md"))
    total_size = sum(f.stat().st_size for f in md_files)
    
    return {
        "entries": len(md_files),
        "size_bytes": total_size,
    }


def clear_cache():
    cache_dir = _get_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)