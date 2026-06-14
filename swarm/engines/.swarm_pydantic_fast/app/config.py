from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    swarn_mode: str = "hitl"
    swarn_project_root: str = ""

    swarn_model_m0: str = "openai:gpt-4o-mini"
    swarn_model_m1: str = "openai:gpt-4o"
    swarn_model_m2: str = "openai:gpt-4o"
    swarn_model_m3: str = "openai:o3-mini"
    swarn_model_m4: str = "openai:gpt-4o-mini"
    swarn_model_m5: str = "anthropic:claude-sonnet-4-20250514"
    swarn_model_m6: str = "openai:gpt-4o-mini"
    swarn_model_orchestrator: str = "openai:gpt-4o-mini"

    @property
    def project_root(self) -> Path:
        if self.swarn_project_root:
            return Path(self.swarn_project_root)
        return Path.cwd()

    @property
    def template_dir(self) -> Path:
        return self.project_root / "swarn_templates"

    @property
    def result_dir(self) -> Path:
        return self.project_root / "app_result"

    @property
    def state_path(self) -> Path:
        return self.template_dir / "states" / "swarm_state.json"

    def model_for(self, agent_id: str) -> str:
        key = f"swarn_model_{agent_id.lower()}"
        return getattr(self, key, "openai:gpt-4o-mini")

    @property
    def is_hitl(self) -> bool:
        return self.swarn_mode == "hitl"

    @property
    def is_auto(self) -> bool:
        return self.swarn_mode == "auto"


settings = Settings()
