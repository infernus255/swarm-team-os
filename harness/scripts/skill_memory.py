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

    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(content)

    print(f"Entrada agregada a {memory_file}")

if __name__ == "__main__":
    main()
