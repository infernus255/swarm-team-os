function getScreenX(worldX, cam) {
    let dx = worldX - (cam.x + cam.viewW / 2);
    dx = ((dx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
    return dx + cam.viewW / 2;
}

class Enemy {
    constructor(x, y, type = 'slime') {
        this.x = x;
        this.type = type;
        // Obelisks and turrets do not move
        this.vx = type === 'pharaoh_guardian' ? 0.2 : (type === 'turret' ? 0.0 : (rng() - 0.5) * 0.8);
        this.vy = 0;
        this.w = type === 'pharaoh_guardian' ? 20 : type === 'bat' ? 6 : (type === 'turret' ? 10 : 8);
        this.h = type === 'pharaoh_guardian' ? 24 : type === 'bat' ? 6 : (type === 'turret' ? 20 : 6);
        this.hp = type === 'pharaoh_guardian' ? 400 : type === 'bat' ? 10 : (type === 'turret' ? 60 : (type === 'jumping_slime' ? 30 : 20));
        this.maxHp = this.hp;
        this.dead = false;
        this.facing = 1;
        this.wanderTimer = 0;
        this.chargeTimer = 0;
        this.shootTimer = 0;
        this.summonTimer = 0;
        this.slowTimer = 0;

        // Shift y-coordinate upward by (height - 1) to align bottom of enemy with the floor cell y
        if (type !== 'pharaoh_guardian' && type !== 'bat') {
            this.y = y - this.h + 1;
        } else {
            this.y = y;
        }
    }

    isSolid(x, y) {
        const i = idx(x | 0, y | 0);
        if (i < 0) return true;
        const t = PROP_TYPE[grid[i]];
        return t === 1 || t === 2;
    }

    checkCollision(nx, ny) {
        for (let dy = 0; dy < this.h; dy++) {
            for (let dx = 0; dx < this.w; dx++) {
                if (this.isSolid(nx + dx, ny + dy)) {
                    return true;
                }
            }
        }
        return false;
    }

    unstuck() {
        if (this.type === 'pharaoh_guardian' || this.type === 'bat') return false; // floating/flying enemies don't get stuck in terrain
        if (this.checkCollision(this.x, this.y)) {
            for (let dy = 1; dy <= 24; dy++) {
                if (!this.checkCollision(this.x, this.y - dy)) {
                    this.y -= dy;
                    this.vy = 0;
                    return true;
                }
            }
        }
        return false;
    }

    update() {
        if (this.dead) return;

        // Perform stuck recovery
        this.unstuck();

        if (this.slowTimer > 0) this.slowTimer--;
        const speedScale = this.slowTimer > 0 ? 0.5 : 1.0;

        const p = game.players[0];
        let pdistX = p.x + PLAYER_W/2 - (this.x + this.w/2);
        pdistX = ((pdistX + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
        const pdistY = p.y + PLAYER_H/2 - (this.y + this.h/2);
        const distToPlayer = Math.sqrt(pdistX*pdistX + pdistY*pdistY);

        if (this.type === 'pharaoh_guardian') {
            this.vx = (pdistX > 0 ? 0.45 : -0.45) * speedScale;
            this.vy = (pdistY > 0 ? 0.35 : -0.35) * speedScale;

            const fury = this.hp < this.maxHp * 0.5;
            if (fury && this.chargeTimer === 0) {
                this.chargeTimer = 1;
                game.audio.playBossPhase();
                game.spawnFloatingText(this.x + this.w/2, this.y, "Furia del Guardián ⚡", "#ff4757");
            }

            this.shootTimer--;
            if (this.shootTimer <= 0) {
                this.shootTimer = fury ? 35 : 55;
                game.projectiles.push(new Projectile(this.x + this.w/2, this.y + this.h/2, p.x + PLAYER_W/2, p.y + PLAYER_H/2, 'boss_energy'));
                game.audio.playShoot();
            }

            if (fury) {
                this.summonTimer--;
                if (this.summonTimer <= 0) {
                    this.summonTimer = 300;
                    if (game.enemies.length < 15) {
                        const bx = ((this.x + (rng() - 0.5) * 40) % WORLD_W + WORLD_W) % WORLD_W;
                        game.enemies.push(new Enemy(bx, this.y - 10, 'bat'));
                        game.spawnFloatingText(this.x + this.w/2, this.y, "¡Esbirro Invocado! 🦇", "#ff6b81");
                    }
                }
            }

            const speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy) || 1;
            const maxSp = (fury ? 1.0 : 0.65) * speedScale;
            if (speed > maxSp) {
                this.vx = (this.vx / speed) * maxSp;
                this.vy = (this.vy / speed) * maxSp;
            }

            this.x = ((this.x + this.vx) % WORLD_W + WORLD_W) % WORLD_W;
            this.y += this.vy;
            if (this.y < 240) this.y = 240;
            if (this.y > 290) this.y = 290;
        } else if (this.type === 'turret') {
            this.vx = 0;
            this.vy = 0;
            this.shootTimer--;
            if (this.shootTimer <= 0) {
                this.shootTimer = 90 + (rng() * 30 | 0);
                if (distToPlayer < 140) {
                    game.projectiles.push(new Projectile(this.x + this.w/2, this.y + 4, p.x + PLAYER_W/2, p.y + PLAYER_H/2, 'turret_shot'));
                    game.audio.playShoot();
                }
            }
        } else if (this.type === 'bat') {
            this.vy *= 0.9;
            this.vx *= 0.9;
            if (distToPlayer < 120) {
                this.vx += (pdistX > 0 ? 0.15 : -0.15);
                this.vy += (pdistY > 0 ? 0.15 : -0.15);
            } else {
                this.wanderTimer--;
                if (this.wanderTimer <= 0) {
                    this.vx = (rng() - 0.5) * 0.8;
                    this.vy = (rng() - 0.5) * 0.8;
                    this.wanderTimer = 40 + (rng() * 60 | 0);
                }
            }
            const speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy);
            const maxSp = 1.8 * speedScale;
            if (speed > maxSp) {
                this.vx = (this.vx / speed) * maxSp;
                this.vy = (this.vy / speed) * maxSp;
            }

            let nextX = this.x + this.vx;
            nextX = ((nextX % WORLD_W) + WORLD_W) % WORLD_W;
            if (this.checkCollision(nextX, this.y)) {
                this.vx = -this.vx;
            } else {
                this.x = nextX;
            }
            const nextY = this.y + this.vy;
            if (this.checkCollision(this.x, nextY)) {
                this.vy = -this.vy;
            } else {
                this.y = nextY;
            }
        } else if (this.type === 'jumping_slime') {
            this.vy += GRAVITY * 0.8;
            if (this.vy > 6) this.vy = 6;

            if (this.chargeTimer > 0) {
                this.chargeTimer--;
                this.vx *= 0.8;
                if (this.chargeTimer === 0) {
                    this.vy = -5.5 * speedScale;
                    this.vx = (pdistX > 0 ? 1.6 : -1.6) * speedScale;
                }
            } else {
                const onGround = this.checkCollision(this.x, this.y + 1);
                if (onGround && distToPlayer < 90 && rng() < 0.02) {
                    this.chargeTimer = 30;
                } else {
                    this.wanderTimer--;
                    if (this.wanderTimer <= 0) {
                        this.vx = (rng() - 0.5) * 0.6 * speedScale;
                        this.wanderTimer = 60 + (rng() * 120 | 0);
                    }
                }
            }

            let nextX = this.x + this.vx;
            nextX = ((nextX % WORLD_W) + WORLD_W) % WORLD_W;
            if (this.checkCollision(nextX, this.y)) {
                this.vx = -this.vx;
            } else {
                this.x = nextX;
            }
            const nextY = this.y + this.vy;
            if (this.checkCollision(this.x, nextY)) {
                if (this.vy > 0) {
                    this.y = Math.floor(this.y);
                    while (!this.checkCollision(this.x, this.y + 1) && this.y < WORLD_H) {
                        this.y++;
                    }
                    this.vy = 0;
                } else {
                    this.vy = 0;
                }
            } else {
                this.y = nextY;
            }
        } else {
            this.vy += GRAVITY * 0.8;
            if (this.vy > 6) this.vy = 6;

            this.wanderTimer--;
            if (this.wanderTimer <= 0) {
                this.vx = (rng() - 0.5) * 0.6 * speedScale;
                this.wanderTimer = 60 + (rng() * 120 | 0);
            }

            let nextX = this.x + this.vx;
            nextX = ((nextX % WORLD_W) + WORLD_W) % WORLD_W;
            if (this.checkCollision(nextX, this.y)) {
                this.vx = -this.vx;
            } else {
                this.x = nextX;
            }

            const nextY = this.y + this.vy;
            if (this.checkCollision(this.x, nextY)) {
                if (this.vy > 0) {
                    this.y = Math.floor(this.y);
                    while (!this.checkCollision(this.x, this.y + 1) && this.y < WORLD_H) {
                        this.y++;
                    }
                    this.vy = 0;
                } else {
                    this.vy = 0;
                }
            } else {
                this.y = nextY;
            }
        }

        if (this.vx !== 0) this.facing = this.vx > 0 ? 1 : -1;

        for (let dy = 0; dy < this.h; dy++) {
            for (let dx = 0; dx < this.w; dx++) {
                const i = idx((this.x + dx) | 0, (this.y + dy) | 0);
                if (i >= 0) {
                    const pm = grid[i];
                    if (pm === MAT.ACID || pm === MAT.LAVA) {
                        this.hp -= (pm === MAT.LAVA ? 1 : 0.5);
                        if (this.hp <= 0) this.die();
                        break;
                    }
                }
            }
        }
    }

    die() {
        this.dead = true;
        if (game) {
            if (this.type === 'pharaoh_guardian') {
                game.score += 1000;
                document.getElementById('v-score').textContent = game.score;
                game.spawnFloatingText(this.x + this.w/2, this.y, "¡JEFE DERROTADO! +1000 pts 🏆", "#ffd700");
                game.items.push(new Item(this.x + this.w/2 - 5, this.y + this.h/2 - 5, 'ankh_of_ra'));
                game.audio.playExplode();
                game.screenShake = 24;
            } else {
                game.score += 25;
                document.getElementById('v-score').textContent = game.score;
                game.spawnFloatingText(this.x + this.w/2, this.y, "+25 pts 💥", "#ff6b6b");
                game.audio.playBreak();
            }
            const particleCount = this.type === 'pharaoh_guardian' ? 24 : 6;
            for (let k = 0; k < particleCount; k++) {
                const px = ((this.x + rng() * this.w) % WORLD_W + WORLD_W) % WORLD_W;
                const py = this.y + rng() * this.h;
                const pi = idx(px | 0, py | 0);
                if (pi >= 0 && grid[pi] === MAT.EMPTY) {
                    setCell(pi, rng() < 0.5 ? MAT.SMOKE : MAT.FIRE);
                }
            }
        }
    }

    draw(ctx, cam) {
        if (this.dead) return;
        const sx = getScreenX(this.x, cam) * cam.zoom;
        const sy = (this.y - cam.y) * cam.zoom;
        const sw = this.w * cam.zoom;
        const sh = this.h * cam.zoom;

        if (this.type === 'pharaoh_guardian') {
            const fury = this.hp < this.maxHp * 0.5;
            ctx.shadowColor = fury ? '#ff3838' : '#00d2d3';
            ctx.shadowBlur = 12;
            ctx.fillStyle = '#ffd700';
            ctx.beginPath();
            ctx.moveTo(sx + sw*0.2, sy + sh*0.9);
            ctx.lineTo(sx + sw*0.1, sy + sh*0.4);
            ctx.lineTo(sx + sw*0.5, sy);
            ctx.lineTo(sx + sw*0.9, sy + sh*0.4);
            ctx.lineTo(sx + sw*0.8, sy + sh*0.9);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = fury ? '#3a0007' : '#1e272e';
            ctx.fillRect(sx + sw*0.2, sy + sh*0.3, sw*0.6, sh*0.15);
            ctx.fillRect(sx + sw*0.15, sy + sh*0.5, sw*0.7, sh*0.15);
            ctx.fillRect(sx + sw*0.1, sy + sh*0.7, sw*0.8, sh*0.1);

            ctx.fillStyle = fury ? '#ff3838' : '#00d2d3';
            ctx.fillRect(sx + sw*0.3, sy + sh*0.35, 2*cam.zoom, 2*cam.zoom);
            ctx.fillRect(sx + sw*0.6, sy + sh*0.35, 2*cam.zoom, 2*cam.zoom);

            ctx.fillStyle = '#ffd700';
            ctx.fillRect(sx + sw*0.45, sy + sh*0.9, sw*0.1, sh*0.2);
            ctx.shadowBlur = 0;
        } else if (this.type === 'turret') {
            ctx.save();
            ctx.fillStyle = '#2d3436';
            ctx.strokeStyle = '#00ecec';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(sx + sw * 0.1, sy + sh);
            ctx.lineTo(sx + sw * 0.3, sy + sh * 0.25);
            ctx.lineTo(sx + sw * 0.5, sy);
            ctx.lineTo(sx + sw * 0.7, sy + sh * 0.25);
            ctx.lineTo(sx + sw * 0.9, sy + sh);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Glowing patterns
            ctx.strokeStyle = '#00d2d3';
            ctx.lineWidth = 1.0;
            ctx.beginPath();
            ctx.moveTo(sx + sw * 0.5, sy + sh * 0.3);
            ctx.lineTo(sx + sw * 0.5, sy + sh * 0.85);
            ctx.stroke();

            // Glowing eye
            ctx.fillStyle = '#ff007f';
            ctx.shadowColor = '#ff007f';
            ctx.shadowBlur = 6;
            ctx.beginPath();
            ctx.arc(sx + sw * 0.5, sy + sh * 0.3, 2.5 * cam.zoom, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        } else if (this.type === 'bat') {
            ctx.fillStyle = '#6c5ce7';
            ctx.fillRect(sx, sy, sw, sh);
            const flap = Math.sin(performance.now() / 80) > 0;
            ctx.fillStyle = '#a29bfe';
            if (flap) {
                ctx.fillRect(sx - 3 * cam.zoom, sy - 2 * cam.zoom, 3 * cam.zoom, 3 * cam.zoom);
                ctx.fillRect(sx + sw, sy - 2 * cam.zoom, 3 * cam.zoom, 3 * cam.zoom);
            } else {
                ctx.fillRect(sx - 3 * cam.zoom, sy + 2 * cam.zoom, 3 * cam.zoom, 3 * cam.zoom);
                ctx.fillRect(sx + sw, sy + 2 * cam.zoom, 3 * cam.zoom, 3 * cam.zoom);
            }
            ctx.fillStyle = '#ff7675';
            const ex = this.facing > 0 ? sw*0.6 : sw*0.2;
            ctx.fillRect(sx + ex, sy + sh*0.2, cam.zoom, cam.zoom);
        } else if (this.type === 'jumping_slime') {
            ctx.fillStyle = '#e67e22';
            ctx.beginPath();
            let squish = 1.0;
            if (this.chargeTimer > 0) squish = 0.5;
            else if (this.vy < 0) squish = 1.4;
            ctx.ellipse(sx + sw/2, sy + sh, sw/2, (sh/2) * squish, 0, Math.PI, 0);
            ctx.fill();

            ctx.fillStyle = '#111';
            const ex1 = this.facing > 0 ? sw*0.6 : sw*0.3;
            const ex2 = this.facing > 0 ? sw*0.8 : sw*0.5;
            ctx.fillRect(sx + ex1, sy + sh * (1 - 0.6 * squish), 2, 2);
            ctx.fillRect(sx + ex2, sy + sh * (1 - 0.6 * squish), 2, 2);
        } else {
            ctx.fillStyle = '#2ed573';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh, sw/2, Math.PI, 0);
            ctx.fill();

            ctx.fillStyle = '#111';
            const ex1 = this.facing > 0 ? sw*0.6 : sw*0.3;
            const ex2 = this.facing > 0 ? sw*0.8 : sw*0.5;
            ctx.fillRect(sx + ex1, sy + sh*0.4, 2, 2);
            ctx.fillRect(sx + ex2, sy + sh*0.4, 2, 2);
        }
    }
}

class Item {
    constructor(x, y, type = 'coin') {
        this.x = x;
        this.y = y;
        this.type = type;
        this.w = (type === 'relic' || type === 'ankh_of_ra') ? 10 : (type === 'chest' || type === 'chest_relic') ? 12 : 6;
        this.h = (type === 'relic' || type === 'ankh_of_ra') ? 10 : (type === 'chest' || type === 'chest_relic') ? 8 : 6;
        this.collected = false;
        this.bobOffset = rng() * Math.PI * 2;
    }

    update() {
        if (this.collected) return;

        game.players.forEach(p => {
            if (this.collected) return;
            let dx = this.x + this.w/2 - (p.x + PLAYER_W/2);
            dx = ((dx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
            const dy = this.y + this.h/2 - (p.y + PLAYER_H/2);
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 10) {
                this.collect();
            }
        });
    }

    collect() {
        this.collected = true;
        if (this.type === 'coin') {
            game.score += 50;
            document.getElementById('v-score').textContent = game.score;
            game.spawnFloatingText(this.x + this.w/2, this.y, "+50 Oro 🪙", "#ffd700");
            game.audio.playMissionComplete();
        } else if (this.type === 'potion_health') {
            const p = game.players[0];
            const added = p.addItem('potion_health');
            if (added) {
                game.spawnFloatingText(this.x + this.w/2, this.y, "+Poción Vida 🧪", "#2ed573");
                game.audio.playMissionComplete();
            } else {
                this.collected = false;
                game.spawnFloatingText(this.x + this.w/2, this.y - 10, "Inventario Lleno", "#ff4757");
            }
        } else if (this.type === 'potion_shield') {
            const p = game.players[0];
            const added = p.addItem('potion_shield');
            if (added) {
                game.spawnFloatingText(this.x + this.w/2, this.y, "+Poción Escudo 🛡️", "#6c5ce7");
                game.audio.playMissionComplete();
            } else {
                this.collected = false;
                game.spawnFloatingText(this.x + this.w/2, this.y - 10, "Inventario Lleno", "#ff4757");
            }
        } else if (this.type === 'relic') {
            game.triggerVictory();
        } else if (this.type === 'chest' || this.type === 'chest_relic') {
            game.audio.playChestOpen();
            game.spawnFloatingText(this.x + this.w/2, this.y, "Cofre Abierto 📦", "#ffd700");
            if (this.type === 'chest_relic') {
                let rtype = 'ankh_of_life';
                if (this.y >= 90 && this.y < 170) rtype = 'eye_of_horus';
                else if (this.y >= 170 && this.y < 245) rtype = 'scarab_of_power';
                game.items.push(new Item(this.x, this.y - 8, rtype));
            } else {
                const count = 1 + (rng() * 2 | 0);
                for (let c = 0; c < count; c++) {
                    const itype = rng() < 0.5 ? 'coin' : (rng() < 0.5 ? 'potion_health' : 'potion_shield');
                    const ix = ((this.x + (rng() - 0.5) * 16) % WORLD_W + WORLD_W) % WORLD_W;
                    const iy = this.y - 8 - c * 6;
                    game.items.push(new Item(ix, iy, itype));
                }
            }
        } else if (this.type === 'eye_of_horus') {
            game.storyArtifacts.eye_of_horus = true;
            game.spawnFloatingText(this.x + this.w/2, this.y, "¡Ojo de Horus! 👁️", "#00d2d3");
            game.audio.playMissionComplete();
            game.updateRelicsHUD();
        } else if (this.type === 'scarab_of_power') {
            game.storyArtifacts.scarab_of_power = true;
            game.spawnFloatingText(this.x + this.w/2, this.y, "¡Escarabajo de Poder! 🪲", "#1dd1a1");
            game.audio.playMissionComplete();
            game.updateRelicsHUD();
            const slider = document.getElementById('brush-slider');
            if (slider) {
                slider.max = "12";
            }
        } else if (this.type === 'ankh_of_life') {
            game.storyArtifacts.ankh_of_life = true;
            game.spawnFloatingText(this.x + this.w/2, this.y, "¡Ankh de Vida! ☥", "#fecb2f");
            game.audio.playMissionComplete();
            game.updateRelicsHUD();
        } else if (this.type === 'ankh_of_ra') {
            game.triggerVictory();
        }
    }

    draw(ctx, cam) {
        if (this.collected) return;

        const sx = getScreenX(this.x, cam) * cam.zoom;
        const bob = Math.sin(performance.now() / 200 + this.bobOffset) * 2;
        const sy = (this.y - cam.y) * cam.zoom + bob;
        const sw = this.w * cam.zoom;
        const sh = this.h * cam.zoom;

        if (this.type === 'coin') {
            ctx.fillStyle = '#ffb300';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = '#ffe082';
            ctx.beginPath();
            ctx.arc(sx + sw/2 - 1, sy + sh/2 - 1, sw/4, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'potion_health') {
            ctx.fillStyle = '#2ed573';
            ctx.fillRect(sx + sw*0.2, sy + sh*0.4, sw*0.6, sh*0.6);
            ctx.fillStyle = '#ffe0c0';
            ctx.fillRect(sx + sw*0.35, sy + sh*0.1, sw*0.3, sh*0.3);
        } else if (this.type === 'potion_shield') {
            ctx.fillStyle = '#00cec9';
            ctx.fillRect(sx + sw*0.2, sy + sh*0.4, sw*0.6, sh*0.6);
            ctx.fillStyle = '#ffe0c0';
            ctx.fillRect(sx + sw*0.35, sy + sh*0.1, sw*0.3, sh*0.3);
        } else if (this.type === 'relic') {
            ctx.shadowColor = '#ffd700';
            ctx.shadowBlur = 15;
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(sx, sy, sw, sh);
            ctx.fillStyle = '#d4af37';
            ctx.strokeRect(sx, sy, sw, sh);
            ctx.shadowBlur = 0;
        } else if (this.type === 'chest' || this.type === 'chest_relic') {
            ctx.fillStyle = '#d4af37';
            ctx.fillRect(sx, sy + sh*0.3, sw, sh*0.7);
            ctx.fillStyle = '#00d2d3';
            ctx.fillRect(sx, sy, sw, sh*0.3);
            ctx.fillStyle = '#fff';
            ctx.fillRect(sx + sw*0.4, sy + sh*0.4, sw*0.2, sh*0.3);
        } else if (this.type === 'eye_of_horus') {
            ctx.fillStyle = '#00d2d3';
            ctx.font = `bold ${Math.floor(10 * cam.zoom)}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('👁️', sx + sw/2, sy + sh/2);
        } else if (this.type === 'scarab_of_power') {
            ctx.fillStyle = '#1dd1a1';
            ctx.font = `bold ${Math.floor(10 * cam.zoom)}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('🪲', sx + sw/2, sy + sh/2);
        } else if (this.type === 'ankh_of_life') {
            ctx.fillStyle = '#fecb2f';
            ctx.font = `bold ${Math.floor(10 * cam.zoom)}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('☥', sx + sw/2, sy + sh/2);
        } else if (this.type === 'ankh_of_ra') {
            ctx.shadowColor = '#ff3838';
            ctx.shadowBlur = 15;
            ctx.fillStyle = '#ff3838';
            ctx.font = `bold ${Math.floor(12 * cam.zoom)}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('☥', sx + sw/2, sy + sh/2);
            ctx.shadowBlur = 0;
        }
    }
}

class Projectile {
    constructor(x, y, tx, ty, type = 'player') {
        this.x = x;
        this.y = y;
        this.type = type;
        let dx = tx - x;
        dx = ((dx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
        const dy = ty - y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        const speed = type === 'boss_energy' ? 2.2 : (type === 'turret_shot' ? 2.5 : 4.0);
        this.vx = (dx / dist) * speed;
        this.vy = (dy / dist) * speed;
        this.w = type === 'boss_energy' ? 5 : (type === 'turret_shot' ? 4 : 4);
        this.h = type === 'boss_energy' ? 5 : (type === 'turret_shot' ? 4 : 4);
        this.dead = false;
        this.life = 120;
    }

    isSolid(x, y) {
        const i = idx(x | 0, y | 0);
        if (i < 0) return true;
        const t = PROP_TYPE[grid[i]];
        return t === 1;
    }

    update() {
        if (this.dead) return;

        if (this.type === 'boss_energy') {
            const p = game.players[0];
            let pdx = p.x + PLAYER_W/2 - this.x;
            pdx = ((pdx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
            const pdy = p.y + PLAYER_H/2 - this.y;
            const pdist = Math.sqrt(pdx*pdx + pdy*pdy) || 1;
            this.vx += (pdx / pdist) * 0.12;
            this.vy += (pdy / pdist) * 0.12;
            const speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy) || 1;
            if (speed > 2.2) {
                this.vx = (this.vx / speed) * 2.2;
                this.vy = (this.vy / speed) * 2.2;
            }
        }

        this.x += this.vx;
        this.x = ((this.x % WORLD_W) + WORLD_W) % WORLD_W;
        this.y += this.vy;
        this.life--;

        if (this.life <= 0) {
            this.dead = true;
            return;
        }

        // Spawning elemental path effects
        if (this.type === 'fire') {
            const pi = idx(this.x | 0, this.y | 0);
            if (pi >= 0 && grid[pi] === MAT.EMPTY && rng() < 0.35) {
                setCell(pi, MAT.FIRE);
            }
        }

        if (this.isSolid(this.x, this.y)) {
            this.explode();
            return;
        }

        if (this.type === 'boss_energy' || this.type === 'turret_shot') {
            game.players.forEach(p => {
                if (this.dead) return;
                let pdx = this.x - (p.x + PLAYER_W/2);
                pdx = ((pdx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
                const pdy = this.y - (p.y + PLAYER_H/2);
                const pdist = Math.sqrt(pdx*pdx + pdy*pdy);
                if (pdist < 8) {
                    if (p.dmgTimer <= 0) {
                        let dmg = this.type === 'boss_energy' ? 15 : 8;
                        if (game.difficulty === 'easy') dmg *= 0.5;
                        else if (game.difficulty === 'hard') dmg *= 2.0;
                        p.hp -= (dmg | 0);
                        p.dmgTimer = 15;
                        game.spawnFloatingText(p.x + PLAYER_W/2, p.y, `-${dmg | 0} HP 💥`, "#ff4757");
                        game.audio.playBreak();
                    }
                    this.explode();
                }
            });
        } else {
            game.enemies.forEach(e => {
                if (e.dead || this.dead) return;
                let edx = this.x - (e.x + e.w/2);
                edx = ((edx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
                const edy = this.y - (e.y + e.h/2);
                const dist = Math.sqrt(edx*edx + edy*edy);
                const hitDist = e.type === 'pharaoh_guardian' ? 14 : 8;
                if (dist < hitDist) {
                    let dmg = 10;
                    if (this.type === 'plasma') dmg = 25;
                    e.hp -= dmg;
                    if (this.type === 'ice') {
                        e.slowTimer = 180;
                        game.spawnFloatingText(e.x + e.w/2, e.y, "Ralentizado ❄️", "#70a1ff");
                    }
                    if (e.hp <= 0) e.die();
                    else {
                        game.spawnFloatingText(e.x + e.w/2, e.y, `-${dmg} HP`, this.type === 'plasma' ? '#eccc68' : '#ffa502');
                        game.audio.playBreak();
                    }
                    this.explode();
                }
            });
        }
    }

    explode() {
        this.dead = true;
        const tx = this.x | 0;
        const ty = this.y | 0;

        if (this.type === 'fire') {
            explode(tx, ty, 6);
            for (let dy = -3; dy <= 3; dy++) {
                for (let dx = -3; dx <= 3; dx++) {
                    const ti = idx(tx+dx, ty+dy);
                    if (ti >= 0 && grid[ti] === MAT.EMPTY && rng() < 0.5) {
                        setCell(ti, MAT.FIRE);
                    }
                }
            }
        } else if (this.type === 'acid') {
            for (let dy = -4; dy <= 4; dy++) {
                for (let dx = -4; dx <= 4; dx++) {
                    if (dx*dx+dy*dy > 16) continue;
                    const ti = idx(tx+dx, ty+dy);
                    if (ti >= 0 && grid[ti] !== MAT.EMPTY && grid[ti] !== MAT.BEDROCK) {
                        setCell(ti, MAT.EMPTY);
                    }
                }
            }
            explode(tx, ty, 4);
        } else if (this.type === 'ice') {
            for (let dy = -3; dy <= 3; dy++) {
                for (let dx = -3; dx <= 3; dx++) {
                    const ti = idx(tx+dx, ty+dy);
                    if (ti >= 0) {
                        const m = grid[ti];
                        if (m === MAT.WATER || m === MAT.OIL) {
                            setCell(ti, MAT.ICE);
                        }
                    }
                }
            }
            explode(tx, ty, 4);
        } else if (this.type === 'plasma') {
            explode(tx, ty, 8);
            for (let dy = -3; dy <= 3; dy++) {
                for (let dx = -3; dx <= 3; dx++) {
                    const ti = idx(tx+dx, ty+dy);
                    if (ti >= 0 && grid[ti] === MAT.STONE) {
                        setCell(ti, MAT.LAVA);
                    }
                }
            }
        } else {
            explode(tx, ty, 4 + (rng() * 3 | 0));
        }
    }

    draw(ctx, cam) {
        if (this.dead) return;

        const sx = getScreenX(this.x, cam) * cam.zoom;
        const sy = (this.y - cam.y) * cam.zoom;
        const sw = this.w * cam.zoom;
        const sh = this.h * cam.zoom;

        ctx.save();
        if (this.type === 'boss_energy') {
            ctx.shadowColor = '#d63031';
            ctx.shadowBlur = 8;
            ctx.fillStyle = '#9b59b6';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = '#e056fd';
            ctx.beginPath();
            ctx.arc(sx + sw/2 - 1, sy + sh/2 - 1, sw/4, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'turret_shot') {
            ctx.shadowColor = '#ff007f';
            ctx.shadowBlur = 8;
            ctx.fillStyle = '#fd79a8';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(sx + sw/2 - 1, sy + sh/2 - 1, sw/4, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'fire') {
            ctx.shadowColor = '#ff7f50';
            ctx.shadowBlur = 6;
            ctx.fillStyle = '#ff7f50';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'acid') {
            ctx.shadowColor = '#2ed573';
            ctx.shadowBlur = 6;
            ctx.fillStyle = '#2ed573';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'ice') {
            ctx.shadowColor = '#70a1ff';
            ctx.shadowBlur = 6;
            ctx.fillStyle = '#70a1ff';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();
        } else if (this.type === 'plasma') {
            ctx.shadowColor = '#ff4757';
            ctx.shadowBlur = 10;
            ctx.fillStyle = '#eccc68';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();
        } else {
            ctx.fillStyle = '#ff5722';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2, sw/2, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = '#ffeb3b';
            ctx.beginPath();
            ctx.arc(sx + sw/2 - 1, sy + sh/2 - 1, sw/4, 0, Math.PI*2);
            ctx.fill();
        }
        ctx.restore();
    }
}

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
        this.shootCooldown = 0;
        this.inventory = [null, null];
        
        // Custom gameplay stats
        this.dashTimer = 0;
        this.dashCooldown = 0;
        this.ankhRegenTimer = 0;
        this.mineCooldown = 0;
        this.paintCooldown = 0;
    }

    checkCollision(px, py) {
        for (let dy = 0; dy < PLAYER_H; dy++) {
            for (let dx = 0; dx < PLAYER_W; dx++) {
                if (this.isSolid(px + dx, py + dy)) {
                    return true;
                }
            }
        }
        return false;
    }

    unstuck() {
        if (this.checkCollision(this.x, this.y)) {
            for (let dy = 1; dy <= 24; dy++) {
                if (!this.checkCollision(this.x, this.y - dy)) {
                    this.y -= dy;
                    this.vy = 0;
                    this.onGround = true;
                    return true;
                }
            }
        }
        return false;
    }

    dash() {
        if (this.dashCooldown > 0) return;
        this.dashTimer = 12;
        this.dashCooldown = 35;
        this.vx = this.facing * 8.0;
        this.vy = 0;
        if (game) {
            game.audio.playDash();
        }
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
        this.dashTimer = 0;
        this.dashCooldown = 0;
    }

    addItem(itemType) {
        if (this.inventory[0] === null) {
            this.inventory[0] = itemType;
            if (game) game.updateInventoryUI();
            return true;
        } else if (this.inventory[1] === null) {
            this.inventory[1] = itemType;
            if (game) game.updateInventoryUI();
            return true;
        }
        return false;
    }

    useItem(slot) {
        const item = this.inventory[slot];
        if (item === null) return;

        if (item === 'potion_health') {
            this.hp = Math.min(MAX_HP, this.hp + 50);
            if (game) game.spawnFloatingText(this.x + PLAYER_W/2, this.y, "+50 HP 🧪", "#2ed573");
            this.inventory[slot] = null;
            if (game) {
                game.audio.playPlace();
                game.updateInventoryUI();
            }
        } else if (item === 'potion_shield') {
            this.dmgTimer = 600;
            if (game) game.spawnFloatingText(this.x + PLAYER_W/2, this.y, "¡ESCUDO ACTIVO! 🛡️", "#00cec9");
            this.inventory[slot] = null;
            if (game) {
                game.audio.playPlace();
                game.updateInventoryUI();
            }
        }
    }

    update() {
        this.unstuck();

        // 1. Relic Passive: Ankh of Life HP Regen
        if (game.storyArtifacts.ankh_of_life) {
            this.ankhRegenTimer = (this.ankhRegenTimer + 1) % 60;
            if (this.ankhRegenTimer === 0 && this.hp < MAX_HP) {
                this.hp = Math.min(MAX_HP, this.hp + 1);
            }
        }

        // 2. Dash physics override
        if (this.dashTimer > 0) {
            this.dashTimer--;
            this.vx = this.facing * 8.0;
            this.vy = 0;
            // Spawn trail particles in the CA grid
            if (game) {
                game.spawnDashParticles(this.x + PLAYER_W/2, this.y + PLAYER_H/2, this.facing);
            }
            // Maintain invincibility frames (iframes)
            this.dmgTimer = Math.max(this.dmgTimer, 2);
        } else {
            // Standard movement
            this.vx += this.ax * PLAYER_SPEED * 0.3;
            this.vx *= 0.82;
            if (Math.abs(this.vx) < 0.05) this.vx = 0;
            if (this.vx !== 0) this.facing = this.vx > 0 ? 1 : -1;

            if (this.jumpReq && this.onGround) { this.vy = PLAYER_JUMP; this.onGround = false; }
            this.jumpReq = false;

            const cx = (this.x + PLAYER_W/2)|0, cy = (this.y + PLAYER_H/2)|0;
            const ci = idx(cx, cy);
            const inLiquid = ci >= 0 && PROP_TYPE[grid[ci]] === 3;
            if (inLiquid) {
                this.vy += GRAVITY * 0.25;
                this.vy *= 0.9;
                if (this.jumpReq || this.ax !== 0) this.vy -= 0.8;
                
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
        }

        this.x += this.vx;
        this.x = ((this.x % WORLD_W) + WORLD_W) % WORLD_W;

        if (this.id === 0 && game.gameMode === 'survival') {
            const hasAllRelics = game.storyArtifacts.eye_of_horus && game.storyArtifacts.scarab_of_power && game.storyArtifacts.ankh_of_life;
            if (!hasAllRelics && this.y >= 250 && this.x >= 445 && this.x <= 575) {
                this.x = this.x < 510 ? 440 : 580;
                this.vx = 0;
                game.audio.playBreak();
                game.screenShake = 6;
                game.spawnFloatingText(this.x + PLAYER_W/2, this.y, "Campo de fuerza de Ra Activo 🛡️", "#ff4757");
            }
        }

        this.resolveX();

        this.y += this.vy;
        this.resolveY();

        if (this.y < 0) { this.y = 0; this.vy = 0; }
        if (this.y > WORLD_H - PLAYER_H - 2) { this.y = WORLD_H - PLAYER_H - 2; this.vy = 0; this.onGround = true; }
        if (this.shootCooldown > 0) this.shootCooldown--;
        if (this.dashCooldown > 0) this.dashCooldown--;
        if (this.mineCooldown > 0) this.mineCooldown--;
        if (this.paintCooldown > 0) this.paintCooldown--;

        this.dmgTimer--;
        if (this.dmgTimer <= 0) {
            for (let dy = 0; dy < PLAYER_H; dy++) {
                for (let dx = 0; dx < PLAYER_W; dx++) {
                    const pi = idx((this.x+dx)|0, (this.y+dy)|0);
                    if (pi < 0) continue;
                    const pm = grid[pi];
                    if (pm === MAT.FIRE || pm === MAT.LAVA || pm === MAT.ACID) {
                        let dmg = (pm === MAT.LAVA ? 3 : pm === MAT.ACID ? 2 : 1);
                        if (game.difficulty === 'easy') dmg *= 0.5;
                        else if (game.difficulty === 'hard') dmg *= 2.0;
                        if (game.storyArtifacts.ankh_of_life) dmg *= 0.75;
                        this.hp -= Math.max(1, dmg | 0);
                        this.dmgTimer = 10;
                        break;
                    }
                }
                if (this.dmgTimer > 0) break;
            }

            if (this.dmgTimer <= 0) {
                game.enemies.forEach(e => {
                    if (e.dead || this.dmgTimer > 0) return;
                    let edx = this.x + PLAYER_W/2 - (e.x + e.w/2);
                    edx = ((edx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
                    const edy = this.y + PLAYER_H/2 - (e.y + e.h/2);
                    const dist = Math.sqrt(edx*edx + edy*edy);
                    const colDist = e.type === 'pharaoh_guardian' ? 14 : 8;
                    if (dist < colDist) {
                        let dmg = e.type === 'pharaoh_guardian' ? 20 : e.type === 'bat' ? 8 : 10;
                        if (game.difficulty === 'easy') dmg *= 0.5;
                        else if (game.difficulty === 'hard') dmg *= 2.0;
                        this.hp -= (dmg | 0);
                        this.dmgTimer = 30;
                        game.spawnFloatingText(this.x + PLAYER_W/2, this.y, `-${dmg | 0} HP 💥`, "#ff4757");
                        game.audio.playBreak();
                        game.screenShake = 8;
                    }
                });
            }
        }
        if (this.hp <= 0) {
            if (game.gameMode === 'survival') {
                game.lives--;
                const livesEl = document.getElementById('v-lives');
                if (livesEl) livesEl.textContent = game.lives;
                if (game.lives <= 0) {
                    game.triggerGameOver();
                    return;
                }
            }
            this.hp = MAX_HP;
            this.spawn();
            const flash = document.getElementById('respawn-flash');
            if (flash) { flash.style.opacity = '1'; setTimeout(() => { flash.style.transition='opacity 0.6s'; flash.style.opacity='0'; setTimeout(()=>{ flash.style.transition='opacity 0.05s'; }, 650); }, 80); }
        }
    }

    isSolid(x, y) {
        const i = idx(x|0, y|0);
        if (i < 0) return true;
        const t = PROP_TYPE[grid[i]];
        return t === 1 || t === 2;
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
        const sx = getScreenX(this.x, cam) * cam.zoom;
        const sy = (this.y - cam.y) * cam.zoom;
        const sw = PLAYER_W * cam.zoom;
        const sh = PLAYER_H * cam.zoom;

        // Recently damaged flicker check or dashing
        const isFlicker = this.dmgTimer > 0 && this.dmgTimer < 60 && (this.dmgTimer % 4 < 2);
        if (isFlicker || this.dashTimer > 0) {
            ctx.save();
            ctx.globalAlpha = this.dashTimer > 0 ? 0.6 : 0.35;
        }

        // Squash & Stretch based on vertical velocity
        let scaleX = 1.0;
        let scaleY = 1.0;
        if (this.vy < 0) { // Jumping
            scaleY = 1.15;
            scaleX = 0.85;
        } else if (this.vy > 1.0 && !this.onGround) { // Falling
            scaleY = 1.25;
            scaleX = 0.8;
        }

        // Idle Bobbing
        const bob = Math.sin(Date.now() * 0.007) * 0.5 * (Math.abs(this.vx) > 0.1 ? 0.2 : 1.0);

        // Draw Ghost Trails if Dashing
        if (this.dashTimer > 0) {
            for (let trail = 1; trail <= 2; trail++) {
                ctx.save();
                ctx.globalAlpha = 0.25 / trail;
                const offsetG = -this.facing * trail * 8 * cam.zoom;
                ctx.fillStyle = '#00f2fe';
                ctx.fillRect(sx + offsetG + sw * 0.1, sy + sh * 0.3 + bob, sw * 0.8, sh * 0.45);
                ctx.fillStyle = '#ff0055';
                ctx.fillRect(sx + offsetG + (this.facing > 0 ? sw * 0.45 : sw * 0.15), sy + sh * 0.12 + bob, sw * 0.4, sh * 0.08);
                ctx.restore();
            }
        }

        ctx.save();
        // Translate to player center to apply squash/stretch scale
        ctx.translate(sx + sw/2, sy + sh);
        ctx.scale(scaleX, scaleY);
        // Translate back (relative to bottom-center of the player)
        ctx.translate(-sw/2, -sh);

        // 1. Draw Player Shadow
        ctx.fillStyle = 'rgba(0,0,0,0.25)';
        ctx.beginPath();
        ctx.ellipse(sw/2, sh - 1, sw*0.8, 3, 0, 0, Math.PI*2);
        ctx.fill();

        // 2. Draw Legs (swinging if moving)
        const isMoving = Math.abs(this.vx) > 0.1;
        const swing = isMoving ? Math.sin(Date.now() * 0.016) * sh * 0.18 : 0;
        const colorS = this.id === 0 ? '#ff6b81' : '#70a1ff';
        
        ctx.fillStyle = '#2f3542'; // Dark legs/boots
        // Left Leg
        ctx.fillRect(sw*0.2 - (isMoving ? swing : 0), sh*0.75 + bob, sw*0.22, sh*0.25);
        // Right Leg
        ctx.fillRect(sw*0.58 + (isMoving ? swing : 0), sh*0.75 + bob, sw*0.22, sh*0.25);

        // 3. Draw Cyber Cape (flowing behind player)
        ctx.fillStyle = this.id === 0 ? 'rgba(235, 77, 75, 0.85)' : 'rgba(74, 105, 189, 0.85)';
        ctx.beginPath();
        const capeDir = -this.facing;
        const capeW = sw * 0.3;
        const capeFlow = isMoving ? Math.sin(Date.now() * 0.02) * sw * 0.15 : 0;
        ctx.moveTo(sw/2 - capeDir*sw*0.1, sh*0.3 + bob);
        ctx.lineTo(sw/2 + capeDir*sw*0.4 + capeFlow, sh*0.75 + bob + sh*0.08);
        ctx.lineTo(sw/2 - capeDir*sw*0.4, sh*0.78 + bob);
        ctx.closePath();
        ctx.fill();

        // 4. Draw Cybernetic Body Armor
        ctx.fillStyle = colorS;
        ctx.fillRect(sw*0.1, sh*0.3 + bob, sw*0.8, sh*0.45);
        // Golden collar plate
        ctx.fillStyle = '#ffd700';
        ctx.fillRect(sw*0.1, sh*0.3 + bob, sw*0.8, sh*0.08);

        // 5. Draw Cyber Nemes Headdress & Head
        // Base Face skin
        ctx.fillStyle = '#ffd2a1';
        ctx.beginPath();
        ctx.arc(sw/2, sh*0.2 + bob, sw*0.38, 0, Math.PI*2);
        ctx.fill();

        // Golden Nemes hood
        ctx.fillStyle = '#ffd700'; // Gold
        ctx.beginPath();
        ctx.moveTo(sw*0.1, sh*0.22 + bob);
        ctx.lineTo(sw*0.9, sh*0.22 + bob);
        ctx.lineTo(sw*0.8, -sh*0.05 + bob);
        ctx.lineTo(sw*0.2, -sh*0.05 + bob);
        ctx.closePath();
        ctx.fill();

        // Nemes Stripes
        ctx.fillStyle = this.id === 0 ? '#1e3799' : '#0a3d62'; // Cyber blue stripes
        ctx.fillRect(sw*0.25, -sh*0.05 + bob, sw*0.1, sh*0.27);
        ctx.fillRect(sw*0.45, -sh*0.05 + bob, sw*0.1, sh*0.27);
        ctx.fillRect(sw*0.65, -sh*0.05 + bob, sw*0.1, sh*0.27);

        // 6. Draw Cyber Visor
        ctx.fillStyle = this.id === 0 ? '#00f2fe' : '#ff0055'; // Neon Cyan or Hot Pink Visor
        const visorX = this.facing > 0 ? sw*0.45 : sw*0.15;
        ctx.fillRect(visorX, sh*0.12 + bob, sw*0.4, sh*0.08);
        // Visor shine
        ctx.fillStyle = '#fff';
        ctx.fillRect(this.facing > 0 ? sw*0.65 : sw*0.25, sh*0.12 + bob, sw*0.1, sh*0.08);

        // 7. Draw Active Handheld Tool
        const handX = this.facing > 0 ? sw * 0.75 : sw * 0.25;
        const handY = sh * 0.5 + bob;
        
        ctx.save();
        ctx.translate(handX, handY);
        ctx.scale(this.facing, 1);
        
        if (this.tool === TOOL_STAFF) {
            // Cyber Staff of Ra
            ctx.strokeStyle = '#2f3542';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(0, sh*0.18);
            ctx.lineTo(sw*0.35, -sh*0.25);
            ctx.stroke();
            // Glowing tip
            ctx.fillStyle = '#ff7f50';
            ctx.beginPath();
            ctx.arc(sw*0.35, -sh*0.25, 2.5, 0, Math.PI*2);
            ctx.fill();
            // Inner glow
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(sw*0.35, -sh*0.25, 1, 0, Math.PI*2);
            ctx.fill();
        } else if (this.tool === TOOL_MINE) {
            // Cyber Pickaxe
            ctx.strokeStyle = '#57606f';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(0, sh*0.1);
            ctx.lineTo(sw*0.3, -sh*0.15);
            ctx.stroke();
            // Pickaxe head
            ctx.strokeStyle = '#a4b0be';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(sw*0.3, -sh*0.15, sw*0.3, Math.PI*0.1, Math.PI*0.9);
            ctx.stroke();
        } else if (this.tool === TOOL_BOMB) {
            // Cyber Bomb
            ctx.fillStyle = '#1e252b';
            ctx.beginPath();
            ctx.arc(sw*0.25, 0, 3, 0, Math.PI*2);
            ctx.fill();
            // Glowing fuse tip
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(sw*0.25, -4, 1.5, 1.5);
        } else if (this.tool === TOOL_PLACE) {
            // Cyber Paintbrush
            ctx.strokeStyle = '#57606f';
            ctx.lineWidth = 1.0;
            ctx.beginPath();
            ctx.moveTo(0, sh*0.1);
            ctx.lineTo(sw*0.3, -sh*0.12);
            ctx.stroke();
            // Color tip based on selected material
            const matColor = PROPS[this.selectedMat]?.color || '#ffffff';
            ctx.fillStyle = matColor;
            ctx.fillRect(sw*0.3, -sh*0.14, 2.5, 2.5);
        }
        ctx.restore();

        ctx.restore(); // End scale/squash transform

        // 8. Draw Cyber Shield Bubble (active shield potion effect)
        if (this.dmgTimer > 60) {
            ctx.save();
            ctx.strokeStyle = 'rgba(0, 206, 203, 0.65)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 3]);
            ctx.beginPath();
            const shieldRadius = sw * 0.95;
            const rot = (Date.now() * 0.003) % (Math.PI*2);
            ctx.arc(sx + sw/2, sy + sh/2 + bob, shieldRadius, rot, rot + Math.PI*2);
            ctx.stroke();
            
            ctx.fillStyle = 'rgba(0, 206, 203, 0.06)';
            ctx.beginPath();
            ctx.arc(sx + sw/2, sy + sh/2 + bob, shieldRadius, 0, Math.PI*2);
            ctx.fill();
            ctx.restore();
        }

        // 9. Draw HP Bar above player
        const hpW = sw + 4;
        const hpRatio = this.hp / MAX_HP;
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillRect(sx - 2, sy - 6, hpW, 3);
        ctx.fillStyle = hpRatio > 0.5 ? '#2ed573' : hpRatio > 0.25 ? '#ffa502' : '#ff4757';
        ctx.fillRect(sx - 2, sy - 6, hpW * hpRatio, 3);

        if (isFlicker) {
            ctx.restore();
        }
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
        let tx = px + PLAYER_W/2 - this.viewW/2;
        tx = ((tx % WORLD_W) + WORLD_W) % WORLD_W;
        const ty = py + PLAYER_H/2 - this.viewH/2;
        const f = 1 - Math.pow(0.02, dt);
        
        let dx = tx - this.x;
        dx = ((dx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
        
        this.x += dx * f;
        this.y += (ty - this.y) * f;
        this.x = ((this.x % WORLD_W) + WORLD_W) % WORLD_W;
        this.y = Math.max(0, Math.min(this.y, WORLD_H - this.viewH));
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

        this.gameMode = 'survival'; // 'survival' or 'sandbox'
        this.lives = 3;
        this.difficulty = 'normal'; // 'easy', 'normal', 'hard'
        this.isGameOver = false;
        this.isVictory = false;
        this.enemies = [];
        this.items = [];
        this.projectiles = [];
        this.storyArtifacts = { eye_of_horus: false, scarab_of_power: false, ankh_of_life: false };
        this.debugMode = false;

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        generateWorld();
        this.players[0].spawn();
        this.spawnEntities();
        this.setupPalette();
        this.setupTools();
        this.setupBrushSlider();
        this.setupEvents();
        this.setupMPPanel();
        this.setupSettingsPanel();
        this.setupInventoryClicks();
        this.selectRandomMission();
        setTimeout(() => { const t = document.getElementById('tutorial'); if(t) t.style.opacity = 0; }, 5000);

        // WebRTC Auto-Join invitation link parsing
        if (window.location.hash && window.location.hash.startsWith('#join=')) {
            const offer = window.location.hash.slice(6);
            if (offer) {
                setTimeout(() => {
                    const mpPanel = document.getElementById('mp-panel');
                    if (mpPanel) mpPanel.classList.add('show');
                    const mpCode = document.getElementById('mp-code');
                    if (mpCode) {
                        mpCode.value = offer;
                        mpCode.style.display = 'block';
                    }
                    const mpActions = document.getElementById('mp-actions');
                    if (mpActions) mpActions.style.display = 'flex';
                    const mpStatus = document.getElementById('mp-status');
                    if (mpStatus) mpStatus.textContent = 'Uniéndose automáticamente... Generando respuesta...';
                    this.mp.join(offer);
                }, 500);
            }
        }
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

    spawnEntities() {
        this.enemies = [];
        this.items = [];
        this.projectiles = [];

        // Clear Boss Chamber at center of Lava Core
        const bx = 512;
        const by = 265;
        for (let dy = -10; dy < 16; dy++) {
            for (let dx = -16; dx < 16; dx++) {
                const pi = idx(bx + dx, by + dy);
                if (pi >= 0 && grid[pi] !== MAT.BEDROCK) {
                    setCell(pi, MAT.EMPTY);
                }
            }
        }
        // Spawn Pharaoh Guardian Boss
        this.enemies.push(new Enemy(bx - 10, by, 'pharaoh_guardian'));

        const findFloorY = (x, startY, endY) => {
            for (let y = startY; y < endY; y++) {
                const i = idx(x, y);
                const belowI = idx(x, y + 1);
                if (i >= 0 && belowI >= 0 && grid[i] === MAT.EMPTY && PROP_TYPE[grid[belowI]] === 1) {
                    return y;
                }
            }
            return -1;
        };

        const clearChamber = (cx, cy, r = 4) => {
            for (let dy = -r; dy <= r; dy++) {
                for (let dx = -r; dx <= r; dx++) {
                    const pi = idx(cx + dx, cy + dy);
                    if (pi >= 0 && grid[pi] !== MAT.BEDROCK) {
                        setCell(pi, MAT.EMPTY);
                    }
                }
            }
        };

        // Spawn 3 Story chests containing relics
        // 1. Ankh of Life in Forest (x=180)
        let fY = findFloorY(180, 20, 85);
        if (fY === -1) fY = 50;
        clearChamber(180, fY, 3);
        this.items.push(new Item(174, fY - 8, 'chest_relic'));

        // 2. Eye of Horus in Crystal Caverns (x=420)
        let cY = findFloorY(420, 95, 165);
        if (cY === -1) cY = 120;
        clearChamber(420, cY, 3);
        this.items.push(new Item(414, cY - 8, 'chest_relic'));

        // 3. Scarab of Power in Poison Caves (x=820)
        let pY = findFloorY(820, 175, 240);
        if (pY === -1) pY = 200;
        clearChamber(820, pY, 3);
        this.items.push(new Item(814, pY - 8, 'chest_relic'));

        // Surface Forest: standard slimes, coins, health potion, and 3 standard chests
        for (let i = 0; i < 20; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 10, 85);
            if (y !== -1) {
                this.enemies.push(new Enemy(x, y, 'slime'));
                if (i < 3) {
                    clearChamber(x, y, 3);
                    this.items.push(new Item(x - 6, y - 8, 'chest'));
                } else {
                    if (rng() < 0.6) this.items.push(new Item(x, y - 10, 'coin'));
                    else if (rng() < 0.2) this.items.push(new Item(x, y - 10, 'potion_health'));
                }
            }
        }

        // Crystal Caverns: jumping slimes, bats, coins, shield potions, and 3 standard chests
        for (let i = 0; i < 25; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 90, 165);
            if (y !== -1) {
                if (rng() < 0.5) this.enemies.push(new Enemy(x, y, 'jumping_slime'));
                else this.enemies.push(new Enemy(x, y - 15, 'bat'));

                if (i < 3) {
                    clearChamber(x, y, 3);
                    this.items.push(new Item(x - 6, y - 8, 'chest'));
                } else {
                    if (rng() < 0.5) this.items.push(new Item(x, y - 10, 'coin'));
                    else if (rng() < 0.15) this.items.push(new Item(x, y - 10, 'potion_shield'));
                }
            }
        }

        // Poison Caves: jumping slimes, bats, coins, health/shield potions, and 3 standard chests
        for (let i = 0; i < 25; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 170, 240);
            if (y !== -1) {
                if (rng() < 0.4) this.enemies.push(new Enemy(x, y, 'jumping_slime'));
                else this.enemies.push(new Enemy(x, y - 15, 'bat'));

                if (i < 3) {
                    clearChamber(x, y, 3);
                    this.items.push(new Item(x - 6, y - 8, 'chest'));
                } else {
                    if (rng() < 0.5) this.items.push(new Item(x, y - 10, 'coin'));
                    else if (rng() < 0.15) this.items.push(new Item(x, y - 10, rng() < 0.5 ? 'potion_health' : 'potion_shield'));
                }
            }
        }

        // Lava Core: bats, jumping slimes, coins
        for (let i = 0; i < 20; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 245, 310);
            if (y !== -1) {
                if (rng() < 0.3) this.enemies.push(new Enemy(x, y, 'jumping_slime'));
                else this.enemies.push(new Enemy(x, y - 15, 'bat'));

                if (rng() < 0.6) this.items.push(new Item(x, y - 10, 'coin'));
            }
        }

        // Spawn active cyber obelisk turrets in the ruins/caverns/caves/core
        // Crystal Caverns (y = 90 to 165)
        for (let i = 0; i < 4; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 90, 165);
            if (y !== -1) {
                this.enemies.push(new Enemy(x, y, 'turret'));
            }
        }
        // Poison Caves (y = 170 to 240)
        for (let i = 0; i < 4; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 170, 240);
            if (y !== -1) {
                this.enemies.push(new Enemy(x, y, 'turret'));
            }
        }
        // Lava Core (y = 245 to 310)
        for (let i = 0; i < 4; i++) {
            const x = Math.floor(rng() * WORLD_W);
            const y = findFloorY(x, 245, 310);
            if (y !== -1) {
                this.enemies.push(new Enemy(x, y, 'turret'));
            }
        }
    }

    updateInventoryUI() {
        const p = this.players[0];
        for (let slot = 0; slot < 2; slot++) {
            const slotEl = document.getElementById(`slot-${slot}`);
            if (slotEl) {
                const iconEl = slotEl.querySelector('.icon');
                const item = p.inventory[slot];
                if (item === 'potion_health') {
                    iconEl.textContent = '🧪 Pocion Vida';
                    slotEl.classList.add('has-item');
                } else if (item === 'potion_shield') {
                    iconEl.textContent = '🛡️ Pocion Escudo';
                    slotEl.classList.add('has-item');
                } else {
                    iconEl.textContent = 'Vacio';
                    slotEl.classList.remove('has-item');
                }
            }
        }
    }

    updateRelicsHUD() {
        const artifacts = ['eye_of_horus', 'scarab_of_power', 'ankh_of_life'];
        artifacts.forEach(art => {
            const el = document.getElementById(art);
            if (el) {
                if (this.storyArtifacts[art]) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            }
        });
    }

    setupInventoryClicks() {
        for (let slot = 0; slot < 2; slot++) {
            const slotEl = document.getElementById(`slot-${slot}`);
            if (slotEl) {
                slotEl.addEventListener('pointerdown', e => {
                    e.stopPropagation();
                    this.players[0].useItem(slot);
                });
            }
        }
    }

    setupSettingsPanel() {
        const btnSettings = document.getElementById('btn-settings');
        const settingsPanel = document.getElementById('settings-panel');
        const btnCloseSettings = document.getElementById('btn-close-settings');

        if (btnSettings && settingsPanel) {
            btnSettings.addEventListener('pointerdown', e => {
                e.stopPropagation();
                settingsPanel.classList.toggle('show');
            });
        }
        if (btnCloseSettings && settingsPanel) {
            btnCloseSettings.addEventListener('pointerdown', e => {
                e.stopPropagation();
                settingsPanel.classList.remove('show');
            });
        }

        // Game Mode option buttons
        const optSurvival = document.getElementById('opt-survival');
        const optSandbox = document.getElementById('opt-sandbox');
        const diffGroup = document.getElementById('diff-group');

        if (optSurvival && optSandbox) {
            optSurvival.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.gameMode = 'survival';
                optSurvival.classList.add('active');
                optSandbox.classList.remove('active');
                if (diffGroup) diffGroup.style.display = 'block';
                document.getElementById('v-mode').textContent = 'Supervivencia';
                const livesEl = document.getElementById('lives-display');
                if (livesEl) livesEl.style.display = 'block';
                this.resetSurvival();
            });
            optSandbox.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.gameMode = 'sandbox';
                optSandbox.classList.add('active');
                optSurvival.classList.remove('active');
                if (diffGroup) diffGroup.style.display = 'none';
                document.getElementById('v-mode').textContent = 'Sandbox';
                const livesEl = document.getElementById('lives-display');
                if (livesEl) livesEl.style.display = 'none';
                // Reset states
                this.isGameOver = false;
                this.isVictory = false;
                const goOverlay = document.getElementById('gameover-overlay');
                if (goOverlay) goOverlay.classList.remove('show');
                const vicOverlay = document.getElementById('victory-overlay');
                if (vicOverlay) vicOverlay.classList.remove('show');
            });
        }

        // Difficulty option buttons
        const optEasy = document.getElementById('opt-easy');
        const optNormal = document.getElementById('opt-normal');
        const optHard = document.getElementById('opt-hard');

        if (optEasy && optNormal && optHard) {
            const setDiff = (diff, activeBtn) => {
                this.difficulty = diff;
                [optEasy, optNormal, optHard].forEach(b => b.classList.remove('active'));
                activeBtn.classList.add('active');
            };
            optEasy.addEventListener('pointerdown', e => { e.stopPropagation(); setDiff('easy', optEasy); });
            optNormal.addEventListener('pointerdown', e => { e.stopPropagation(); setDiff('normal', optNormal); });
            optHard.addEventListener('pointerdown', e => { e.stopPropagation(); setDiff('hard', optHard); });
        }

        // Debug toggle button
        const optDebug = document.getElementById('opt-debug');
        if (optDebug) {
            optDebug.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.debugMode = !this.debugMode;
                optDebug.classList.toggle('active', this.debugMode);
                const dbOverlay = document.getElementById('debug-overlay');
                if (dbOverlay) {
                    dbOverlay.style.display = this.debugMode ? 'block' : 'none';
                }
            });
        }

        // Volume slider
        const volSlider = document.getElementById('volume-slider');
        if (volSlider) {
            volSlider.addEventListener('input', e => {
                this.audio.setVolume(parseFloat(e.target.value));
            });
            volSlider.addEventListener('pointerdown', e => e.stopPropagation());
        }

        // Restart buttons in overlays
        const btnRestartGo = document.getElementById('btn-restart-go');
        const btnRestartVic = document.getElementById('btn-restart-vic');
        if (btnRestartGo) {
            btnRestartGo.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.resetSurvival();
            });
        }
        if (btnRestartVic) {
            btnRestartVic.addEventListener('pointerdown', e => {
                e.stopPropagation();
                this.resetSurvival();
            });
        }
    }

    triggerGameOver() {
        this.isGameOver = true;
        this.audio.playBreak();
        const overlay = document.getElementById('gameover-overlay');
        if (overlay) {
            overlay.classList.add('show');
            document.getElementById('go-score').textContent = this.score;
        }
    }

    triggerVictory() {
        this.isVictory = true;
        this.audio.playMissionComplete();
        const overlay = document.getElementById('victory-overlay');
        if (overlay) {
            overlay.classList.add('show');
            document.getElementById('vic-score').textContent = this.score;
        }
    }

    resetSurvival() {
        this.isGameOver = false;
        this.isVictory = false;
        this.lives = 3;
        this.score = 0;
        this.storyArtifacts = { eye_of_horus: false, scarab_of_power: false, ankh_of_life: false };
        this.updateRelicsHUD();
        document.getElementById('v-score').textContent = '0';
        const livesEl = document.getElementById('v-lives');
        if (livesEl) livesEl.textContent = '3';
        const goOverlay = document.getElementById('gameover-overlay');
        if (goOverlay) goOverlay.classList.remove('show');
        const vicOverlay = document.getElementById('victory-overlay');
        if (vicOverlay) vicOverlay.classList.remove('show');
        
        generateWorld();
        this.players[0].spawn();
        this.players[0].hp = MAX_HP;
        this.players[0].inventory = [null, null];
        this.updateInventoryUI();
        this.spawnEntities();
        this.selectRandomMission();
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
            const code = document.getElementById('mp-code').value.trim();
            if (this.mp.isHost && code) {
                const url = window.location.origin + window.location.pathname + '#join=' + code;
                navigator.clipboard?.writeText(url);
                document.getElementById('mp-status').textContent = '¡Enlace de invitación copiado!';
            } else {
                navigator.clipboard?.writeText(code);
                document.getElementById('mp-status').textContent = 'Copiado!';
            }
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

    spawnDashParticles(px, py, facing) {
        for (let i = 0; i < 4; i++) {
            const dx = -facing * (4 + i * 2) + (rng() - 0.5) * 4;
            const dy = (rng() - 0.5) * 8;
            const tx = ((px + dx) % WORLD_W + WORLD_W) % WORLD_W;
            const ty = py + dy;
            const ti = idx(tx|0, ty|0);
            if (ti >= 0 && grid[ti] === MAT.EMPTY) {
                setCell(ti, rng() < 0.6 ? MAT.EMBER : MAT.SMOKE);
            }
        }
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
                this.currentTool = (this.currentTool + 1) % 4;
                document.querySelectorAll('#tools .btn').forEach((b,i)=>{b.classList.toggle('active',i===this.currentTool);});
            }
            if (e.code === 'KeyQ') {
                this.players[0].useItem(0);
            }
            if (e.code === 'KeyR') {
                this.players[0].useItem(1);
            }
            if (e.code === 'Space') {
                e.preventDefault();
                this.players[0].dash();
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

        if (this.currentTool === TOOL_STAFF) {
            if (p.shootCooldown <= 0) {
                p.shootCooldown = 15;
                let projType = 'fire';
                if (this.currentMat === MAT.ACID) projType = 'acid';
                else if (this.currentMat === MAT.ICE) projType = 'ice';
                else if (this.currentMat === MAT.LAVA) projType = 'plasma';
                else if (this.currentMat === MAT.FIRE) projType = 'fire';
                else {
                    if (p.selectedMat === MAT.ACID) projType = 'acid';
                    else if (p.selectedMat === MAT.ICE) projType = 'ice';
                    else if (p.selectedMat === MAT.LAVA) projType = 'plasma';
                }
                this.projectiles.push(new Projectile(pcx, pcy - 4, wx, wy, projType));
                this.audio.playShoot();
            }
            return;
        }

        const dist = Math.sqrt((wx-pcx)**2 + (wy-pcy)**2);
        if (dist > INTERACTION_RANGE) return;

        if (this.currentTool === TOOL_PLACE) {
            if (p.paintCooldown > 0) return;
            p.paintCooldown = 2;
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
            if (p.mineCooldown > 0) return;
            p.mineCooldown = this.storyArtifacts.scarab_of_power ? 4 : 8;
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
        if (this.isGameOver || this.isVictory) {
            // Keep decay animations and text rendering running
            for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
                const ft = this.floatingTexts[i];
                ft.update();
                if (ft.life <= 0) this.floatingTexts.splice(i, 1);
            }
            return;
        }

        // Continuous action for active pointers on the right-side of the screen
        for (const pid in this.pointers) {
            const ptr = this.pointers[pid];
            if (ptr.x >= window.innerWidth / 2.5) {
                this.doAction(ptr.x, ptr.y);
            }
        }

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

        // Update and filter enemies
        this.enemies.forEach(e => e.update());
        this.enemies = this.enemies.filter(e => !e.dead);

        const boss = this.enemies.find(e => e.type === 'pharaoh_guardian');
        const bossHpContainer = document.getElementById('boss-hp-container');
        if (boss) {
            if (bossHpContainer) {
                bossHpContainer.style.display = 'block';
                const bossHpFill = document.getElementById('boss-hp-fill');
                if (bossHpFill) {
                    const ratio = Math.max(0, boss.hp / boss.maxHp);
                    bossHpFill.style.width = `${ratio * 100}%`;
                }
            }
        } else {
            if (bossHpContainer) {
                bossHpContainer.style.display = 'none';
            }
        }

        // Update and filter items
        this.items.forEach(i => i.update());
        this.items = this.items.filter(i => !i.collected);

        // Update and filter projectiles
        this.projectiles.forEach(pr => pr.update());
        this.projectiles = this.projectiles.filter(pr => !pr.dead);

        // CA Simulation
        simulate();

        // Camera
        this.cam.follow(this.players[0].x, this.players[0].y, dt);

        // Update debug overlay if active
        if (this.debugMode) {
            const p = this.players[0];
            const pxEl = document.getElementById('db-px');
            const pyEl = document.getElementById('db-py');
            const pvelEl = document.getElementById('db-pvel');
            const camxEl = document.getElementById('db-camx');
            const camyEl = document.getElementById('db-camy');
            const relicsEl = document.getElementById('db-relics');
            const ffEl = document.getElementById('db-forcefield');
            const enemiesEl = document.getElementById('db-enemies');
            
            if (pxEl) pxEl.textContent = p.x.toFixed(2);
            if (pyEl) pyEl.textContent = p.y.toFixed(2);
            if (pvelEl) pvelEl.textContent = `${p.vx.toFixed(2)}, ${p.vy.toFixed(2)}`;
            if (camxEl) camxEl.textContent = this.cam.x.toFixed(2);
            if (camyEl) camyEl.textContent = this.cam.y.toFixed(2);
            
            let relicCount = 0;
            if (this.storyArtifacts.eye_of_horus) relicCount++;
            if (this.storyArtifacts.scarab_of_power) relicCount++;
            if (this.storyArtifacts.ankh_of_life) relicCount++;
            if (relicsEl) relicsEl.textContent = `${relicCount}/3`;
            
            const inForcefieldRange = p.y >= 250 && p.x >= 445 && p.x <= 575;
            if (ffEl) {
                ffEl.textContent = inForcefieldRange ? "BLOCKED 🛡️" : "Free";
                ffEl.style.color = inForcefieldRange ? "#ff4757" : "#00ffcc";
            }
            if (enemiesEl) enemiesEl.textContent = this.enemies.length;
        }

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

        // Draw Eye of Horus Chest Locator Line
        if (this.storyArtifacts.eye_of_horus) {
            const p = this.players[0];
            let closestChest = null;
            let minDist = Infinity;
            this.items.forEach(item => {
                if ((item.type === 'chest' || item.type === 'chest_relic') && !item.collected) {
                    let dx = item.x + item.w/2 - (p.x + PLAYER_W/2);
                    dx = ((dx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
                    const dy = item.y + item.h/2 - (p.y + PLAYER_H/2);
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < minDist) {
                        minDist = dist;
                        closestChest = item;
                    }
                }
            });
            if (closestChest) {
                ctx.save();
                ctx.strokeStyle = 'rgba(0, 210, 211, 0.65)';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([4, 4]);
                ctx.shadowColor = '#00d2d3';
                ctx.shadowBlur = 4;
                ctx.beginPath();
                const psx = getScreenX(p.x + PLAYER_W/2, this.cam) * this.cam.zoom;
                const psy = (p.y + PLAYER_H/2 - this.cam.y) * this.cam.zoom;
                let cdx = closestChest.x + closestChest.w/2 - (p.x + PLAYER_W/2);
                cdx = ((cdx + WORLD_W/2) % WORLD_W + WORLD_W) % WORLD_W - WORLD_W/2;
                const csx = psx + cdx * this.cam.zoom;
                const csy = (closestChest.y + closestChest.h/2 - this.cam.y) * this.cam.zoom;
                ctx.moveTo(psx, psy);
                ctx.lineTo(csx, csy);
                ctx.stroke();
                ctx.restore();
            }
        }

        // Draw items, enemies, and projectiles
        this.items.forEach(i => i.draw(ctx, this.cam));
        this.enemies.forEach(e => e.draw(ctx, this.cam));
        this.projectiles.forEach(pr => pr.draw(ctx, this.cam));

        // Draw cyber-forcefield boundaries (if active in story mode)
        const hasAllRelics = this.storyArtifacts.eye_of_horus && this.storyArtifacts.scarab_of_power && this.storyArtifacts.ankh_of_life;
        if (this.gameMode === 'survival' && !hasAllRelics) {
            ctx.save();
            ctx.strokeStyle = 'rgba(0, 210, 211, 0.45)';
            ctx.lineWidth = 2;
            
            const syStart = (250 - this.cam.y) * this.cam.zoom;
            const syEnd = (296 - this.cam.y) * this.cam.zoom;
            const sxL = getScreenX(445, this.cam) * this.cam.zoom;
            const sxR = getScreenX(575, this.cam) * this.cam.zoom;
            
            const drawBarrier = (sx) => {
                ctx.beginPath();
                ctx.moveTo(sx, syStart);
                ctx.lineTo(sx, syEnd);
                ctx.stroke();
                
                // Horizontal energy pulses
                const pulseGap = 8 * this.cam.zoom;
                for (let y = syStart; y <= syEnd; y += pulseGap) {
                    ctx.beginPath();
                    ctx.moveTo(sx - 8 * this.cam.zoom, y);
                    ctx.lineTo(sx + 8 * this.cam.zoom, y);
                    ctx.stroke();
                }
            };
            
            if (sxL >= 0 && sxL <= cw) drawBarrier(sxL);
            if (sxR >= 0 && sxR <= cw) drawBarrier(sxR);
            ctx.restore();
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
