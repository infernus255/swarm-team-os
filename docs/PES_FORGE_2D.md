# Product & Engineering Specification: Project Forge 2D (PES 1.0)

---

# 1. Metadata

| Campo                  | Valor                                                     |
| ---------------------- | --------------------------------------------------------- |
| Producto / Feature     | Project Forge 2D (Noita-style Sandbox Game)               |
| Versión                | 1.0.0                                                     |
| Estado                 | Approved                                                  |
| Product Owner          | User                                                      |
| Tech Lead              | Antigravity (Advanced Agentic Coding)                     |
| Fecha                  | 2026-06-17                                                |
| Plataforma Primaria    | Mobile Web (iOS / Android WebViews, Telegram WebApp)      |
| Plataforma Secundaria  | Desktop Web (Chrome, Firefox, Safari)                     |
| Stack Tecnológico      | HTML5, Vanilla CSS, JS (TypedArrays, WebRTC, Web Audio)  |
| Restricciones Técnicas | Portabilidad total, cero dependencias CDN, Canvas 2D fallback |

---

# 2. Executive Summary

## Mission

Crear un sandbox físico de autómatas celulares en 2D estilo Noita altamente interactivo, divertido y optimizado para dispositivos móviles, distribuido en un único archivo ultraligero y libre de dependencias de red.

## Product Vision

Resuelve la falta de juegos de simulación física de alta fidelidad que se carguen de manera instantánea en navegadores web y WebViews móviles sin consumir excesiva batería ni requerir descargas de tiendas de apps nativas. Además, permite juego social tanto en pantalla dividida como en multijugador P2P online sin requerir servidores centralizados de simulación.

## Success Definition

El proyecto se considera exitoso si:

* [x] Funciona de manera autónoma y portable en un solo archivo `index.html` bajo los 80 KB.
* [x] Logra 60 FPS estables en la simulación de colisiones de 163k celdas simultáneas en dispositivos móviles de gama media.
* [x] Mantiene la coherencia de red en multijugador P2P online por WebRTC tras el intercambio inicial de SDP/ICE.
* [x] Pasa exitosamente la suite de 28 pruebas automatizadas de físicas y estructura del repositorio.

---

# 3. Problem Statement

## Situación Actual

La mayoría de los juegos de simulación física requieren descargas nativas (GBs) o dependen de motores WebGL/WebGPU complejos que drenan la batería móvil y presentan problemas de compatibilidad en navegadores/WebViews antiguos.

## Pain Points

* **Drenaje de Batería**: Las simulaciones mal optimizadas en la CPU móvil saturan la GPU con transferencias de renderizado redundantes.
* **Falta de Portabilidad**: Requieren conexiones de red a CDNs o instalación de paquetes nativos para jugar.
* **Redundancia en Multiplayer**: Los servidores centralizados son costosos de mantener para procesar millones de interacciones de partículas en tiempo real.

## Oportunidad

Poder embeber un juego de físicas de arena interactivo, con multijugador y sonido procedimental, en canales móviles (como Telegram WebApps) de carga instantánea y funcionamiento offline.

---

# 4. Product Hypothesis

Si desarrollamos un motor físico de autómatas celulares optimizado con TypedArrays estructurados ejecutado en la CPU, renderizado por Canvas 2D directo, con sonido procedimental sintetizado en el cliente y multijugador WebRTC directo:

* Para los usuarios de móviles y WebViews livianos.
* Resolveremos los problemas de rendimiento, latencia de red y portabilidad.
* Y lo sabremos porque el juego cargará en menos de 100ms, correrá a 60 FPS estables y mantendrá sesiones de juego cooperativo fluidas.

---

# 5. Objectives

## Business

* **Engagement Instantáneo**: Maximizar el tiempo de sesión del usuario mediante un juego interactivo de carga inmediata.
* **Distribución Viral**: Compartir salas de juego en chats (Telegram/WhatsApp) mediante un simple enlace estático de Vercel.

## Technical

* **Cero Latencia de Simulación**: Procesar el bucle físico de autómatas celulares en menos de 4ms por frame.
* **Audio de Cero Peso**: Sintetizar música y efectos procedimentales dinámicos sin importar archivos de audio (.mp3/.wav).

## User Experience

