from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class M0Manifest(BaseModel):
    project_name: str
    project_goal: str
    milestones: List[str] = Field(default_factory=list)
    board_epics: List[Dict[str, Any]] = Field(default_factory=list)


class M1Tdp(BaseModel):
    technical_approach: str
    stack_decisions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class M2Bsp(BaseModel):
    business_rules: List[str] = Field(default_factory=list)
    features: List[Dict[str, Any]] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)


class M3Architecture(BaseModel):
    architecture_pattern: str
    components: List[Dict[str, Any]] = Field(default_factory=list)
    technology_stack: Dict[str, str] = Field(default_factory=dict)
    diagrams: List[str] = Field(default_factory=list)


class M4QaPlan(BaseModel):
    testing_strategy: str
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    coverage_goals: Dict[str, float] = Field(default_factory=dict)
    automation_framework: str = ""


class M5CodeOutput(BaseModel):
    files_created: List[str] = Field(default_factory=list)
    summary: str = ""
    tech_debt_notes: List[str] = Field(default_factory=list)


class M6DeployOutput(BaseModel):
    dockerfile_path: Optional[str] = None
    pipeline_files: List[str] = Field(default_factory=list)
    infrastructure_as_code: List[str] = Field(default_factory=list)
    deployment_notes: str = ""


AgentResult = (
    M0Manifest
    | M1Tdp
    | M2Bsp
    | M3Architecture
    | M4QaPlan
    | M5CodeOutput
    | M6DeployOutput
)
