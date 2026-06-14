from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class AgentContract(BaseModel):
    agent_id: str
    name: str
    role: str
    input_sources: List[str] = Field(default_factory=list)
    output_paths: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


CONTRACTS: Dict[str, AgentContract] = {
    "M0": AgentContract(
        agent_id="M0",
        name="Foundation / Bootstrapper",
        role="Project Manager. Entrevista al usuario y define el PROJECT_MANIFEST.md y BOARD.md.",
        input_sources=[],
        output_paths=["app_result/PROJECT_MANIFEST.md", "app_result/BOARD.md"],
        success_criteria=["Estructura base creada", "Alcance definido en app_result/"],
    ),
    "M1": AgentContract(
        agent_id="M1",
        name="System Analyst / Discovery",
        role="Analista de Sistemas. Crea el TDP.md desde el manifest o desde codigo legacy.",
        input_sources=["app_result/PROJECT_MANIFEST.md"],
        output_paths=["app_result/tdp/TDP.md"],
        success_criteria=["Documentacion tecnica inicial persistida en app_result/tdp/"],
    ),
    "M2": AgentContract(
        agent_id="M2",
        name="Business Analyst / BSP",
        role="Business Analyst. Transforma el TDP en BSP.md con reglas de negocio.",
        input_sources=["app_result/tdp/TDP.md"],
        output_paths=["app_result/bsp/BSP.md"],
        success_criteria=["Reglas de negocio claras", "Hitos extraibles para BOARD"],
    ),
    "M3": AgentContract(
        agent_id="M3",
        name="Enterprise Architect",
        role="Arquitecto de Software. Define stack y topologia en ARCHITECTURE.md.",
        input_sources=["app_result/bsp/BSP.md"],
        output_paths=["app_result/architecture/ARCHITECTURE.md"],
        success_criteria=["Stack base ratificado", "Topologia definida"],
    ),
    "M4": AgentContract(
        agent_id="M4",
        name="QA Engineer",
        role="Ingeniero de QA. Genera plan de pruebas y test specs.",
        input_sources=["app_result/bsp/BSP.md", "app_result/architecture/ARCHITECTURE.md"],
        output_paths=["app_result/docs/qa_plan.md", "app_result/tests/specs/"],
        success_criteria=["Criterios de aceptacion transformados en estrategias de testing"],
    ),
    "M5": AgentContract(
        agent_id="M5",
        name="Code Generator",
        role="Senior Fullstack Developer. Genera codigo fuente en app_result/src/.",
        input_sources=[
            "app_result/bsp/BSP.md",
            "app_result/architecture/ARCHITECTURE.md",
            "app_result/MEMORY.md",
        ],
        output_paths=["app_result/src/"],
        success_criteria=["Codigo compilable", "Cumple 1:1 con especificaciones"],
    ),
    "M6": AgentContract(
        agent_id="M6",
        name="DevOps & Release Engineer",
        role="DevOps Engineer. Genera Dockerfiles y pipelines CI/CD.",
        input_sources=["app_result/src/"],
        output_paths=["app_result/deploy/"],
        success_criteria=["Infraestructura declarada de manera agnostica y funcional"],
    ),
}
