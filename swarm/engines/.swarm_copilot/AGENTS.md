# SWARM Agent Instructions for GitHub Copilot

Este proyecto utiliza un pipeline multi-agente secuencial (SWARM) con los siguientes agentes:

## Agentes del Pipeline

| @mention | Rol | Funcion |
|----------|-----|---------|
| `@orchestrator` | Gatekeeper | Gestiona el DAG, valida contratos, orquesta subagentes |
| `@m0-bootstrapper` | Project Manager | Define alcance y epicas del proyecto |
| `@m1-system-analyst` | System Analyst | Crea el Technical Design Proposal |
| `@m2-business-analyst` | Business Analyst | Define reglas de negocio y features |
| `@m3-architect` | Enterprise Architect | Disena la arquitectura y stack |
| `@m4-qa-engineer` | QA Engineer | Plan de pruebas y test specs |
| `@m5-code-generator` | Fullstack Developer | Genera codigo fuente |
| `@m6-devops` | DevOps Engineer | Prepara artefactos de despliegue |

## Flujo del Pipeline

```
M0 → M1 → M2 → M3 → M4 → M5 → M6
```

- **Greenfield:** Empieza en M0 (proyecto desde cero)
- **Brownfield:** Empieza en M1 (codigo legacy existente)

## Contratos

Cada agente escribe exclusivamente en `app_result/`:
- M0: `app_result/PROJECT_MANIFEST.md`, `app_result/BOARD.md`
- M1: `app_result/tdp/TDP.md`
- M2: `app_result/bsp/BSP.md`
- M3: `app_result/architecture/ARCHITECTURE.md`
- M4: `app_result/docs/qa_plan.md`, `app_result/tests/specs/`
- M5: `app_result/src/`
- M6: `app_result/deploy/`

Para comenzar, invoca a `@orchestrator` con tu requerimiento.