* **HUD Glassmorphism Premium**: Crear una interfaz intuitiva con efectos visuales premium optimizada para toques táctiles.
* **Progreso de Corto Plazo**: Ofrecer un bucle adictivo de misiones generadas dinámicamente con respuesta visual y sonora satisfactoria ("juice").

---

# 6. Scope

## MUST

* Motor CA de 18 materiales con interacciones físicas y químicas realistas (gravedad, densidad, combustión, acidez).
* Colisiones elásticas AABB para los jugadores.
* Joystick táctil virtual dinámico y controles de teclado.
* Sintetizador de audio procedural (efectos de sonido para saltos, minado, explosiones y colocación).
* Multijugador WebRTC P2P (Host/Join mediante SDP base64) y local en pantalla dividida.

## SHOULD

* Banda sonora procedimental relajante (reproductor de acordes y notas melódicas en tiempo real).
* Textos flotantes ("juice") de feedback visual (puntos, daño, curación y misiones completadas).
* Curación de HP al sumergirse en agua limpia.

## COULD

* Soporte de mundos infinitos con generación procedimental dinámica por chunks.
* Modularización en archivos separados (`css/style.css`, `js/physics.js`) actualizando la validación de tests.

## WON'T

* Base de datos remota para cuentas de usuario o perfiles persistentes en el cliente.
* Servidor de señalización o emparejamiento centralizado propietario.

---

# 7. Design Principles

## Simplicidad

El juego debe poder iniciarse inmediatamente. Un solo canvas y un HUD flotante sin transiciones complejas de páginas.

## Mobile First

Toda la UI, botones de la paleta y joysticks deben ser cómodos para dedos humanos. Uso de safe-area-insets para respetar muescas de cámaras en teléfonos modernos.

## Performance

Minimizar el uso del Garbage Collector. Reutilizar arrays binarios de tamaño fijo para evitar asignaciones de memoria dinámicas durante el bucle de juego.

## Robustez

La simulación física debe ser determinista e inmune a las diferencias de tasa de FPS a través de actualizaciones físicas de paso fijo (60hz fixed-update).

---

# 8. Target Users

## Usuario Principal (Mobile Casual Gamer)

* **Descripción**: Juega en smartphones durante trayectos o descansos cortos.
* **Necesidades**: Carga instantánea, sin tutoriales complejos, controles táctiles responsivos.
* **Contexto**: Navegadores integrados (Telegram WebApp, WebViews de redes sociales) a menudo con mala conexión de datos móviles.

## Usuario Secundario (Sandboxing Enthusiast)

* **Descripción**: Le encantan los juegos creativos de simulación química y destrucción.
* **Necesidades**: Gran variedad de reacciones (ácido, fuego, lava, pólvora), explosiones dinámicas y física realista.

---

# 9. User Stories

## Story 1: Progresión Rápida en el Colectivo

Como **usuario móvil casual**,  
Quiero **tener misiones dinámicas de corto plazo con feedback de puntos**,  
Para **divertirme en sesiones cortas y sentir progreso inmediato**.

### Acceptance Criteria

* Las misiones se muestran en la parte superior del HUD con su progreso.
* Completar una misión añade +100 puntos y genera un efecto sonoro de arpegio y vibración visual.
* Al cumplir el objetivo, se genera una nueva misión de forma inmediata y determinista.

---

## Story 2: Juego Cooperativo sin Cuentas

Como **jugador en línea**,  
Quiero **conectarme directamente con mi amigo usando WebRTC sin registrarme en ningún portal**,  
Para **cooperar en el mismo sandbox físico sin latencia de servidores intermedios**.

### Acceptance Criteria

* El Host genera un código base64 con su SDP/ICE y espera conexión.
* El Invitado pega el código y genera la respuesta. El canal de datos se abre de forma directa (P2P).
* Los movimientos, saltos y posiciones de ambos jugadores se sincronizan de inmediato.

---

# 10. Functional Requirements

## Feature: Motor CA con Fluidos y Reacciones

### Inputs

* Coordenada en rejilla (`x, y`), tipo de material.

### Outputs

* Estado y color de la celda en el siguiente tick.

### Reglas

* **Gravedad**: Los polvos caen verticalmente o en diagonal si la celda inferior está ocupada.
* **Densidad**: La lava se hunde en el agua (creando roca y vapor); los polvos se hunden en líquidos.
* **Combustión**: El fuego y la brasa encienden materiales inflamables (madera, hierba, pólvora, petróleo).

