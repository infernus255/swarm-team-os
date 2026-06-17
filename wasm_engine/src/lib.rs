/*!
 * forge_simulation - WebAssembly Cellular Automata Physics Engine
 *
 * Project Forge 2D - Roadmap V2: WebAssembly Integration
 * Migrates the core `simulate()` loop from JavaScript to Rust/WASM
 * for 1024x1024 cell grid support at 60 FPS.
 *
 * Build:
 *   wasm-pack build --target web --out-dir ../wasm_pkg
 *
 * Usage in JS:
 *   import init, { simulate } from '../wasm_pkg/forge_simulation.js';
 *   await init();
 *   simulate(gridPtr, colorPtr, clockPtr, lifePtr, WORLD_W, WORLD_H);
 */

use wasm_bindgen::prelude::*;

// ──────────────────────────────────────────────────────────────────────────────
// Material IDs (must match js/physics.js MAT constants)
// ──────────────────────────────────────────────────────────────────────────────
const EMPTY: u8 = 0;
const SAND: u8 = 1;
const WATER: u8 = 2;
const STONE: u8 = 3;
const WOOD: u8 = 4;
const FIRE: u8 = 5;
const LAVA: u8 = 6;
const STEAM: u8 = 7;
const OIL: u8 = 8;
const ACID: u8 = 9;
const GUNPOWDER: u8 = 10;
const SMOKE: u8 = 11;
const DIRT: u8 = 12;
const GRASS: u8 = 13;
const GLASS: u8 = 14;
const ICE: u8 = 15;
const EMBER: u8 = 16;
const BEDROCK: u8 = 17;

// ──────────────────────────────────────────────────────────────────────────────
// Property type bitmasks (must match PROP_TYPE in physics.js)
//   1 = solid, 2 = powder, 3 = liquid, 4 = gas, 5 = special
// ──────────────────────────────────────────────────────────────────────────────
const PROP_TYPE: [u8; 18] = [
    0, // EMPTY
    2, // SAND  (powder)
    3, // WATER (liquid)
    1, // STONE (solid)
    1, // WOOD  (solid)
    5, // FIRE  (special)
    3, // LAVA  (liquid)
    4, // STEAM (gas)
    3, // OIL   (liquid)
    3, // ACID  (liquid)
    2, // GUNPOWDER (powder)
    4, // SMOKE (gas)
    2, // DIRT  (powder)
    2, // GRASS (powder)
    1, // GLASS (solid)
    1, // ICE   (solid)
    5, // EMBER (special)
    1, // BEDROCK (solid)
];

// ──────────────────────────────────────────────────────────────────────────────
// LCG PRNG - deterministic, matching JavaScript implementation
// ──────────────────────────────────────────────────────────────────────────────
static mut RNG_SEED: u32 = 1337;

