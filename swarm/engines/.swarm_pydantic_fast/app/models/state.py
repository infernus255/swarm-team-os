from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
