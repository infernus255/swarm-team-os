// =====================================================
// 7. PLAYER CONTROLLER
// =====================================================
class Player {
    constructor(id, keymap) {
        this.id = id;
        this.x = 0; this.y = 0;
        this.vx = 0; this.vy = 0;
        this.ax = 0; this.jumpReq = false;
        this.onGround = false;
        this.hp = MAX_HP;
        this.tool = TOOL_PLACE;
        this.selectedMat = MAT.SAND;
        this.facing = 1;
        this.keymap = keymap;
        this.dmgTimer = 0;
    }

    spawn() {
        this.x = WORLD_W * (this.id === 0 ? 0.5 : 0.6);
        for (let y = 0; y < WORLD_H; y++) {
            if (grid[y * WORLD_W + (this.x|0)] !== MAT.EMPTY) {
                this.y = y - PLAYER_H - 1;
                break;
            }
        }
        this.vx = 0; this.vy = 0; this.hp = MAX_HP;
    }

    update() {
        // Acceleration
        this.vx += this.ax * PLAYER_SPEED * 0.3;
        this.vx *= 0.82;
        if (Math.abs(this.vx) < 0.05) this.vx = 0;
        if (this.vx !== 0) this.facing = this.vx > 0 ? 1 : -1;

        // Jump
        if (this.jumpReq && this.onGround) { this.vy = PLAYER_JUMP; this.onGround = false; }
        this.jumpReq = false;

        // In liquid?
        const cx = (this.x + PLAYER_W/2)|0, cy = (this.y + PLAYER_H/2)|0;
        const ci = idx(cx, cy);
        const inLiquid = ci >= 0 && PROPS[grid[ci]]?.t === 3;
        if (inLiquid) {
            this.vy += GRAVITY * 0.25;
            this.vy *= 0.9;
            if (this.jumpReq || this.ax !== 0) this.vy -= 0.8; // swim
            
            // Clean water heals player slowly
            if (grid[ci] === MAT.WATER && this.hp < MAX_HP && this.dmgTimer <= 0) {
                this.hp = Math.min(MAX_HP, this.hp + 2);
                this.dmgTimer = 15;
                if (game) {
                    game.spawnFloatingText(this.x + PLAYER_W/2, this.y, "+2 HP", "#2ed573");
                    if (game.activeMission && game.activeMission.type === 'heal_water') {
                        game.missionProgress += 2;
                        game.updateMissionUI();
                        game.checkMissionComplete();
                    }
                }
            }
        } else {
            this.vy += GRAVITY;
        }
        if (this.vy > 8) this.vy = 8;

        // Move X
        this.x += this.vx;
        this.x = ((this.x % WORLD_W) + WORLD_W) % WORLD_W;
        this.resolveX();

        // Move Y
        this.y += this.vy;
        this.resolveY();

        // Clamp Y
        if (this.y < 0) { this.y = 0; this.vy = 0; }
        if (this.y > WORLD_H - PLAYER_H - 2) { this.y = WORLD_H - PLAYER_H - 2; this.vy = 0; this.onGround = true; }

        // Damage from environment
        this.dmgTimer--;
        if (this.dmgTimer <= 0) {
            for (let dy = 0; dy < PLAYER_H; dy++) {
                for (let dx = 0; dx < PLAYER_W; dx++) {
                    const pi = idx((this.x+dx)|0, (this.y+dy)|0);
                    if (pi < 0) continue;
                    const pm = grid[pi];
                    if (pm === MAT.FIRE || pm === MAT.LAVA || pm === MAT.ACID) {
                        this.hp -= (pm === MAT.LAVA ? 3 : pm === MAT.ACID ? 2 : 1);
                        this.dmgTimer = 10;
                        break;
                    }
                }
                if (this.dmgTimer > 0) break;
            }
        }
        if (this.hp <= 0) {
            this.hp = MAX_HP;
            this.spawn();
            // Respawn flash effect
            const flash = document.getElementById('respawn-flash');
            if (flash) { flash.style.opacity = '1'; setTimeout(() => { flash.style.transition='opacity 0.6s'; flash.style.opacity='0'; setTimeout(()=>{ flash.style.transition='opacity 0.05s'; }, 650); }, 80); }
        }
    }

