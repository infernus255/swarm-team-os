import argparse
import sys
from pathlib import Path
import json
from datetime import datetime

# Path setup to include core
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.services.memory_service import MemoryService

def format_timestamp(ts):
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts

def run_dashboard():
    parser = argparse.ArgumentParser(description="SwarmTeam OS Observability Dashboard")
    parser.add_argument("view", choices=["l0", "l1", "guru"], help="Capa de memoria a visualizar")
    parser.add_argument("--limit", type=int, default=5, help="Número de registros a mostrar")
    parser.add_argument("--project", help="Filtrar por ID de proyecto")

    args = parser.parse_args()
    memory = MemoryService()

    print(f"\n🖥️  [SwarmTeam OS Dashboard] - {args.view.upper()} View")
    print("="*60)

    if args.view == "l0":
        # Simulación de estados de proyecto (Meta-State)
        print("🔍 Consultando Estado Global de Proyectos (SGA L0)...")
        # En una implementación real, esto consultaría una tabla de proyectos
        # Por ahora usamos query_global_memory con un filtro conceptual
        results = memory.query_global_memory(query="project state", limit=args.limit)
        print(results)

    elif args.view == "l1":
        print("🧠 Consultando Conocimiento Atómico (SGA L1)...")
        results = memory.query_global_memory(query="technical insight", limit=args.limit)
        print(results)

    elif args.view == "guru":
        print("🕵️  Consultando Últimos Insights de Guru-Watch...")
        results = memory.query_global_memory(query="architectural_update", limit=args.limit)
        print(results)

    print("\n" + "="*60)
    print("✅ Fin del reporte.")

if __name__ == "__main__":
    run_dashboard()
