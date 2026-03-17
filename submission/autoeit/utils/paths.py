"""Small filesystem helpers shared across services.

Kept deliberately narrow. This project does not need a general-purpose utility
grab bag, but path handling shows up in a couple of places and is easier to
reason about when it is consistent.
"""

from __future__ import annotations

from pathlib import Path


def ensure_parent_dir(path: str | Path) -> Path:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def default_downgrade_path(scores_path: str | Path) -> Path:
    return Path(scores_path).with_name("AutoEIT_ambiguous_downgrades.csv")