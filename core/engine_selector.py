import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from memory.sga_client import sga_client

from core.providers.llm import llm_provider

class EngineSelector:
    """Selects and executes the best Swarm engine for a given task."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.engines_dir = self.repo_root / "swarm" / "engines"

    async def select_engine(self, prompt: str) -> str:
        """Selects engine folder name based on intelligent classification."""
        print("🧠 [Engine Selector]: Classifying task with Tier 1 LLM...")
        classification = await llm_provider.classify_task(prompt)
        
        engine_name = classification.get("selected_engine")
        reason = classification.get("reason", "No reason provided.")
        complexity = classification.get("complexity", "medium")
        
        print(f"🎯 [Engine Selector]: Selected {engine_name} (Complexity: {complexity})")
        print(f"📝 [Engine Selector]: Reason: {reason}")

        # Validation: check if the folder exists
        if engine_name and (self.engines_dir / engine_name).exists():
            return engine_name

        # Fallback to keyword matching if LLM failed or suggested non-existent engine
        print("⚠️ [Engine Selector]: Intelligent classification failed or engine not found. Falling back to keyword matching.")
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["antigravity", "gemini sdk", "google sdk", "google-antigravity"]):
            return ".swarm_antigravity_sdk"
        elif any(k in prompt_lower for k in ["fastapi", "pydantic", "pydanticai", "pydantic-ai"]):
            return ".swarm_pydantic_fast"
        elif any(k in prompt_lower for k in ["copilot", "github copilot", "vs code", "vscode"]):
            return ".swarm_copilot"
        
        # HITL Fallback Selection
        if sys.stdin.isatty():
            print("\n🤖 [Engine Selector] No clear engine match found in prompt.")
            print("Please select an engine from the list below:")
            print("1. Google Antigravity SDK Swarm (.swarm_antigravity_sdk) [Default]")
            print("2. FastAPI + PydanticAI Swarm (.swarm_pydantic_fast)")
            print("3. VS Code Copilot Instructions (.swarm_copilot)")
            print("4. Baseline Swarm Template (.swarm_template)")
            
            try:
                choice = input("Enter selection (1-4, default 1): ").strip()
            except Exception:
                choice = "1"
                
            if choice == "2":
                return ".swarm_pydantic_fast"
            elif choice == "3":
                return ".swarm_copilot"
            elif choice == "4":
                return ".swarm_template"
            else:
                return ".swarm_antigravity_sdk"
        else:
            print("\n🤖 [Engine Selector] Non-interactive session, defaulting to Google Antigravity SDK Swarm (.swarm_antigravity_sdk)")
            return ".swarm_antigravity_sdk"

    async def execute_engine(self, engine_name: str, prompt: str) -> Dict[str, Any]:
        """Executes the selected engine subprocess, passing application_requirement_prompt.md."""
        engine_path = self.engines_dir / engine_name
        
        # 1. Write the application requirement prompt in app_result
        requirement_file = self.repo_root / "app_result" / "application_requirement_prompt.md"
        requirement_file.parent.mkdir(parents=True, exist_ok=True)
        requirement_file.write_text(f"# Application Requirement\n\n{prompt}\n", encoding="utf-8")
        print(f"[*] Prompt written to {requirement_file.relative_to(self.repo_root)}")

        # 2. Check if .swarm_copilot is selected
        if engine_name == ".swarm_copilot":
            src_github = engine_path / ".github"
            dest_github = self.repo_root / ".github"
            if src_github.exists():
                print(f"📂 [Copilot]: Copying instructions to {dest_github}")
                if dest_github.exists():
                    shutil.rmtree(dest_github)
                shutil.copytree(src_github, dest_github)
                return {
                    "status": "SUCCESS",
                    "details": "VS Code Copilot agent instructions copied to .github/ folder.",
                    "project_id": "copilot_setup"
                }
            else:
                return {
                    "status": "ERROR",
                    "details": f"Source .github directory not found in {engine_path}"
                }

        # 3. Setup subprocess environment
        from core.config import settings
        env = os.environ.copy()
        # Set project root env vars so engine knows where to output app_result
        env["SWARM_PROJECT_ROOT"] = str(self.repo_root)
        env["SWARN_PROJECT_ROOT"] = str(self.repo_root)
        
        # Inject Model Tiers
        env["TIER1_MODEL"] = settings.model_tier1
        env["TIER2_MODEL"] = settings.model_tier2
        env["TIER3_MODEL"] = settings.model_tier3
        
        # Set PYTHONPATH so absolute app/ imports work inside subprocesses
        env["PYTHONPATH"] = str(engine_path) + os.pathsep + env.get("PYTHONPATH", "")

        # SGA dynamic memory synchronization
        try:
            print("🔄 [Engine Selector]: Synchronizing latest L1 memories from SGA...")
            latest_memories = sga_client.query_global_memory(query="development", limit=10)
            if latest_memories and latest_memories != "No global memory context available.":
                # Choose the appropriate path structure depending on the engine
                if (engine_path / "swarn_templates").exists():
                    fp = engine_path / "swarn_templates" / "memory" / "SHARED_FOUNDATIONS.md"
                else:
                    fp = engine_path / ".swarn" / "memory" / "SHARED_FOUNDATIONS.md"
                
                fp.parent.mkdir(parents=True, exist_ok=True)
                header = "# SHARED FOUNDATIONS (Synced from SGA)\n\n"
                fp.write_text(header + latest_memories, encoding="utf-8")
                print(f"✅ [Engine Selector]: Synced SGA memories to {fp.relative_to(self.repo_root)}")
        except Exception as e:
            print(f"⚠️ [Engine Selector]: SGA memory sync skipped: {e}")

        # 4. Resolve run commands
        try:
            if engine_name == ".swarm_template":
                return {
                    "status": "ERROR",
                    "details": "The baseline .swarm_template is a non-executable blueprint containing specs and prompts. Falling back to core GraphRunner."
                }
            elif engine_name == ".swarm_antigravity_sdk":
                script_path = str(engine_path / "app" / "main.py")
                init_cmd = ["python", script_path, "init", "--prompt", prompt, "--mode", "auto"]
                run_cmd = ["python", script_path, "run", "all", "--prompt", prompt]
                
            elif engine_name == ".swarm_pydantic_fast":
                script_path = str(engine_path / "app" / "cli" / "commands.py")
                init_cmd = ["python", script_path, "init", "--prompt", prompt, "--mode", "greenfield"]
                run_cmd = ["python", script_path, "run"]
            else:
                return {
                    "status": "ERROR",
                    "details": f"Subprocess execution not defined for engine: {engine_name}"
                }

            print(f"🏃 [Engine Selector]: Running init: {' '.join(init_cmd)}")
            proc_init = subprocess.run(init_cmd, capture_output=True, text=True, env=env, cwd=str(self.repo_root))
            if proc_init.returncode != 0:
                print(f"❌ [Engine Selector] Init command failed:\nSTDOUT:\n{proc_init.stdout}\nSTDERR:\n{proc_init.stderr}")
                return {"status": "ERROR", "details": f"Initialization command failed: {proc_init.stderr}"}

            print(f"🏃 [Engine Selector]: Running run: {' '.join(run_cmd)}")
            proc_run = subprocess.run(run_cmd, capture_output=True, text=True, env=env, cwd=str(self.repo_root))
            if proc_run.returncode != 0:
                print(f"❌ [Engine Selector] Run command failed:\nSTDOUT:\n{proc_run.stdout}\nSTDERR:\n{proc_run.stderr}")
                return {"status": "ERROR", "details": f"Run command failed: {proc_run.stderr}"}

            print(f"✅ [Engine Selector]: Execution completed successfully.")

            # 5. Extract project_id from states
            project_id = "swarm_project"
            state_paths = [
                self.repo_root / ".swarn" / "states" / "swarm_state.json",
                self.repo_root / "swarn_templates" / "states" / "swarm_state.json",
                self.repo_root / "app_result" / ".swarn" / "states" / "swarm_state.json"
            ]
            for sp in state_paths:
                if sp.exists():
                    try:
                        state_data = json.loads(sp.read_text(encoding="utf-8"))
                        if "project_id" in state_data:
                            project_id = state_data["project_id"]
                            break
                    except Exception:
                        pass

            # 6. Read L1 memory (app_result/MEMORY.md) and push to SGA
            memory_file = self.repo_root / "app_result" / "MEMORY.md"
            if memory_file.exists():
                try:
                    memory_content = memory_file.read_text(encoding="utf-8")
                    print(f"🧠 [SGA]: Uploading L1 Memory for {project_id}...")
                    sga_client.push_memory(
                        project_id=project_id,
                        phase="SWARM_COMPLETE",
                        content=memory_content,
                        metadata={"engine": engine_name, "prompt": prompt}
                    )
                except Exception as e:
                    print(f"⚠️ [SGA]: Failed to write L1 memory: {e}")

            return {
                "status": "SUCCESS",
                "project_id": project_id,
                "engine": engine_name,
                "stdout": proc_run.stdout
            }

        except Exception as e:
            print(f"❌ [Engine Selector] Unexpected exception: {e}")
            return {"status": "ERROR", "details": str(e)}
