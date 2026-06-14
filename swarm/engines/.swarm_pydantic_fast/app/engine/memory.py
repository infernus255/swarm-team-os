from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.config import settings


class MemoryManager:
    MEMORY_FILE = "MEMORY.md"

    def read(self) -> str:
        path = settings.result_dir / self.MEMORY_FILE
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def update(self, phase: str, bullet_points: List[str]) -> None:
        path = settings.result_dir / self.MEMORY_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        existing = self.read().strip()
        new_entries = "\n".join(f"- {bp}" for bp in bullet_points[:3])

        if existing:
            content = f"{existing}\n\n## {phase}\n{new_entries}\n"
        else:
            content = f"# Swarm Memory\n\n## {phase}\n{new_entries}\n"

        path.write_text(content, encoding="utf-8")

    def get_recent(self, max_phases: int = 3) -> str:
        path = settings.result_dir / self.MEMORY_FILE
        if not path.exists():
            return "No memory available."
        lines = path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-max_phases * 5:])


memory = MemoryManager()
