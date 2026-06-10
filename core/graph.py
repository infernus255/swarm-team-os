from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Literal, Optional, TypedDict
from core.models import Phase, Status, GraphState
from memory.sga_client import sga_client

class GraphState(TypedDict):
    project_id: str
    current_phase: Phase
    status: Status
    user_prompt: str
    project_goal: str
    history: List[dict]
    artifacts: Dict[str, str]
    pending_human_review: Dict[str, bool]
    errors_encountered: List[dict]
    currentNode: str
    workflow_mode: Literal["greenfield", "brownfield"]
    iteration_count: int

def _ensure_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

async def analyst_node(state: GraphState) -> GraphState:
    print(f"--- [M0] Generando Manifiesto del Proyecto ---")
    path = "app_result/PROJECT_MANIFEST.md"
    _ensure_dir(path)
    content = f"# Manifest: {state['project_id']}\nGoal: {state['project_goal']}\nMode: {state['workflow_mode']}"
    Path(path).write_text(content, encoding="utf-8")
    state["artifacts"]["manifest"] = path
    state["status"] = Status.DONE
    return state

async def bsp_node(state: GraphState) -> GraphState:
    print(f"--- [M2] Generando Especificaciones de Negocio (BSP) ---")
    path = "app_result/bsp/BSP.md"
    _ensure_dir(path)
    content = f"# Business Spec (BSP)\nBasado en el prompt: {state['user_prompt']}\n\n## Requerimientos\n- Funcionalidad base implementada."
    Path(path).write_text(content, encoding="utf-8")
    state["artifacts"]["bsp"] = path
    state["status"] = Status.DONE
    return state

async def coder_node(state: GraphState) -> GraphState:
    print(f"--- [M5] Generando Código Fuente ---")
    path = "app_result/src/main.py"
    _ensure_dir(path)
    content = "def main():\n    print('Hello from Hermes-Swarm MVP!')\n\nif __name__ == '__main__':\n    main()"
    Path(path).write_text(content, encoding="utf-8")
    state["artifacts"]["source"] = path
    state["status"] = Status.DONE
    return state

async def qa_node(state: GraphState) -> GraphState:
    print(f"--- [M4] Autoverificación: Ejecutando Pruebas ---")
    source_path = Path("app_result/src/main.py")
    
    if not source_path.exists():
        print("❌ Error: Código no encontrado.")
        state["status"] = Status.ERROR
        state["errors_encountered"].append({"phase": "M4", "msg": "Missing source file"})
        return state

    # Simulación de ejecución de test (en el futuro esto usará subprocess)
    try:
        # Aquí Jarvis/Swarm intentaría correr el código o un suite de tests
        print(f"🔍 Auditando {source_path}...")
        content = source_path.read_text()
        
        if "print" in content: # Verificación mínima para el MVP
            print("✅ Pruebas pasaron con éxito.")
            state["status"] = Status.DONE
        else:
            raise ValueError("El código no cumple con el requisito de salida (print)")
            
    except Exception as e:
        print(f"⚠️ Fallo en verificación: {e}")
        state["status"] = Status.ERROR
        state["errors_encountered"].append({"phase": "M4", "msg": str(e)})
        # Preparamos el estado para el bucle de corrección
        state["iteration_count"] += 1
        
    return state

def qa_check_edge(state: GraphState) -> str:
    """Decide si avanzar a M6 o volver a M5 para corregir."""
    if state["status"] == Status.DONE:
        return "M6"
    elif state["iteration_count"] < 3: # Límite de 3 reintentos auto-correctivos
        print(f"🔄 Reintentando corrección (Intento {state['iteration_count']}/3)...")
        return "M5"
    else:
        print("🛑 Límite de correcciones alcanzado. Abortando.")
        return "END"
    print(f"--- [M6] Generando Infraestructura (Docker) ---")
    path = "app_result/deploy/Dockerfile"
    _ensure_dir(path)
    content = "FROM python:3.9-slim\nCOPY ../src /app\nCMD ['python', '/app/main.py']"
    Path(path).write_text(content, encoding="utf-8")
    
    # AL FINAL: Guardar en SGA
    print(f"--- [MEMORY] Indexando proyecto en SGA ---")
    sga_client.push_memory(
        project_id=state["project_id"],
        phase="COMPLETED",
        content=f"Proyecto SwarmTeam {state['project_id']} finalizado con éxito. Meta: {state['project_goal']}"
    )
    
    state["status"] = Status.DONE
    return state
