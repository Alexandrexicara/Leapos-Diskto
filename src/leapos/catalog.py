"""Catalogo local dos aplicativos integrados ao LeapOS."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"config"/"apps.json"

def load_apps():
    try:
        data=json.loads(CATALOG.read_text(encoding="utf-8"))
        return [a for a in data.get("apps",[]) if a.get("enabled",True) and a.get("url","").startswith(("https://","http://"))]
    except (OSError,ValueError):
        return []

def save_apps(apps):
    CATALOG.parent.mkdir(parents=True,exist_ok=True)
    CATALOG.write_text(json.dumps({"apps":apps},ensure_ascii=False,indent=2),encoding="utf-8")
