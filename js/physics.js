// =====================================================
// 1. CONSTANTS & CONFIGURATION
// =====================================================
const WORLD_W = 1024;
const WORLD_H = 320;
const GRAVITY = 0.4;
const PLAYER_SPEED = 1.8;
const PLAYER_JUMP = -4.5;
const PLAYER_W = 6;
const PLAYER_H = 12;
const MAX_HP = 100;
const INTERACTION_RANGE = 40;

// =====================================================
// 2. MATERIAL SYSTEM
// =====================================================
const MAT = {
    EMPTY:0, SAND:1, WATER:2, STONE:3, WOOD:4, FIRE:5, LAVA:6,
    STEAM:7, OIL:8, ACID:9, GUNPOWDER:10, SMOKE:11, DIRT:12,
    GRASS:13, GLASS:14, ICE:15, EMBER:16, BEDROCK:17,
    METAL:18, ELECTRICITY:19
};
const PROPS = [];
// type: 0=empty, 1=solid, 2=powder, 3=liquid, 4=gas, 5=special
PROPS[MAT.EMPTY]       = { n:'Vacio',    t:0, d:0,   fl:0, ar:1 };
PROPS[MAT.SAND]        = { n:'Arena',    t:2, d:5,   fl:0, ar:0 };
PROPS[MAT.WATER]       = { n:'Agua',     t:3, d:3,   fl:0, ar:1 };
PROPS[MAT.STONE]       = { n:'Piedra',   t:1, d:10,  fl:0, ar:0 };
PROPS[MAT.WOOD]        = { n:'Madera',   t:1, d:8,   fl:1, ar:0 };
PROPS[MAT.FIRE]        = { n:'Fuego',    t:5, d:-2,  fl:0, ar:1 };
PROPS[MAT.LAVA]        = { n:'Lava',     t:3, d:7,   fl:0, ar:1 };
PROPS[MAT.STEAM]       = { n:'Vapor',    t:4, d:-1,  fl:0, ar:1 };
PROPS[MAT.OIL]         = { n:'Petroleo', t:3, d:2,   fl:1, ar:0 };
PROPS[MAT.ACID]        = { n:'Acido',    t:3, d:3.5, fl:0, ar:1 };
PROPS[MAT.GUNPOWDER]   = { n:'Polvora',  t:2, d:4,   fl:1, ar:0 };
PROPS[MAT.SMOKE]       = { n:'Humo',     t:4, d:-1,  fl:0, ar:1 };
PROPS[MAT.DIRT]        = { n:'Tierra',   t:2, d:7,   fl:0, ar:0 };
PROPS[MAT.GRASS]       = { n:'Hierba',   t:2, d:7,   fl:1, ar:0 };
PROPS[MAT.GLASS]       = { n:'Cristal',  t:1, d:9,   fl:0, ar:1 };
PROPS[MAT.ICE]         = { n:'Hielo',    t:1, d:3,   fl:0, ar:1 };
PROPS[MAT.EMBER]       = { n:'Brasa',    t:2, d:2,   fl:0, ar:1 };
PROPS[MAT.BEDROCK]     = { n:'Roca',     t:1, d:99,  fl:0, ar:1 };
PROPS[MAT.METAL]       = { n:'Metal',    t:1, d:15,  fl:0, ar:1 };
PROPS[MAT.ELECTRICITY] = { n:'Rayo',     t:5, d:0,   fl:0, ar:1 };

// High-Performance Flat TypedArrays for hot simulation loops
const PROP_TYPE = new Uint8Array(20);
const PROP_DENSITY = new Float32Array(20);
const PROP_FLAMMABLE = new Uint8Array(20);
const PROP_ACID_RESIST = new Uint8Array(20);
const PROP_NAME = [];
for (let m = 0; m < 20; m++) {
    const p = PROPS[m];
    if (p) {
        PROP_TYPE[m] = p.t;
        PROP_DENSITY[m] = p.d;
        PROP_FLAMMABLE[m] = p.fl;
        PROP_ACID_RESIST[m] = p.ar;
        PROP_NAME[m] = p.n;
    }
}

