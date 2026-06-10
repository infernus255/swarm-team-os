from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Literal, TypedDict
from pydantic import BaseModel, Field

# --- Enums de Orquestación ---

class Phase(str, Enum):
    M0_FOUNDATION = "M0_FOUNDATION"
    M1_TDP = "M1_TDP"
    M2_BSP = "M2_BSP"
    M3_ARCHITECTURE = "M3_ARCHITECTURE"
    M4_QA = "M4_QA"
    M5_CODE = "M5_CODE"
    M6_DEVOPS = "M6_DEVOPS"
    COMPLETED = "COMPLETED"

class Status(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"
    REJECTED = "REJECTED"

# --- Contratos de Agentes ---

class AgentContract(BaseModel):
    agent_id: str
    name: str
    role: str
    input_sources: List[str] = Field(default_factory=list)
    output_paths: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)

# --- Estado del Grafo (Pydantic para Persistencia) ---

class Transition(BaseModel):
    from_phase: Optional[str] = Field(None, alias="from")
    to: str
    timestamp: str
    status: Status = Status.PENDING

class SwarmError(BaseModel):
    phase: str
    message: str
    timestamp: str

class SwarmState(BaseModel):
    project_id: str = ""
    current_phase: Phase = Phase.M0_FOUNDATION
    status: Status = Status.PENDING
    user_prompt: str = ""
    project_goal: str = ""
    history: List[Transition] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    pending_human_review: Dict[str, Any] = Field(default_factory=dict)
    errors_encountered: List[SwarmError] = Field(default_factory=list)
    final_product: Dict[str, Any] = Field(default_factory=dict)
    currentNode: str = "M0"
    workflow_mode: str = "greenfield"  # greenfield | brownfield

# --- Estado del Grafo (TypedDict para el Engine de Grafo) ---

class GraphState(TypedDict):
    project_id: str
    current_phase: Phase
    status: Status
    user_prompt: str
    project_goal: str
    history: List[dict]
    artifacts: Dict[str, str]
    pending_human_review: Dict[str, bool]
    errors_encountered: List[dict]
    currentNode: str
    workflow_mode: Literal["greenfield", "brownfield"]
    iteration_count: int
