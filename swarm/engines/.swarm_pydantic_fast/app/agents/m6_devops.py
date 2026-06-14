from __future__ import annotations

from pydantic_ai import Agent

from app.config import settings
from app.models.results import M6DeployOutput
from app.models.state import SwarmState
from app.agents.tools import list_dir, read_file, write_file

m6_agent = Agent(
    model=settings.model_for("M6"),
    result_type=M6DeployOutput,
    deps_type=SwarmState,
    system_prompt="""Eres M6: DevOps & Release Engineer.

Tu rol es preparar la infraestructura de despliegue.

RESPONSABILIDADES:
- Lees el codigo fuente de app_result/src/
- Creas Dockerfile para contenerizacion
- Creas pipelines CI/CD
- Defines infraestructura como codigo

REGLAS ESTRICTAS:
- SOLO produces artifacts en app_result/deploy/
- Infraestructura declarada de manera agnostica y funcional
- No modifiques el codigo fuente
""",
)

@m6_agent.tool_plain
async def list_source() -> str:
    """Lista los archivos en app_result/src/."""
    files = await list_dir("app_result/src")
    return "\n".join(files) if files else "No source files found."


@m6_agent.tool_plain
async def read_source(path: str) -> str:
    """Lee un archivo de app_result/src/."""
    return await read_file(path)


@m6_agent.tool_plain
async def write_artifact(path: str, content: str) -> bool:
    """Escribe artifacts de deploy en app_result/deploy/."""
    return await write_file(path, content)
