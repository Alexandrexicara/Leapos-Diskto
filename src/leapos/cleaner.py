"""Analise e limpeza de caches conhecidos, sem tocar em perfis."""
from pathlib import Path
from .safety import remove_cache_entry

HOME = Path.home()
CANDIDATES = (
    HOME / ".cache/thumbnails",
    HOME / ".cache/mozilla/firefox",
    HOME / ".cache/chromium",
    HOME / ".cache/google-chrome",
)

def analyze():
    found = []
    for root in CANDIDATES:
        if not root.is_dir() or root.is_symlink():
            continue
        total = 0
        for item in root.rglob("*"):
            try:
                if not item.is_symlink() and item.is_file():
                    total += item.stat().st_size
            except OSError:
                pass
        found.append((root, total))
    return found

def clean_selected(selected):
    removed = 0
    for root, _size in analyze():
        if root not in selected:
            continue
        for child in list(root.iterdir()):
            if child.is_symlink():
                continue
            removed += remove_cache_entry(child, (root,))
    return removed