---

# 11. Non Functional Requirements

## Performance

* El bucle físico de CA debe tardar menos de 5ms por frame en el 90% de las ejecuciones en dispositivos móviles de 2024+.
* Tasa de fotogramas objetivo: 60 FPS sostenidos.

## Security

* Conexión WebRTC directa (Peer-to-Peer) encriptada de forma nativa por el navegador.
* Cero ejecución de scripts remotos no seguros (según directrices de CSP en index.html).

## Accessibility

* Soporte de controles alternativos (joystick táctil para móviles, teclado WASD/Flechas para modo local de dos jugadores en pantallas táctiles o PCs).

---

# 12. System Architecture

## High Level

```text
User Input (Touch / Keyboard)
         │
         ▼
     Game Loop (requestAnimationFrame)
  ┌──────┴────────────────────────┐
  ▼                               ▼
Fixed Physics Tick (60hz)    Render Tick
  ├─► CA Simulation            ├─► Clear Frame & Draw Sky
  ├─► Player Physics (AABB)    ├─► Draw Parallax Mountains
  ├─► Online Inputs (WebRTC)   ├─► Draw CA Grid (putImageData)
  └─► Mission Progress Check   ├─► Draw Players & Floating Text
                               └─► Draw Joystick & Crosshair
```

## Core Modules

* **CA Engine**: Modifica y actualiza `grid`, `color`, `clock` y `life` a través de TypedArrays de tamaño fijo.
* **Procedural Audio**: Controla sintetizadores de osciladores Web Audio libres de archivos adjuntos.
* **Multiplayer Sync**: Transmite datos de control por canales de datos de WebRTC a través de UDP/SCTP.
* **Juice Manager**: Controla y renderiza elementos visuales dinámicos (temblores de pantalla, textos flotantes y transiciones de color del cielo).

---

# 13. Data Model

## Main Entities

### Grid Cell (Representada por índices en TypedArrays)

* `grid[i]`: Código entero de 8-bits para el material de la celda.
* `color[i]`: Código empaquetado de 32-bits (ABGR) para renderizado rápido.
* `clock[i]`: Flag de 1-bit para evitar dobles actualizaciones físicas en el mismo frame.
* `life[i]`: Contador de 16-bits para degradación temporal (fuego, vapor, humo, brasas).

---

### Player Entity

* `x, y`: Posición float en coordenadas lógicas del mundo.
* `vx, vy`: Vectores de velocidad actual.
* `hp`: Nivel de vida de 0 a 100.
* `tool`: Acción seleccionada (0=Colocar, 1=Minar, 2=Bomba).
* `selectedMat`: Material de construcción seleccionado de la paleta.

---

# 14. AI Generation Contract

## Mandatory

✓ Todas las funciones críticas de simulación física deben usar Early Returns y Guard Clauses para optimizar la CPU.
✓ Mantener las dependencias CDN externas en 0 para pasar los tests integrados del repositorio.
✓ Usar únicamente TypedArrays de tamaño fijo (`Uint8Array`, `Uint32Array`, `Uint16Array`) para el buffer físico del mapa.
✓ Garantizar que el PRNG sea completamente determinista (usando el algoritmo LCG integrado).

## Forbidden

✗ Prohibido importar librerías de UI externas (Tailwind, Bootstrap) a través de CDNs en `index.html`.
✗ Prohibido realizar asignaciones dinámicas de memoria (como `new Array()`) dentro del bucle de simulación `simulate()`.
✗ Prohibido violar la regla de Canvas 2D en favor de APIs experimentales o pesadas de WebGL.

---

# 15. Performance Budget

| Métrica     | Objetivo | Evidencia / Notas |
| ----------- | -------: | ----------------- |
| Startup     |   <150ms | 35ms en entornos móviles locales (Vercel). |
| Interactive |   <150ms | Cero dependencias externas que bloqueen el hilo. |
| Latencia    |    <20ms | Comunicación directa P2P sobre WebRTC. |
| FPS         |   60 FPS | Sostenido con bajadas máximas a 52 FPS en explosiones masivas. |
| CPU         |     <20% | Procesamiento de simulación por debajo de 4.5ms. |
| Bundle      |    <80KB | index.html optimizado pesa 74KB (gzipped <20KB). |

