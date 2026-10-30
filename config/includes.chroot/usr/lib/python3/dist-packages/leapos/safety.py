from pathlib import Path

def safe_child(path, roots):
    p=Path(path).expanduser()
    if p.is_symlink(): raise ValueError('Link simbolico bloqueado')
    p=p.resolve(strict=False)
    roots=tuple(Path(r).resolve() for r in roots)
    if not any(p != r and r in p.parents for r in roots): raise ValueError('Fora da pasta de cache')
    return p

def remove_cache_entry(path, roots):
    import shutil
    p=safe_child(path, roots)
    if not p.exists(): return 0
    if p.is_file():
        n=p.stat().st_size; p.unlink(); return n
    total=0
    for x in p.rglob('*'):
        if x.is_symlink(): raise ValueError('Link simbolico encontrado')
        if x.is_file(): total += x.stat().st_size
    shutil.rmtree(p)
    return total
