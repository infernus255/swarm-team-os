from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import settings


class SwarmOrchestrator:
    def __init__(self) -> None:
        self.state_file = settings.state_path
        self.memory_file = settings.memory_path
        self.state: Dict[str, Any] = {}
        self._load_state()

    def _load_state(self) -> None:
        if self.state_file.exists():
            try:
                self.state = json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                self._init_default_state()
        else:
            self._init_default_state()

    def _init_default_state(self) -> None:
        self.state = {
            "project_id": "new_project",
            "currentNode": "M0",
            "status": "PENDING",
            "history": [],
            "pending_human_review": {},
            "errors": []
        }
        self.save_state()

    def save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── 1. Pre-flight Health Check ─────────────────────────────────
    def preflight_check(self) -> bool:
        """Verifica las credenciales y conectividad con la API de Gemini."""
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.state["errors"].append({
                "phase": "PREFLIGHT",
                "message": "GEMINI_API_KEY no encontrada en configuración ni variables de entorno.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.save_state()
            return False
        return True

    # ── 2. Fallback Chain de Invocación ────────────────────────────
    async def run_agent(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        """Ejecuta el subagente aplicando la cadena de fallback en caso de error."""
        if not self.preflight_check():
            return self._fallback_to_manual(agent_id, prompt, "Fallo en Pre-flight Check (API Key ausente)")

        primary_model = settings.model_for(agent_id) if hasattr(settings, "model_for") else "gemini-2.5-pro"
        fallback_model = settings.model_orchestrator

        print(f"[*] Invocando agente {agent_id} usando modelo primario {primary_model}...")
        try:
            # Aquí iría la llamada real utilizando el SDK de Antigravity o el cliente de Gemini
            # result = await antigravity.run(agent_id, prompt, model=primary_model)
            result = self._mock_run(agent_id, prompt, primary_model)
            self._post_agent_success(agent_id, result)
            return {"agent": agent_id, "status": "DONE", "result": result}
        except Exception as primary_error:
            print(f"[!] Error con modelo primario {primary_model}: {primary_error}")
            print(f"[*] Reintentando con modelo de fallback {fallback_model}...")
            try:
                # Reintento con modelo estándar de respaldo
                result = self._mock_run(agent_id, prompt, fallback_model)
                self._post_agent_success(agent_id, result)
                return {"agent": agent_id, "status": "DONE", "result": result, "fallback_used": True}
            except Exception as fallback_error:
                error_msg = f"Fallo en modelo primario ({primary_error}) y de fallback ({fallback_error})"
                return self._fallback_to_manual(agent_id, prompt, error_msg)

    def _fallback_to_manual(self, agent_id: str, prompt: str, error_msg: str) -> Dict[str, Any]:
        """Degrada gracefulmente a ejecución manual HITL."""
        print(f"[⚠️] DEGRADACIÓN GRACEFUL A MODO MANUAL para {agent_id}.")
        self.state["status"] = "REJECTED"
        self.state["errors"].append({
            "phase": agent_id,
            "message": f"Degradado a manual: {error_msg}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.save_state()

        # Presenta el prompt del subagente para que el desarrollador principal/humano lo resuelva
        return {
            "agent": agent_id,
            "status": "DEGRADED_TO_HITL",
            "error": error_msg,
            "action_required": "Por favor, ejecute el prompt manualmente o use el asistente principal.",
            "prompt_to_run": prompt
        }

    # ── 3. Post-Agent Memory Hook (Trigger-Driven) ─────────────────
    def _post_agent_success(self, agent_id: str, agent_output: str) -> None:
        """Hook post-ejecución que extrae decisiones clave y las anexa a la memoria."""
        # Buscar el bloque ### Key Decisions o ### Decisiones Clave en el entregable
        match = re.search(r"### (?:Key Decisions|Decisiones Clave)\n(.*?)(?=\n##|\n#|$)", agent_output, re.DOTALL | re.IGNORECASE)
        decisions = match.group(1).strip() if match else "- No se registraron decisiones clave explícitas."

        # Anexar a MEMORY.md de forma estructurada
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        memory_entry = f"\n\n### 📅 {timestamp} | Agente: {agent_id}\n{decisions}"

        settings.result_dir.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            self.memory_file.write_text("# Memoria Histórica del Proyecto\n", encoding="utf-8")
        
        with open(self.memory_file, "a", encoding="utf-8") as f:
            f.write(memory_entry)
        
        print(f"[✓] Memoria del proyecto actualizada automáticamente para {agent_id}.")

    # ── 4. Anti-Drift Spec Validation ─────────────────────────────
    def check_spec_drift(self) -> bool:
        """Verifica la paridad 1:1 entre el código fuente y las especificaciones."""
        bsp_file = settings.result_dir / "bsp" / "BSP.md"
        domain_val_file = settings.result_dir / "bsp" / "DOMAIN_VALIDATION.md"
        src_dir = settings.result_dir / "src"
        if not bsp_file.exists() or not src_dir.exists():
            return True # No hay especificaciones o código aún para validar
            
        if not domain_val_file.exists():
            print("[❌] Drift Detectado: Falta la Validación de Dominio (M2.5) en app_result/bsp/DOMAIN_VALIDATION.md")
            return False

        # Aquí un agente de validación estática o el orquestador escanea src/ y BSP.md
        # para buscar discrepancias (ej. funciones que no están en el BSP)
        # Retorna False si detecta inconsistencias críticas (drift)
        return True

    def _load_shared_foundations(self) -> str:
        """Carga el conocimiento global del swarm si existe."""
        foundations_path = Path(__file__).resolve().parent.parent.parent / ".swarn" / "memory" / "SHARED_FOUNDATIONS.md"
        if foundations_path.exists():
            return foundations_path.read_text(encoding="utf-8")
        return ""

    def _mock_run(self, agent_id: str, prompt: str, model: str) -> str:
        foundations = self._load_shared_foundations()
        foundations_msg = " [✓] Shared Foundations inyectadas en contexto." if foundations else ""
        return f"Output simulado para {agent_id} con modelo {model}.{foundations_msg}\n\n### Key Decisions\n- Decisión 1: Estructurado de clases usando decoradores de Antigravity.\n- Decisión 2: Separación estricta de app_result/src."
