from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    swarm_mode: str = "hitl"  # hitl | auto
    swarm_project_root: str = ""

    # Modelos por defecto para los agentes
    model_orchestrator: str = "gemini-2.5-flash"
    model_m0: str = "gemini-2.5-flash"
    model_m1: str = "gemini-2.5-flash"
    model_m2: str = "gemini-2.5-flash"
    model_m3: str = "gemini-2.5-pro"
    model_m4: str = "gemini-2.5-flash"
    model_m5: str = "gemini-2.5-pro"
    model_m6: str = "gemini-2.5-flash"

    @property
    def project_root(self) -> Path:
        if self.swarm_project_root:
            return Path(self.swarm_project_root)
        return Path.cwd()

    @property
    def result_dir(self) -> Path:
        # El código resultante se escribe siempre en la raíz del proyecto, fuera del swarm
        return self.project_root / "app_result"

    @property
    def state_path(self) -> Path:
        return self.project_root / ".swarn" / "states" / "swarm_state.json"

    @property
    def memory_path(self) -> Path:
        return self.result_dir / "MEMORY.md"

    @property
    def is_hitl(self) -> bool:
        return self.swarm_mode == "hitl"


settings = Settings()
