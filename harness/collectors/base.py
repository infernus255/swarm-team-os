import subprocess
import shutil
from typing import Dict, Any

class GitCollector:
    def collect(self) -> Dict[str, Any]:
        git = {"branch": None, "commit": None, "status": {"modified": 0, "untracked": 0}}
        if not shutil.which("git"):
            return git

        try:
            git["branch"] = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            git["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            status = subprocess.check_output(["git", "status", "--short"], text=True)
            for line in status.splitlines():
                if line.startswith("??"): git["status"]["untracked"] += 1
                else: git["status"]["modified"] += 1
        except Exception:
            pass
        return git

class SystemCollector:
    def collect(self) -> Dict[str, Any]:
        import platform
        import os
        return {
            "node": platform.node(),
            "os": os.name,
            "version": platform.version(),
            "is_container": os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"),
            "is_codespaces": os.getenv("CODESPACES") == "true"
        }