    isSolid(x, y) {
        const i = idx(x|0, y|0);
        if (i < 0) return true;
        const t = PROPS[grid[i]]?.t;
        return t === 1 || t === 2; // solid or powder
    }

    resolveX() {
        for (let dy = 0; dy < PLAYER_H; dy++) {
            for (let dx = 0; dx < PLAYER_W; dx++) {
                if (this.isSolid(this.x + dx, this.y + dy)) {
                    if (this.vx > 0) this.x = Math.floor(this.x + dx) - dx - 0.01;
                    else if (this.vx < 0) this.x = Math.floor(this.x + dx) + 1 - dx + 0.01;
                    this.vx = 0;
                    return;
                }
            }
        }
    }

    resolveY() {
        this.onGround = false;
        for (let dy = 0; dy < PLAYER_H; dy++) {
            for (let dx = 0; dx < PLAYER_W; dx++) {
                if (this.isSolid(this.x + dx, this.y + dy)) {
                    if (this.vy > 0) {
                        this.y = Math.floor(this.y + dy) - dy - 0.01;
                        this.vy = 0;
                        this.onGround = true;
                    } else if (this.vy < 0) {
                        this.y = Math.floor(this.y + dy) + 1 - dy + 0.01;
                        this.vy = 0;
                    }
                    return;
                }
            }
        }
    }

    draw(ctx, cam) {
        const sx = (this.x - cam.x) * cam.zoom;
        const sy = (this.y - cam.y) * cam.zoom;
        const sw = PLAYER_W * cam.zoom;
        const sh = PLAYER_H * cam.zoom;

        // Shadow
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        ctx.fillRect(sx-1, sy+sh-2, sw+2, 3);

        // Body
        ctx.fillStyle = this.id === 0 ? '#ff6b6b' : '#6baaff';
        ctx.fillRect(sx, sy + sh*0.3, sw, sh*0.5);

        // Head
        ctx.fillStyle = '#ffe0c0';
        ctx.beginPath();
        ctx.arc(sx + sw/2, sy + sh*0.22, sw*0.45, 0, Math.PI*2);
        ctx.fill();

        // Eyes
        ctx.fillStyle = '#333';
        const ex = this.facing > 0 ? sw*0.6 : sw*0.25;
        ctx.fillRect(sx + ex, sy + sh*0.18, 2, 2);

        // HP bar above player
        const hpW = sw + 4;
        const hpRatio = this.hp / MAX_HP;
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillRect(sx - 2, sy - 6, hpW, 3);
        ctx.fillStyle = hpRatio > 0.5 ? '#2ed573' : hpRatio > 0.25 ? '#ffa502' : '#ff4757';
        ctx.fillRect(sx - 2, sy - 6, hpW * hpRatio, 3);
    }
}

// =====================================================
// 9. CAMERA SYSTEM
// =====================================================
class Camera {
    constructor() { this.x = 0; this.y = 0; this.zoom = 3; this.viewW = 0; this.viewH = 0; }
    resize(sw, sh) {
        this.zoom = Math.max(2, Math.min(4, Math.floor(Math.min(sw, sh) / 160)));
        this.viewW = sw / this.zoom;
        this.viewH = sh / this.zoom;
    }
    follow(px, py, dt) {
        const tx = px + PLAYER_W/2 - this.viewW/2;
        const ty = py + PLAYER_H/2 - this.viewH/2;
        const f = 1 - Math.pow(0.02, dt);
        this.x += (tx - this.x) * f;
        this.y += (ty - this.y) * f;
        this.y = Math.max(0, Math.min(this.y, WORLD_H - this.viewH));
        // X wraps, no clamping needed but keep in range for rendering
        if (this.x < 0) this.x += WORLD_W;
        if (this.x >= WORLD_W) this.x -= WORLD_W;
    }
}

