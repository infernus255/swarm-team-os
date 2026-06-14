# SWARN — FastAPI + PydanticAI

Pipeline multi-agente secuencial (M0–M6) con orquestación tipada, contratos validables y soporte multi-modelo.

## Stack

- FastAPI — API REST + WebSocket
- PydanticAI — Agentes con outputs estructurados y tools tipadas
- Typer — CLI
- JSON — Persistencia de estado (compatible con swarm/engines/.swarm_template/)

## Arquitectura

M0 (Bootstrapper) → M1 (TDP) → M2 (BSP) → M3 (Arch) → M4 (QA) → M5 (Code) → M6 (DevOps)

## Endpoints API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | /swarm/init | Inicializa proyecto |
| GET | /swarm/state | Estado actual |
| POST | /swarm/transition | Transiciona al siguiente agente |
| POST | /swarm/agents/{id}/run | Ejecuta un agente |
| POST | /swarm/validate | Aprueba/rechaza paso (HITL) |
| GET | /swarm/history | Historial de transiciones |
| GET | /swarm/artifacts | Artefactos generados |
| WS | /swarm/ws | Tiempo real |

---

## 👥 Gobernanza: Humanos vs. Agentes

Para operar este framework con éxito, es fundamental distinguir el propósito y destinatario de cada archivo clave:

### Archivos para Humanos (Human-Facing)
*   **`README.md`:** Guía del programador para el stack de FastAPI y PydanticAI, y endpoints expuestos.
*   **`pyproject.toml` / `requirements.txt`:** Control de dependencias de Python y configuraciones locales del entorno.
*   **`app_result/docs/testing_guide.md`:** Guía de ejecución de pruebas para que la IA sepa cómo correr pytest.
*   **`implementation_plan.md` / `walkthrough.md` / `task.md`:** Reportes generados por la IA para control del desarrollador.

### Archivos para Agentes (Agent-Facing)
*   **`.clinerules`:** Reglas leídas automáticamente por el agente para asegurar SDD, tipado y evitar placeholders.
*   **`swarn_templates/states/swarm_state.json`:** Registro del estado actual de la máquina de estados.
*   **`app_result/MEMORY.md`:** Memoria histórica del proyecto indexada de forma trigger-driven.

