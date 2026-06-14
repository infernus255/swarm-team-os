# Registro de Memoria del Sistema y Aprendizajes

## 📅 Últimas Actualizaciones (Junio 2026)

- **Validación de API Keys**: En entornos Windows y Docker, para que pase la validación de API keys, es necesario crear `api_key_limits.json` en la raíz del repositorio con los límites correspondientes y declarar las claves en `hermes.env` con el prefijo 'alias:' (ej. `GEMINI_API_KEY=primary:CLAVE`). Además, si Hermes se ejecuta únicamente dentro de Docker, se debe construir la imagen y etiquetarla como `hermes-test:latest`.

- **Manejo de Prefijos en API Keys**: Se corrigió el error 'model provider failed' al limpiar las claves API de los prefijos de alias en el entrypoint del contenedor (`docker-entrypoint.sh`). Esto permite que la telemetría mantenga el alias para mapear los límites, mientras que Hermes recibe la clave limpia.

- **Migración a Neon Cloud DB (SGA)**: Se migró la base de datos de persistencia a Neon.tech (PostgreSQL serverless). El nuevo inicializador `infra/db_init.py` habilita la extensión `vector` e implementa índices HNSW. El cliente `memory/sga_client.py` ahora implementa un pool de conexión persistente e inyecta embeddings Gemini con dimensión exacta de 768.

- **Bypass de PEP 668**: La instalación de paquetes sobre el contenedor basado en Ubuntu 24.04 arrojó errores de entorno administrado. Se resolvió usando el flag `--break-system-packages` de pip en el `Dockerfile`.

- **Mapeo de Rutas y Persona**: Se reestructuró `docker-compose.yml` para montar la raíz completa en `/app`. Se implementó un perfil de sistema maestro `infra/hermes/SOUL.md` que inyecta la personalidad de Jarvis OS al agente Hermes.
