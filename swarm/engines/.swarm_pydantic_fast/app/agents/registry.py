from __future__ import annotations

from typing import Dict, Optional

from pydantic_ai import Agent

from app.models.results import AgentResult


_AGENT_REGISTRY: Dict[str, Agent] = {}


def register(slug: str, agent: Agent) -> None:
    _AGENT_REGISTRY[slug] = agent


def get_agent(slug: str) -> Optional[Agent]:
    return _AGENT_REGISTRY.get(slug)


def list_agents() -> Dict[str, str]:
    return {slug: str(type(a).__name__) for slug, a in _AGENT_REGISTRY.items()}


def build_all_agents() -> None:
    from app.agents.m0_bootstrapper import m0_agent
    from app.agents.m1_system_analyst import m1_agent
    from app.agents.m2_business_analyst import m2_agent
    from app.agents.m3_architect import m3_agent
    from app.agents.m4_qa_engineer import m4_agent
    from app.agents.m5_code_generator import m5_agent
    from app.agents.m6_devops import m6_agent

    register("M0", m0_agent)
    register("M1", m1_agent)
    register("M2", m2_agent)
    register("M3", m3_agent)
    register("M4", m4_agent)
    register("M5", m5_agent)
    register("M6", m6_agent)
