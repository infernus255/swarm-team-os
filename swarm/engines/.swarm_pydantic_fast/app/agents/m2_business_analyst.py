from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M2Bsp
from app.models.state import SwarmState
from app.agents.tools import read_file, write_file

m2_agent = Agent(
    model=settings.model_for("M2"),
    result_type=M2Bsp,
    deps_type=SwarmState,
    system_prompt="""Eres M2: Business Analyst / BSP (Analista de Negocio).

Tu rol es transformar el TDP en un Business Specification Document (BSP).

RESPONSABILIDADES:
- Lees TDP.md de app_result/tdp/
- Defines reglas de negocio claras
- Listas funcionalidades con criterios de aceptacion
- Defines hitos de negocio

REGLAS ESTRICTAS:
- SOLO produces BSP.md en app_result/bsp/
- CERO codigo. CERO arquitectura tecnica.
- Las reglas de negocio deben ser claras y validables.
""",
)

@m2_agent.tool_plain
async def read_tdp() -> str:
    """Lee el TDP.md de app_result/tdp/."""
    return await read_file("app_result/tdp/TDP.md")


@m2_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe el BSP en app_result/bsp/."""
    return await write_file(path, content)
