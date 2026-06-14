# 🤖 SwarmTeam OS: Multi-Agent Pipeline Framework

Bienvenido al sistema unificado de ingeniería autónoma **SwarmTeam**. Este repositorio es un framework agnóstico, determinista y con memoria de largo plazo diseñado para la creación de aplicaciones mediante pipelines multi-agente.

## 🏗️ Arquitectura Unificada (Clean Architecture)
El sistema se organiza bajo el principio de **Separación de Responsabilidades** para maximizar la eficiencia de tokens y minimizar alucinaciones:

- **`core/`**: El Motor (Stateful Graph Engine). Contiene la lógica del grafo cíclico y los modelos únicos (`models.py`).
- **`swarm/`**: La Inteligencia. Prompts maestros y reglas de diseño (Spec-Driven Development).
- **`harness/`**: El Chasis (Hardware/OS). Gestiona la telemetría del entorno (`state.json`), Git, Docker y skills personalizadas.
- **`memory/`**: El Cerebro. Cliente de integración con el **Semantic Graph Agent (SGA)** para persistencia vectorial en Neon DB.

## 🚀 Inicio Rápido (MVP)
Para lanzar el ciclo de desarrollo autónomo:

1. Asegúrate de tener configurado tu `hermes.env` con tu `GEMINI_API_KEY`.
2. Ejecuta el orquestador:
```bash
python main.py "Crear una aplicación de gestión de inventario"
```

## 🧠 Ciclo de Vida del Desarrollo (SDD)
El sistema sigue un pipeline secuencial contractuado, pero capaz de ciclos de retroalimentación:
1.  **M0**: Análisis de Requerimientos.
2.  **M2**: Definición de Reglas de Negocio (BSP).
3.  **M3**: Diseño de Arquitectura.
4.  **M4**: Ingeniería de QA (Tests).
5.  **M5**: Generación de Código (con bucle de auto-corrección M4-M5).
6.  **M6**: DevOps e Infraestructura.

## 🛠️ Skills del Harness
Puedes invocar habilidades deterministas desde el celular (vía Telegram) o CLI:
- `skill_state.py`: Telemetría de hardware y salud del sistema.
- `skill_docker.py`: Control de contenedores y parsing de Dockerfiles.
- `skill_commit_push.py`: Validación integral y sincronización con GitHub.

---
**Mantenimiento:** Este repositorio se autogestiona mediante reglas estrictas de Anti-Drift. No modifiques las especificaciones en `app_result/` sin pasar por el flujo de diseño correspondiente.
