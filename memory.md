
### 2026-06-11T06:13:52.822246Z
- Initial environment adaptation setup complete.

### 2026-06-12T19:14:33.062401Z
- En entornos Windows y Docker, para que pase la validación de API keys, es necesario crear api_key_limits.json en la raíz del repositorio con los límites correspondientes y declarar las claves en hermes.env con el prefijo 'alias:' (ej. GEMINI_API_KEY=primary:CLAVE). Además, si Hermes se ejecuta únicamente dentro de Docker, se debe construir la imagen y etiquetarla como 'hermes-test:latest' para que la validación de estado la reconozca. Las imágenes privadas en GHCR requieren un PAT con scope 'read:packages' para evitar errores 'not found'.

### 2026-06-13T00:50:03.586830Z
- Se corrigió el error 'model provider failed after retries' al limpiar las claves API de los prefijos de alias (ej. 'primary:') en el entrypoint del contenedor (docker-entrypoint.sh) antes de inyectarlas en la configuración de Hermes (.env). Esto permite que el analizador de telemetría mantenga el alias para mapear los límites, mientras que Hermes recibe la clave API limpia para autenticarse con el proveedor.

### 2026-06-13T14:30:00.000000Z
- **Migración a Neon Cloud DB & Persistencia Vectorial Directa (SGA)**: Se migró la base de datos de persistencia a Neon.tech (PostgreSQL serverless) para eliminar el contenedor local redundante de SGA. El nuevo inicializador `infra/db_init.py` habilita la extensión vector, crea las tablas con tokens SHA-256 e implementa índices vectoriales HNSW. El cliente de memoria directo `memory/sga_client.py` ahora implementa un caché/pool de conexión persistente para evitar handshakes TCP repetitivos (reduciendo latencias de 60s a milisegundos) e inyecta embeddings Gemini con dimensión exacta de 768 mediante `gemini-embedding-2` con `outputDimensionality: 768`, cayendo a búsquedas keyword ILIKE en L0 si el proveedor de embeddings falla.
- **Bypass de PEP 668 en Ubuntu 24.04 (Docker)**: La instalación de paquetes psycopg2-binary y pgvector sobre el contenedor basado en Ubuntu 24.04 arrojó errores de entorno externamente administrado. Se resolvió usando el flag `--break-system-packages` de pip en las rutas de virtualenv y globales en el `Dockerfile`.
- **Mapeo de Rutas y Persona de Jarvis OS en Telegram**: Para que el agente Hermes ejecutado en Docker herede el contexto de este repositorio y deje de reportar que la carpeta `/root` está vacía, se reestructuró `docker-compose.yml` para montar la raíz completa en `/app` de forma de lectura (`.:/app:ro`) superponiendo escrituras de estado, y se redefinió `WORKDIR /app` en el `Dockerfile`. Se implementó un perfil de sistema maestro `infra/hermes/SOUL.md` que le inyecta al agente la personalidad de Jarvis OS, dándole visibilidad completa del árbol de archivos, del chasis del harness y de las skills de ejecución, copiándose a `~/.hermes/SOUL.md` en el entrypoint.

