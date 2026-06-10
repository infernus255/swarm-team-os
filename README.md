# SwarmTeam OS: Unified Engineering Framework

Bienvenido al sistema unificado de ingeniería autónoma **SwarmTeam**. Este repositorio es un framework agnóstico, determinista y con memoria de largo plazo diseñado para la creación de aplicaciones mediante pipelines multi-agente.

## 🏗️ Arquitectura Unificada (Clean Architecture)

El sistema se organiza bajo el principio de **Separación de Responsabilidades** para maximizar la eficiencia de tokens y minimizar alucinaciones:

- **`core/`**: El Motor (Stateful Graph Engine). Contiene la lógica del grafo cíclico y los modelos únicos (`models.py`).
- **`swarm/blueprints/`**: Los Planos (Inteligencia). Contiene los prompts maestros y reglas SDD (Spec-Driven Development) en Markdown.
- **`harness/`**: El Chasis (Hardware/OS). Gestiona la telemetría del entorno (`state.json`), Git, Docker y skills personalizadas.
- **`memory/`**: El Cerebro. Cliente de integración con el **Semantic Graph Agent (SGA)** para persistencia vectorial.
- **`app_result/`**: El Taller. Espacio de trabajo aislado donde se generan los productos finales.

## 🚀 Inicio Rápido (MVP)

Este repositorio incluye un orquestador simplificado para validar la arquitectura.

### 1. Requisitos
- Docker y Docker Compose.
- Python 3.9+ instalado localmente (para el orquestador).
- Un token de Telegram y API Keys de LLMs (Gemini/OpenAI) en `hermes.env`.

### 2. Levantar Infraestructura
El sistema utiliza SGA (Semantic Graph Agent) con Postgres+pgvector para la memoria:
```bash
docker compose up -d
```

### 3. Ejecutar el Swarm
Lanza el flujo completo (M0 -> M6) con un solo comando:
```bash
python main.py "Crear una aplicación de gestión de inventario"
```

## 🧠 Ciclo de Vida del Desarrollo (SDD)

El sistema sigue un pipeline secuencial contractuado, pero capaz de ciclos de retroalimentación:
1.  **M0-M1**: Descubrimiento y Manifiesto.
2.  **M2**: Definición de Reglas de Negocio (BSP).
3.  **M3**: Diseño de Arquitectura.
4.  **M4**: Ingeniería de QA (Tests).
5.  **M5**: Generación de Código (con bucle de auto-corrección M4-M5).
6.  **M6**: Despliegue y Ops.

## 🛠️ Skills del Harness
Puedes invocar habilidades deterministas desde el celular (vía Telegram) o CLI:
- `skill_state.py`: Sincroniza la salud del sistema.
- `skill_commit_push.py`: Valida, comitea y pushea cambios, indexando el aprendizaje en el SGA.

---
**Mantenimiento:** Este repositorio se autogestiona mediante reglas estrictas de Anti-Drift. No modifiques las especificaciones en `app_result/` sin pasar por el flujo de diseño correspondiente.
