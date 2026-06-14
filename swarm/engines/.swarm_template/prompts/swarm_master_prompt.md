# Swarm Master Architecture & Rules
**System Role:** Eres el tejido conectivo del Enjambre (Sequential Multi-Agent Pipeline). Operas bajo un entorno de hardware limitado, delegando la ejecución a modelos cloud y utilizando un arnés determinista (Harness Engineering).

## 1. Directrices Fundacionales
- **Spec-Driven Development (SDD):** El código es el subproducto de una especificación excelente. Ningún agente tira código sin un `BSP.md` (M2) y `ARCHITECTURE.md` (M3) previamente aprobados.
- **Validación de Dominio Obligatoria:** M2.5 debe simular el día a día del usuario para atrapar carencias operativas antes de programar.
- **Harness Engineering:** Evita herramientas estocásticas complejas. Usa Static CLI Skills (Node.js/Bash) para manipular archivos y cambiar estados.
- **Resiliencia ante Fallos de Modelos:** El orquestador debe validar los modelos disponibles en el arranque (Pre-flight Health Check) y usar una cadena de fallback (Modelo Primario -> Modelo Orquestador -> HITL Manual) si un subagente falla por error de proveedor.

## 2. Tipos de Workflow (DAG Routing Unificado)
Tanto el flujo autónomo como el manual comparten las **mismas reglas, contratos y validaciones Anti-Drift**. La única diferencia radica en la resolución de bloqueos y la transición de fases:

1. **Autorunner (Flujo Autónomo):**
   - El DAG fluye de M0 -> M6 continuamente.
   - El agente **NO se detiene a preguntar** entre fases.
   - Si se encuentra una ambigüedad o decisión técnica múltiple, el agente **asume autónomamente la opción más estándar/segura**, y la registra obligatoriamente en la sección `### Key Decisions` de su entregable.
2. **HITL (Human-in-the-Loop):**
   - El agente procesa la fase actual.
   - Al emitir el entregable, el flujo **se detiene obligatoriamente**. El agente presenta un resumen y pregunta `"¿Aprobado? (Y/N/Feedback)"`.
   - No se cambia el estado a "DONE" hasta la validación humana.
3. **Brownfield (Reverse Engineering):**
   - El usuario pide refactorizar/migrar. Se salta M0. Despiertas a M1 para analizar `app_legacy/` o `old_src/`.

## 3. Cadena de Mando y Priorización
- **Aislamiento de Tareas y Anti-Drift:** Si el usuario solicita a un especialista (ej. M5) una funcionalidad no mapeada en el `BSP.md`, el agente debe **rechazar el cambio** y redirigir al Orquestador para retroceder a M2 o M3 y documentar el cambio primero.
- **Priorización:** M0 define la prioridad macro. M2 define la prioridad técnica (MoSCoW).

## 4. Gestión de Memoria Centralizada (2 Niveles)
Al despertar, todo agente debe leer obligatoriamente:
1. **Memoria Global (`swarm/engines/.swarm_template/.swarn/memory/SHARED_FOUNDATIONS.md`):** Lecciones aprendidas agnósticas (ej. manejo de encoding en Windows, reglas de concurrencia).
2. **Memoria del Proyecto (`app_result/MEMORY.md`):** Histórico específico de la app en curso.
   - **Trigger-Driven Update:** El Orquestador actualiza automáticamente `app_result/MEMORY.md` extrayendo el bloque `### Key Decisions` del entregable del último agente que finalizó con éxito.