import subprocess
import json
import sys
import os
from pathlib import Path

def run_command(cmd, desc):
    print(f"🔄 [AI-BOOTSTRAP] Ejecutando: {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.stderr.strip(), "code": e.returncode}

def main():
    """
    Script diseñado para ser ejecutado por un Agente de IA (ej. Antigravity, Copilot).
    Ejecuta la configuración del entorno y devuelve un JSON estructurado para que el agente
    pueda analizar el resultado sin parsear logs de bash confusos.
    """
    repo_root = Path(__file__).resolve().parents[1]
    setup_script = repo_root / "infra" / "universal-setup.sh"
    
    if not setup_script.exists():
        print(json.dumps({"error": "Setup script no encontrado", "path": str(setup_script)}))
        sys.exit(1)

    # Determinar el flag según el entorno
    flag = ""
    if os.getenv("IS_PENTIUM_NODE") == "true" or "--server" in sys.argv:
        flag = "--server"

    print(json.dumps({"event": "bootstrap_started", "script": str(setup_script), "flag": flag}))
    
    # Ejecutar el script bash
    cmd = f"bash {setup_script} {flag}"
    result = run_command(cmd, "Universal Setup Bash Script")
    
    # Analizar resultado
    if result["status"] == "success":
        final_state = {
            "bootstrap": "COMPLETED",
            "hermes_installed": "hermes" in result["output"].lower(),
            "docker_installed": "docker" in result["output"].lower(),
            "next_action_required_by_ai": "Validar config/api_orchestrator.json e iniciar jarvis.py"
        }
        print(json.dumps({"event": "bootstrap_finished", "details": final_state}, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"event": "bootstrap_failed", "error": result}, indent=2))
        sys.exit(result.get("code", 1))

if __name__ == "__main__":
    main()