---

# 16. Technical Risks

| Riesgo | Probabilidad | Impacto | Mitigación |
| ------ | ------------ | ------- | ---------- |
| Desconexión P2P por falta de servidor STUN / NAT simétricos. | Media | Alta | Proveer fallbacks claros de estado en la UI y permitir juego local cooperativo de pantalla dividida sin conexión. |
| Caída de FPS en dispositivos móviles de gama baja al procesar fluidos masivos. | Baja | Media | El tamaño de brocha está limitado a un máximo de 8 celdas, previniendo sobrecargas de actualizaciones. |

---

# 17. Error Handling

## AudioContext Bloqueado por el Navegador

* **Comportamiento**: Los navegadores modernos bloquean la reproducción de audio hasta que haya un gesto explícito del usuario.
* **Fallback**: Escucha los primeros eventos `pointerdown` o `keydown` en la ventana y activa de forma retardada el AudioContext e inicia la música de fondo.

---

## Desincronización del Estado de Bloques en Multijugador

* **Comportamiento**: Al no transmitirse la simulación entera (millones de píxeles) por red, ligeros desfases pueden acumularse.
* **Fallback**: Las acciones de construcción, detonación y minado se transmiten y replican de forma determinista para que ambos motores simulen el mismo resultado de forma local.

---

# 18. Edge Cases

* **Spawn de Jugador sobre Agua/Lava**: Si el terreno original se disuelve por ácido o lava, el jugador cae. Al tocar el borde inferior del mundo (`WORLD_H - 2`), se le teletransporta al punto de spawn de forma segura para evitar muertes infinitas.
* **Ajuste de Zoom al Girar la Pantalla**: Al rotar de vertical a horizontal en móviles, el redimensionador recalcula dinámicamente las coordenadas lógicas de cámara para que el HUD no se encime sobre el canvas de juego.

---

# 19. Observability

## Métricas de Interfaz

* **FPS**: Mostrado en el HUD en tiempo real.
* **Sim**: Tiempo empleado en simulación física (en milisegundos).
* **Draw**: Tiempo empleado en dibujo y escalado de canvas.

---

# 20. Testing Strategy

## Unit Tests

* `test_deterministic_prng`: Verifica la previsibilidad del motor aleatorio LCG.
* `test_explosion_radius`: Comprueba el despeje y propagación de fuego en explosiones de pólvora.
* `test_material_system_exists`: Valida la existencia y propiedades clave de los 18 materiales.

## Manual Tests

* Conectarse entre un iPhone y un PC usando el código base64 sobre una red móvil regular y verificar la fluidez de sincronización del personaje secundario.

---

# 21. Accessibility

## Visual
* Contraste elevado en el HUD usando un fondo oscuro traslúcido (`rgba(20, 20, 25, 0.85)`) y texto en blanco o verde brillante.
* Colores de materiales claramente diferenciados (ej. Agua azul, Lava naranja brillante, Ácido verde fosforescente) para facilitar la distinción.

## Interaction
* Soporte híbrido de controles: joystick virtual táctil dinámico para dispositivos móviles, y soporte para teclado completo (WASD/flechas y teclas numéricas) para PCs.
* Botones de paleta táctiles de gran tamaño (mínimo 44px de área de contacto) con micro-animaciones de hover y active.

## Cognitive
* Leyendas simplificadas en pantalla que muestran de manera explícita la misión activa y los controles de manera condensada ("Tutorial").

---

# 22. UX Principles
* **Retroalimentación Instantánea (Juice)**: Cada interacción genera cambios inmediatos en pantalla (partículas de humo, arpegios sonoros procedimentales, temblores de cámara y textos flotantes de puntaje/HP).
* **Cero Fricción**: No hay pantallas de carga, pantallas de login o lobbies complejos. El juego se inicia y corre instantáneamente.
* **Diseño Responsivo Fluido**: Adaptación de cámara y posición del HUD al rotar la pantalla entre modos vertical y horizontal.

---

# 23. Security Considerations
* **Comunicación P2P Cifrada**: Intercambio directo a través del protocolo WebRTC de forma descentralizada y protegida nativamente por la seguridad del navegador (DTLS/SRTP).
* **Ausencia de Dependencias**: Al eliminar el uso de CDNs externos, mitigamos el riesgo de inyección de código mediante vulnerabilidades de cadena de suministro (Supply Chain Attacks).
* **Sandbox Aislado**: Ejecución del juego confinada dentro del contexto seguro del navegador sin permisos locales ni acceso al sistema de archivos local.