// =====================================================
// 10.5 JUICE & FEEDBACK: FLOATING TEXT
// =====================================================
class FloatingText {
    constructor(x, y, text, color) {
        this.x = x; this.y = y; this.text = text; this.color = color;
        this.life = 50;
        this.vy = -0.6 - rng()*0.5;
        this.vx = (rng()-0.5)*0.3;
    }
    update() { this.x += this.vx; this.y += this.vy; this.life--; }
    draw(ctx, cam) {
        const sx = (this.x - cam.x) * cam.zoom;
        const sy = (this.y - cam.y) * cam.zoom;
        const alpha = Math.min(1, this.life / 15);
        ctx.save();
        ctx.font = `bold ${Math.floor(9 * cam.zoom)}px sans-serif`;
        ctx.fillStyle = this.color;
        ctx.globalAlpha = alpha;
        ctx.shadowColor = 'rgba(0,0,0,0.8)';
        ctx.shadowBlur = 3;
        ctx.textAlign = 'center';
        ctx.fillText(this.text, sx, sy);
        ctx.restore();
    }
}

// =====================================================
// 11. GAME CLASS
// =====================================================
let game = null;

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.offCanvas = document.createElement('canvas');
        this.offCanvas.width = WORLD_W;
        this.offCanvas.height = WORLD_H;
        this.offCtx = this.offCanvas.getContext('2d');
        this.imgData = this.offCtx.createImageData(WORLD_W, WORLD_H);
        this.pixels32 = new Uint32Array(this.imgData.data.buffer);
        this.bgNoise = new Noise2D(90);

        this.players = [new Player(0, { l:'KeyA', r:'KeyD', u:'KeyW', d:'KeyS', j:'KeyW' })];
        this.cam = new Camera();
        this.audio = new Audio();
        this.mp = new Multiplayer();

        this.keys = {};
        this.joystick = { active:false, pid:null, sx:0, sy:0, cx:0, cy:0, rad:50, threshold:8 };
        this.pointers = {};
        this.screenShake = 0;
        this.skyTime = 6000;
        this.fps = 0;
        this.simTime = 0;
        this.drawTime = 0;

        this.currentTool = TOOL_PLACE;
        this.currentMat = MAT.SAND;
        this.brushSize = 3;

        this.floatingTexts = [];
        this.score = 0;
        this.activeMission = null;
        this.missionProgress = 0;
        this.missionTimeCounter = 0;

        this.cursor = { x: -9999, y: -9999, visible: false }; // world-space cursor
        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        generateWorld();
        this.players[0].spawn();
        this.setupPalette();
        this.setupTools();
        this.setupBrushSlider();
        this.setupEvents();
        this.setupMPPanel();
        this.selectRandomMission();
        setTimeout(() => { const t = document.getElementById('tutorial'); if(t) t.style.opacity = 0; }, 5000);
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.cam.resize(this.canvas.width, this.canvas.height);
    }

    setupPalette() {
        const cont = document.getElementById('palette');
        cont.innerHTML = '';
        PALETTE.forEach((m, i) => {
            const btn = document.createElement('div');
            btn.className = `mat-btn${i===0?' sel':''}`;
            btn.style.background = matCSS(m);
            btn.innerHTML = `<span class="mat-label">${PROPS[m].n}</span>`;
            btn.addEventListener('pointerdown', e => {
                e.stopPropagation();
                document.querySelectorAll('.mat-btn').forEach(b => b.classList.remove('sel'));
                btn.classList.add('sel');
                this.currentMat = m;
                this.players[0].selectedMat = m;
                this.audio.playPlace();
            });
            cont.appendChild(btn);
        });
    }

    setupTools() {
        const cont = document.getElementById('tools');
        cont.innerHTML = '';
        TOOL_ICONS.forEach((icon, i) => {
            const btn = document.createElement('button');
            btn.className = `btn${i===0?' active':''}`;
            btn.textContent = icon;
            btn.addEventListener('pointerdown', e => {
                e.stopPropagation();
                document.querySelectorAll('#tools .btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = i;
                this.players[0].tool = i;
            });
            cont.appendChild(btn);
        });
    }

    setupBrushSlider() {
        const slider = document.getElementById('brush-slider');
        const val = document.getElementById('brush-val');
        if (!slider) return;
        slider.addEventListener('input', () => {
            this.brushSize = parseInt(slider.value);
            val.textContent = slider.value;
        });
        slider.addEventListener('pointerdown', e => e.stopPropagation());
    }

    setupMPPanel() {
        document.getElementById('btn-mp').addEventListener('pointerdown', e => {
            e.stopPropagation();
            document.getElementById('mp-panel').classList.toggle('show');
        });
        document.getElementById('mp-local').addEventListener('pointerdown', e => {
            e.stopPropagation();
            this.mp.startLocal();
            if (this.players.length < 2) {
                const p2 = new Player(1, { l:'ArrowLeft', r:'ArrowRight', u:'ArrowUp', d:'ArrowDown', j:'ArrowUp' });
                p2.spawn();
                this.players.push(p2);
            }
        });
        document.getElementById('mp-host').addEventListener('pointerdown', e => { e.stopPropagation(); this.mp.host(); });
        document.getElementById('mp-join').addEventListener('pointerdown', e => {
            e.stopPropagation();
            const code = document.getElementById('mp-code').value.trim();
            if (code) this.mp.join(code);
            else { document.getElementById('mp-code').style.display='block'; document.getElementById('mp-actions').style.display='flex'; document.getElementById('mp-status').textContent = 'Pega el codigo del host y presiona Aplicar'; }
        });
        document.getElementById('mp-copy').addEventListener('pointerdown', e => {
            e.stopPropagation();
            navigator.clipboard?.writeText(document.getElementById('mp-code').value);
            document.getElementById('mp-status').textContent = 'Copiado!';
        });
        document.getElementById('mp-apply').addEventListener('pointerdown', e => {
            e.stopPropagation();
            const code = document.getElementById('mp-code').value.trim();
            if (this.mp.isHost) this.mp.applyAnswer(code);
            else this.mp.join(code);
        });
    }

    selectRandomMission() {
        const list = [
            { type: 'mine_glass', desc: 'Mina 10 bloques de Cristal', target: 10 },
            { type: 'mine_gunpowder', desc: 'Mina 5 depósitos de Pólvora', target: 5 },
            { type: 'survive_deep', desc: 'Sobrevive 12s en la profundidad', target: 12 },
            { type: 'heal_water', desc: 'Cúrate 20 HP en el Agua', target: 20 }
        ];
        const idx = Math.floor(rng() * list.length);
        this.activeMission = list[idx];
        this.missionProgress = 0;
        this.missionTimeCounter = 0;
        this.updateMissionUI();
    }

    updateMissionUI() {
        const display = document.getElementById('mission-display');
        if (display && this.activeMission) {
            display.textContent = `Misión: ${this.activeMission.desc} (${Math.min(this.missionProgress, this.activeMission.target)}/${this.activeMission.target})`;
        }
    }

    checkMissionComplete() {
        if (this.activeMission && this.missionProgress >= this.activeMission.target) {
            this.score += 100;
            document.getElementById('v-score').textContent = this.score;
            this.audio.playMissionComplete();
            const p = this.players[0];
            this.spawnFloatingText(p.x + PLAYER_W/2, p.y - 10, "¡MISIÓN COMPLETADA! +100 pts 🎉", "#ffd700");
            this.screenShake = 6;
            const panel = document.getElementById('mission-panel');
            if (panel) {
                panel.style.backgroundColor = 'rgba(255, 215, 0, 0.25)';
                setTimeout(() => { panel.style.backgroundColor = ''; }, 300);
            }
            this.selectRandomMission();
        } else {
            this.updateMissionUI();
        }
    }

    spawnFloatingText(x, y, text, color) {
        this.floatingTexts.push(new FloatingText(x, y, text, color));
    }

    setupEvents() {
        this.canvas.addEventListener('pointerdown', e => this.onPtrDown(e));
        this.canvas.addEventListener('pointermove', e => this.onPtrMove(e));
        this.canvas.addEventListener('pointerup', e => this.onPtrUp(e));
        this.canvas.addEventListener('pointercancel', e => this.onPtrUp(e));
        window.addEventListener('keydown', e => {
            this.keys[e.code] = true;
            // Number keys for material
            if (e.key >= '1' && e.key <= '9') {
                const idx = parseInt(e.key)-1;
                if (idx < PALETTE.length) {
                    this.currentMat = PALETTE[idx];
                    this.players[0].selectedMat = PALETTE[idx];
                    document.querySelectorAll('.mat-btn').forEach((b,i)=>{b.classList.toggle('sel',i===idx);});
                }
            }
            if (e.code === 'KeyE') {
                this.currentTool = (this.currentTool + 1) % 3;
                document.querySelectorAll('#tools .btn').forEach((b,i)=>{b.classList.toggle('active',i===this.currentTool);});
            }
        });
        window.addEventListener('keyup', e => { this.keys[e.code] = false; });
        document.getElementById('btn-sound').addEventListener('pointerdown', e => {
            e.stopPropagation();
            this.audio.muted = !this.audio.muted;
            e.target.textContent = this.audio.muted ? '🔇' : '🔊';
        });
        const btnMusic = document.getElementById('btn-music');
        if (btnMusic) {
            btnMusic.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.audio.musicMuted = !this.audio.musicMuted;
                btnMusic.textContent = this.audio.musicMuted ? '🔇🎵' : '🎵';
                if (!this.audio.musicMuted) this.audio.startMusic();
                else this.audio.stopMusic();
            });
        }
        const startOnInteraction = () => {
            if (!this.audio.musicTimer && !this.audio.musicMuted) {
                this.audio.startMusic();
            }
            window.removeEventListener('pointerdown', startOnInteraction);
            window.removeEventListener('keydown', startOnInteraction);
        };
        window.addEventListener('pointerdown', startOnInteraction);
        window.addEventListener('keydown', startOnInteraction);

        document.getElementById('btn-reset').addEventListener('pointerdown', e => {
            e.stopPropagation();
            this.players.forEach(p => p.spawn());
        });
    }

    onPtrDown(e) {
        e.preventDefault();
        try { e.target.setPointerCapture(e.pointerId); } catch(ex){}
        this.pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        if (e.clientX < window.innerWidth / 2.5) {
            if (!this.joystick.active) {
                this.joystick.active = true;
                this.joystick.pid = e.pointerId;
                this.joystick.sx = e.clientX; this.joystick.sy = e.clientY;
                this.joystick.cx = e.clientX; this.joystick.cy = e.clientY;
            }
        } else {
            this.cursor.visible = true;
            this.cursor.x = (e.clientX / this.cam.zoom + this.cam.x);
            this.cursor.y = (e.clientY / this.cam.zoom + this.cam.y);
            this.doAction(e.clientX, e.clientY);
        }
    }
    onPtrMove(e) {
        e.preventDefault();
        if (!this.pointers[e.pointerId]) return;
        this.pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        if (this.joystick.active && this.joystick.pid === e.pointerId) {
            this.joystick.cx = e.clientX; this.joystick.cy = e.clientY;
            const dx = this.joystick.cx - this.joystick.sx;
            const dy = this.joystick.cy - this.joystick.sy;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > this.joystick.threshold) {
                this.players[0].ax = Math.max(-1, Math.min(dx / this.joystick.rad, 1));
                if (dy < -this.joystick.rad * 0.65) this.players[0].jumpReq = true;
            } else {
                this.players[0].ax = 0;
            }
        } else {
            this.cursor.visible = true;
            this.cursor.x = (e.clientX / this.cam.zoom + this.cam.x);
            this.cursor.y = (e.clientY / this.cam.zoom + this.cam.y);
            this.doAction(e.clientX, e.clientY);
        }
    }
    onPtrUp(e) {
        e.preventDefault();
        try { e.target.releasePointerCapture(e.pointerId); } catch(ex){}
        delete this.pointers[e.pointerId];
        if (this.joystick.active && this.joystick.pid === e.pointerId) {
            this.joystick.active = false;
            this.joystick.pid = null;
            this.players[0].ax = 0;
        }
        // Hide cursor if no more right-side touches
        const rightTouches = Object.values(this.pointers).filter(p => p.x >= window.innerWidth / 2.5);
        if (rightTouches.length === 0) this.cursor.visible = false;
    }

    doAction(screenX, screenY) {
        const wx = (screenX / this.cam.zoom + this.cam.x) | 0;
        const wy = (screenY / this.cam.zoom + this.cam.y) | 0;
        const p = this.players[0];
        const pcx = p.x + PLAYER_W/2, pcy = p.y + PLAYER_H/2;
        const dist = Math.sqrt((wx-pcx)**2 + (wy-pcy)**2);
        if (dist > INTERACTION_RANGE) return;

        if (this.currentTool === TOOL_PLACE) {
            const bs = this.brushSize;
            for (let dy = -bs; dy <= bs; dy++) {
                for (let dx = -bs; dx <= bs; dx++) {
                    if (dx*dx+dy*dy > bs*bs) continue;
                    const ti = idx(wx+dx, wy+dy);
                    if (ti >= 0 && grid[ti] === MAT.EMPTY) {
                        setCell(ti, this.currentMat);
                    }
                }
            }
            this.audio.playPlace();
        } else if (this.currentTool === TOOL_MINE) {
            const bs = this.brushSize;
            let minedGlass = 0;
            let minedGunpowder = 0;
            for (let dy = -bs; dy <= bs; dy++) {
                for (let dx = -bs; dx <= bs; dx++) {
                    if (dx*dx+dy*dy > bs*bs) continue;
                    const ti = idx(wx+dx, wy+dy);
                    if (ti >= 0 && grid[ti] !== MAT.EMPTY && grid[ti] !== MAT.BEDROCK) {
                        const tm = grid[ti];
                        if (tm === MAT.GLASS) minedGlass++;
                        else if (tm === MAT.GUNPOWDER) minedGunpowder++;
                        setCell(ti, MAT.EMPTY);
                    }
                }
            }
            if (minedGlass > 0) {
                this.score += minedGlass * 10;
                document.getElementById('v-score').textContent = this.score;
                this.spawnFloatingText(wx, wy, `+${minedGlass * 10} Cristal`, "#ffd700");
                if (this.activeMission && this.activeMission.type === 'mine_glass') {
                    this.missionProgress += minedGlass;
                    this.checkMissionComplete();
                }
            }
            if (minedGunpowder > 0) {
                this.score += minedGunpowder * 5;
                document.getElementById('v-score').textContent = this.score;
                this.spawnFloatingText(wx, wy, `+${minedGunpowder * 5} Pólvora`, "#ff4757");
                if (this.activeMission && this.activeMission.type === 'mine_gunpowder') {
                    this.missionProgress += minedGunpowder;
                    this.checkMissionComplete();
                }
            }
            this.audio.playMine();
        } else if (this.currentTool === TOOL_BOMB) {
            explode(wx, wy, 12 + (rng()*5|0));
        }
    }

    update(dt) {
        // Keyboard input for players
        this.players.forEach(p => {
            const k = p.keymap;
            if (p.id === 0 && this.joystick.active) {
                // Touch joystick overrides keyboard for P1
            } else {
                p.ax = 0;
                if (this.keys[k.l]) p.ax = -1;
                else if (this.keys[k.r]) p.ax = 1;
                if (this.keys[k.j]) p.jumpReq = true;
            }
            p.update();
        });

        // Online multiplayer input sync
        if (this.mp.connected) {
            const p = this.players[0];
            this.mp.send({ ax: p.ax, j: p.jumpReq, x: p.x, y: p.y });
            const ri = this.mp.remoteInputs;
            if (this.players.length < 2) {
                const p2 = new Player(1, {});
                p2.spawn();
                this.players.push(p2);
            }
            const rp = this.players[1];
            if (ri.x !== undefined) { rp.x = ri.x; rp.y = ri.y; }
            rp.ax = ri.ax || 0;
            if (ri.j) rp.jumpReq = true;
        }

        // CA Simulation
        simulate();

        // Camera
        this.cam.follow(this.players[0].x, this.players[0].y, dt);

        // Screen shake decay
        if (this.screenShake > 0) this.screenShake *= 0.85;
        if (this.screenShake < 0.5) this.screenShake = 0;

        // Day/night
        this.skyTime = (this.skyTime + dt * 20) % 24000;

        // Update floating texts
        for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
            const ft = this.floatingTexts[i];
            ft.update();
            if (ft.life <= 0) this.floatingTexts.splice(i, 1);
        }

        // Track survive deep mission
        if (this.activeMission && this.activeMission.type === 'survive_deep') {
            if (this.players[0].y > WORLD_H * 0.65) {
                this.missionTimeCounter += dt;
                if (this.missionTimeCounter >= 1.0) {
                    this.missionProgress++;
                    this.missionTimeCounter = 0;
                    this.checkMissionComplete();
                }
            }
        }

        // HP UI
        document.getElementById('hp-fill').style.width = `${(this.players[0].hp / MAX_HP) * 100}%`;
    }

    render() {
        const ctx = this.ctx;
        const cw = this.canvas.width, ch = this.canvas.height;

        // Sky gradient
        this.drawSky(ctx, cw, ch);

        // Parallax mountains
        this.drawParallax(ctx, cw, ch);

        // World pixels: copy color buffer to ImageData
        // color[] already stores 0 for EMPTY cells (set in setCell), so direct copy works
        this.pixels32.set(color);

        this.offCtx.putImageData(this.imgData, 0, 0);

        // Draw world to main canvas
        ctx.imageSmoothingEnabled = false;

        const shakeX = this.screenShake ? (rng()-0.5) * this.screenShake * 2 : 0;
        const shakeY = this.screenShake ? (rng()-0.5) * this.screenShake * 2 : 0;

        const sx = this.cam.x;
        const sy = this.cam.y;
        const sw = this.cam.viewW;
        const sh = this.cam.viewH;

        // Handle horizontal wrapping rendering
        const rightOverflow = sx + sw - WORLD_W;
        if (rightOverflow > 0 && sx < WORLD_W) {
            // Draw main portion
            ctx.drawImage(this.offCanvas, sx, sy, sw - rightOverflow, sh, shakeX, shakeY, (sw - rightOverflow) * this.cam.zoom, ch);
            // Draw wrapped portion
            ctx.drawImage(this.offCanvas, 0, sy, rightOverflow, sh, (sw - rightOverflow) * this.cam.zoom + shakeX, shakeY, rightOverflow * this.cam.zoom, ch);
        } else {
            ctx.drawImage(this.offCanvas, sx, sy, sw, sh, shakeX, shakeY, cw, ch);
        }

        // Draw players
        this.players.forEach(p => p.draw(ctx, this.cam));

        // Draw floating texts
        this.floatingTexts.forEach(ft => ft.draw(ctx, this.cam));

        // Draw placement cursor crosshair
        if (this.cursor.visible) this.drawCursor(ctx);

        // Draw joystick
        if (this.joystick.active) this.drawJoystick(ctx);

        // HUD update
        document.getElementById('v-fps').textContent = this.fps|0;
        document.getElementById('v-sim').textContent = this.simTime.toFixed(1);
        document.getElementById('v-draw').textContent = this.drawTime.toFixed(1);
        document.getElementById('v-pos').textContent = `${this.players[0].x|0},${this.players[0].y|0}`;
        document.getElementById('v-cells').textContent = totalCells;
    }

    drawSky(ctx, w, h) {
        const t = this.skyTime;
        let topR, topG, topB, botR, botG, botB;
        if (t >= 4000 && t < 12000) {
            topR=135;topG=206;topB=235; botR=224;botG=246;botB=255;
        } else if (t >= 12000 && t < 16000) {
            const r = (t-12000)/4000;
            topR=135-r*117|0;topG=206-r*190|0;topB=235-r*203|0;
            botR=224-r*13|0;botG=246-r*162|0;botB=255-r*255|0;
        } else if (t >= 16000 || t < 4000) {
            const r = t >= 16000 ? (t-16000)/8000 : (t+8000)/12000;
            topR=13;topG=14;topB=21; botR=5;botG=5;botB=8;
            if (t < 4000) { const rr = t/4000; topR+=rr*122|0;topG+=rr*192|0;topB+=rr*214|0;botR+=rr*219|0;botG+=rr*241|0;botB+=rr*247|0; }
        } else {
            topR=135;topG=206;topB=235; botR=224;botG=246;botB=255;
        }
        const grad = ctx.createLinearGradient(0,0,0,h);
        grad.addColorStop(0, `rgb(${topR},${topG},${topB})`);
        grad.addColorStop(1, `rgb(${botR},${botG},${botB})`);
        ctx.fillStyle = grad;
        ctx.fillRect(0,0,w,h);

        // Stars at night
        if (this.skyTime > 16000 || this.skyTime < 4000) {
            let alpha = 0.6;
            if (this.skyTime >= 14000 && this.skyTime <= 16000) alpha = (this.skyTime-14000)/2000*0.6;
            if (this.skyTime < 4000) alpha = (1 - this.skyTime/4000)*0.6;
            ctx.fillStyle = `rgba(255,255,255,${alpha})`;
            rngSeed(2026);
            for (let i = 0; i < 50; i++) {
                ctx.beginPath();
                ctx.arc(rng()*w, rng()*h*0.6, 0.8+rng()*1.5, 0, Math.PI*2);
                ctx.fill();
            }
        }
    }

    drawParallax(ctx, w, h) {
        ctx.fillStyle = 'rgba(35,38,58,0.35)';
        ctx.beginPath(); ctx.moveTo(0, h);
        for (let x = 0; x <= w; x += 12) {
            const my = h * 0.7 + this.bgNoise.noise((x + this.cam.x * 0.08) * 0.004, 0) * 100;
            ctx.lineTo(x, my);
        }
        ctx.lineTo(w, h); ctx.fill();

        ctx.fillStyle = 'rgba(50,60,80,0.25)';
        ctx.beginPath(); ctx.moveTo(0, h);
        for (let x = 0; x <= w; x += 12) {
            const my = h * 0.78 + this.bgNoise.noise((x + this.cam.x * 0.2) * 0.006, 50) * 60;
            ctx.lineTo(x, my);
        }
        ctx.lineTo(w, h); ctx.fill();
    }

    drawCursor(ctx) {
        ctx.save();
        const sx = (this.cursor.x - this.cam.x) * this.cam.zoom;
        const sy = (this.cursor.y - this.cam.y) * this.cam.zoom;
        const bs = this.brushSize * this.cam.zoom;
        // Outer ring
        ctx.strokeStyle = 'rgba(255,255,255,0.6)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.arc(sx, sy, bs + 2, 0, Math.PI*2);
        ctx.stroke();
        // Inner dot
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(255,255,255,0.8)';
        ctx.beginPath();
        ctx.arc(sx, sy, 2, 0, Math.PI*2);
        ctx.fill();
        // Crosshair lines
        ctx.strokeStyle = 'rgba(255,255,255,0.4)';
        ctx.lineWidth = 1;
        const cLen = 8;
        ctx.beginPath();
        ctx.moveTo(sx - bs - cLen, sy); ctx.lineTo(sx - bs + 4, sy);
        ctx.moveTo(sx + bs - 4, sy); ctx.lineTo(sx + bs + cLen, sy);
        ctx.moveTo(sx, sy - bs - cLen); ctx.lineTo(sx, sy - bs + 4);
        ctx.moveTo(sx, sy + bs - 4); ctx.lineTo(sx, sy + bs + cLen);
        ctx.stroke();
        ctx.restore();
    }

    drawJoystick(ctx) {
        ctx.save();
        const dx = this.joystick.cx - this.joystick.sx;
        const dy = this.joystick.cy - this.joystick.sy;
        const dist = Math.sqrt(dx*dx + dy*dy);
        const isJumping = dy < -this.joystick.rad * 0.65;

        // Outer ring with glow when active
        ctx.shadowColor = isJumping ? 'rgba(255,215,0,0.5)' : 'rgba(255,255,255,0.15)';
        ctx.shadowBlur = 12;
        ctx.fillStyle = isJumping ? 'rgba(255,215,0,0.1)' : 'rgba(255,255,255,0.06)';
        ctx.strokeStyle = isJumping ? 'rgba(255,215,0,0.7)' : 'rgba(255,255,255,0.25)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(this.joystick.sx, this.joystick.sy, this.joystick.rad, 0, Math.PI*2);
        ctx.fill(); ctx.stroke();

        // Direction indicator lines
        if (dist > this.joystick.threshold) {
            ctx.strokeStyle = 'rgba(255,255,255,0.12)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(this.joystick.sx, this.joystick.sy);
            ctx.lineTo(this.joystick.cx, this.joystick.cy);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        const a = Math.atan2(dy, dx);
        const d = Math.min(dist, this.joystick.rad);
        const kx = this.joystick.sx + Math.cos(a)*d;
        const ky = this.joystick.sy + Math.sin(a)*d;

        ctx.shadowColor = isJumping ? 'rgba(255,215,0,0.8)' : 'rgba(255,255,255,0.3)';
        ctx.shadowBlur = 16;
        ctx.fillStyle = isJumping ? 'rgba(255,215,0,0.95)' : 'rgba(255,255,255,0.75)';
        ctx.beginPath();
        ctx.arc(kx, ky, 20, 0, Math.PI*2);
        ctx.fill();

        // Jump arrow indicator
        if (isJumping) {
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#333';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('↑', kx, ky);
        }
        ctx.restore();
    }
}
