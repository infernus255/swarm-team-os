# Environment State Summary

## 14. Estado actual y validación

### Entorno actual
- Environment ID: DESKTOP-Q0NMPDE:host:swarm-team-os
- Environment type: host

### Hermes
- Instalado: True
- Versión: None
- Proveedor: None
- Modelo por defecto: None
- Base URL: None
- Gateway Telegram: None

### Sistema operativo
- Nombre: nt
- Versión: 10.0.22000
- Paquetes verificados:

### API keys
- Total de claves detectadas: 0
- Proveedores: 

### Repositorio git
- Rama: develop
- Commit: b71d96f7ab3f41f17270813a53a5e26fd25ab529
- Mensaje: git hygiene: untrack compiled Python cache files (.pyc)

Removes tracked cache files in __pycache__ directories. They are already ignored in .gitignore but were previously tracked, causing dirty status edits.
- Cambios modificados: 12
- Archivos no rastreados: 1
- Ahead: 0
- Behind: 0


## 15. Autorunner para IA de bajo tier

Sigue estos pasos exactos en el orden dado. No hagas suposiciones adicionales.

1. Actualiza el estado del proyecto:
   - `python3 harness/scripts/skill_state.py`

2. Actualiza el plan con el estado actual:
   - `python3 harness/scripts/skill_plan.py`

3. Si hay un nuevo aprendizaje, agrégalo a la memoria:
   - `bash harness/scripts/skill_memory.sh "Texto del aprendizaje"`

4. Sincroniza Docker con el estado del sistema operativo:
   - `python3 harness/scripts/skill_docker.py`

5. Reconstruye el contenedor para aplicar los cambios:
   - `docker compose build --progress=plain`

6. Verifica el contenedor y el gateway:
   - `docker compose up -d`
   - `docker compose logs -f`

Este autorunner está diseñado para ser seguido literalmente por una IA de bajo tier.
