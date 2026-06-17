// =====================================================
// 10. MULTIPLAYER MANAGER
// =====================================================
class Multiplayer {
    constructor() {
        this.mode = 'solo'; // solo, local, online
        this.pc = null;
        this.dc = null;
        this.isHost = false;
        this.connected = false;
        this.remoteInputs = { ax:0, jump:false, actions:[] };
    }
    startLocal() {
        this.mode = 'local';
        document.getElementById('mp-status').textContent = 'Pantalla dividida activa';
        document.getElementById('v-mode').textContent = 'Local 2P';
    }
    async host() {
        this.isHost = true; this.mode = 'online';
        const cfg = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
        this.pc = new RTCPeerConnection(cfg);
        this.dc = this.pc.createDataChannel('g', { ordered: false, maxRetransmits: 0 });
        this._setupDC(this.dc);
        this.pc.onicecandidate = () => {};
        const offer = await this.pc.createOffer();
        await this.pc.setLocalDescription(offer);
        // Wait for ICE gathering with 800ms timeout fallback for offline/restricted environments
        await new Promise(r => {
            let done = false;
            const finish = () => { if (!done) { done = true; r(); } };
            if (this.pc.iceGatheringState === 'complete') finish();
            else {
                this.pc.onicegatheringstatechange = () => { if (this.pc.iceGatheringState === 'complete') finish(); };
            }
            setTimeout(finish, 800);
        });
        const code = btoa(JSON.stringify(this.pc.localDescription));
        const ta = document.getElementById('mp-code');
        ta.style.display = 'block';
        ta.value = code;
        document.getElementById('mp-actions').style.display = 'flex';
        document.getElementById('mp-status').textContent = 'Esperando jugador... Copia y comparte el codigo';
    }
    async join(offerCode) {
        this.mode = 'online';
        const cfg = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
        this.pc = new RTCPeerConnection(cfg);
        this.pc.ondatachannel = e => { this.dc = e.channel; this._setupDC(this.dc); };
        const offer = JSON.parse(atob(offerCode));
        await this.pc.setRemoteDescription(offer);
        const answer = await this.pc.createAnswer();
        await this.pc.setLocalDescription(answer);
        // Wait for ICE gathering with 800ms timeout fallback for offline/restricted environments
        await new Promise(r => {
            let done = false;
            const finish = () => { if (!done) { done = true; r(); } };
            if (this.pc.iceGatheringState === 'complete') finish();
            else {
                this.pc.onicegatheringstatechange = () => { if (this.pc.iceGatheringState === 'complete') finish(); };
            }
            setTimeout(finish, 800);
        });
        const code = btoa(JSON.stringify(this.pc.localDescription));
        const ta = document.getElementById('mp-code');
        ta.value = code;
        document.getElementById('mp-status').textContent = 'Respuesta lista. Copia y enviale al host';
    }
    async applyAnswer(answerCode) {
        const answer = JSON.parse(atob(answerCode));
        await this.pc.setRemoteDescription(answer);
    }
    _setupDC(dc) {
        dc.onopen = () => {
            this.connected = true;
            document.getElementById('mp-status').textContent = 'Conectado!';
            document.getElementById('v-mode').textContent = 'Online P2P';
        };
        dc.onmessage = e => {
            try { this.remoteInputs = JSON.parse(e.data); } catch(ex){}
        };
        dc.onclose = () => {
            this.connected = false;
            document.getElementById('mp-status').textContent = 'Desconectado';
        };
    }
    send(data) {
        if (this.dc && this.dc.readyState === 'open') {
            try { this.dc.send(JSON.stringify(data)); } catch(ex){}
        }
    }
}
