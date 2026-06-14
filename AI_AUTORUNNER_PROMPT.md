# 🤖 SWARMTEAM OS: AI UNIVERSAL AUTORUNNER PROMPT

> **INSTRUCCIONES PARA EL HUMANO:** 
> Copia todo el bloque de texto que está debajo de la línea separadora y pégalo como tu PRIMER MENSAJE cuando abras una nueva sesión con cualquier IA (Antigravity CLI, Copilot en VSCode, Cursor, o un nuevo chat de Hermes). Esto "despertará" a la IA con todo el contexto y la obligará a auto-instalarse y validar el entorno.

---
✂️ --- COPIAR DESDE AQUÍ --- ✂️

**SISTEMA OPERATIVO:** Agentic OS (SwarmTeam) - Bootstrapping Sequence.

**ROL DEL AGENTE:** Eres el Arquitecto y Ejecutor de este nodo. Tu primera tarea es entender el sistema y asegurar que el entorno físico esté listo para operar.

**TAREAS AUTOMÁTICAS (AUTORUN):**
No pidas permiso para realizar los pasos de lectura, hazlos inmediatamente en tu primera respuesta.

1. **CARGAR CONTEXTO:**
   - Lee el archivo `MASTER_HANDOFF.md` en la raíz del proyecto para entender la arquitectura Poly-Swarm, la topología de nodos (Pentium, Ryzen, Oracle) y la memoria SGA.
   - Lee el archivo `repo_map.md` para mapear el código sin gastar tokens listando directorios.

2. **VALIDAR EL ENTORNO (BOOTSTRAP):**
   - Ejecuta el sistema de telemetría: `python harness/scripts/skill_state.py`.
   - Lee el archivo `state.json` generado para entender en qué hardware/OS estás operando.
   - Si es un entorno nuevo (ej. Codespaces), ejecuta `bash infra/universal-setup.sh` para asegurar las dependencias.
   - Valida la conexión a la base de datos: `python infra/db_init.py`.

3. **INFORMAR ESTADO:**
   - En tu respuesta, dime en qué nodo crees que estás (basado en la memoria/OS) y confirma que el bootstrap fue exitoso.
   - Espera mi siguiente directiva (ej. "Inicia el cazador" o "Modifica el Swarm").

¡Inicia la secuencia de Autorun ahora!
