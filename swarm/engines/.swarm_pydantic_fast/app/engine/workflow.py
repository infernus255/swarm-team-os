from __future__ import annotations

from typing import Dict, List, Optional

from app.models.state import Phase, Status

GREENFIELD_DAG: List[str] = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"]
BROWNFIELD_DAG: List[str] = ["M1", "M2", "M3", "M4", "M5", "M6"]

PHASE_MAP: Dict[str, Phase] = {
    "M0": Phase.M0_FOUNDATION,
    "M1": Phase.M1_TDP,
    "M2": Phase.M2_BSP,
    "M3": Phase.M3_ARCHITECTURE,
    "M4": Phase.M4_QA,
    "M5": Phase.M5_CODE,
    "M6": Phase.M6_DEVOPS,
}


def get_dag(mode: str) -> List[str]:
    if mode == "brownfield":
        return BROWNFIELD_DAG
    return GREENFIELD_DAG


def get_next_agent(current: str, mode: str) -> Optional[str]:
    dag = get_dag(mode)
    try:
        idx = dag.index(current)
        if idx + 1 < len(dag):
            return dag[idx + 1]
    except ValueError:
        pass
    return None


def get_previous_agent(current: str, mode: str) -> Optional[str]:
    dag = get_dag(mode)
    try:
        idx = dag.index(current)
        if idx > 0:
            return dag[idx - 1]
    except ValueError:
        pass
    return None


def phase_for_agent(agent_id: str) -> Optional[Phase]:
    return PHASE_MAP.get(agent_id)


def status_for_agent(state: "SwarmState", agent_id: str) -> Status:
    for t in reversed(state.history):
        if t.to == agent_id:
            return t.status
    return Status.PENDING if agent_id == "M0" else Status.PENDING
