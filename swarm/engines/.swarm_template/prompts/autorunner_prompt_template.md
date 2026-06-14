# Template de Ejecución: Modo Autorunner (Autónomo)

*Copia y pega este prompt al asistente primario de tu IDE (ej. Cline, Roo Code, Antigravity) cuando quieras que el Swarm diseñe y desarrolle la aplicación completa de principio a fin sin detenerse a preguntarte, tomando decisiones autónomas basadas en las buenas prácticas.*

---

**[Copia desde aquí]**

Actúa como el **Orquestador del Swarm** (lee las reglas en `swarm/engines/.swarm_template/prompts/swarm_master_prompt.md`). 
Quiero iniciar un nuevo proyecto utilizando el **Modo Autorunner (Flujo Autónomo)**.

**Contexto del Proyecto:**
Por favor, lee el archivo `swarm/engines/.swarm_template/prompts/application_requirement_prompt.md` donde he detallado los requerimientos, el perfil del usuario y los flujos críticos. 

**Instrucciones de Ejecución Autónoma:**
1. Lee `swarm/engines/.swarm_template/.swarn/memory/SHARED_FOUNDATIONS.md` para asimilar las lecciones de proyectos anteriores y usarlas como base.
2. Inicia el flujo en **M0** y avanza secuencialmente a través de **TODO el DAG** (M0 -> M1 -> M2 -> M2.5 -> M3 -> M4 -> M5 -> M6).
3. **NO te detengas a preguntar.** Tu directiva es completar el proyecto entero en una sola ejecución.
4. Si encuentras múltiples caminos técnicos o decisiones de diseño ambiguas, **asume la decisión más estándar, segura y probada**. Estás autorizado a tomar decisiones arquitectónicas autónomas.
5. Es **obligatorio** que registres cualquier asunción o decisión autónoma en la sección `### Key Decisions` del entregable del agente correspondiente.
6. El Orquestador debe extraer esas decisiones y anexarlas a `app_result/MEMORY.md` en tiempo real mientras avanza el flujo.
7. Al finalizar la fase M6, entrégame un reporte final indicando que el proyecto está compilado y listo en `app_result/`.

Comencemos. Lee los requerimientos y ejecuta el enjambre completo ahora.
