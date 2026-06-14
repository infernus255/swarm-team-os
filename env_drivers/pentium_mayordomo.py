import platform
import psutil
from .base_driver import BaseDriver

class PentiumMayordomoDriver(BaseDriver):
    """Driver para hardware de bajos recursos (Pentium/Atom).
    Prioriza el ahorro de tokens y la delegación de tareas pesadas.
    """
    def get_env_name(self) -> str:
        return "Nodo Mayordomo (Pentium Local)"

    def get_telemetry_overrides(self) -> dict:
        # Obtener uso real para que Jarvis no se sobrecargue
        ram_total = psutil.virtual_memory().total / (1024**3)
        return {
            "performance_profile": "LOW_RESOURCE",
            "max_concurrent_agents": 2,
            "delegate_heavy_tasks": True,
            "target_delegate": "RYZEN_DESKTOP",
            "local_ram_gb": f"{ram_total:.1f}",
            "persistence_strategy": "Local-First / Async-Cloud"
        }

    def run_environment_setup(self) -> bool:
        # Aquí Jarvis se asegura de que el script de caza esté corriendo
        return True
