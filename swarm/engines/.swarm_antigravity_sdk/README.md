# SWARM — Google Antigravity SDK Blueprint

Este es un template especializado de **SWARM** optimizado para construir aplicaciones y sistemas multi-agente utilizando el **Google Antigravity Python SDK** y los modelos de la familia **Gemini**.

---

## 🧠 Filosofía del Swarm
Este swarm está diseñado bajo las directrices del **Spec-Driven Development (SDD)**. La aplicación resultante se genera dinámicamente en el directorio `app_result/` de la raíz del proyecto para mantener el motor del swarm aislado del código fuente de producción.

## 📁 Estructura del Swarm

*   `app/`: Contiene el motor de orquestación y los prompts de sistema de los agentes especializados.
    *   `agents/`: Definición de los agentes (M0-M6) con instrucciones entrenadas específicamente para diseñar, codificar y desplegar agentes del Antigravity SDK.
    *   `engine/`: Orquestador de estados (`swarm_state.json`), hooks de memoria (`MEMORY.md`) y validación de entregables.
*   `.swarn/`: Especificaciones, reglas y contratos estáticos del enjambre.
*   `app_result/`: Directorio donde el enjambre genera el código de la aplicación. **Permanece vacío en este template** (excepto por marcadores de posición) para que copies, pegues e inicies limpio.

---

## 🚀 Ciclo de Vida de Desarrollo (M0-M6)

1.  **M0 — Bootstrapper:** Diseña el alcance general del sistema de agentes (ej. cuántos agentes se necesitan, sus roles y sus metas).
2.  **M1 — System Analyst:** Genera el TDP técnico para estructurar la topología de red de agentes.
3.  **M2 — Business Analyst (BSP):** Define las especificaciones de comportamiento, herramientas (*tools*) y APIs que consumirán los agentes.
4.  **M3 — Enterprise Architect:** Establece el diseño técnico de los agentes utilizando las APIs del Google Antigravity SDK en Python (Gemini 2.5 Flash/Pro, esquemas de definición de tools, etc.).
5.  **M4 — QA Engineer:** Genera los suites de prueba autónomos para validar el comportamiento lógico de los agentes.
6.  **M5 — Code Generator (Developer):** Escribe el código fuente compilable en `app_result/src/` utilizando la librería `google-antigravity`.
7.  **M6 — DevOps:** Configura los archivos Docker y variables de entorno (`.env`) para empaquetar y desplegar el sistema.

---

## 🛠️ Requisitos e Instalación

Para arrancar el motor de este swarm en tu entorno local:

1.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configura tu clave de API de Gemini en el archivo `.env`:
    ```env
    GEMINI_API_KEY=tu_clave_api_aqui
    ```
3.  Inicializa el pipeline usando el orquestador:
    ```bash
    python app/main.py init --mode greenfield --prompt "Diseña un asistente de atención médica con herramientas de consulta"
    ```

---

## 👥 Gobernanza: Humanos vs. Agentes

Para operar este framework con éxito, es fundamental distinguir el propósito y destinatario de cada archivo clave:

### Archivos para Humanos (Human-Facing)
*   **`README.md`:** Guía del desarrollador para el stack de Python y Antigravity SDK, y flujos M0-M6.
*   **`requirements.txt` / `.gitignore`:** Configuración de dependencias de Python y exclusión de archivos.
*   **`app_result/docs/testing_guide.md`:** Guía de ejecución de pruebas para que la IA sepa cómo correr pytest en el SDK.
*   **`implementation_plan.md` / `walkthrough.md` / `task.md`:** Reportes de diseño y seguimiento humano.

### Archivos para Agentes (Agent-Facing)
*   **`.clinerules`:** Reglas del workspace leídas por el agente para evitar spec-drift o placeholders.
*   **`.swarn/states/swarm_state.json`:** Registro del estado actual del DAG de la máquina de estados.
*   **`app_result/MEMORY.md`:** Memoria de decisiones clave extraída automáticamente post-agente.
*   **`.swarn/specs/CONTRACTS.md` y `RULES.MD`:** Contratos y reglas adaptadas a Antigravity.

