import os
import requests
from typing import Any, Dict, Optional

class SGAClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("SGA_URL", "http://sga:8000")

    def push_memory(self, project_id: str, phase: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Pushes a memory entry (decision or summary) to the SGA service."""
        payload = {
            "project_id": project_id,
            "phase": phase,
            "content": content,
            "metadata": metadata or {},
            "type": "agent_decision"
        }
        try:
            response = requests.post(f"{self.base_url}/memory", json=payload, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[SGA] Error pushing memory: {e}")
            return False

    def query_global_memory(self, query: str, limit: int = 5) -> str:
        """Queries the SGA for global foundations or similar project decisions."""
        try:
            response = requests.get(f"{self.base_url}/query", params={"q": query, "limit": limit}, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Assuming SGA returns a list of matching entries
            memories = data.get("results", [])
            return "\n\n".join([m.get("content", "") for m in memories])
        except Exception as e:
            print(f"[SGA] Error querying memory: {e}")
            return "No global memory context available."

sga_client = SGAClient()
