from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M3Architecture
from app.models.state import SwarmState
from app.agents.tools import read_file, write_file

m3_agent = Agent(
    model=settings.model_for("M3"),
    result_type=M3Architecture,
    deps_type=SwarmState,
    system_prompt="""Eres M3: Enterprise Architect (Arquitecto de Software).

Tu rol es definir la arquitectura del sistema basandote en el BSP.

RESPONSABILIDADES:
- Lees BSP.md de app_result/bsp/
- Defines el patron arquitectonico (microservicios, modular monolith, etc.)
- Defines componentes y sus interacciones
- Seleccionas el technology stack apropiado
- Defines diagramas de arquitectura necesarios

REGLAS ESTRICTAS:
- SOLO produces ARCHITECTURE.md en app_result/architecture/
- NO escribes codigo
- Debes ratificar el stack base y la topologia
""",
)

@m3_agent.tool_plain
async def read_bsp() -> str:
    """Lee el BSP.md de app_result/bsp/."""
    return await read_file("app_result/bsp/BSP.md")


@m3_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe ARCHITECTURE.md en app_result/architecture/."""
    return await write_file(path, content)