// Palette materials player can place
const PALETTE = [MAT.SAND, MAT.WATER, MAT.STONE, MAT.WOOD, MAT.FIRE, MAT.OIL, MAT.GUNPOWDER, MAT.LAVA, MAT.ACID, MAT.DIRT, MAT.GLASS, MAT.ICE, MAT.EMBER, MAT.METAL];
const TOOL_PLACE = 0, TOOL_MINE = 1, TOOL_BOMB = 2, TOOL_STAFF = 3;
const TOOL_ICONS = ['🖌️','⛏️','💣','🔥'];

// Color generators (packed ABGR for little-endian Uint32Array → RGBA in ImageData)
function packC(r,g,b,a){return((a<<24)|(b<<16)|(g<<8)|r)>>>0;}
function matColor(m) {
    const v = (rng()*40-20)|0;
    switch(m) {
        case MAT.SAND:      return packC(194+v, 178+v, 128+v, 255);
        case MAT.WATER:     return packC(40+(v>>1), 110+v, 220+(v>>1), 195);
        case MAT.STONE:     return packC(120+v, 120+v, 125+v, 255);
        case MAT.WOOD:      return packC(90+v, 65+(v>>1), 35, 255);
        case MAT.FIRE:      return packC(255, 120+(rng()*80|0), 20, 230);
        case MAT.LAVA:      return packC(220+(v>>1), 80+v, 15, 240);
        case MAT.STEAM:     return packC(200+v, 210+v, 225+v, 90);
        case MAT.OIL:       return packC(30+v, 25+v, 18, 230);
        case MAT.ACID:      return packC(50+v, 210+v, 50, 210);
        case MAT.GUNPOWDER: return packC(55+v, 50+v, 50+v, 255);
        case MAT.SMOKE:     return packC(80+v, 80+v, 85+v, 80);
        case MAT.DIRT:      return packC(100+v, 70+v, 45, 255);
        case MAT.GRASS:     return packC(60+v, 140+v, 50, 255);
        case MAT.GLASS:     return packC(200+(v>>1), 220+(v>>1), 240, 70);
        case MAT.ICE:       return packC(180+v, 210+v, 240, 200);
        case MAT.EMBER:     return packC(200+v, 100+(rng()*40|0), 20, 200);
        case MAT.BEDROCK:   return packC(30+v, 30+v, 35+v, 255);
        case MAT.METAL:     return packC(160+v, 160+v, 175+v, 255);
        case MAT.ELECTRICITY: return packC(100+v, 200+v, 255, 255);
        default:            return 0;
    }
}
// CSS color for palette buttons
function matCSS(m) {
    switch(m) {
        case MAT.SAND: return '#c2b280'; case MAT.WATER: return '#2870dc';
        case MAT.STONE: return '#787878'; case MAT.WOOD: return '#5a4123';
        case MAT.OIL: return '#1e1912'; case MAT.GUNPOWDER: return '#373232';
        case MAT.LAVA: return '#dc5010'; case MAT.ACID: return '#32d232';
        case MAT.DIRT: return '#644628'; case MAT.GLASS: return '#c8dcf0';
        case MAT.ICE: return '#b4d2f0'; case MAT.FIRE: return '#ff6a00';
        case MAT.EMBER: return '#c85a00'; case MAT.METAL: return '#a0a0af';
        case MAT.ELECTRICITY: return '#64c8ff'; default: return '#444';
    }
}

// =====================================================
// 3. DETERMINISTIC PRNG (LCG)
// =====================================================
let rngState = 20260617;
function rng() { rngState = (rngState * 1664525 + 1013904223) & 0x7FFFFFFF; return rngState / 2147483647; }
function rngSeed(s) { rngState = s; }