#[inline(always)]
fn rng() -> f32 {
    unsafe {
        RNG_SEED = RNG_SEED.wrapping_mul(1664525).wrapping_add(1013904223);
        (RNG_SEED >> 8) as f32 / 16777216.0
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Helper: safe index into flat grid array
// ──────────────────────────────────────────────────────────────────────────────
#[inline(always)]
fn idx(x: i32, y: i32, w: i32, h: i32) -> Option<usize> {
    if x < 0 || y < 0 || x >= w || y >= h {
        return None;
    }
    Some((y * w + x) as usize)
}

/// Core cellular automata simulation step.
///
/// # Safety
/// The caller (JavaScript) must ensure that the pointers reference valid
/// SharedArrayBuffer / WebAssembly memory regions of the correct length:
///   - `grid`  : Uint8Array  of length `w * h`
///   - `clock` : Uint8Array  of length `w * h`
///   - `life`  : Uint16Array of length `w * h` (passed as u32 ptr, 2 bytes/cell)
///
/// This function is intentionally `unsafe` because it operates on raw pointers
/// shared with JavaScript via WebAssembly linear memory.
#[wasm_bindgen]
pub fn simulate(
    grid_ptr: *mut u8,
    clock_ptr: *mut u8,
    life_ptr: *mut u16,
    w: i32,
    h: i32,
    tick: u8,
) {
    let len = (w * h) as usize;
    let grid = unsafe { std::slice::from_raw_parts_mut(grid_ptr, len) };
    let clock = unsafe { std::slice::from_raw_parts_mut(clock_ptr, len) };
    let life = unsafe { std::slice::from_raw_parts_mut(life_ptr, len) };

    // Iterate bottom-up so gravity propagates correctly in a single pass
    for y in (0..h - 1).rev() {
        let dir: i32 = if rng() < 0.5 { 1 } else { -1 };
        let x_range: Vec<i32> = if dir == 1 {
            (0..w).collect()
        } else {
            (0..w).rev().collect()
        };

        for &x in &x_range {
            let i = match idx(x, y, w, h) {
                Some(v) => v,
                None => continue,
            };

            // Skip already-updated cells this tick
            if clock[i] == tick {
                continue;
            }

            let mat = grid[i];

            match mat {
                // ── Powders (sand, dirt, gunpowder, grass) ────────────────────
                m if PROP_TYPE[m as usize] == 2 => {
                    // Try to fall straight down
                    if let Some(bi) = idx(x, y + 1, w, h) {
                        if grid[bi] == EMPTY || PROP_TYPE[grid[bi] as usize] == 3 {
                            let tmp = grid[bi];
                            grid[bi] = mat;
                            grid[i] = tmp;
                            clock[bi] = tick;
                            continue;
                        }
                    }
                    // Try diagonal fall
                    let d1 = dir;
                    let d2 = -dir;
                    let mut fell = false;
                    for &dx in &[d1, d2] {
                        if let Some(di) = idx(x + dx, y + 1, w, h) {
                            if grid[di] == EMPTY || PROP_TYPE[grid[di] as usize] == 3 {
                                let tmp = grid[di];
                                grid[di] = mat;
                                grid[i] = tmp;
                                clock[di] = tick;
                                fell = true;
                                break;
                            }
                        }
                    }
                    let _ = fell;
                }

                // ── Liquids (water, lava, oil, acid) ──────────────────────────
                m if PROP_TYPE[m as usize] == 3 => {
                    // Try to fall down
                    if let Some(bi) = idx(x, y + 1, w, h) {
                        if grid[bi] == EMPTY {
                            grid[bi] = mat;
                            grid[i] = EMPTY;
                            clock[bi] = tick;
                            continue;
                        }
                    }
                    // Try to spread sideways
                    for &dx in &[dir, -dir] {
                        if let Some(si) = idx(x + dx, y, w, h) {
                            if grid[si] == EMPTY {
                                grid[si] = mat;
                                grid[i] = EMPTY;
                                clock[si] = tick;
                                break;
                            }
                        }
                    }
                }

                // ── Gas (steam, smoke) ─────────────────────────────────────────
                m if PROP_TYPE[m as usize] == 4 => {
                    // Gases rise
                    if let Some(ui) = idx(x, y - 1, w, h) {
                        if grid[ui] == EMPTY {
                            grid[ui] = mat;
                            grid[i] = EMPTY;
                            clock[ui] = tick;
                            continue;
                        }
                    }
                    // Random drift
                    let dx = if rng() < 0.5 { 1i32 } else { -1i32 };
                    if let Some(si) = idx(x + dx, y, w, h) {
                        if grid[si] == EMPTY {
                            grid[si] = mat;
                            grid[i] = EMPTY;
                            clock[si] = tick;
                        }
                    }
                    // Lifetime decay
                    if life[i] > 0 {
                        life[i] -= 1;
                    } else {
                        grid[i] = EMPTY;
                    }
                }

                // ── Fire / Ember ───────────────────────────────────────────────
                FIRE | EMBER => {
                    if life[i] > 0 {
                        life[i] -= 1;
                    } else {
                        grid[i] = if mat == FIRE { SMOKE } else { EMPTY };
                        continue;
                    }

                    // Rise as smoke when energy is low
                    if rng() < 0.08 {
                        if let Some(ui) = idx(x, y - 1, w, h) {
                            if grid[ui] == EMPTY {
                                grid[ui] = SMOKE;
                                life[ui] = 30 + (rng() * 30.0) as u16;
                                clock[ui] = tick;
                            }
                        }
                    }

                    // Ignite neighbors
                    for ny in [y - 1, y, y + 1] {
                        for nx in [x - 1, x, x + 1] {
                            if let Some(ni) = idx(nx, ny, w, h) {
                                let nm = grid[ni];
                                let ignites = matches!(nm, WOOD | GRASS | OIL | GUNPOWDER);
                                if ignites && rng() < 0.04 {
                                    grid[ni] = FIRE;
                                    life[ni] = 60 + (rng() * 80.0) as u16;
                                    clock[ni] = tick;
                                }
                            }
                        }
                    }
                }

                // ── Everything else: no movement ──────────────────────────────
                _ => {}
            }
        }
    }
}

/// Reset the internal PRNG seed (called at world generation to ensure
/// determinism across host and joiner in multiplayer sessions).
#[wasm_bindgen]
pub fn reset_rng(seed: u32) {
    unsafe {
        RNG_SEED = seed;
    }
}

/// Returns the wasm_engine build version string for health checks.
#[wasm_bindgen]
pub fn version() -> String {
    String::from("forge_simulation 0.1.0")
}
