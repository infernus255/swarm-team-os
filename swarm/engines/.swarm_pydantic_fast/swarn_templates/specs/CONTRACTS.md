# Contratos de Agentes (I/O Specifications & Pathing)

**Directiva Principal:** `.swarm/` es el cerebro estático y normativo. `app_result/` es el lienzo de trabajo dinámico. Ningún agente (salvo el Orquestador o M0) modifica archivos fuera de sus outputs designados.

## M0: Foundation / Bootstrapper
- **Input:** Interacción humana o prompt inicial.
- **Output Requerido:** `app_result/PROJECT_MANIFEST.md` y `app_result/BOARD.md`.
- **Criterio de Éxito:** Se ha creado la estructura base y el alcance en `app_result/`.

## M1: System Analyst (Discovery & TDP)
- **Input (Greenfield):** `app_result/PROJECT_MANIFEST.md`.
- **Input (Brownfield):** `/app_legacy` o `/old_src`.
- **Output Requerido:** `app_result/tdp/TDP.md`.
- **Criterio de Éxito:** Documentación técnica inicial persistida en el directorio TDP.

## M2: Business Analyst (BSP)
- **Input:** `app_result/tdp/TDP.md`.
- **Output Requerido:** `app_result/bsp/BSP.md`.
- **Criterio de Éxito:** Reglas de negocio claras. El Orquestador puede extraer hitos para el BOARD.

## M3: Enterprise Architect (Assessment)
- **Input:** `app_result/bsp/BSP.md`.
- **Output Requerido:** `app_result/architecture/ARCHITECTURE.md`.
- **Criterio de Éxito:** Stack base (.NET Core / Next.js) ratificado, y topología definida.

## M4: QA Engineer
- **Input:** `app_result/bsp/BSP.md` y `app_result/architecture/ARCHITECTURE.md`.
- **Output Requerido:** `app_result/docs/qa_plan.md` y `app_result/tests/specs/`.
- **Criterio de Éxito:** Criterios de aceptación transformados en estrategias de testing comprobables.

## M5: Generador de Código
- **Input Primario:** Todo el material validado en `app_result/bsp/`, `app_result/architecture/` y contexto global en `app_result/MEMORY.md`.
- **Output Requerido:** Código compilable exclusivamente en `app_result/src/`.
- **Criterio de Éxito:** El código cumple 1:1 con las especificaciones.

## M6: DevOps & Release Engineer
- **Input:** `app_result/src/`.
- **Output Requerido:** Artefactos de despliegue en `app_result/deploy/` (ej. Dockerfiles, pipelines).
- **Criterio de Éxito:** Infraestructura declarada de manera agnóstica y funcional.