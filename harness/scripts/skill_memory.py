#!/usr/bin/env python3
import sys
from datetime import datetime, timezone
from utils.state_loader import StateLoader

def main():
    if len(sys.argv) < 2:
        print("Uso: python harness/scripts/skill_memory.py \"Texto de aprendizaje\"")
        sys.exit(1)

    entry = " ".join(sys.argv[1:])
    loader = StateLoader()
    memory_file = loader.repo_root / "memory.md"

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    content = f"\n### {timestamp}\n- {entry}\n"

    # 1. Log locally
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"Entrada agregada a {memory_file}")

    # 2. Push to Neon Database (SGA L0/L1)
    try:
        # Add repo root to python path to import core/memory modules
        if str(loader.repo_root) not in sys.path:
            sys.path.insert(0, str(loader.repo_root))
        
        from memory.sga_client import sga_client
        
        # Get project id from current folder name or metadata
        project_id = loader.repo_root.name
        
        success = sga_client.push_memory(
            project_id=project_id,
            phase="LEARNING",
            content=entry,
            metadata={"source": "harness_skill_memory"}
        )
        if success:
            print("Entrada subida exitosamente a la base de datos Neon (SGA L0/L1)")
        else:
            print("Advertencia: No se pudo subir a la base de datos Neon (verifique autenticación/tokens)")
    except Exception as e:
        print(f"Error al conectar con la base de datos Neon: {e}")

if __name__ == "__main__":
    main()
