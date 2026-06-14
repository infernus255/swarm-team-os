from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M4QaPlan
from app.models.state import SwarmState
from app.agents.tools import read_file, write_file

m4_agent = Agent(
    model=settings.model_for("M4"),
    result_type=M4QaPlan,
    deps_type=SwarmState,
    system_prompt="""Eres M4: QA Engineer (Ingeniero de Calidad).

Tu rol es disenar el plan de pruebas basado en el BSP y la arquitectura.

RESPONSABILIDADES:
- Lees BSP.md y ARCHITECTURE.md
- Defines la estrategia de testing
- Creas casos de prueba basados en los criterios de aceptacion del BSP
- Defines metas de cobertura
- Seleccionas el framework de automatizacion

REGLAS ESTRICTAS:
- SOLO produces qa_plan.md en app_result/docs/ y specs en app_result/tests/specs/
- NO escribes codigo de produccion
- Los casos de prueba deben ser comprobables
""",
)

@m4_agent.tool_plain
async def read_bsp() -> str:
    """Lee el BSP.md de app_result/bsp/."""
    return await read_file("app_result/bsp/BSP.md")


@m4_agent.tool_plain
async def read_architecture() -> str:
    """Lee ARCHITECTURE.md de app_result/architecture/."""
    return await read_file("app_result/architecture/ARCHITECTURE.md")


@m4_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe planes de prueba en app_result/docs/ o app_result/tests/specs/."""
    return await write_file(path, content)
