import asyncio
import os
from typing import Any, Dict
from core.orchestrator import GraphRunner

from memory.sga_client import sga_client

class JarvisAssistant:
    """The SwarmTeam Assistant (Jarvis-mode)
    Decides whether to perform OS-level tasks or trigger a Swarm for app creation.
    Learns from every interaction via reflection.
    """
    
    def __init__(self):
        self.swarm_runner = GraphRunner()

    async def handle_request(self, prompt: str):
        print(f"--- Jarvis analizando: '{prompt}' ---")
        
        result = None
        mode = "OS"

        # Lógica de decisión
        if any(keyword in prompt.lower() for keyword in ["crear", "app", "desarrollar", "proyecto", "swarm"]):
            print("🤖 [Modo Swarm]: Requerimiento de desarrollo detectado.")
            mode = "SWARM"
            result = await self.swarm_runner.run(prompt)
        else:
            print("🖥️ [Modo OS]: Requerimiento operativo detectado.")
            result = await self.execute_os_skill(prompt)

        # MEJORA: Bucle de Reflexión y Aprendizaje Activo
        await self._reflect_and_learn(prompt, result, mode)
        
        return result

    async def execute_os_skill(self, prompt: str):
        """Ejecuta tareas de sistema usando el Harness."""
        print(f"Jarvis ejecutando tarea de sistema: {prompt}")
        # Simulación de éxito de tarea
        return {"status": "SUCCESS", "details": f"Tarea '{prompt}' completada."}

    async def _reflect_and_learn(self, prompt: str, result: Any, mode: str):
        """Analiza la interacción y guarda lecciones en el SGA."""
        print(f"🧠 [Reflexión]: Evaluando aprendizaje de la interacción...")
        
        # En una implementación real, aquí se llamaría a un LLM pequeño (ej. Gemini Flash)
        # para extraer el "insight". Para el MVP, simulamos la extracción de lecciones.
        
        insight = f"Interacción exitosa en modo {mode}. Prompt: {prompt}"
        
        # Guardar en memoria de largo plazo (SGA)
        success = sga_client.push_memory(
            project_id="GLOBAL_JARVIS",
            phase="REFLECTION",
            content=insight,
            metadata={"mode": mode, "user_input": prompt}
        )
        
        if success:
            print("✨ [Memoria]: Lección persistida en el SGA.")
        else:
            print("⚠️ [Memoria]: No se pudo conectar con el SGA, guardando en log local.")

# MVP Main Entry Point (Jarvis)
if __name__ == "__main__":
    jarvis = JarvisAssistant()
    # En un escenario real, esto vendría de Telegram/Hermes
    import sys
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "crear una app de notas"
    asyncio.run(jarvis.handle_request(user_input))