// =====================================================
// 4. PERLIN-LIKE NOISE (for world gen)
// =====================================================
class Noise2D {
    constructor(seed) {
        this.p = new Uint8Array(512);
        const r = () => { seed = (seed * 16807 + 0) % 2147483647; return seed / 2147483647; };
        for (let i = 0; i < 256; i++) this.p[i] = i;
        for (let i = 255; i > 0; i--) { const j = (r() * (i+1))|0; [this.p[i], this.p[j]] = [this.p[j], this.p[i]]; }
        for (let i = 0; i < 256; i++) this.p[256+i] = this.p[i];
    }
    fade(t){return t*t*t*(t*(t*6-15)+10);}
    lerp(t,a,b){return a+t*(b-a);}
    grad(h,x,y){const v=h&7;const u=v<4?x:y;const w=v<4?y:x;return((v&1)?-u:u)+((v&2)?-w:w);}
    noise(x,y){
        const X=Math.floor(x)&255,Y=Math.floor(y)&255;
        x-=Math.floor(x);y-=Math.floor(y);
        const u=this.fade(x),v=this.fade(y);
        const A=this.p[X]+Y,B=this.p[X+1]+Y;
        return this.lerp(v,this.lerp(u,this.grad(this.p[A],x,y),this.grad(this.p[B],x-1,y)),this.lerp(u,this.grad(this.p[A+1],x,y-1),this.grad(this.p[B+1],x-1,y-1)));
    }
}

// =====================================================
// 5. CELLULAR AUTOMATA ENGINE
// =====================================================
const totalCells = WORLD_W * WORLD_H;
const grid  = new Uint8Array(totalCells);
const color = new Uint32Array(totalCells);
const clock = new Uint8Array(totalCells);
const life  = new Uint16Array(totalCells);
let frameClock = 0;

function idx(x, y) {
    if (y < 0 || y >= WORLD_H) return -1;
    x = ((x % WORLD_W) + WORLD_W) % WORLD_W; // horizontal wrap
    return y * WORLD_W + x;
}
function setCell(i, mat) {
    if (i < 0 || i >= totalCells) return;
    grid[i] = mat;
    color[i] = mat === MAT.EMPTY ? 0 : matColor(mat);
    clock[i] = frameClock;
    if (mat === MAT.FIRE) life[i] = 60 + (rng()*80|0);
    else if (mat === MAT.STEAM) life[i] = 120 + (rng()*100|0);
    else if (mat === MAT.SMOKE) life[i] = 80 + (rng()*60|0);
    else if (mat === MAT.EMBER) life[i] = 30 + (rng()*40|0);
    else if (mat === MAT.ELECTRICITY) life[i] = 5 + (rng()*10|0);
    else life[i] = 0;
}
function swap(a, b) {
    const tm = grid[a], tc = color[a], tl = life[a];
    grid[a] = grid[b]; color[a] = color[b]; life[a] = life[b]; clock[a] = frameClock;
    grid[b] = tm; color[b] = tc; life[b] = tl; clock[b] = frameClock;
}
function canDisplace(mover, target) {
    if (target === MAT.EMPTY) return true;
    const tt = PROP_TYPE[target];
    if (tt === 1) return false; // can't displace solids
    const mt = PROP_TYPE[mover];
    if (mt === 2 && tt >= 3) return true; // powder sinks in liquid/gas
    if (mt === 3 && tt === 4) return true; // liquid sinks through gas
    if (PROP_DENSITY[mover] > PROP_DENSITY[target] && tt !== 1) return true;
    return false;
}

function simulate() {
    frameClock = 1 - frameClock;
    for (let y = WORLD_H - 2; y >= 1; y--) {
        const lr = (y + frameClock) & 1;
        const sx = lr ? 1 : WORLD_W - 2, ex = lr ? WORLD_W - 1 : 0, st = lr ? 1 : -1;
        for (let x = sx; x !== ex; x += st) {
            const i = y * WORLD_W + x;
            if (clock[i] === frameClock) continue;
            const m = grid[i];
            if (m === MAT.EMPTY) continue;
            const t = PROP_TYPE[m];
            if (t === 1) continue; // Skip static solids (Stone, Wood, Dirt, Grass, Glass, Ice, Bedrock)
            if (t === 2) simPowder(x, y, i, m);
            else if (t === 3) simLiquid(x, y, i, m);
            else if (t === 4) simGas(x, y, i, m);
            simInteract(x, y, i, m);
        }
    }
}

