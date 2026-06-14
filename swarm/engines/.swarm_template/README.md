# ROO-CODE-SWARM Template (Enterprise AI Agent Framework)

Este repositorio es un template arquitectónico para orquestar un enjambre de agentes de IA secuenciales (Sequential Multi-Agent Pipeline) bajo la estricta metodología de **Spec-Driven Development (SDD)** y **Harness Engineering**.

## 🧠 Filosofía Arquitectónica
Este framework parte de la premisa de que los LLMs son motores estocásticos (probabilísticos). Para generar software determinista, de calidad empresarial y libre de alucinaciones en hardware local/cloud, el enjambre se rige por:
1. **Cero Código sin Contrato:** Ningún agente programa (M5) sin un documento de negocio (BSP) y de arquitectura técnica (TDP) validados.
2. **Separation of Concerns (SoC) Agéntico:** Roles divididos (PM, BA, Arquitecto, QA, Developer, DevOps) que no se solapan.
3. **El Orquestador como Gatekeeper:** Un único punto de control que valida los *inputs/outputs* de cada fase antes de mover el grafo.

## 📁 Estructura del Framework
El sistema mantiene una separación inmutable entre el "motor" y el "resultado":
- `.swarm/`: Cerebro inmutable. Contiene especificaciones (`specs/`), contratos (`CONTRACTS.md`) y el motor de validación.
- `app_result/`: Espacio de trabajo dinámico. Aquí se generan el código, la arquitectura, los planes de prueba y la memoria del proyecto.

## 🚀 Workflows Soportados
- **Greenfield (Desde Cero):** Ideación -> Manifiesto -> Especificaciones -> Código -> Infraestructura.
- **Brownfield (Legacy):** Ingeniería Inversa desde repositorios existentes -> Documentación Automática -> Refactorización.

---

## 👥 Gobernanza: Humanos vs. Agentes

Para operar este framework con éxito, es fundamental distinguir el propósito y destinatario de cada archivo clave:

### Archivos para Humanos (Human-Facing)
*   **`README.md` / `SETUP.md`:** Instrucciones de instalación y arranque del enjambre.
*   **`app_result/docs/testing_guide.md`:** Guía escrita por el desarrollador para que los agentes aprendan a correr y validar los tests del proyecto.
*   **`implementation_plan.md` / `walkthrough.md` / `task.md`:** Documentos generados por la IA para revisión, aprobación y seguimiento del desarrollador.

### Archivos para Agentes (Agent-Facing)
*   **`.clinerules`:** Reglas del workspace que los agentes de codificación leen de forma automática en cada interacción para aplicar estándares de codificación y evitar spec-drift o placeholders.
*   **`.roomodes` / `opencode.json`:** Definiciones de roles, permisos y configuraciones de modelos de IA.
*   **`.swarm/specs/CONTRACTS.md` y `RULES.MD`:** Contratos I/O y reglas generales de Spec-Driven Development que limitan la autonomía del enjambre.
*   **`app_result/MEMORY.md`:** Memoria histórica concisa del proyecto que consumen los agentes al iniciar cada paso para no perder contexto.