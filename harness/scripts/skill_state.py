import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

from core.config import settings
from harness.collectors.base import GitCollector, SystemCollector

class TelemetryOrchestrator:
    def __init__(self):
        self.git = GitCollector()
        self.system = SystemCollector()
        self.state_file = settings.repo_root / "state.json"

    def run(self):
        print(f"🔄 [Telemetry] Collecting data for v{settings.version}...")
        
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.version,
            "node": settings.node_id,
            "git": self.git.collect(),
            "system": self.system.collect()
        }

        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"✅ [Telemetry] State saved to {self.state_file}")

if __name__ == "__main__":
    TelemetryOrchestrator().run()
