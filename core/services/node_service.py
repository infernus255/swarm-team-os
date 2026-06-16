import os
import platform
import subprocess
import json
import socket
from datetime import datetime
from typing import Dict, Any

class NodeService:
    """
    Servicio Core para la gestión y auditoría del nodo físico/virtual.
    Sigue el principio de Responsabilidad Única (SRP) al encargarse solo 
    de la recolección de métricas y estado del sistema.
    """

    def get_system_metrics(self) -> Dict[str, Any]:
        """Recolecta información estática y dinámica del hardware."""
        return {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "is_container": self._is_container()
        }

    def get_vcs_state(self) -> Dict[str, Any]:
        """Obtiene el estado del control de versiones (Git)."""
        try:
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            return {"branch": branch, "commit": commit, "available": True}
        except Exception:
            return {"available": False, "error": "VCS not detected"}

    def check_runtime_dependencies(self) -> Dict[str, str]:
        """Valida la disponibilidad de herramientas críticas en el PATH."""
        deps = ["python3", "git", "docker", "pytest"]
        return {dep: self._check_bin(dep) for dep in deps}

    def check_centralized_config(self) -> Dict[str, bool]:
        """Verifica si las claves críticas están presentes en el entorno."""
        keys = ["GEMINI_API_KEY", "DATABASE_URL"]
        return {key: (os.getenv(key) is not None) for key in keys}

    def _is_container(self) -> bool:
        return os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')

    def _check_bin(self, binary: str) -> str:
        try:
            subprocess.check_output(["which", binary], text=True)
            return "installed"
        except Exception:
            return "missing"

    def generate_snapshot(self) -> Dict[str, Any]:
        """Genera un snapshot completo del estado del nodo para la SGA."""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_metrics(),
            "vcs": self.get_vcs_state(),
            "dependencies": self.check_runtime_dependencies()
        }
