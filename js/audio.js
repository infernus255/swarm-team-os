// =====================================================
// 8. SOUND SYNTHESIZER
// =====================================================
class Audio {
    constructor() { this.ctx = null; this.muted = false; this.musicMuted = false; this.musicTimer = null; this.masterGain = null; }
    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext||window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.masterGain.connect(this.ctx.destination);
            this.masterGain.gain.value = 1.0;
        }
    }
    setVolume(vol) {
        this.init();
        if (this.masterGain) {
            this.masterGain.gain.setValueAtTime(vol, this.ctx.currentTime);
        }
    }
    _play(type, f1, f2, dur, vol) {
        if (this.muted) return;
        this.init();
        if (this.ctx.state==='suspended') this.ctx.resume();
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        if (this.masterGain) gain.connect(this.masterGain);
        else gain.connect(this.ctx.destination);
        osc.type = type;
        osc.frequency.setValueAtTime(f1, now);
        osc.frequency.exponentialRampToValueAtTime(Math.max(f2,1), now+dur);
        gain.gain.setValueAtTime(vol, now);
        gain.gain.linearRampToValueAtTime(0.01, now+dur);
        osc.start(now); osc.stop(now+dur);
    }
    playPlace() { this._play('sine', 280, 180, 0.08, 0.12); }
    playMine() { this._play('sawtooth', 90+rng()*30, 30, 0.06, 0.1); }
    playBreak() { this._play('sawtooth', 110, 20, 0.12, 0.18); }
    playJump() { this._play('sine', 160, 360, 0.1, 0.1); }
    playDash() {
        this._play('sine', 150, 600, 0.12, 0.15);
        this._play('triangle', 300, 900, 0.08, 0.08);
    }
    playExplode() {
        this._play('sawtooth', 80, 15, 0.3, 0.25);
        this._play('square', 60, 10, 0.25, 0.15);
    }
    playShoot() {
        this._play('sine', 480, 240, 0.15, 0.1);
    }
    playChestOpen() {
        this._play('square', 220, 660, 0.25, 0.12);
        this._play('triangle', 330, 880, 0.2, 0.1);
    }
    playBossPhase() {
        this._play('sawtooth', 180, 90, 0.4, 0.2);
        this._play('square', 120, 60, 0.5, 0.15);
    }
    playMissionComplete() {
        if (this.muted) return;
        this.init();
        if (this.ctx.state==='suspended') this.ctx.resume();
        const now = this.ctx.currentTime;
        const notes = [261.63, 329.63, 392.00, 523.25]; // C4, E4, G4, C5
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.connect(gain);
            if (this.masterGain) gain.connect(this.masterGain);
            else gain.connect(this.ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + idx * 0.08);
            gain.gain.setValueAtTime(0.06, now + idx * 0.08);
            gain.gain.linearRampToValueAtTime(0.005, now + idx * 0.08 + 0.2);
            osc.start(now + idx * 0.08);
            osc.stop(now + idx * 0.08 + 0.2);
        });
    }
    startMusic() {
        if (this.musicTimer) return;
        this.init();
        const progressions = [
            [
                [110.00, 130.81, 164.81, 196.00, 246.94], // Am9
                [87.31, 130.81, 174.61, 220.00, 261.63], // Fmaj7
                [130.81, 164.81, 196.00, 261.63, 329.63], // Cmaj7
                [98.00, 146.83, 196.00, 246.94, 293.66]  // G6
            ],
            [
                [146.83, 174.61, 220.00, 261.63, 329.63], // Dm9
                [98.00, 146.83, 196.00, 246.94, 392.00],  // G7
                [130.81, 164.81, 196.00, 261.63, 329.63], // Cmaj7
                [130.81, 164.81, 196.00, 261.63, 329.63]  // Cmaj7
            ]
        ];
        let progIdx = 0, chordIdx = 0;
        const playNextChord = () => {
            if (this.muted || this.musicMuted) return;
            this.init();
            if (this.ctx.state==='suspended') this.ctx.resume();
            const now = this.ctx.currentTime;
            const prog = progressions[progIdx];
            const chord = prog[chordIdx];
            chord.forEach((freq) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.connect(gain);
                if (this.masterGain) gain.connect(this.masterGain);
                else gain.connect(this.ctx.destination);
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, now);
                const vol = 0.025 / chord.length;
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(vol, now + 1.2);
                gain.gain.setValueAtTime(vol, now + 2.5);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 4.5);
                osc.start(now); osc.stop(now + 4.5);
            });
            if (rng() < 0.75) {
                const melody = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50];
                const note = melody[Math.floor(rng() * melody.length)];
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.connect(gain);
                if (this.masterGain) gain.connect(this.masterGain);
                else gain.connect(this.ctx.destination);
                osc.type = 'sine';
                const delay = 0.5 + rng() * 1.5;
                osc.frequency.setValueAtTime(note, now + delay);
                gain.gain.setValueAtTime(0, now + delay);
                gain.gain.linearRampToValueAtTime(0.012, now + delay + 0.5);
                gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 2.5);
                osc.start(now + delay); osc.stop(now + delay + 2.5);
            }
            chordIdx = (chordIdx + 1) % prog.length;
            if (chordIdx === 0) progIdx = (progIdx + 1) % progressions.length;
        };
        playNextChord();
        this.musicTimer = setInterval(playNextChord, 4000);
    }
    stopMusic() {
        if (this.musicTimer) { clearInterval(this.musicTimer); this.musicTimer = null; }
    }
}
