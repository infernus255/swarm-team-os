from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M1Tdp
from app.models.state import SwarmState
from app.agents.tools import file_exists, list_dir, read_file, write_file

m1_agent = Agent(
    model=settings.model_for("M1"),
    result_type=M1Tdp,
    deps_type=SwarmState,
    system_prompt="""Eres M1: System Analyst / Discovery (Analista de Sistemas).

Tu rol es analizar los requerimientos y producir el Technical Design Proposal (TDP).

MODO GREENFIELD:
- Lees PROJECT_MANIFEST.md de app_result/
- Defines el enfoque tecnico, decisiones de stack, restricciones y recomendaciones

MODO BROWNFIELD:
- Buscas codigo existente en app_legacy/ o old_src/
- Documentas el estado actual y produces el TDP

REGLAS ESTRICTAS:
- SOLO produces TDP.md en app_result/tdp/
- NO escribes codigo ni reglas de negocio
- Usa las tools para leer archivos de entrada y escribir tu output
""",
)

@m1_agent.tool_plain
async def read_artifact(path: str) -> str:
    """Lee un archivo del proyecto."""
    return await read_file(path)


@m1_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe el TDP en app_result/tdp/."""
    return await write_file(path, content)


@m1_agent.tool_plain
async def search_legacy(dir_path: str) -> str:
    """Lista archivos en un directorio legacy (app_legacy/ o old_src/)."""
    files = await list_dir(dir_path)
    return "\n".join(files) if files else "No legacy files found."
