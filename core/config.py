import os
import platform
from pathlib import Path
from typing import Optional

def load_env_file(filepath: Path):
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                val = val.strip().strip("'\"")
                if key.strip() not in os.environ:
                    os.environ[key.strip()] = val
    except Exception as e:
        print(f"[Config Warning] Could not load env file {filepath}: {e}")

class Settings:
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        
        # Priority loading
        load_env_file(self.repo_root / "hermes.env")
        load_env_file(Path.home() / ".hermes" / ".env")
        load_env_file(self.repo_root / ".env")

        self.database_url = os.getenv("DATABASE_URL") or "postgresql://neondb_owner:npg_ofE7Ie8gQasT@ep-fancy-thunder-ack1oc7m.sa-east-1.aws.neon.tech/neondb?sslmode=require"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.node_id = os.getenv("NODE_ID") or platform.node() or "unknown_node"
        self.node_token = os.getenv("NODE_TOKEN", "default_secret_node_token")
        self.env_tier = os.getenv("ENV_TIER", "DEV")
        self.ntfy_topic = os.getenv("NTFY_TOPIC") or "jarvis_os"
        self.version = self._get_version()

        # AI Model Tiers (FinOps Cascading - 2026 Standards)
        self.model_tier1 = os.getenv("TIER1_MODEL", "gemini-3.5-flash") # Efficient Routing / Small Tasks
        self.model_tier2 = os.getenv("TIER2_MODEL", "gemini-3.1-flash-lite") # Context-rich fast reasoning
        self.model_tier3 = os.getenv("TIER3_MODEL", "gemini-3.5-pro") # Elite Coding / Architecture

    def _get_version(self) -> str:
        version_file = self.repo_root / "VERSION"
        return version_file.read_text().strip() if version_file.exists() else "0.0.0"

settings = Settings()
