# SHARED FOUNDATIONS (Memoria Inter-Proyectos)

Este archivo es el **repositorio global de conocimiento** del Swarm. Las lecciones aprendidas en ramas pasadas se consolidan aquí para que todo nuevo proyecto herede esta experiencia desde el Nodo M0.

El Orquestador debe consultar obligatoriamente este documento durante el arranque (Pre-flight) y pasarlo como contexto a los Agentes M2, M3 y M5.

---

## 1. Patrones de Sistema Operativo y Codificación
- **Windows y UTF-8**: Al ejecutar scripts en Python en entornos Windows (especialmente comandos interactivos o CLI tools), siempre se debe inyectar la variable de entorno `$env:PYTHONIOENCODING="utf-8"` en el comando de arranque. De lo contrario, los caracteres especiales (emojis, acentos) causarán un `UnicodeEncodeError`. Los archivos generados por M5 deben estar forzosamente codificados en UTF-8 sin BOM.
- **NLP Local vs APIs Externas**: En entornos con baja conectividad, procesar las transcripciones de voz locales en el cliente usando expresiones regulares optimizadas reduce la latencia de red a cero y abarata costes de infraestructura, proporcionando una usabilidad óptima en campo.

## 2. Persistencia y Bases de Datos
- **Migraciones SQLite (Constraints)**: SQLite no soporta la sintaxis `ALTER TABLE ... DROP CONSTRAINT` ni la adición de `CHECK` constraints en tablas existentes. Si la arquitectura requiere modificar un esquema, el agente M5 debe generar un script de migración que:
  1. Renombre la tabla actual a `_old`.
  2. Cree la nueva tabla con las restricciones actualizadas.
  3. Ejecute un `INSERT INTO ... SELECT ...` con transformación de datos (ej. mediante `CASE WHEN`).
  4. Haga `DROP` de la tabla vieja.
- **Locks de SQLite en Excepciones y Tests**: Si ocurre un fallo en los CHECK constraints, la excepción interrumpe la ejecución antes del cierre de la conexión, bloqueando la base de datos para futuras escrituras. Se debe forzar el cierre de las conexiones usando `try...finally` o manejadores de contexto transaccionales. Asimismo, en pytest, evitar bases de datos en `:memory:` si se abren y cierran conexiones múltiples veces; usar una ruta física temporal y borrarla en el teardown.

## 3. Concurrencia y Event Loops
- **Bots Asíncronos + Web Servers**: Cuando se desplieguen soluciones que combinen un bot (ej. Telegram con `python-telegram-bot`) y un servidor web (ej. `FastAPI`/`uvicorn`) en el mismo proceso, NO se deben usar métodos bloqueantes como `app.run_polling()`. Se debe utilizar `asyncio.gather()` para lanzar ambos servicios sobre el mismo *event loop* asíncrono y gestionar correctamente las señales de apagado graceful.

## 4. UI/UX y Dashboards
- **Diseños Modernos en Vanilla JS**: Al prescindir de frameworks pesados de Frontend, priorizar el uso de CSS Variables nativas, `backdrop-filter` para glassmorphism, y Flexbox/CSS Grid.
- **Micro-interacciones**: Para aplicaciones tipo Single Page Application (SPA), las interacciones (como clickear en una agenda) deben actualizar el DOM vía funciones JavaScript, hacer `scrollIntoView()` y animar colores de fila para mantener el contexto del usuario sin recargar la página.
- **Sincronización Offline y Conflictos**: Implementar una cola local (`syncQueue` en `localStorage` o `IndexedDB`) con reintentos automáticos gatillados por el evento `online` del navegador. Los conflictos deben manejarse de forma optimista con timestamps en el backend ("Last-Write-Wins") y marcarse visualmente como `conflict` en el cliente para alertar al usuario y que resuelva de forma rápida e interactiva.

---
*(Los agentes deben seguir agregando secciones "Key Decisions" agnósticas aquí cuando completen proyectos exitosos).*
