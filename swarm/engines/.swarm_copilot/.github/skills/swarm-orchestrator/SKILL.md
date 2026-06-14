---
name: swarm-orchestrator
description: SWARM Orchestrator Skill - Pipeline multi-agente secuencial M0→M6 con Spec-Driven Development
---

# SWARM Orchestrator Skill

Este skill define el flujo de trabajo del pipeline multi-agente secuencial para GitHub Copilot en VS Code.

## Agentes Disponibles

- **@orchestrator**: Gatekeeper del DAG. Gestiona estados, valida contratos, invoca subagentes.
- **@m0-bootstrapper**: Project Manager. Define PROJECT_MANIFEST.md y BOARD.md.
- **@m1-system-analyst**: System Analyst. Crea el Technical Design Proposal (TDP.md).
- **@m2-business-analyst**: Business Analyst. Transforma TDP en BSP.md.
- **@m3-architect**: Enterprise Architect. Define stack y topologia en ARCHITECTURE.md.
- **@m4-qa-engineer**: QA Engineer. Genera plan de pruebas y test specs.
- **@m5-code-generator**: Senior Fullstack Developer. Genera codigo en app_result/src/.
- **@m6-devops**: DevOps Engineer. Genera artefactos de despliegue.

## Contratos I/O

Cada agente escribe exclusivamente en `app_result/`:
- M0 → `app_result/PROJECT_MANIFEST.md`, `app_result/BOARD.md`
- M1 → `app_result/tdp/TDP.md`
- M2 → `app_result/bsp/BSP.md`
- M3 → `app_result/architecture/ARCHITECTURE.md`
- M4 → `app_result/docs/qa_plan.md`, `app_result/tests/specs/`
- M5 → `app_result/src/`
- M6 → `app_result/deploy/`

## Workflows

### Greenfield (Desde Cero)
@orchestrator recibe prompt → @m0-bootstrapper → @m1-system-analyst → @m2-business-analyst → @m3-architect → @m4-qa-engineer → @m5-code-generator → @m6-devops

### Brownfield (Legacy)
@orchestrator recibe ruta legacy → SALTEA M0 → @m1-system-analyst analiza codigo → continua flujo normal desde M2