function simPowder(x, y, i, m) {
    const b = idx(x, y+1);
    if (b >= 0 && canDisplace(m, grid[b])) { swap(i, b); return; }
    const d = rng() < 0.5 ? 1 : -1;
    const d1 = idx(x+d, y+1), d2 = idx(x-d, y+1);
    if (d1 >= 0 && canDisplace(m, grid[d1])) swap(i, d1);
    else if (d2 >= 0 && canDisplace(m, grid[d2])) swap(i, d2);
}
function simLiquid(x, y, i, m) {
    const b = idx(x, y+1);
    if (b >= 0 && canDisplace(m, grid[b])) { swap(i, b); return; }
    const d = rng() < 0.5 ? 1 : -1;
    const d1 = idx(x+d, y+1), d2 = idx(x-d, y+1);
    if (d1 >= 0 && canDisplace(m, grid[d1])) { swap(i, d1); return; }
    if (d2 >= 0 && canDisplace(m, grid[d2])) { swap(i, d2); return; }
    // Spread horizontally (with dispersion)
    const spread = m === MAT.WATER ? 3 : (m === MAT.LAVA ? 1 : 2);
    for (let s = 1; s <= spread; s++) {
        const s1 = idx(x + d*s, y), s2 = idx(x - d*s, y);
        if (s1 >= 0 && canDisplace(m, grid[s1])) { swap(i, s1); return; }
        if (s2 >= 0 && canDisplace(m, grid[s2])) { swap(i, s2); return; }
    }
}
function simGas(x, y, i, m) {
    const a = idx(x, y-1);
    if (a >= 0 && (grid[a] === MAT.EMPTY || (PROP_TYPE[grid[a]] === 3))) { swap(i, a); return; }
    const d = rng() < 0.5 ? 1 : -1;
    const d1 = idx(x+d, y-1);
    if (d1 >= 0 && grid[d1] === MAT.EMPTY) { swap(i, d1); return; }
    const s1 = idx(x+d, y);
    if (s1 >= 0 && grid[s1] === MAT.EMPTY) swap(i, s1);
}

function simInteract(x, y, i, m) {
    // Lifetime-based materials
    if (m === MAT.FIRE || m === MAT.STEAM || m === MAT.SMOKE || m === MAT.EMBER || m === MAT.ELECTRICITY) {
        life[i]--;
        if (life[i] <= 0) {
            if (m === MAT.FIRE) setCell(i, rng()<0.25 ? MAT.SMOKE : MAT.EMPTY);
            else if (m === MAT.STEAM) setCell(i, rng()<0.35 ? MAT.WATER : MAT.EMPTY);
            else if (m === MAT.EMBER) setCell(i, MAT.EMPTY);
            else if (m === MAT.ELECTRICITY) setCell(i, MAT.EMPTY);
            else setCell(i, MAT.EMPTY);
            return;
        }
        // Flicker color
        if (m === MAT.FIRE) color[i] = matColor(MAT.FIRE);
        if (m === MAT.EMBER) color[i] = matColor(MAT.EMBER);
        if (m === MAT.ELECTRICITY) color[i] = matColor(MAT.ELECTRICITY);
    }

    // Check neighbors for reactions
    const nb = [idx(x,y-1), idx(x,y+1), idx(x-1,y), idx(x+1,y)];
    for (let k = 0; k < 4; k++) {
        const ni = nb[k];
        if (ni < 0) continue;
        const nm = grid[ni];
        if (nm === MAT.EMPTY) continue;

        // Fire/Lava ignites flammable
        if ((m === MAT.FIRE || m === MAT.LAVA || m === MAT.EMBER) && PROP_FLAMMABLE[nm] && rng() < 0.04) {
            setCell(ni, MAT.FIRE);
        }
        // Fire + Water = Steam
        if (m === MAT.FIRE && nm === MAT.WATER) { setCell(i, MAT.EMPTY); setCell(ni, MAT.STEAM); return; }
        // Lava + Water = Stone + Steam
        if (m === MAT.LAVA && nm === MAT.WATER) { setCell(i, MAT.STONE); setCell(ni, MAT.STEAM); return; }
        // Water + Fire = Steam
        if (m === MAT.WATER && nm === MAT.FIRE) { setCell(ni, MAT.STEAM); setCell(i, MAT.EMPTY); return; }
        // Lava + Ice = Stone + Water
        if (m === MAT.LAVA && nm === MAT.ICE) { setCell(i, MAT.STONE); setCell(ni, MAT.WATER); return; }
        // Fire + Ice = Water
        if ((m === MAT.FIRE || m === MAT.EMBER) && nm === MAT.ICE && rng()<0.08) { setCell(ni, MAT.WATER); }
        // Acid dissolves non-resistant materials
        if (m === MAT.ACID && !PROP_ACID_RESIST[nm] && nm !== MAT.EMPTY && rng() < 0.06) {
            setCell(ni, MAT.EMPTY);
            if (rng()<0.4) setCell(i, rng()<0.5 ? MAT.SMOKE : MAT.EMPTY);
            return;
        }
        // Gunpowder near fire/lava/ember = EXPLOSION
        if (m === MAT.GUNPOWDER && (nm === MAT.FIRE || nm === MAT.LAVA || nm === MAT.EMBER)) {
            explode(x, y, 10 + (rng()*6|0));
            return;
        }
        // ELECTRICITY CONDUCTIVITY
        if (m === MAT.ELECTRICITY && clock[ni] !== frameClock) {
            if (nm === MAT.WATER || nm === MAT.METAL) {
                if (rng() < 0.7) {
                    setCell(ni, MAT.ELECTRICITY);
                    life[ni] = 4 + (rng() * 8 | 0);
                    clock[ni] = frameClock;
                }
            }
        }
    }
}

