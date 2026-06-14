import asyncio
import sys
import os
from pathlib import Path

# Add current dir to sys.path
sys.path.append(os.getcwd())

from core.config import settings
from core.services.memory_service import MemoryService
from core.orchestrator import GraphRunner
from core.engine_selector import EngineSelector

class JarvisAssistant:
    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service
        self.swarm_runner = GraphRunner()
        self.engine_selector = EngineSelector(settings.repo_root)
        self._check_version()

    def _check_version(self):
        latest = self.memory.get_latest_system_version()
        if settings.version < latest:
            print(f"⚠️ [Jarvis] Outdated version: v{settings.version} < v{latest}")
        else:
            print(f"✅ [Jarvis] Version up-to-date: v{settings.version}")

    async def handle_request(self, prompt: str):
        print(f"--- Jarvis analizando: '{prompt}' ---")
        
        # Decision Logic
        if any(keyword in prompt.lower() for keyword in ["crear", "app", "swarm"]):
            engine = self.engine_selector.select_engine(prompt)
            result = await self.engine_selector.execute_engine(engine, prompt)
        else:
            result = {"status": "SUCCESS", "details": f"OS task '{prompt}' completed."}

        await self._learn(prompt, result)
        return result

    async def _learn(self, prompt: str, result: dict):
        insight = f"Interaction: {prompt} | Result: {result.get('status')}"
        self.memory.push_memory("GLOBAL_JARVIS", "REFLECTION", insight, {"input": prompt})
        print("🧠 [Jarvis] Memory persisted.")

if __name__ == "__main__":
    mem = MemoryService()
    jarvis = JarvisAssistant(mem)
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "verify version"
    asyncio.run(jarvis.handle_request(user_input))
