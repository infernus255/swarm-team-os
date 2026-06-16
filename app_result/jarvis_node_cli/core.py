import os
import platform
import subprocess
import json
import socket
from datetime import datetime

class NodeCollector:
    """Recolecta información técnica del nodo local de forma determinista."""

    @staticmethod
    def get_system_info():
        return {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "is_container": os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
        }

    @staticmethod
    def get_git_status():
        try:
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            return {"branch": branch, "commit": commit, "available": True}
        except Exception:
            return {"available": False, "error": "No git repository found"}

    @staticmethod
    def check_dependencies():
        deps = ["python3", "git", "pytest"]
        results = {}
        for dep in deps:
            try:
                subprocess.check_output(["which", dep], text=True)
                results[dep] = "installed"
            except Exception:
                results[dep] = "missing"
        return results

    def collect_all(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "git": self.get_git_status(),
            "dependencies": self.check_dependencies()
        }

    def save_to_ledger(self, path="local_ledger.json"):
        data = self.collect_all()
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return path
