import asyncio
import sys
from core.orchestrator import GraphRunner

async def main():
    print("--- SWARM-TEAM OS: UNIFIED ENGINE ---")
    
    # Prompt por defecto o por argumento
    prompt = "Crear un sistema de gestión simple"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    
    print(f"Entrada del usuario: '{prompt}'")
    print("-" * 40)

    # Inicializar el orquestador
    runner = GraphRunner()
    
    # Ejecutar el flujo del Swarm
    final_state = await runner.run(prompt)
    
    print("-" * 40)
    print("RESULTADO DEL MVP:")
    print(f"ID Proyecto: {final_state['project_id']}")
    print(f"Estado Final: {final_state['status']}")
    print(f"Artefactos generados: {list(final_state['artifacts'].keys())}")
    print(f"Historial de fases: {[h['node'] for h in final_state['history']]}")

if __name__ == "__main__":
    asyncio.run(main())
