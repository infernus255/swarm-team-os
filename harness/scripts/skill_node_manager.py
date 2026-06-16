import argparse
import sys
import json
from pathlib import Path

# Añadir el root al path para permitir importaciones core
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.services.node_service import NodeService

def run_skill():
    """
    Skill Determinista: Node Manager.
    Actúa como interfaz entre el operador (Jarvis/Humano) y el NodeService.
    """
    parser = argparse.ArgumentParser(description="SwarmTeam OS Node Manager Skill")
    parser.add_argument("action", choices=["info", "register", "check"], help="Acción a ejecutar")
    parser.add_argument("--output", help="Ruta para guardar el ledger de estado")

    args = parser.parse_args()
    service = NodeService()

    if args.action == "info":
        state = service.generate_snapshot()
        print(f"\n🧬 [Node Manager] Host: {state['system']['hostname']}")
        print(f"   OS: {state['system']['os']} | Arch: {state['system']['architecture']}")
        print(f"   VCS: {state['vcs'].get('branch', 'N/A')} @ {state['vcs'].get('commit', 'N/A')[:8]}")

    elif args.action == "register":
        output_path = args.output or "state.json"
        state = service.generate_snapshot()
        with open(output_path, "w") as f:
            json.dump(state, f, indent=4)
        print(f"✅ State snapshot saved to: {output_path}")

    elif args.action == "check":
        deps = service.check_runtime_dependencies()
        configs = service.check_centralized_config()
        
        print("\n🔍 [Dependency Audit]")
        for dep, status in deps.items():
            color = "✅" if status == "installed" else "❌"
            print(f"   {color} {dep:10} -> {status}")
            
        print("\n🔑 [Centralized Config Audit]")
        all_ok = True
        for key, present in configs.items():
            color = "✅" if present else "❌"
            status = "present" if present else "MISSING"
            print(f"   {color} {key:15} -> {status}")
            if not present: all_ok = False
            
        if not all_ok:
            print("\n💡 [Action Required]:")
            print("   Para centralizar tus claves y evitar este mensaje en todos tus entornos:")
            print("   1. Ve a: GitHub Repository -> Settings -> Codespaces -> Secrets")
            print("   2. Agrega las claves faltantes mencionadas arriba.")
            print("   3. Reinicia tu Codespace.")
        print("")

if __name__ == "__main__":
    run_skill()
