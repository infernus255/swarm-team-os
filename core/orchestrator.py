from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.models import Phase, Status, SwarmState, GraphState
from core.graph import GraphState, analyst_node, bsp_node, coder_node, qa_node, devops_node

class GraphRunner:
    def __init__(self, state: Optional[GraphState] = None):
        self.state = state or self._init_state()

    def _init_state(self) -> GraphState:
        return {
            "project_id": f"proj_{uuid.uuid4().hex[:8]}",
            "current_phase": Phase.M0_FOUNDATION,
            "status": Status.PENDING,
            "user_prompt": "",
            "project_goal": "",
            "history": [],
            "artifacts": {},
            "pending_human_review": {},
            "errors_encountered": [],
            "currentNode": "M0",
            "workflow_mode": "greenfield",
            "iteration_count": 0
        }

    async def run(self, initial_prompt: str):
        self.state["user_prompt"] = initial_prompt
        self.state["project_goal"] = initial_prompt
        
        print(f"🚀 Iniciando SwarmTeam OS para proyecto: {self.state['project_id']}")
        
        nodes: Dict[str, Callable] = {
            "M0": analyst_node,
            "M2": bsp_node,
            "M5": coder_node,
            "M4": qa_node,
            "M6": devops_node
        }

        # Flujo Dinámico basado en Grafo
        current = "M0"
        
        while current != "END" and self.state["status"] != Status.REJECTED:
            self.state["currentNode"] = current
            self.state["status"] = Status.RUNNING
            
            node_func = nodes.get(current)
            if not node_func:
                break
                
            self.state = await node_func(self.state)
            self._log_transition(current)

            # Lógica de Enrutamiento Dinámico (Edges)
            if current == "M0": current = "M2"
            elif current == "M2": current = "M5"
            elif current == "M5": current = "M4"
            elif current == "M4":
                from core.graph import qa_check_edge
                next_node = qa_check_edge(self.state)
                if next_node == "M6": current = "M6"
                elif next_node == "M5": current = "M5" # BUCLE DE CORRECCIÓN
                else: current = "END"
            elif current == "M6": current = "END"

        print(f"✅ Proceso Finalizado. Estado Final: {self.state['status']}")
        return self.state

    def _log_transition(self, node_id: str):
        self.state["history"].append({
            "node": node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": self.state["status"]
        })
