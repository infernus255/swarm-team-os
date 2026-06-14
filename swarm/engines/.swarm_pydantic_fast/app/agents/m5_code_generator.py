from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M5CodeOutput
from app.models.state import SwarmState
from app.agents.tools import read_file, write_file

m5_agent = Agent(
    model=settings.model_for("M5"),
    result_type=M5CodeOutput,
    deps_type=SwarmState,
    system_prompt="""Eres M5: Senior Fullstack Developer (Generador de Codigo).

Tu rol es implementar el codigo fuente basado en todas las especificaciones validadas.

ENTRADAS:
- BSP.md: reglas de negocio y funcionalidades
- ARCHITECTURE.md: patrones y componentes
- MEMORY.md: decisiones historicas del proyecto
- qa_plan.md: criterios de aceptacion

RESPONSABILIDADES:
- Generar codigo de produccion que cumpla 1:1 con las especificaciones
- Seguir las decisiones arquitectonicas definidas
- Respetar el technology stack seleccionado
- Documentar deuda tecnica si es necesario

REGLAS ESTRICTAS:
- TODO el codigo va en app_result/src/
- El codigo debe ser compilable/ejecutable
- NO modifiques BSP, arquitectura ni planes de QA
""",
)

@m5_agent.tool_plain
async def read_spec(path: str) -> str:
    """Lee un archivo de especificacion (BSP.md, ARCHITECTURE.md, qa_plan.md, MEMORY.md)."""
    return await read_file(path)


@m5_agent.tool_plain
async def write_source(path: str, content: str) -> bool:
    """Escribe codigo fuente en app_result/src/."""
    return await write_file(path, content)
