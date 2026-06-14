# HISTORIAL DE APRENDIZAJES Y MEJORAS DEL SWARM

Este documento actúa como la bitácora histórica de errores, hallazgos y aprendizajes recolectados de cada proyecto desarrollado bajo este framework para optimizar el comportamiento del Swarm.

---

## 🐢 Proyecto 1: TMNT Arcade Retro Game (Juego Combate 2D)

### Contexto del Proyecto
Intento de desarrollo de un juego de combate retro en 2D basado en las Tortugas Ninja usando subagentes automáticos de principio a fin (M0-M6).

### Errores del Swarm Detectados
1. **Fallo Crítico de Subagentes:** Los subagentes configurados con modelos no estándar (ej. deepseek) fallaron inmediatamente al no estar registrados en el runtime local (`ProviderModelNotFoundError`), interrumpiendo el flujo.
2. **Amnesia de Contexto / Spec Drift:** Al fallar los subagentes, la memoria centralizada quedó desactualizada y el código generado comenzó a desviarse del diseño del BSP sin que ningún validador lo detectara.
3. **Ausencia de Auditoría de Calidad:** El código del juego aspiraba a calidad "AAA" pero carecía de una fase de benchmark objetivo que lo comparara contra el estándar real del mercado (TMNT: Shredder's Revenge).

### Mejoras Aplicadas al Swarm
- **Creación de la Fase M4b (Competitive QA Analyst):** Se introdujo una fase obligatoria post-pruebas para contrastar el diseño contra el "Gold Standard" de la industria antes de generar el código.
- **Cadena de Fallback (Fallback Chain):** Implementación en el orquestador de un flujo de reintentos automático ante fallos de proveedores: `Modelo Primario -> Modelo Orquestador -> HITL Manual`.
- **Pre-flight Health Check:** Diagnóstico de disponibilidad de claves de API y modelos antes de iniciar la ejecución.
- **Actualización de Memoria Automatizada:** Creación de un hook post-agente trigger-driven que extrae la sección `### Key Decisions` del entregable e indexa la información en `MEMORY.md`.

---

## 💈 Proyecto 2: Asistente de Peluquería (Citas & Inventario)

### Contexto del Proyecto
Desarrollo de un sistema de reservas de citas con inventario integrado, panel web FastAPI y un bot de Telegram.

### Errores y Desafíos Técnicos
1. **Conflicto de Loops de Eventos:** Intentar correr la API web de FastAPI (`uvicorn`) y el bot de Telegram (`python-telegram-bot` polling) en hilos separados generaba bloqueos y caídas del socket de red local.
2. **UnicodeEncodeError en Windows:** Caracteres decorativos y emojis (`[✓]`, `[⚠️]`) provocaban caídas del CLI de orquestación en terminales de Windows debido al encoding por defecto CP1252.
3. **Restricciones CHECK Inmutables:** Modificaciones al modelo de datos (cambios de estados en reservas) fallaban porque SQLite no soporta la edición de restricciones de integridad directas en tablas con datos.

### Mejoras Aplicadas al Swarm y Desarrollo
- **Event Loop Unificado:** Uso obligatorio de `asyncio.gather` para orquestar múltiples deamons asíncronos concurrentes sobre el mismo ciclo de eventos de Python.
- **Encoding de Consola UTF-8:** Inyección de `$env:PYTHONIOENCODING="utf-8"` en los comandos de ejecución del CLI en entornos Windows.
- **Mecanismo de Migración de SQLite:** Documentar el patrón de recreación de esquemas (renombrar a `_old`, crear nueva tabla con constraints actualizadas, migrar datos con mapping y descartar tabla vieja).

---

## 🏗️ Proyecto 3: Gestión de Obras v2 (Contratista Mobile-First)

### Contexto del Proyecto
Desarrollo de una PWA offline-first con entrada de voz y parser inteligente local para el registro rápido de gastos, personal y logística.

### Errores y Desafíos Técnicos
1. **Bloqueo de Base de Datos (`database is locked`):** Excepciones lanzadas por CHECK constraints de SQLite en el backend interrumpían el flujo antes de que la conexión pudiera cerrarse (`conn.close()`), dejando la base de datos bloqueada para operaciones concurrentes.
2. **Pérdida de Datos en Pytest con `:memory:`:** Al probar funciones que abren y cierran conexiones múltiples veces, la base de datos `:memory:` de SQLite se destruía entre transacciones, provocando errores `no such table`.

### Mejoras Aplicadas al Swarm y Desarrollo
- **Manejador de Transacciones Seguro:** Introducción de un context manager (`@contextlib.contextmanager`) en la persistencia del backend que asegura transacciones limpias (`commit`/`rollback`) y garantiza el cierre (`close`) de conexiones en el bloque `finally` bajo cualquier excepción.
- **Persistencia Física en Pruebas:** Modificación de fixtures de pytest para utilizar un archivo de base de datos temporal físico (`test_contratista_temp.db`) que se elimina limpiamente en el teardown del fixture.
- **ASR & NLP local responsivo:** Implementación de procesamiento inteligente local en JS/Python basado en expresiones regulares para evitar la dependencia de APIs pagas o latencia de red en campo.
