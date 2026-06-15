# 🧠 SwarmTeam OS: SGA Memory Architecture (v3.0)

La **SGA (Shared Global Alignment)** es la infraestructura de memoria distribuida que permite que todos los nodos de SwarmTeam OS operen con una consciencia compartida.

## 🏛️ Estructura de Capas (L0 / L1)

### L0: Memoria de Contexto y Meta-Estado (Local/Relacional)
- **Propósito:** Gestionar el "quién es quién" y el estado conversacional.
- **Tabla:** `sga_l0_context`
- **Campos Clave:** `node_id`, `project_id`, `phase`, `metadata`.
- **Uso:** Jarvis utiliza esta capa para saber en qué hardware está corriendo y cuál es el historial inmediato con el usuario.

### L1: Memoria de Conocimiento y Sabiduría (Vectorial/Global)
- **Propósito:** Almacenar patrones de ingeniería, arquitecturas y lecciones aprendidas.
- **Tabla:** `sga_l1_swarm_knowledge`
- **Motor:** pgvector (PostgreSQL) + Gemini Embeddings (768d).
- **Uso:** Los motores de Swarm consultan esta capa para evitar repetir errores pasados y aplicar las mejores prácticas (JIT Context).

## 🕵️ Integración Guru-Watch
La capa L1 se alimenta automáticamente de fuentes externas de élite mediante el protocolo **Guru-Watch**, asegurando que el conocimiento del enjambre esté siempre a la vanguardia.

## 🛠️ Comandos de Mantenimiento
- **Inicializar DB:** `python infra/db_init.py`
- **Validar Conexión:** `python tests/test_sga_client.py`
- **Sincronizar Gurus:** `python harness/scripts/skill_guru_watch.py`

---
*La memoria es el único activo que crece con cada ejecución.*