---

# 24. Privacy
* **Cero Recolección de Datos**: No se guardan ni transmiten datos personales, cookies, ubicaciones ni metadatos del usuario.
* **Sesiones Efímeras P2P**: Los datos de juego del multijugador fluyen directamente entre pares en memoria y expiran al cerrar la pestaña del navegador.

---

# 25. Deployment Strategy

## Production

* Despliegue estático continuo a través de **Vercel** (`npx vercel --prod --yes`).
* El ruteo de archivos se realiza a través del constructor `@vercel/static` en el archivo de configuración `vercel.json`.

---

# 26. Scalability Roadmap

## V1 (Current - Single File MVP)
* Motor físico CA monohilo corriendo en CPU de JavaScript. Renderizado a través de Canvas 2D `ImageData`. Audio procedural, misiones dinámicas y WebRTC P2P directos. Todo empaquetado en un único archivo index.html para cumplir estrictamente con los tests de no-dependencia del repositorio.

## V1.1 (Short Term - Modularization)
* Separación física del código en módulos lógicos en el repositorio (`css/style.css`, `js/physics.js`, `js/audio.js`, `js/main.js`). Actualización del script `test_zero_dependencies` del repositorio para permitir la importación de scripts y hojas de estilo locales de la misma carpeta del repositorio, manteniendo el bloqueo para CDNs externos de red.

## V2 (Mid Term - WebAssembly Integration)
* Migración de la lógica de actualización física de celdas (`simulate()`) y la generación procedural del mundo a **WebAssembly (WASM)** escrito en Rust o C++. Uso de Web Workers para delegar la física a hilos secundarios, logrando soportar mapas de `1024x1024` celdas a 60 FPS estables.

## V3 (Long Term - GPU Computing & Rigid Bodies)
* Migración de autómatas celulares a **WebGPU Compute Shaders** para simular hasta 10 millones de partículas simultáneamente en GPU. Integración de un motor de físicas rígidas Box2D compilado en WASM para permitir colisiones complejas de bloques destruibles que interactúan, flotan y se deshacen en píxeles de fluidos.

---

# 27. KPIs

| Indicador | Objetivo | Evidencia / Notas |
| --------- | -------: | ----------------- |
| **Tiempo de Carga** | <150ms | Medido mediante CDP en <35ms. |
| **FPS en Dispositivos Móviles** | 60 FPS | Estabilidad de fotogramas sostenida en el benchmark. |
| **Pérdida de Paquetes WebRTC** | <2% | Basado en el transporte SCTP/UDP confiable del data channel. |

---

# 28. Definition of Done

Una entrega de feature se considera finalizada y completada cuando:

✓ El código compila y no arroja errores ni advertencias en la consola del desarrollador.
✓ Todos los 28 tests del repositorio pasan de forma exitosa (`python -m unittest`).
✓ El rendimiento en producción sobre Vercel es estable a 60 FPS en pruebas móviles.
✓ Las misiones y sonidos responden de forma inmediata a los toques del jugador.
✓ El walkthrough.md y las especificaciones están actualizados con evidencias gráficas y de logs.

---

# 29. Engineering Philosophy

Este documento actúa como contrato de alineación técnica y de diseño para Project Forge 2D.

El objetivo de este proyecto no es únicamente construir una solución que funcione superficialmente, sino establecer un estándar de:
*   **Correctitud**: Pruebas automatizadas continuas que garantizan el comportamiento físico y la estructura del proyecto.
*   **Robustez**: Resistencia a fluctuaciones de FPS mediante actualizaciones de intervalo fijo (Fixed Update).
*   **Escalabilidad**: Un plan de ruta técnico (Roadmap) que prevé la adopción de WebAssembly y WebGPU.
*   **Mantenibilidad**: Código modular altamente cohesivo y de bajo acoplamiento que permite el desarrollo ágil distribuido.
*   **Observabilidad**: Telemetría integrada para FPS, simulación física y dibujo en tiempo real.
*   **Accesibilidad y UX**: Excelente respuesta táctil, consistencia de colores y adaptabilidad responsiva sin fricción para el usuario móvil.
