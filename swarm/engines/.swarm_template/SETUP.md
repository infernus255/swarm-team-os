# Guía de Setup y Arranque

Para inicializar un nuevo proyecto utilizando el ROO-CODE-SWARM, sigue estos pasos:

## 1. Preparación del Entorno
1. Clona este repositorio template en tu máquina local.
2. Asegúrate de tener Node.js instalado (para la posterior ejecución del arnés `swarm_flow_orchestrator.js`).
3. Renombra la carpeta raíz con el nombre de tu nuevo proyecto.

## 2. Inicialización del Enjambre
El enjambre depende de la configuración de roles y permisos. 
1. Verifica que el archivo `.roomodes` en la raíz esté correctamente mapeado en tu extensión de entorno (Roo Code / Claude / Cursor).
2. Asegúrate de que las rutas dentro de `.roomodes` apunten correctamente a `.swarm/specs/` y `app_result/`.

## 3. Arrancando el Proyecto
Tienes dos formas de iniciar:

### Opcion A: Modo HITL (Interactivo - Recomendado)
1. Abre un chat con el agente **Orquestador Central**.
2. Escribe el comando: `"Inicia el proyecto en modo Greenfield HITL con el siguiente requerimiento: [PEGA TU PROMPT DE NEGOCIO AQUI]"`.
3. El Orquestador despertará a **M0** para iniciar la entrevista funcional.

### Opción B: Modo Ingeniería Inversa (Legacy)
1. Copia tu código fuente existente dentro de una carpeta llamada `app_legacy/` en la raíz.
2. Abre un chat con el **Orquestador Central**.
3. Escribe el comando: `"Inicia el flujo de Ingeniería Inversa sobre la carpeta /app_legacy"`.
4. El Orquestador se saltará a M0 y despertará a **M1** para analizar el código.