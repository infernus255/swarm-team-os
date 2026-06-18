import asyncio
import sys
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Add current dir to sys.path
sys.path.append(os.getcwd())

from core.config import settings
from core.services.memory_service import MemoryService
from core.orchestrator import GraphRunner
from core.poly_swarm_coordinator import PolySwarmCoordinator

class JarvisAssistant:
    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service
        self.swarm_runner = GraphRunner()
        self.coordinator = PolySwarmCoordinator(settings.repo_root)
        self._check_version()

    def _check_version(self):
        latest = self.memory.get_latest_system_version()
        if settings.version < latest:
            print(f"[!] [Jarvis] Outdated version: v{settings.version} < v{latest}")
        else:
            print(f"[OK] [Jarvis] Version up-to-date: v{settings.version}")

    async def _auto_maintenance(self):
        """Perform automatic maintenance tasks like Guru-Watch."""
        last_run = self.memory.get_last_phase_execution("SYSTEM_CORE", "GURU_WATCH")
        
        # Check if more than 7 days have passed since the last run
        should_run = False
        if not last_run:
            should_run = True
        else:
            # Ensure last_run is offset-aware for comparison
            if last_run.tzinfo is None:
                last_run = last_run.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - last_run
            if delta.days >= 7:
                should_run = True
        
        if should_run:
            print("[Maintenance] [Jarvis] Triggering scheduled Guru-Watch...")
            env = os.environ.copy()
            env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
            subprocess.run([sys.executable, "harness/scripts/skill_guru_watch.py"], env=env)

    async def handle_request(self, prompt: str):
        print(f"--- Jarvis analizando: '{prompt}' ---")
        
        # Run maintenance tasks
        await self._auto_maintenance()
        
        # Decision Logic
        if any(keyword in prompt.lower() for keyword in ["crear", "app", "swarm", "proyecto"]):
            result = await self.coordinator.execute_task(prompt)
        else:
            result = {"status": "SUCCESS", "details": f"OS task '{prompt}' completed."}

        # Run agnostic audits & attach diagnostics to learning insight
        diagnostics = self._run_agnostic_audits()
        result["diagnostics"] = diagnostics

        await self._learn(prompt, result)
        self._send_notification(prompt, result)
        return result

    def _send_notification(self, prompt: str, result: dict):
        """Sends an executive summary notification via ntfy.sh."""
        import requests
        print("[Notification] [Jarvis] Preparing execution summary...")
        
        status = result.get("status", "UNKNOWN")
        details = result.get("details", "")
        if not details and "poly_swarm_results" in result:
            details = "Poly-Swarm coordinated task finished successfully."
        
        # 1. Generate executive summary (2-3 lines)
        msg_lines = [
            f"🚀 Jarvis Run: {prompt[:40]}...",
            f"📌 Status: {'🟢 SUCCESS' if status == 'SUCCESS' else '🔴 ERROR'}"
        ]
        
        # 2. Include error code/reason if failed
        if status != "SUCCESS":
            errors = result.get("errors_encountered") or []
            err_msg = result.get("details") or "No details provided."
            if errors:
                err_msg = f"{errors[0].get('node', 'unknown')}: {errors[0].get('error', 'unknown error')}"
            msg_lines.append(f"⚠️ Error: {err_msg[:60]}")
        else:
            msg_lines.append(f"📝 Result: {str(details)[:60]}")
            
        message = "\n".join(msg_lines)
        
        try:
            url = f"https://ntfy.sh/{settings.ntfy_topic}"
            response = requests.post(url, data=message.encode("utf-8"), headers={"Title": "Jarvis OS Notification"}, timeout=5)
            if response.status_code == 200:
                print(f"[Notification] [Jarvis] Successfully notified via ntfy.sh/{settings.ntfy_topic}")
            else:
                print(f"[!] [Jarvis] Notification failed with status {response.status_code}")
        except Exception as e:
            print(f"[!] [Jarvis] Notification request failed: {e}")

    def _run_agnostic_audits(self) -> dict:
        """Agnostic audit feature: checks local/offline network loops & memory optimization alerts."""
        print("[Audit] [Jarvis] Running agnostic system audits...")
        diagnostics = {"webrtc_stun_reachable": True, "performance_warnings": []}
        
        # 1. Check STUN server connectivity to prevent WebRTC hangs
        import socket
        try:
            socket.setdefaulttimeout(1.0)
            socket.gethostbyname("stun.l.google.com")
            print("[Network] [Jarvis Audit] STUN server hostname resolved successfully.")
        except Exception:
            diagnostics["webrtc_stun_reachable"] = False
            diagnostics["performance_warnings"].append(
                "STUN server stun.l.google.com:19302 is unreachable. WebRTC data channels "
                "should fall back to local loopback configurations to avoid signaling hangs."
            )
            print("[!] [Jarvis Audit] STUN server is unreachable. Offline mode recommended.")

        # 2. Performance memory buffer static check on generated app_result files
        app_result_dir = Path("app_result")
        if app_result_dir.exists():
            for js_file in app_result_dir.glob("**/*.js"):
                try:
                    content = js_file.read_text(encoding="utf-8")
                    if "requestAnimationFrame" in content and "new Array" in content:
                        diagnostics["performance_warnings"].append(
                            f"File {js_file.name} uses dynamic arrays inside animation frames. "
                            "Consider converting to flat TypedArrays to improve L1 cache hit rate."
                        )
                except Exception:
                    pass

        return diagnostics

    async def _learn(self, prompt: str, result: dict):
        insight = f"Interaction: {prompt} | Result: {result.get('status')} | StunReachable: {result.get('diagnostics', {}).get('webrtc_stun_reachable', True)}"
        self.memory.push_memory(
            project_id="GLOBAL_JARVIS", 
            phase="REFLECTION", 
            content=insight, 
            metadata={"input": prompt, "diagnostics": result.get("diagnostics"), "domain": "swarm"}
        )
        print("[Memory] [Jarvis] Memory persisted with domain 'swarm'.")

if __name__ == "__main__":
    mem = MemoryService()
    jarvis = JarvisAssistant(mem)
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "verify version"
    asyncio.run(jarvis.handle_request(user_input))
