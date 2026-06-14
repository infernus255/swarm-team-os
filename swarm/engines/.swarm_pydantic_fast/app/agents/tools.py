from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.engine.validator import validator as contract_validator


async def read_file(path: str) -> str:
    full = _resolve(path)
    if not full.exists():
        return f"ERROR: File not found: {path}"
    return full.read_text(encoding="utf-8")


async def write_file(path: str, content: str) -> bool:
    full = _resolve(path)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return True


async def list_dir(path: str) -> List[str]:
    full = _resolve(path)
    if not full.exists() or not full.is_dir():
        return []
    return sorted(str(p.relative_to(settings.project_root)) for p in full.iterdir())


async def file_exists(path: str) -> bool:
    return _resolve(path).exists()


def _resolve(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return (settings.project_root / path).resolve()


async def read_template(name: str) -> str:
    tmpl_dir = settings.template_dir / "specs"
    path = tmpl_dir / name
    if not path.exists():
        return f"ERROR: Template not found: {name}"
    return path.read_text(encoding="utf-8")
