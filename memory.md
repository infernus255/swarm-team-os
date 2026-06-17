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

### 2026-06-17T05:45:06.023222Z
- Lecciones Aprendidas: 1. Render optimizado de autómatas celulares sin loops redundantes para celdas vacías (color=0). 2. Motores HTML5 autocontenidos sin CDNs externos. 3. Multijugador WebRTC P2P híbrido con pantalla dividida. 4. LCG PRNG para simulación física reproducible. 5. Despliegue estático en Vercel.

### 2026-06-17T05:52:57.164450Z
- Lecciones Aprendidas (Versión Audiencia Masiva): 1. Implementación de un bucle de juego basado en misiones procedimentales para incentivar la exploración y minado. 2. Incorporación de textos flotantes (FloatingText) para dar feedback visual inmediato ('juice'). 3. Sintetizador de música de fondo ambiental procedimental con Web Audio, optimizando la experiencia relajante del sandbox. 4. Redespliegue estático automatizado en Vercel con bypass de cache de Firecrawl mediante timestamps en la URL.

### 2026-06-17T19:44:00.000000Z
- Lecciones Aprendidas (V1.3 - Cyber Egypt & DB Sync): 1. Implementación de una estructura narrativa ('Kemet-Delta') donde cofres especiales (Cyber-Sarcophagus) contienen las reliquias necesarias (Ankh de Vida, Ojo de Horus, Escarabajo de Poder) para disipar un campo de fuerza protector. 2. Desarrollo de un enemigo tipo Jefe final ('Pharaoh Guardian') con dos fases tácticas (proyectiles de energía guiados y modo furia con bolas de fuego y llamados de esbirros). 3. Automatización de carga de conocimientos y lecciones de ingeniería y lore directamente a la base de datos distribuida (Neon PG SGA Capa L0/L1) con vectores de búsqueda. 4. Confirmación de compatibilidad con multijugador offline y online WebRTC P2P.
