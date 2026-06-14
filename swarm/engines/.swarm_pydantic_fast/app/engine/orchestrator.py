from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.engine.memory import memory
from app.engine.validator import validator
from app.engine.workflow import (
    get_dag,
    get_next_agent,
    get_previous_agent,
    phase_for_agent,
)
from app.models.state import Phase, Status, SwarmError, SwarmState, Transition


class SwarmOrchestrator:
    def __init__(self) -> None:
        self.state = SwarmState()
        self._load_state()

    # ── State Persistence ──────────────────────────────────────────

    def _state_path(self) -> Path:
        return settings.state_path

    def _load_state(self) -> None:
        path = self._state_path()
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.state = SwarmState(**raw)
        else:
            self.state = SwarmState(
                currentNode="M0",
                current_phase=Phase.M0_FOUNDATION,
                status=Status.PENDING,
                history=[],
            )
            self._save_state()

    def _save_state(self) -> None:
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            self.state.model_dump_json(indent=2, by_alias=True), encoding="utf-8"
        )

    # ── Initialization ─────────────────────────────────────────────

    def init_project(
        self,
        prompt: str = "",
        mode: str = "greenfield",
        project_name: str = "",
    ) -> SwarmState:
        dag = get_dag(mode)
        first = dag[0]
        self.state = SwarmState(
            project_id=project_name or f"proj_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            current_phase=phase_for_agent(first) or Phase.M0_FOUNDATION,
            status=Status.PENDING,
            user_prompt=prompt,
            project_goal=prompt,
            history=[],
            currentNode=first,
            workflow_mode=mode,
        )
        self._save_state()
        return self.state

    # ── Transitions ────────────────────────────────────────────────

    def transition(self, to_agent: Optional[str] = None) -> SwarmState:
        dag = get_dag(self.state.workflow_mode)
        target = to_agent or get_next_agent(self.state.currentNode, self.state.workflow_mode)
        if not target:
            self.state.status = Status.DONE
            self.state.current_phase = Phase.COMPLETED
            self._save_state()
            return self.state

        if target not in dag:
            raise ValueError(f"Invalid target agent: {target}. Allowed: {dag}")

        self.state.history.append(
            Transition(
                from_phase=self.state.currentNode,
                to=target,
                timestamp=datetime.now(timezone.utc).isoformat(),
                status=Status.PENDING,
            )
        )
        self.state.currentNode = target
        self.state.current_phase = phase_for_agent(target) or self.state.current_phase
        self.state.status = Status.PENDING
        self._save_state()
        return self.state

    # ── Agent Execution ────────────────────────────────────────────

    def _load_shared_foundations(self) -> str:
        """Carga el conocimiento global del swarm si existe."""
        foundations_path = Path(__file__).resolve().parent.parent.parent / "swarn_templates" / "memory" / "SHARED_FOUNDATIONS.md"
        if foundations_path.exists():
            return foundations_path.read_text(encoding="utf-8")
        return ""

    async def run_agent(self, agent_id: str, prompt: str = "") -> Dict[str, Any]:
        from app.agents.registry import get_agent

        self.state.status = Status.RUNNING
        self._save_state()

        agent = get_agent(agent_id)
        if agent is None:
            raise ValueError(f"Unknown agent: {agent_id}")

        memory_context = memory.get_recent()
        foundations = self._load_shared_foundations()

        # Construct a comprehensive prompt enclosing global learnings and local memories
        full_prompt = ""
        if foundations:
            full_prompt += f"--- GLOBAL SWARM LEARNINGS (SGA) ---\n{foundations}\n\n"
        full_prompt += f"--- LOCAL PROJECT MEMORIES ---\nProject Goal: {self.state.project_goal}\nRecent Memory:\n{memory_context}\n\n"
        full_prompt += f"--- CURRENT REQUIREMENT ---\n{prompt}"

        try:
            result = await agent.run(full_prompt, deps=self.state)

            self.state.status = Status.DONE
            val_result = validator.validate_artifacts(agent_id, self.state)
            if not val_result:
                self.state.errors_encountered.append(
                    SwarmError(
                        phase=agent_id,
                        message="; ".join(val_result.errors),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )

            if settings.is_hitl:
                self.state.pending_human_review[agent_id] = True

            self._save_state()
            return {"agent": agent_id, "result": result.data.model_dump(), "valid": bool(val_result)}

        except Exception as e:
            self.state.status = Status.ERROR
            self.state.errors_encountered.append(
                SwarmError(
                    phase=agent_id,
                    message=str(e),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            )
            self._save_state()
            raise

    # ── HITL Validation ────────────────────────────────────────────

    def validate_step(self, agent_id: str, approved: bool) -> SwarmState:
        if approved:
            self.state.pending_human_review.pop(agent_id, None)
            for t in reversed(self.state.history):
                if t.to == agent_id:
                    t.status = Status.DONE
                    break
            self.state.status = Status.DONE
        else:
            self.state.status = Status.REJECTED
            prev = get_previous_agent(agent_id, self.state.workflow_mode)
            if prev:
                self.state.currentNode = prev
                self.state.current_phase = phase_for_agent(prev) or self.state.current_phase

        self._save_state()
        return self.state

    # ── Queries ────────────────────────────────────────────────────

    def get_state(self) -> SwarmState:
        self._load_state()
        return self.state

    def get_history(self) -> List[Transition]:
        return self.state.history

    def get_artifacts(self) -> Dict[str, str]:
        return self.state.artifacts


orchestrator = SwarmOrchestrator()
