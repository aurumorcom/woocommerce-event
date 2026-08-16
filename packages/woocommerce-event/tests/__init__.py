"""Tests root package."""

import sys
from pathlib import Path

tests_dir = Path(__file__).resolve().parent
pkg_dir = tests_dir.parents[0]
root = tests_dir.parents[2]
for p in [
    str(root),
    str(pkg_dir),
    str(pkg_dir / "src"),
    str(root / "src"),
    str(
        root
        / ".agents"
        / "skills"
        / "python-logging"
        / "modules"
        / "python-logging"
        / "src"
    ),
]:
    if p not in sys.path:
        sys.path.insert(0, p)
