from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from app.agents.registry import list_agents
from app.engine.orchestrator import orchestrator
from app.engine.workflow import get_dag
from app.models.contracts import CONTRACTS
from app.models.state import SwarmState, Transition

router = APIRouter(prefix="/swarm", tags=["swarm"])


@router.post("/init")
async def init_project(prompt: str = "", mode: str = "greenfield", name: str = "") -> SwarmState:
    return orchestrator.init_project(prompt=prompt, mode=mode, project_name=name)


@router.get("/state")
async def get_state() -> SwarmState:
    return orchestrator.get_state()


@router.post("/transition")
async def transition(to: Optional[str] = None) -> SwarmState:
    try:
        return orchestrator.transition(to_agent=to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str, prompt: str = "") -> Dict[str, Any]:
    valid_agents = list(CONTRACTS.keys())
    if agent_id not in valid_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not found. Valid: {valid_agents}",
        )
    try:
        return await orchestrator.run_agent(agent_id, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_step(agent_id: str, approved: bool = True) -> SwarmState:
    return orchestrator.validate_step(agent_id, approved)


@router.get("/history")
async def get_history() -> List[Transition]:
    return orchestrator.get_history()


@router.get("/artifacts")
async def get_artifacts() -> Dict[str, str]:
    return orchestrator.get_artifacts()


@router.get("/agents")
async def list_all_agents() -> Dict[str, Any]:
    return {
        "agents": list_agents(),
        "contracts": {k: v.model_dump() for k, v in CONTRACTS.items()},
        "dag": get_dag(orchestrator.state.workflow_mode),
    }
