# Contratos de Agentes (I/O Specifications & Pathing)

**Directiva Principal:** `.swarm/` es el cerebro estático y normativo. `app_result/` es el lienzo de trabajo dinámico. Ningún agente (salvo el Orquestador o M0) modifica archivos fuera de sus outputs designados.
Todos los agentes de diseño y arquitectura (M0-M4) deben incluir de forma obligatoria un bloque delimitado con el título `### Key Decisions` al final de sus entregables para alimentar el hook de actualización automática de memoria.

## M0: Foundation / Bootstrapper
- **Input:** Interacción humana o prompt inicial.
- **Output Requerido:** `app_result/PROJECT_MANIFEST.md` y `app_result/BOARD.md`.
- **Criterio de Éxito:** Se ha creado la estructura base y el alcance en `app_result/`, incluyendo el bloque obligatorio `### Key Decisions` al final del manifiesto.

## M1: System Analyst (Discovery & TDP)
- **Input (Greenfield):** `app_result/PROJECT_MANIFEST.md`.
- **Input (Brownfield):** `/app_legacy` o `/old_src`.
- **Output Requerido:** `app_result/tdp/TDP.md`.
- **Criterio de Éxito:** Documentación técnica inicial persistida en el TDP, incluyendo el bloque obligatorio `### Key Decisions` con las decisiones críticas de análisis.

## M2: Business Analyst (BSP)
- **Input:** `app_result/tdp/TDP.md`.
- **Output Requerido:** `app_result/bsp/BSP.md`.
- **Criterio de Éxito:** Reglas de negocio claras e hitos extraíbles para el BOARD, incluyendo el bloque obligatorio `### Key Decisions` de reglas funcionales.

## M2.5: Domain Validator (Simulation)
- **Input:** `app_result/bsp/BSP.md`.
- **Output Requerido:** `app_result/bsp/DOMAIN_VALIDATION.md`.
- **Criterio de Éxito:** Simular 5 a 10 escenarios cotidianos de uso contra el BSP para detectar fricciones o acciones omitidas (ej. flujos muy largos, faltantes de acciones frecuentes). Si hay omisiones, obligar a M2 a iterar antes de pasar a arquitectura. Incluir bloque `### Key Decisions`.

## M3: Enterprise Architect (Assessment)
- **Input:** `app_result/bsp/BSP.md` y `app_result/bsp/DOMAIN_VALIDATION.md`.
- **Output Requerido:** `app_result/architecture/ARCHITECTURE.md`.
- **Criterio de Éxito:** Stack base ratificado y topología definida, incluyendo el bloque obligatorio `### Key Decisions` de decisiones de arquitectura.

## M4: QA Engineer
- **Input:** `app_result/bsp/BSP.md` y `app_result/architecture/ARCHITECTURE.md`.
- **Output Requerido:** `app_result/docs/qa_plan.md` y `app_result/tests/specs/`.
- **Criterio de Éxito:** Criterios de aceptación transformados en estrategias de testing comprobables, incluyendo el bloque obligatorio `### Key Decisions` de estrategia de pruebas.

## M4b: Competitive QA Analyst
- **Input:** `app_result/bsp/BSP.md`, `app_result/architecture/ARCHITECTURE.md` y `app_result/docs/qa_plan.md`.
- **Output Requerido:** `app_result/docs/competitive_benchmark.md`.
- **Criterio de Éxito:** Evaluar el diseño propuesto frente a los "Gold Standards" o estándares de la industria aplicables. Si el producto resulta ser inferior al mercado ("clone mediocre"), forzar a los agentes previos a iterar el diseño antes de generar el código. Incluir bloque obligatorio `### Key Decisions`.

## M5: Generador de Código
- **Input Primario:** Todo el material validado en `app_result/bsp/`, `app_result/architecture/` y contexto global en `app_result/MEMORY.md`.
- **Output Requerido:** Código compilable exclusivamente en `app_result/src/`.
- **Criterio de Éxito:** El código cumple 1:1 con las especificaciones del BSP y la Arquitectura (Cero Drift). Se debe certificar la correspondencia estricta contra las especificaciones del diseño.

## M6: DevOps & Release Engineer
- **Input:** `app_result/src/`.
- **Output Requerido:** Artefactos de despliegue en `app_result/deploy/` (ej. Dockerfiles, pipelines).
- **Criterio de Éxito:** Infraestructura declarada de manera agnóstica y funcional, incluyendo el bloque `### Key Decisions` de DevOps.