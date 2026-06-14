# Contratos de Agentes — Google Antigravity SDK Swarm

**Directiva Principal:** `.swarm/` es el cerebro estático y normativo. `app_result/` es el lienzo de trabajo dinámico. Ningún agente (salvo el Orquestador o M0) modifica archivos fuera de sus outputs designados.
Todos los agentes de diseño (M0-M4) deben incluir un bloque delimitado `### Key Decisions` para alimentar el hook de actualización de memoria.

## M0: Foundation / Bootstrapper
- **Input:** Interacción humana o prompt inicial.
- **Output Requerido:** `app_result/PROJECT_MANIFEST.md` y `app_result/BOARD.md`.
- **Criterio de Éxito:** Se ha creado la estructura base y el alcance del sistema de agentes en `app_result/`.

## M1: System Analyst (Discovery & TDP)
- **Input (Greenfield):** `app_result/PROJECT_MANIFEST.md`.
- **Output Requerido:** `app_result/tdp/TDP.md`.
- **Criterio de Éxito:** TDP.md estructurando las entidades de negocio y la propuesta de arquitectura de agentes.

## M2: Business Analyst (BSP)
- **Input:** `app_result/tdp/TDP.md`.
- **Output Requerido:** `app_result/bsp/BSP.md`.
- **Criterio de Éxito:** Reglas de comportamiento, flujos lógicos y herramientas (*tools*) requeridas por los agentes especificadas al 100%.

## M3: Enterprise Architect (Assessment)
- **Input:** `app_result/bsp/BSP.md`.
- **Output Requerido:** `app_result/architecture/ARCHITECTURE.md`.
- **Criterio de Éxito:** Stack de agentes definido, asignando modelos de Gemini adecuados, esquemas de tools y topología de red de agentes.

## M4: QA Engineer
- **Input:** `app_result/bsp/BSP.md` y `app_result/architecture/ARCHITECTURE.md`.
- **Output Requerido:** `app_result/docs/qa_plan.md` y `app_result/tests/specs/`.
- **Criterio de Éxito:** Escenarios de prueba automatizados para validar que los agentes responden de acuerdo con las especificaciones y herramientas dadas.

## M5: Generador de Código (Python Antigravity Developer)
- **Input Primario:** `app_result/bsp/BSP.md`, `app_result/architecture/ARCHITECTURE.md` y `app_result/MEMORY.md`.
- **Output Requerido:** Código compilable en `app_result/src/`.
- **Criterio de Éxito:** El código es Python puro utilizando la librería `google-antigravity` para implementar la red de agentes y las herramientas definidas, sin placeholders y cumpliendo 1:1 con las especificaciones.

## M6: DevOps & Release Engineer
- **Input:** `app_result/src/`.
- **Output Requerido:** Artefactos de despliegue en `app_result/deploy/` (Dockerfiles, `.env.example`).
- **Criterio de Éxito:** Infraestructura de ejecución de contenedores declarada de forma funcional y agnóstica.