function explode(cx, cy, radius) {
    const r2 = radius * radius;
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            const d2 = dx*dx + dy*dy;
            if (d2 > r2) continue;
            const ni = idx(cx+dx, cy+dy);
            if (ni < 0 || grid[ni] === MAT.BEDROCK) continue;
            const ratio = Math.sqrt(d2) / radius;
            if (ratio < 0.55) {
                setCell(ni, MAT.EMPTY);
            } else if (ratio < 0.8) {
                if (PROP_FLAMMABLE[grid[ni]]) setCell(ni, MAT.FIRE);
                else if (grid[ni] !== MAT.EMPTY) setCell(ni, MAT.EMBER);
            } else {
                if (PROP_FLAMMABLE[grid[ni]] && rng()<0.5) setCell(ni, MAT.FIRE);
            }
        }
    }
    if (game) { game.screenShake = 12; game.audio.playExplode(); }
}

// =====================================================
// 6. WORLD GENERATION
// =====================================================
function generateWorld() {
    const noise = new Noise2D(2026);
    const noise2 = new Noise2D(1337);
    const noise3 = new Noise2D(5678);
    rngSeed(42);
    grid.fill(MAT.EMPTY);
    color.fill(0);
    clock.fill(0);
    life.fill(0);

    // Pre-compute surface heights
    const surfHeights = new Int32Array(WORLD_W);
    for (let x = 0; x < WORLD_W; x++) {
        const surfNoise = noise.noise(x * 0.015, 0) * 22 + noise.noise(x * 0.06, 10) * 8;
        surfHeights[x] = Math.floor(WORLD_H * 0.3 + surfNoise);
    }

    for (let x = 0; x < WORLD_W; x++) {
        const surfY = surfHeights[x];

        for (let y = 0; y < WORLD_H; y++) {
            const i = y * WORLD_W + x;
            if (y >= WORLD_H - 3) { setCell(i, MAT.BEDROCK); continue; }
            if (y < surfY) continue; // sky

            if (y < 90) {
                // Biome 1: Surface Forest
                if (y === surfY) { setCell(i, MAT.GRASS); }
                else if (y < surfY + 5) { setCell(i, MAT.DIRT); }
                else { setCell(i, MAT.STONE); }
            } else if (y < 170) {
                // Biome 2: Crystal Caverns
                const caveN = noise.noise(x * 0.05, y * 0.05);
                const caveN2 = noise2.noise(x * 0.08, y * 0.08);
                if (caveN > 0.25 && caveN2 > -0.1) {
                    if (rng() < 0.02) setCell(i, MAT.WATER);
                    continue;
                }
                const mn = noise2.noise(x * 0.12, y * 0.12);
                const mn3 = noise3.noise(x * 0.18, y * 0.18);
                if (mn3 > 0.5) setCell(i, MAT.GLASS);
                else if (mn > 0.45) setCell(i, MAT.ICE);
                else if (rng() < 0.05) setCell(i, MAT.SAND);
                else setCell(i, MAT.STONE);
            } else if (y < 245) {
                // Biome 3: Poison/Toxic Caves
                const caveN = noise.noise(x * 0.05, y * 0.05);
                const caveN2 = noise2.noise(x * 0.08, y * 0.08);
                if (caveN > 0.25 && caveN2 > -0.1) {
                    if (rng() < 0.04) setCell(i, MAT.ACID);
                    else if (rng() < 0.03) setCell(i, MAT.OIL);
                    continue;
                }
                if (rng() < 0.08) setCell(i, MAT.DIRT);
                else setCell(i, MAT.STONE);
            } else {
                // Biome 4: Lava Core
                const caveN = noise.noise(x * 0.05, y * 0.05);
                const caveN2 = noise2.noise(x * 0.08, y * 0.08);
                if (caveN > 0.25 && caveN2 > -0.1) {
                    if (rng() < 0.08) setCell(i, MAT.LAVA);
                    else if (rng() < 0.03) setCell(i, MAT.FIRE);
                    else if (rng() < 0.03) setCell(i, MAT.EMBER);
                    continue;
                }
                if (rng() < 0.08) setCell(i, MAT.EMBER);
                else setCell(i, MAT.STONE);
            }
        }
    }

    // Surface water lakes in valleys
    rngSeed(777);
    for (let x = 10; x < WORLD_W - 10; x++) {
        // Find valley spots (where surface is lower than neighbors)
        const sy = surfHeights[x];
        const syL = surfHeights[Math.max(0, x-5)];
        const syR = surfHeights[Math.min(WORLD_W-1, x+5)];
        if (sy > syL && sy > syR && rng() < 0.15) {
            // Place water above surface in valley
            for (let wy = sy - 1; wy >= sy - 4; wy--) {
                const wi = idx(x, wy);
                if (wi >= 0 && grid[wi] === MAT.EMPTY) setCell(wi, MAT.WATER);
            }
        }
    }

    // Trees
    rngSeed(1005);
    for (let x = 5; x < WORLD_W - 5; x++) {
        if (rng() > 0.06) continue;
        let sy = -1;
        for (let y = 0; y < WORLD_H; y++) { if (grid[y*WORLD_W+x] !== MAT.EMPTY) { sy = y; break; } }
        if (sy < 0 || grid[sy*WORLD_W+x] !== MAT.GRASS) continue;
        // Check not in water
        const aboveI = idx(x, sy - 1);
        if (aboveI >= 0 && grid[aboveI] === MAT.WATER) continue;
        const th = 5 + (rng()*5|0);
        for (let t = 1; t <= th; t++) { const ti = idx(x, sy-t); if(ti>=0) setCell(ti, MAT.WOOD); }
        // Leafy canopy
        const canopyR = 2 + (rng()*2|0);
        for (let lx = -canopyR; lx <= canopyR; lx++) {
            for (let ly = -canopyR; ly <= 1; ly++) {
                if (Math.abs(lx)+Math.abs(ly) > canopyR + 1) continue;
                const li = idx(x+lx, sy-th+ly);
                if (li >= 0 && grid[li] === MAT.EMPTY) setCell(li, MAT.GRASS);
            }
        }
        x += 3 + (rng()*3|0);
    }

    // Surface gunpowder deposits (Easter egg)
    rngSeed(9999);
    for (let x = 20; x < WORLD_W - 20; x += 40 + (rng()*30|0)) {
        const sy = surfHeights[x];
        for (let gy = sy + 8; gy < sy + 14; gy++) {
            for (let gx = x - 2; gx <= x + 2; gx++) {
                const gi = idx(gx, gy);
                if (gi >= 0 && grid[gi] === MAT.STONE && rng() < 0.5) setCell(gi, MAT.GUNPOWDER);
            }
        }
    }
}
