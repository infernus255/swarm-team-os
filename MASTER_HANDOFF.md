# 🤖 SWARMTEAM OS: MASTER ARCHITECTURE & HANDOFF (v3.0 Elite)

> **META-INSTRUCTION:** Este es el "Source of Truth" definitivo. Ningún agente debe operar fuera de estos parámetros. El sistema es un **OS Agentic Distribuido** diseñado para la máxima eficiencia de tokens y precisión de ingeniería.

---

## 🏛️ 1. FILOSOFÍA: AGENTIC ENGINEERING & SDD
SwarmTeam OS opera bajo el paradigma de **Spec-Driven Development (SDD)**. El código es un artefacto secundario; la especificación y la arquitectura son primarias.
- **Hermes (The Runtime):** El framework de agente subyacente instalado en la máquina. Recibe disparadores (CLI, Telegram, Webhook) y ejecuta el Repo.
- **Jarvis (The Intelligence/Dispatcher):** El script `jarvis.py`. Actúa como el cerebro local. **Múltiples instancias de Jarvis pueden correr simultáneamente en diferentes nodos** (ej. una en Oracle manejando Telegram, otra en el Pentium manejando tareas locales). Se sincronizan vía SGA y Git.
- **Poly-Swarm (The Workforce):** Motores especializados en `swarm/engines/` (Copilot, Antigravity, PydanticAI) invocados por Jarvis para tareas específicas.
- **Harness Engineering:** Uso de skills deterministas para interactuar con el mundo físico.

---

## 🚀 2. TOPOLOGÍA DE NODOS & CAPACIDADES (Elite Cluster)
El sistema se adapta a su entorno vía `env_drivers/`. Cada dispositivo tiene roles primarios pero puede actuar como una instancia de Jarvis:

1. **Oracle Cloud (The C2 / Public Gateway):** 
   - **Specs:** ARM Ampere (4 OCPU, 24GB RAM), Ubuntu 24.04.
   - **Capabilities:** Telegram webhook siempre online, orquestador de swarms pesados en la nube. El "Public Jarvis" primario.
2. **Pentium (The Anchor / Local Mayordomo):**
   - **Specs:** PC local de bajos recursos, 120GB SSD, Ubuntu Server.
   - **Capabilities:** Host de la base de datos SGA (PostgreSQL+pgvector). Ejecuta el OCI Hunter (`cazador.py`). Gestiona el gateway/firewall local.
3. **Ryzen Desktop (The Muscle / Battle Station):**
   - **Specs:** Ryzen 3600X, RX 5600XT (6GB VRAM), 16GB RAM, Windows 11.
   - **Capabilities:** Computación pesada vía Docker (invisible para gaming). Inferencia de LLM local, compilación pesada y generación de medios.
4. **Notebook HP (The Mobile Lab / Media Library):**
   - **Specs:** i7 6th Gen, 16GB RAM, NVIDIA 940M, Pop!_OS / CachyOS.
   - **Capabilities:** Estación de dev portátil. Banco de pruebas para Swarms. Servidor de medios gestionado por Jarvis.
5. **Xiaomi 15 Ultra (The Mobile Sensor):**
   - **Capabilities:** Comandos de voz, acceso a dashboard móvil, autenticación biométrica para tareas críticas y procesamiento rápido de imágenes/visión.
6. **MX9 Box (The Dashboard / TV Eye):**
   - **Capabilities:** Android TV (SlimBoxTV). Dashboard visual del estado del OS y streaming de medios orquestado por el Pentium/Notebook.

---

## 🧠 3. SISTEMA DE MEMORIA SGA (DUAL-LAYER)
La memoria es el pegamento del sistema distribuido, alojada en **Neon PostgreSQL + pgvector**.
- **L0 (Jarvis OS Meta-State):** 
  - Almacena el estado de los nodos, contexto conversacional y preferencias del usuario.
  - Trazabilidad de fases en `core/orchestrator.py`.
- **L1 (Autonomous Swarm Knowledge):**
  - Conocimiento técnico atomizado (coding paradigms, bug resolutions).
  - **Guru-Watch Insights:** Novedades de la industria inyectadas automáticamente.

---

## 🕵️ 4. GURU-WATCH & AUTO-MEJORA
El sistema nunca queda obsoleto gracias al **Guru-Watch Protocol**:
1. El script `harness/scripts/skill_guru_watch.py` monitorea repositorios de vanguardia (Nous Research, PydanticAI, Google Antigravity).
2. Los descubrimientos se vuelcan en `docs/architecture_insights.md` (La Biblia Agéntica).
3. Se inyectan en la SGA L1 para ser usados como **Just-in-Time Context** por cualquier enjambre.

---

## 🛡️ 5. PROTOCOLO DE CONTROL DE REGRESIONES & SEGURIDAD
1. **Validation Gate:** Cada cambio en el `core/` debe pasar `tests/test_swarm_core.py`.
2. **Agnostic Audit:** Prohibido inyectar lógica de producto en el core.
3. **Snapshot Mandatory:** Cada transición de fase genera un commit de Git automático.
4. **state.json Persistence:** El archivo `state.json` es el ledger global. **NUNCA debe ser sobrescrito o borrado.** Los nuevos nodos deben añadirse al diccionario `environments`.
5. **Guardrails:** Nunca borrar documentación operacional o historial de estado. Leer `state.json` antes de proponer cambios.

---

## 🔄 6. BOOTSTRAPPING & RUNTIME FLOW
1. **Trigger:** El usuario habla a Hermes (Telegram/CLI).
2. **Boot:** Hermes lee el repo e identifica `jarvis.py` como punto de entrada.
3. **Context Awareness:** Jarvis usa `env_drivers/` para saber *dónde* está y lee `state.json` para entender el estado global.
4. **Self-Update:** Antes de cada ciclo, Jarvis hace un `git pull` para sincronizar cambios realizados por otros nodos o agentes.

---
**¡SwarmTeam OS Elite v3.0 está en línea!**
