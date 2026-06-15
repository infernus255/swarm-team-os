import os
import requests
import json
from datetime import datetime
from pathlib import Path
from core.services.memory_service import MemoryService

# URLs de los "Gurus" y Repositorios Clave
GURU_SOURCES = [
    "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md",
    "https://raw.githubusercontent.com/pydantic/pydantic-ai/main/README.md",
    "https://raw.githubusercontent.com/google/antigravity/main/README.md"
]

class GuruWatch:
    def __init__(self):
        self.memory = MemoryService()
        self.insights_path = Path("docs/architecture_insights.md")

    def fetch_latest_insights(self):
        print("🕵️ [Guru-Watch] Buscando novedades de los Gurus...")
        all_insights = []
        for url in GURU_SOURCES:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Extraer solo la parte de arquitectura/principios (simulado)
                    content = response.text[:2000] # Tomar un fragmento para procesar
                    all_insights.append(f"Source: {url}\nContent: {content}")
            except Exception as e:
                print(f"⚠️ Error al conectar con {url}: {e}")
        
        return "\n\n---\n\n".join(all_insights)

    def update_bible(self, new_data: str):
        # Aquí Jarvis/Swarm procesaría el data para extraer principios reales
        # Por ahora, registramos la actividad en la SGA
        print("🧠 [Guru-Watch] Indexando nuevos insights en la SGA L1...")
        self.memory.push_memory(
            project_id="SYSTEM_CORE",
            phase="GURU_WATCH",
            content=f"Insights actualizados el {datetime.now().isoformat()}.\n{new_data}",
            metadata={"type": "architectural_update"}
        )

if __name__ == "__main__":
    watcher = GuruWatch()
    data = watcher.fetch_latest_insights()
    if data:
        watcher.update_bible(data)
        print("✨ [Guru-Watch] Protocolo completado exitosamente.")
