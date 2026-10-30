"""Validacao conservadora de caminhos para operacoes de cache."""
from pathlib import Path

HOME = Path.home().resolve()
PROTECTED = {".ssh", ".gnupg", ".config", ".local", "Documents", "Downloads", "Desktop", "Pictures", "Videos", "Music"}

def safe_child(path: str | Path, roots: tuple[Path, ...]) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("Links simbolicos nao sao aceitos.")
    resolved = candidate.resolve(strict=False)
    valid_roots = tuple(root.resolve() for root in roots)
    if not any(resolved != root and root in resolved.parents for root in valid_roots):
        raise ValueError("Caminho fora da area de cache permitida.")
    if any(part in PROTECTED for part in resolved.parts):
        raise ValueError("Area protegida; operacao cancelada.")
    return resolved

def remove_cache_entry(path: str | Path, roots: tuple[Path, ...]) -> int:
    import shutil
    target = safe_child(path, roots)
    if not target.exists():
        return 0
    if target.is_file():
        size = target.stat().st_size
        target.unlink()
        return size
    size = 0
    for item in target.rglob("*"):
        if item.is_symlink():
            raise ValueError("Link simbolico encontrado; limpeza cancelada.")
        if item.is_file():
            size += item.stat().st_size
    shutil.rmtree(target)
    return size
