from __future__ import annotations

import uuid
import json
import subprocess
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.models import Phase, Status, SwarmState, GraphState
from core.graph import analyst_node, bsp_node, coder_node, qa_node, devops_node
from core.services.memory_service import MemoryService

class GraphRunner:
    def __init__(self, state: Optional[GraphState] = None, memory_service: Optional[MemoryService] = None):
        self.state = state or self._init_state()
        self.memory = memory_service or MemoryService()

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
        
        print(f"🚀 [Orchestrator] Iniciando SwarmTeam OS para: {self.state['project_id']}")
        
        nodes: Dict[str, Callable] = {
            "M0": analyst_node,
            "M2": bsp_node,
            "M5": coder_node,
            "M4": qa_node,
            "M6": devops_node
        }

        current = "M0"
        
        while current != "END" and self.state["status"] != Status.REJECTED:
            self.state["currentNode"] = current
            self.state["status"] = Status.RUNNING
            
            node_func = nodes.get(current)
            if not node_func:
                break
                
            # --- SNAPSHOT BEFORE ACTION ---
            snapshot_msg = f"Snapshot before {current} for {self.state['project_id']}"
            self._take_snapshot(snapshot_msg)

            try:
                self.state = await node_func(self.state)
                self._log_transition(current)
                
                # PERSIST TO SGA
                self.memory.push_memory(
                    project_id=self.state["project_id"],
                    phase=current,
                    content=f"Phase {current} completed successfully.",
                    metadata={"artifacts": self.state["artifacts"]}
                )

            except Exception as e:
                print(f"❌ [Rollback]: Fallo en {current}. Revirtiendo cambios...")
                self._rollback()
                self.state["errors_encountered"].append({"node": current, "error": str(e)})
                self.state["status"] = Status.ERROR
                self.memory.push_memory(
                    project_id=self.state["project_id"],
                    phase=current,
                    content=f"Phase {current} failed: {str(e)}",
                    metadata={"error": True}
                )
                break

            # Routing Logic
            if current == "M0": current = "M2"
            elif current == "M2": current = "M5"
            elif current == "M5": current = "M4"
            elif current == "M4":
                from core.graph import qa_check_edge
                next_node = qa_check_edge(self.state)
                if next_node == "M6": current = "M6"
                elif next_node == "M5": current = "M5"
                else: current = "END"
            elif current == "M6": current = "END"

        print(f"✅ [Orchestrator] Proceso Finalizado. Estado Final: {self.state['status']}")
        return self.state

    def _log_transition(self, node_id: str):
        self.state["history"].append({
            "node": node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": self.state["status"]
        })

    def _take_snapshot(self, message: str):
        try:
            status = subprocess.check_output(["git", "status", "--porcelain"], text=True)
            if not status.strip():
                return

            subprocess.run(["git", "add", "."], capture_output=True)
            subprocess.run(["git", "commit", "-m", message], capture_output=True)
            print(f"📸 [Snapshot]: Phase state saved to Git.")
        except Exception:
            pass

    def _rollback(self):
        try:
            subprocess.run(["git", "reset", "--hard", "HEAD~1"], capture_output=True)
            print(f"⏪ [Rollback]: Restored to last stable phase.")
        except Exception:
            pass
