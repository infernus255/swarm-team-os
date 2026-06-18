# 🏺 Project Forge 2D — SwarmTeam OS

**Un sandbox de físicas de autómatas celulares estilo Noita**, jugable en el navegador con multijugador WebRTC P2P, modo historia con lore del Antiguo Egipto cibernético, y cero dependencias de CDN.

🌐 **Demo en vivo:** [project-forge-2d.vercel.app](https://project-forge-2d.vercel.app)

---

## 🎮 Features del Juego

- **18 materiales** con física y química (arena, agua, lava, ácido, pólvora, hielo...)
- **Modo Historia** — Civilización egipcia cibernética: busca 3 reliquias, derrota al Pharaoh Guardian
- **Multijugador WebRTC P2P** — host/join directo con link `#join=...` sin servidor
- **Co-op local** en pantalla dividida (WASD + Flechas)
- **3 biomas** — Superficie, Cavernas de Cristal, Cuevas de Veneno + Reactor Geotérmico
- **Mecánicas avanzadas** — Cyber-dash (Space), báculo elemental (fire/acid/ice/plasma), torretas obelisco
- **Dificultad configurable** — Fácil / Normal / Difícil + modo Sandbox libre

---

## 🗂️ Estructura del Repositorio

```
├── index.html              # Entry point — shell HTML + constantes de juego
├── css/
│   └── style.css           # Glassmorphism HUD, animaciones, layout responsivo
├── js/
│   ├── physics.js          # Motor CA: materiales, simulate(), generateWorld()
│   ├── audio.js            # Web Audio API: música procedural + SFX
│   ├── multiplayer.js      # WebRTC P2P: host/join, data channel, sync
│   ├── game.js             # Game loop, Player, Enemy, Projectile, Item, Game
│   └── main.js             # Bootstrap: new Game()
├── wasm_engine/            # (V2) Motor de física en Rust/WASM — scaffold listo
│   ├── Cargo.toml
│   ├── src/lib.rs
│   └── build_wasm.ps1
├── docs/
│   └── PES_FORGE_2D.md     # Product & Engineering Specification completa (PES 1.4)
├── tests/
│   ├── test_physics_simulation.py   # 33 tests de física, gameplay y estructura
│   ├── test_mobile_game.py          # 4 tests de HTML, dependencias y módulos
│   └── test_repo_validation.py      # 4 tests de validación del repo
├── scratch/
│   ├── play_game_e2e.js             # E2E Playwright — gameplay completo
│   ├── play_local_mp_e2e.js         # E2E co-op local
│   └── play_multiplayer_e2e.js      # E2E WebRTC P2P end-to-end
├── vercel.json             # Config de deployment estático
├── requirements.txt        # Dependencias Python (tests + swarm core)
└── package.json            # Dependencias Node.js (Playwright E2E)
```

---

## ⚡ Quick Start — Replicar en un nuevo entorno

### 1. Clonar el repositorio
```bash
git clone https://github.com/infernus255/swarm-team-os.git
cd swarm-team-os
git checkout feat/mobile-game
```

### 2. Instalar dependencias Python (tests)
```bash
pip install -r requirements.txt
```

### 3. Instalar dependencias Node.js (E2E Playwright)
```bash
npm install
npx playwright install chromium
```

### 4. Correr el juego localmente
```bash
# Cualquiera de estas opciones sirve:
npx serve .                         # Node.js simple HTTP server
python -m http.server 8080          # Python built-in
npx vercel dev                      # Vercel dev server (replica producción)
```
Luego abrir: `http://localhost:3000` (o el puerto que indique el servidor)

### 5. Correr los tests
```bash
# Unit tests (37 tests)
python -m unittest discover -s tests

# E2E Playwright (requiere Node.js y Chromium instalado)
node scratch/play_game_e2e.js
node scratch/play_local_mp_e2e.js
node scratch/play_multiplayer_e2e.js
```

---

## 🚀 Deploy a Vercel

```bash
# Primera vez — crear proyecto (interactive)
npx vercel

# Deploy a producción
npx vercel --prod --yes
```

**El juego es 100% estático** — cualquier hosting de archivos estáticos sirve (Vercel, Netlify, GitHub Pages, Nginx, Apache).

---

## 🦀 Motor WebAssembly (Roadmap V2 — Opcional)

El directorio `wasm_engine/` contiene el motor de física reescrito en Rust, listo para compilar:

```bash
# Prerequisitos
rustup target add wasm32-unknown-unknown
cargo install wasm-pack

# Build
./wasm_engine/build_wasm.ps1         # Windows (PowerShell)
# o manualmente:
cd wasm_engine && wasm-pack build --target web --release --out-dir ../wasm_pkg
```

---

## 🧪 Estado de Tests

```
Ran 37 tests in ~0.12s — OK  ✅
E2E Gameplay:     ✅  FPS ~52, Sim ~1.8ms, 0 errores JS
E2E Co-op local:  ✅  P2 spawneado y sincronizado
E2E WebRTC P2P:   ✅  Conexión directa + sync de movimiento
```

---

## 🏛️ Lore — Civilización Kemet-Delta

La antigua civilización **Kemet-Delta** dominó una forma de energía solar concentrada llamada **Ra-Flux**. Su desaparición fue causada por la corrupción de su **Reactor Geotérmico Central**, custodiado por el **Pharaoh Guardian** — una entidad cibernética de 400 HP.

Para acceder al reactor en modo historia debes encontrar:
- ☥ **Ankh de Vida** — bioma Superficie (cofre dorado)
- 👁️ **Ojo de Horus** — Cavernas de Cristal (cofre cian)
- 🪲 **Escarabajo de Poder** — Cuevas de Veneno (cofre verde)

---

## 🔧 Stack Técnico

| Componente | Tecnología |
|-----------|-----------|
| Física / Simulación | JavaScript ES2022, TypedArrays (Uint8Array, Uint32Array) |
| Renderizado | Canvas 2D (`putImageData`) |
| Audio | Web Audio API (osciladores procedurales, sin archivos .mp3) |
| Multijugador | WebRTC Data Channel (P2P, sin servidor de relay) |
| Estilo | Vanilla CSS (Glassmorphism, CSS Custom Properties) |
| Tests | Python `unittest`, Playwright |
| Deploy | Vercel (static) |
| WASM (V2) | Rust + `wasm-bindgen` + `wasm-pack` |

**Cero dependencias de CDN** — funciona 100% offline tras la primera carga.

---

## 📐 Especificación Técnica

Ver [docs/PES_FORGE_2D.md](docs/PES_FORGE_2D.md) para la especificación completa de producto e ingeniería (PES 1.4), incluyendo roadmap V1→V3, KPIs, modelo de datos y principios de diseño.

---

*SwarmTeam OS · Project Forge 2D · PES 1.4 · feat/mobile-game*
