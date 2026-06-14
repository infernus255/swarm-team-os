from __future__ import annotations

from pydantic_ai import Agent, RunContext

from app.config import settings
from app.models.results import M0Manifest
from app.models.state import SwarmState
from app.agents.tools import read_file, read_template, write_file

m0_agent = Agent(
    model=settings.model_for("M0"),
    result_type=M0Manifest,
    deps_type=SwarmState,
    system_prompt="""Eres M0: Foundation / Bootstrapper (Project Manager).

Tu rol es entrevistar al usuario y definir la base del proyecto.

RESPONSABILIDADES:
- Definir el nombre del proyecto (project_name)
- Definir el objetivo principal (project_goal)
- Listar los hitos iniciales (milestones)
- Crear epicas para el BOARD usando MoSCoW prioritization

REGLAS ESTRICTAS:
- SOLO produces el PROJECT_MANIFEST.md y BOARD.md en app_result/
- NO escribes codigo ni disenas arquitectura
- NO analizas requerimientos tecnicos
- Usa las tools disponibles para leer templates y escribir artefactos

OUTPUT:
Debes producir un M0Manifest con project_name, project_goal, milestones y epicas.
""",
)

@m0_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe contenido en un archivo en app_result/."""
    return await write_file(path, content)


@m0_agent.tool_plain
async def load_template(name: str) -> str:
    """Lee un template de swarn_templates/specs/. Ej: BOARD.md, PROJECT_MANIFEST.md"""
    return await read_template(name)
