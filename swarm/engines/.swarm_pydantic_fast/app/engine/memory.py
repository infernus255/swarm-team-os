from __future__ import annotations

import os
import psycopg2
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.config import settings

class MemoryManager:
    MEMORY_FILE = "MEMORY.md"

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _get_conn(self):
        if not self.db_url:
            return None
        try:
            return psycopg2.connect(self.db_url)
        except Exception:
            return None

    def read(self) -> str:
        path = settings.result_dir / self.MEMORY_FILE
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def update(self, project_id: str, phase: str, bullet_points: List[str]) -> None:
        # 1. Update local MEMORY.md
        path = settings.result_dir / self.MEMORY_FILE
        path.parent.mkdir(parents=True, exist_ok=True)

        existing = self.read().strip()
        new_entries = "\n".join(f"- {bp}" for bp in bullet_points[:3])

        if existing:
            content = f"{existing}\n\n## {phase}\n{new_entries}\n"
        else:
            content = f"# Swarm Memory\n\n## {phase}\n{new_entries}\n"

        path.write_text(content, encoding="utf-8")

        # 2. Push to SGA Neon DB
        conn = self._get_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO sga_l0_context (project_id, phase, content, created_at) VALUES (%s, %s, %s, %s)",
                        (project_id, phase, new_entries, datetime.now(timezone.utc))
                    )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ SGA Sync Failed: {e}")

    def query_global(self, query: str, limit: int = 5) -> str:
        """Retrieves knowledge from L1 global memory using semantic search (simulated here via recent insights)."""
        conn = self._get_conn()
        if not conn:
            return "Global memory unreachable."
        try:
            with conn.cursor() as cur:
                # Simulating a simple search by project/category if pgvector is not directly used here
                # In a full implementation, we would use embeddings.
                cur.execute(
                    "SELECT content, project_id, metadata->>'category' FROM sga_l1_swarm_knowledge ORDER BY created_at DESC LIMIT %s",
                    (limit,)
                )
                rows = cur.fetchall()
                conn.close()
                if not rows: return "No global insights found."
                return "\n\n".join([f"[{r[1]}] [{r[2]}]: {r[0]}" for r in rows])
        except Exception as e:
            return f"Error querying global memory: {e}"

    def get_recent(self, max_phases: int = 3) -> str:
        path = settings.result_dir / self.MEMORY_FILE
        if not path.exists():
            return "No local memory available."
        lines = path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-max_phases * 5:])


memory = MemoryManager()
