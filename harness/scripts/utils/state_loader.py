import json
import os
from pathlib import Path

class StateLoader:
    def __init__(self, workspace_root=None):
        self.repo_root = Path(workspace_root or os.getcwd()).resolve()
        self.state_file = self.repo_root / "state.json"

    def acquire_lock(self):
        import time
        self.lock_file = self.repo_root / "state.lock"
        start_time = time.time()
        while True:
            try:
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                if time.time() - start_time > 10.0:
                    try:
                        os.remove(self.lock_file)
                    except OSError:
                        pass
                time.sleep(0.1)

    def release_lock(self):
        if hasattr(self, "lock_file") and self.lock_file.exists():
            try:
                os.remove(self.lock_file)
            except OSError:
                pass

    def load_state(self, force_reload=False):
        if not self.state_file.exists():
            return {}
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_state(self, state):
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def discover_base_system(self):
        # Basic system discovery for state tracking
        import platform
        return {
            "os_name": os.name,
            "os_version": platform.version(),
            "packages_checked": [],
            "required_packages": []
        }
