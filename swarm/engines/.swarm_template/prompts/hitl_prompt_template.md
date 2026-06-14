# Template de Ejecución: Modo HITL (Human-in-the-Loop)

*Copia y pega este prompt al asistente primario de tu IDE (ej. Cline, Roo Code, Antigravity) para iniciar un nuevo proyecto en modo interactivo, donde tú tendrás el control total sobre cada decisión del Swarm.*

---

**[Copia desde aquí]**

Actúa como el **Orquestador del Swarm** (lee las reglas en `swarm/engines/.swarm_template/prompts/swarm_master_prompt.md`). 
Quiero iniciar un nuevo proyecto utilizando el **Modo HITL (Human-in-the-Loop)**.

**Contexto del Proyecto:**
Por favor, lee el archivo `swarm/engines/.swarm_template/prompts/application_requirement_prompt.md`. Ahí encontrarás la plantilla con los requerimientos de mi nueva aplicación. He completado el perfil del usuario, las acciones diarias principales y las restricciones. 

**Instrucciones de Ejecución:**
1. Lee `swarm/engines/.swarm_template/.swarn/memory/SHARED_FOUNDATIONS.md` para asimilar las lecciones de proyectos anteriores y usarlas como base.
2. Inicia el flujo en el agente **M0 (Bootstrapper)** para crear la estructura base en `app_result/`.
3. **Regla de Parada Estricta:** Al finalizar CADA fase (M0, M1, M2, M2.5, etc.), debes **detenerte inmediatamente**.
4. Muéstrame un resumen de lo que generó el agente y pregúntame: `"¿Aprobado? (Y/N/Feedback)"`.
5. No puedes avanzar al siguiente nodo del DAG hasta que yo te dé el "Y". Si te doy feedback, debes hacer que el agente de esa fase itere y corrija su entregable.
6. Al recibir el "Y", extrae las `### Key Decisions`, actualiza el `app_result/MEMORY.md` y recién ahí avanza al siguiente agente.

Comencemos. Lee los requerimientos y ejecuta M0.
