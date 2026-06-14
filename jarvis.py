import asyncio
import os
from typing import Any, Dict
from pathlib import Path
from core.orchestrator import GraphRunner
from core.engine_selector import EngineSelector
from memory.sga_client import sga_client

class JarvisAssistant:
    """The SwarmTeam Assistant (Jarvis-mode)
    Decides whether to perform OS-level tasks or trigger a Swarm for app creation.
    Learns from every interaction via reflection.
    """
    
    def __init__(self):
        self.swarm_runner = GraphRunner()
        self.engine_selector = EngineSelector(Path.cwd())
        self._check_version()

    def _check_version(self):
        """Checks if the current Jarvis version is outdated compared to the swarm."""
        latest_version = sga_client.get_latest_system_version()
        local_version = sga_client.local_version
        
        if local_version < latest_version:
            print(f"⚠️ [VERSION]: Estás ejecutando una versión antigua (v{local_version}).")
            print(f"🚀 [VERSION]: La última versión curada en el enjambre es v{latest_version}.")
            print(f"💡 [VERSION]: Por favor, ejecuta 'git pull' para actualizar este nodo.")
        else:
            print(f"✅ [VERSION]: Jarvis OS v{local_version} está actualizado.")

    async def handle_request(self, prompt: str):
        print(f"--- Jarvis analizando: '{prompt}' ---")
        
        result = None
        mode = "OS"

        # Lógica de decisión
        if any(keyword in prompt.lower() for keyword in ["crear", "app", "desarrollar", "proyecto", "swarm"]):
            print("🤖 [Modo Swarm]: Requerimiento de desarrollo detectado.")
            mode = "SWARM"
            selected_engine = self.engine_selector.select_engine(prompt)
            print(f"🤖 [Engine Selector]: Selected Swarm Engine '{selected_engine}'")
            
            try:
                result = await self.engine_selector.execute_engine(selected_engine, prompt)
                if result.get("status") == "ERROR":
                    print("⚠️ [Jarvis]: Swarm Engine execution failed, falling back to local GraphRunner...")
                    result = await self.swarm_runner.run(prompt)
            except Exception as e:
                print(f"⚠️ [Jarvis]: Exception during Swarm Engine execution: {e}. Falling back to local GraphRunner...")
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
