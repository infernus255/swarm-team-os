from __future__ import annotations

from typing import Dict, Any


class M0Bootstrapper:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.system_instruction = (
            "Eres el agente M0 (Foundation / Bootstrapper) de Antigravity Swarm.\n"
            "Tu tarea es entrevistar al usuario, clarificar el alcance del proyecto y redactar "
            "los archivos PROJECT_MANIFEST.md y BOARD.md en app_result/.\n"
            "Al finalizar tu entregable, debes incluir de forma obligatoria un bloque delimitado "
            "con el título '### Key Decisions' resumiendo las decisiones tomadas."
        )

    def run(self, prompt: str, history: list) -> Dict[str, Any]:
        """Ejecuta el agente utilizando las instrucciones del sistema."""
        # En la implementación real:
        # client = genai.Client()
        # response = client.models.generate_content(
        #     model=self.model_name,
        #     contents=prompt,
        #     config=types.GenerateContentConfig(system_instruction=self.system_instruction)
        # )
        return {
            "agent": "M0",
            "model_used": self.model_name,
            "output_manifest": "# Project Manifest\n\n- **Project:** Antigravity Agentic App\n- **Goal:** Built with Google Antigravity SDK\n\n### Key Decisions\n- Decisión 1: Estructurar agentes en app_result/src/agents/.\n- Decisión 2: Usar Pydantic para tipado de tools."
        }
