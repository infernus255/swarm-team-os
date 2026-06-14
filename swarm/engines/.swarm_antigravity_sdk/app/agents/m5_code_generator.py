from __future__ import annotations

from typing import Dict, Any


class M5CodeGenerator:
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model_name = model_name
        self.system_instruction = (
            "Eres el agente M5 (Code Generator) de Antigravity Swarm.\n"
            "Tu tarea es generar código de producción compilable en Python utilizando la librería "
            "google-antigravity para definir agentes, herramientas y flujos de ejecución.\n"
            "Reglas críticas:\n"
            "1. El código generado debe guardarse únicamente en app_result/src/.\n"
            "2. Debes respetar los contratos de BSP.md y ARCHITECTURE.md al 100% (cero spec-drift).\n"
            "3. No dejes placeholders, bloques vacíos o comentarios de 'TODO' sin implementar.\n"
            "4. Incluye un bloque '### Key Decisions' al final de tu salida detallando los detalles de tu implementación."
        )

    def run(self, prompt: str, bsp_content: str, architecture_content: str) -> Dict[str, Any]:
        """Ejecuta el agente utilizando las especificaciones de diseño."""
        # En la implementación real:
        # response = client.models.generate_content(...)
        return {
            "agent": "M5",
            "model_used": self.model_name,
            "output_code_files": [
                {
                    "path": "app_result/src/agents/assistant.py",
                    "content": "import google.antigravity as ag\n\n# Agente de ejemplo generado por M5\nassistant = ag.Agent(name='Assistant', prompt='You are a helpful assistant.')"
                }
            ],
            "key_decisions": "### Key Decisions\n- Decisión 1: Registro dinámico de herramientas mediante decoradores en src/tools/.\n- Decisión 2: Inicialización limpia del cliente Antigravity con control de excepciones."
        }
