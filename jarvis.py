import asyncio
import os
from typing import Any, Dict
from core.orchestrator import GraphRunner

class JarvisAssistant:
    """The SwarmTeam Assistant (Jarvis-mode)
    Decides whether to perform OS-level tasks or trigger a Swarm for app creation.
    """
    
    def __init__(self):
        self.swarm_runner = GraphRunner()

    async def handle_request(self, prompt: str):
        print(f"--- Jarvis analizando: '{prompt}' ---")
        
        # Lógica de decisión simplificada
        if any(keyword in prompt.lower() for keyword in ["crear", "app", "desarrollar", "proyecto", "swarm"]):
            print("🤖 [Modo Swarm]: Requerimiento de desarrollo detectado. Iniciando SwarmTeam.")
            return await self.swarm_runner.run(prompt)
        else:
            print("🖥️ [Modo OS]: Requerimiento operativo detectado. Ejecutando skill del Harness.")
            return await self.execute_os_skill(prompt)

    async def execute_os_skill(self, prompt: str):
        # Aquí Jarvis usaría el harness/skills/ directamente
        # Ejemplo simulado de una respuesta operativa
        print(f"Jarvis ejecutando tarea de sistema: {prompt}")
        return {"status": "OS_TASK_COMPLETED", "task": prompt}

# MVP Main Entry Point (Jarvis)
if __name__ == "__main__":
    jarvis = JarvisAssistant()
    # En un escenario real, esto vendría de Telegram/Hermes
    import sys
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "crear una app de notas"
    asyncio.run(jarvis.handle_request(user_input))
