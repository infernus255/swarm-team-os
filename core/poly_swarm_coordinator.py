import asyncio
from typing import Dict, Any, List
from pathlib import Path
from core.providers.llm import llm_provider
from core.engine_selector import EngineSelector
from core.services.memory_service import MemoryService
import time

class PolySwarmCoordinator:
    """
    Orchestrates complex tasks across multiple specialized Swarm engines.
    Phase 3: Poly-Swarm Orchestration (Multi-Node).
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.engine_selector = EngineSelector(repo_root)
        self.memory = MemoryService()

    async def execute_task(self, prompt: str) -> Dict[str, Any]:
        """
        Takes a complex prompt, breaks it down into sub-tasks (if necessary),
        and dispatches them to one or more engines.
        """
        print(f"\n🌐 [Poly-Swarm] Coordinating task: {prompt[:50]}...")
        start_time = time.time()

        # 1. Analyze and classify the overarching task
        classification = await llm_provider.classify_task(prompt)
        complexity = classification.get("complexity", "medium")
        
        results = []
        diagnostics = {}

        if complexity == "high":
            # For complex tasks, we could split it here. 
            # For Phase 3 MVP, we run the primary engine, then we could run a secondary QA/Review engine.
            # Currently just running the primary selected engine as a baseline.
            print("🌐 [Poly-Swarm] High complexity detected. Dispatching to primary specialized engine.")
            result = await self.engine_selector.execute_engine(classification, prompt)
            results.append(result)
            
            # Simulated secondary execution (e.g., if we had a dedicated review engine)
            # print("🌐 [Poly-Swarm] Dispatching to secondary QA engine (placeholder)...")
        else:
            print("🌐 [Poly-Swarm] Medium/Low complexity. Dispatching to single engine.")
            result = await self.engine_selector.execute_engine(classification, prompt)
            results.append(result)

        end_time = time.time()
        
        # 2. Synthesize results
        final_status = "SUCCESS" if all(r.get("status") == "SUCCESS" for r in results) else "ERROR"
        
        # 3. Store high-level orchestration memory
        if final_status == "SUCCESS":
             project_id = results[0].get("project_id", "poly_swarm_task")
             self.memory.push_memory(
                 project_id=project_id,
                 phase="POLY_SWARM_ORCHESTRATION",
                 content=f"Poly-Swarm coordinated task '{prompt}'. Complexity: {complexity}. Engines used: {classification.get('selected_engine')}. Duration: {end_time - start_time:.2f}s",
                 metadata={"domain": "swarm", "engines": [classification.get("selected_engine")]}
             )

        return {
            "status": final_status,
            "poly_swarm_results": results,
            "duration": end_time - start_time
        }
