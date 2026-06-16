import argparse
import sys
import json
from .core import NodeCollector

def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Node Manager CLI - Herramienta de gestión de nodos para SwarmTeam OS"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: info
    subparsers.add_parser("info", help="Muestra información detallada del nodo actual")

    # Comando: register
    register_parser = subparsers.add_parser("register", help="Registra el estado del nodo en un archivo ledger")
    register_parser.add_argument("--output", default="local_ledger.json", help="Ruta del archivo de salida (default: local_ledger.json)")

    # Comando: check
    subparsers.add_parser("check", help="Verifica las dependencias del sistema para Jarvis OS")

    args = parser.parse_args()
    collector = NodeCollector()

    if args.command == "info":
        data = collector.collect_all()
        print("\n🤖 [Jarvis Node Info]")
        print(f"  - Hostname:     {data['system']['hostname']}")
        print(f"  - OS:           {data['system']['os']} ({data['system']['architecture']})")
        print(f"  - Python:       {data['system']['python_version']}")
        print(f"  - Container:    {data['system']['is_container']}")
        if data['git']['available']:
            print(f"  - Git Branch:   {data['git']['branch']}")
        else:
            print(f"  - Git:          Not available")
        print("")

    elif args.command == "register":
        path = collector.save_to_ledger(args.output)
        print(f"✅ [Jarvis Node] Estado registrado exitosamente en: {path}")

    elif args.command == "check":
        results = collector.check_dependencies()
        print("\n🛡️ [Dependency Check]")
        for dep, status in results.items():
            icon = "✅" if status == "installed" else "❌"
            print(f"  {icon} {dep:10}: {status}")
        print("")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
