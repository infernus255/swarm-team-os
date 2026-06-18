# 🎮 Swarm Jump AAA: Game Design Document (GDD)

## 🎯 1. VISIÓN Y CONCEPTO
**Swarm Jump AAA** es un juego *Hybrid-Casual* diseñado para sesiones ultra-rápidas (30s) con una estética pulida de "Ingeniería Limpia". El jugador controla un "Enjambre de Bits" que debe saltar obstáculos y atravesar puertas multiplicadoras para maximizar su tamaño antes de llegar al mainframe final.

### Premisa "Triple AAA Express"
- **Visuales**: Minimalismo premium con gradientes ASMR y feedback de partículas.
- **Divertido**: Satisfacción instantánea al ver el enjambre crecer de 1 a 500 unidades.
- **Fácil/Intuitivo**: Control de una sola mano (Swipe Horizontal).

---

## 🏗️ 2. ANÁLISIS DE MERCADO VS. ALTERNATIVAS

| Plataforma | Facilidad de Desarrollo | Calidad Visual | Facilidad de Testeo | Decisión |
| :--- | :---: | :---: | :---: | :--- |
| **APK Nativo (Kotlin/Java)** | ❌ Baja | ✅ Alta | ❌ Difícil (requiere emulador) | Descartado por fricción. |
| **Telegram Bot (WebApp)** | ✅ Alta | ✅ Media | ✅ Fácil (Multiplataforma) | **GANADOR (PWA)** |
| **Web PWA (Three.js/Canvas)** | ✅ Alta | ✅ Alta | ✅ Instantáneo (Chrome/Safari) | **GANADOR (PWA)** |

**Decisión Arquitectónica**: Usaremos **HTML5 Canvas + Vanilla JS (E2E Ready)**. Se puede jugar en el navegador del móvil, dentro de un bot de Telegram, o empaquetado como APK con un WebView.

---

## 🕹️ 3. MECÁNICAS CORE
1.  **Movimiento**: El enjambre avanza automáticamente. El usuario desliza el dedo horizontalmente para moverlo.
2.  **Puertas Multiplicadoras**: 
    *   Puerta Azul: `x2`, `x5` (Aumenta el enjambre).
    *   Puerta Roja: `-10`, `/2` (Disminuye el enjambre).
3.  **Obstáculos**: Si un bit toca un obstáculo, desaparece.
4.  **Meta (Mainline)**: Cuantos más bits lleguen, mayor es el puntaje de "Sincronización SGA".

---

## 🧪 4. ESTRATEGIA DE VALIDACIÓN (E2E)
El juego se testeará usando un script determinista que simula eventos de "touch" y valida que el puntaje y el tamaño del enjambre respondan a las leyes físicas del juego.
- **Test 01**: Colisión con puerta `x2` -> ¿El enjambre se duplicó?
- **Test 02**: Rendimiento -> ¿Corre a 60FPS en dispositivos gama baja (Pentium/Xiaomi)?

---

## 📅 5. ROADMAP EXPRESS
1.  **Fase 1**: Prototipo funcional (Cuadros de colores + Lógica de puertas).
2.  **Fase 2**: Pulido visual (Efectos ASMR + Gradientes "Elite").
3.  **Fase 3**: Empaquetado y Deploy (PWA + Telegram WebApp link).

---
*Documento aprobado por Jarvis para SwarmTeam OS.*
