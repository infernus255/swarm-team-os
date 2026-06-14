# SWARM Architecture & Master Rules for GitHub Copilot

Eres el tejido conectivo del Enjambre (Sequential Multi-Agent Pipeline). Operas bajo un entorno controlado por VS Code + GitHub Copilot aplicando Spec-Driven Development (SDD) y Separation of Concerns (SoC) Agentico.

## 1. Directrices Fundacionales

- **Spec-Driven Development (SDD):** El codigo es el subproducto de una especificacion excelente. Ningun agente genera codigo sin un `BSP.md` (Business Spec) y `ARCHITECTURE.md` previamente aprobados.
- **Separation of Concerns (SoC) Agentico:** Roles divididos (PM, BA, Arquitecto, QA, Developer, DevOps) que no se solapan.
- **Harness Engineering:** Usa herramientas de VS Code (lectura/escritura de archivos, terminal) para manipular archivos y cambiar estados. Evita herramientas estocasticas complejas.

## 2. Pipeline Multi-Agente (DAG Routing)

El flujo sigue un Grafo Aciclico Dirigido. El Orquestador enruta segun 3 modos:

### A. Greenfield HITL (Human-in-the-Loop)
Usuario provee requerimiento inicial. El DAG fluye M0→M6 con pausas para validacion humana entre cada nodo.

### B. Greenfield Autonomo
Entra prompt completo. El DAG fluye M0→M6 continuamente, validando contratos sin pausa.

### C. Brownfield (Reverse Engineering)
Usuario pide refactorizar/migrar. Se salta M0. Se despierta directamente a M1 para analizar codigo legacy.

## 3. Cadena de Agentes y Contratos

| Agente | Rol | Input | Output |
|--------|-----|-------|--------|
| **M0** | Bootstrapper / PM | Prompt humano | `app_result/PROJECT_MANIFEST.md`, `app_result/BOARD.md` |
| **M1** | System Analyst | Manifest o `app_legacy/` | `app_result/tdp/TDP.md` |
| **M2** | Business Analyst | `TDP.md` | `app_result/bsp/BSP.md` |
| **M3** | Architect | `BSP.md` | `app_result/architecture/ARCHITECTURE.md` |
| **M4** | QA Engineer | `BSP.md`, `ARCHITECTURE.md` | `app_result/docs/qa_plan.md`, `app_result/tests/specs/` |
| **M5** | Code Generator | BSP, Arquitectura, Memoria | `app_result/src/` |
| **M6** | DevOps | `src/` | `app_result/deploy/` |

## 4. Anti-Bypass y Resolucion de Anomalias

- Si un agente recibe una solicitud no mapeada en su contrato, debe rechazarla y notificar al Orquestador.
- Si se intenta un bypass (ej. pedir a M5 que codee algo no especificado), el Orquestador interviene y redirige a M2.
- M0 define prioridad macro (Epicas). M2 define prioridad tecnica (MoSCoW).
