from pathlib import Path
import pytest
from leapos.safety import safe_child

def test_rejects_root_itself(tmp_path):
    with pytest.raises(ValueError):
        safe_child(tmp_path, (tmp_path,))

def test_rejects_outside_root(tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError):
        safe_child(outside, (root,))
