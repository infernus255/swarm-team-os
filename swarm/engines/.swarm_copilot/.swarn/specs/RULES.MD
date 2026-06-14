# Swarm General Rules & Spec-Driven Development (SDD) Guidelines

Este documento establece las políticas y normas fundamentales de gobernanza técnica y desarrollo que rigen para todos los agentes (M0-M6) y la interacción humana en el pipeline secuencial.

---

## 1. El Código es un Subproducto de la Especificación
- **Regla de Oro:** Ningún agente de desarrollo (M5) ni desarrollador humano puede escribir o alterar código fuente en `app_result/src/` si dicho cambio no está previamente fundamentado, analizado y aprobado en el Documento de Especificación de Negocio (`BSP.md` - M2) y ratificado en el documento técnico de arquitectura (`ARCHITECTURE.md` - M3).

## 2. Política de Prevención de Desviaciones (Anti-Drift)
- **Definición de Drift:** El drift ocurre cuando el código fuente introduce lógica de negocio, estructuras de datos, variables o integraciones que no figuran en las especificaciones, o cuando hay cambios funcionales no documentados.
- **Acciones Ante el Drift:**
  1. Si se identifica que las especificaciones actuales son insuficientes durante la fase de codificación (M5), se debe **detener la generación de código**.
  2. El orquestador o el usuario debe ejecutar una **transición inversa** (retroceder el DAG) hacia M2 (Business Analyst) y/o M3 (Enterprise Architect).
  3. M2/M3 actualizarán los entregables correspondientes (`BSP.md` y/o `ARCHITECTURE.md`) detallando la nueva decisión o cambio.
  4. Una vez aprobados los nuevos specs mediante validación HITL, se reanuda la generación de código en M5.

## 3. Aislamiento Estricto de Tareas (Separation of Concerns)
- Cada agente tiene asignado un contrato rígido de rutas de entrada (Inputs) y salida (Outputs) especificado en `CONTRACTS.md`.
- **Prohibición de Bypass:** Ningún agente de diseño (M0, M1, M2, M3) puede generar o editar archivos de código fuente. Ningún agente de código (M5) puede editar directamente los archivos del plan de QA o especificaciones de diseño.
- Si un agente recibe instrucciones que violan su contrato de rutas de salida, debe rechazar la tarea y reportar la anomalía al Orquestador para su redirección.

## 4. Registro Estructurado de Decisiones
- Cada entregable de diseño o arquitectura debe contener una sección explícita al final titulada `### Key Decisions`.
- Esta sección debe ser un bloque de texto Markdown conciso que resuma las decisiones técnicas o de negocio críticas tomadas en ese paso. Esto permite al orquestador actualizar la memoria (`MEMORY.md`) de manera trigger-driven e independiente de la interacción del usuario.

## 5. Cierre de Proyecto y Consolidación de Aprendizajes
- **Gobernanza Post-Proyecto:** Al finalizar el ciclo de desarrollo (con la finalización de M6), es mandatorio actualizar el histórico global de lecciones aprendidas del framework.
- El desarrollador o el agente orquestador debe extraer los aprendizajes técnicos y errores operativos de la bitácora y registrarlos en `.swarm_template/.swarn/memory/development_process_memory.md` (Memoria de Mejora del Swarm) antes de dar por cerrada la rama.
