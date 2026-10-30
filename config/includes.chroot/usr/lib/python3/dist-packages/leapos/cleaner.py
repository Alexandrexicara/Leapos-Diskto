from pathlib import Path
from .safety import remove_cache_entry
H=Path.home()
ROOTS=(H/'.cache/thumbnails',H/'.cache/mozilla/firefox',H/'.cache/chromium',H/'.cache/google-chrome')
def analyze():
 out=[]
 for root in ROOTS:
  if not root.is_dir() or root.is_symlink(): continue
  size=0
  for p in root.rglob('*'):
   try:
    if not p.is_symlink() and p.is_file(): size += p.stat().st_size
   except OSError: pass
  out.append((root,size))
 return out
def clean_selected(selected):
 total=0
 for root,_ in analyze():
  if root in selected:
   for p in list(root.iterdir()):
    if not p.is_symlink(): total += remove_cache_entry(p,(root,))
 return total
