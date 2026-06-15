# 🧠 AGENTIC ENGINEERING BIBLE (v1.0 - 2026 Standards)

Este documento es el núcleo de conocimiento de SwarmTeam OS. Integra los principios de Nous Hermes, Pydantic-AI, Antigravity y las mejores prácticas de los "gurus" de AI Engineering.

## 🏛️ 1. PRINCIPIOS ARQUITECTÓNICOS (SGA-Core)

### A. Orquestación Basada en Grafos Cíclicos
*   **No más flujos lineales:** El sistema debe operar en grafos donde el Agente M4 (Evaluador) puede devolver el flujo al Agente M5 (Codificador) hasta que se cumpla la rúbrica.
*   **Desacoplamiento Total:** Los agentes no conocen la implementación de otros. Se comunican mediante **Contratos Tipados (Pydantic)** y la **SGA (Shared Global Alignment)**.

### B. Memoria Dual (L0/L1) y JIT Context
*   **L0 (Meta-State):** Estado del hardware y la conversación. No contamina la lógica de ingeniería.
*   **L1 (Domain Knowledge):** Conocimiento técnico atomizado. Cada "insight" de un swarm debe ser indexado para ser inyectado como **Just-in-Time Context** en futuras ejecuciones.
*   **Principio Guru:** "No rellenes el prompt con basura; inyecta solo lo necesario cuando el agente llame a una herramienta."

### C. SDD (Spec-Driven Development)
*   El código es un subproducto de la especificación. Si falla el código, primero se audita el `BSP.md` o el `ARCHITECTURE.md`.
*   **Gatekeeping:** El Agente M4 (QA) es el dueño de la verdad. Si no hay tests unitarios exitosos, el proyecto no existe.

## 🛠️ 2. HARNESS ENGINEERING & DETERMINISMO

### A. Herramientas Estáticas vs. Estocásticas
*   Usa exclusivamente herramientas CLI deterministas (`bash`, `python`, `git`).
*   Cada acción del agente debe dejar un rastro en el **Observability Layer** (logs de ejecución y snapshots de Git).

### B. Presupuestos de Agente (Safety & FinOps)
*   **Step Budget:** Límite de iteraciones para evitar bucles infinitos.
*   **Token Budget:** Límites de costo por tarea.
*   **Time Budget:** Límites de tiempo real para sesiones autónomas.

## 🧘 3. GURU-WATCH PROTOCOL (Auto-Mejora Continua)

Para evitar la obsolescencia, SwarmTeam OS debe seguir este protocolo de actualización:

1.  **Trigger Semanal:** El sistema debe ejecutar un "Research Swarm" buscando novedades en:
    *   *Nous Research (Hermes Agent updates)*
    *   *PydanticAI (Structured Output standards)*
    *   *Antigravity (Swarm coordination patterns)*
    *   *Publicaciones de Andrej Karpathy, Simon Willison y Anthropic Agents SDK.*
2.  **Ingestión de "Insights":** Cada descubrimiento se vuelca en `docs/architecture_insights.md` y se atomiza en la SGA L1.
3.  **Refactorización Sugerida:** Si una nueva práctica (ej. una nueva arquitectura de Router-Specialist) supera la actual, el sistema debe proponer un plan de migración al humano.

---
*Documento autogenerado por SwarmTeam OS Elite v2.1.*
