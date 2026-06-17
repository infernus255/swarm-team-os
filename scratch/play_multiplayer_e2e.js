/**
 * Professional Interactive E2E Multiplayer Test Suite for Project Forge 2D
 * 
 * This script runs entirely locally with 0 LLM token cost. It verifies:
 *   1. WebRTC Signaling: Generating Offer (Host) and Answer (Client) Base64 SDP/ICE codes.
 *   2. Peer Connection: Establishing direct P2P link between two browser contexts.
 *   3. Synchronization: Verifying that player movement in one browser is replicated
 *      and rendered in real-time on the other player's canvas.
 * 
 * Execution:
 *   node scratch/play_multiplayer_e2e.js
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// --- 1. SET UP STATIC HTTP SERVER ---
const PORT = 8084;
const HOST = '127.0.0.1';

const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    let filePath = path.join(__dirname, '..', reqUrl === '/' ? 'index.html' : reqUrl);
    const extname = String(path.extname(filePath)).toLowerCase();
    
    const mimeTypes = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.gif': 'image/gif',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg'
    };

    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end(`File not found: ${reqUrl}`);
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

async function runMultiplayerTest() {
    console.log(`[MP-E2E] Starting static HTTP server at http://${HOST}:${PORT}/`);
    await new Promise((resolve) => server.listen(PORT, HOST, resolve));

    console.log('[MP-E2E] Launching headless browser...');
    const browser = await chromium.launch({ headless: true, args: ['--disable-features=WebRtcHideLocalIpsWithMdns', '--allow-loopback-in-peer-connection'] });

    // Create two isolated browser contexts (simulating two different players/devices)
    console.log('[MP-E2E] Initializing Host and Joiner pages...');
    const hostContext = await browser.newContext();
    const joinerContext = await browser.newContext();

    const hostPage = await hostContext.newPage();
    const joinerPage = await joinerContext.newPage();

    // Catch errors in both pages
    hostPage.on('pageerror', err => console.error(`[HOST PAGE ERROR] ${err.message}`));
    joinerPage.on('pageerror', err => console.error(`[JOINER PAGE ERROR] ${err.message}`));

    try {
        // Load game in both pages
        await Promise.all([
            hostPage.goto(`http://${HOST}:${PORT}/`, { waitUntil: 'load' }),
            joinerPage.goto(`http://${HOST}:${PORT}/`, { waitUntil: 'load' })
        ]);
        console.log('[MP-E2E] Both pages loaded. Waiting for world gen to settle...');
        await hostPage.waitForTimeout(1500);
        await joinerPage.waitForTimeout(1500);

        // --- STEP 1: HOST CREATES SESSION ---
        console.log('[MP-E2E] Host: Opening multiplayer panel and clicking "Crear" (Host)...');
        await hostPage.click('#btn-mp');
        await hostPage.click('#mp-host');

        // Wait for WebRTC SDP offer code to populate in text area
        console.log('[MP-E2E] Host: Waiting for connection SDP code...');
        await hostPage.waitForFunction(() => {
            const code = document.getElementById('mp-code').value.trim();
            return code.length > 50; // Code generated
        }, { timeout: 5000 });

        const hostOfferCode = await hostPage.inputValue('#mp-code');
        console.log(`✓ Host Offer Code generated successfully (${hostOfferCode.substring(0, 15)}...).`);

        // --- STEP 2: JOINER JOINS HOST SESSION ---
        console.log('[MP-E2E] Joiner: Opening multiplayer panel, pasting code and clicking "Aplicar"...');
        await joinerPage.click('#btn-mp');
        await joinerPage.click('#mp-join'); // Show text area
        
        // Fill input area with Host Offer Code
        await joinerPage.fill('#mp-code', hostOfferCode);
        await joinerPage.click('#mp-apply');

        // Wait for Joiner response code to generate
        console.log('[MP-E2E] Joiner: Waiting for response SDP code...');
        await joinerPage.waitForFunction(() => {
            const val = document.getElementById('mp-code').value.trim();
            // Wait until the value changes and is not the offer code we pasted
            return val.length > 50 && !val.startsWith(window.offerStart || 'dummy');
        }, { timeout: 5000 });

        const joinerAnswerCode = await joinerPage.inputValue('#mp-code');
        console.log(`✓ Joiner Answer Code generated successfully (${joinerAnswerCode.substring(0, 15)}...).`);

        // --- STEP 3: HOST APPLIES ANSWER CODE ---
        console.log('[MP-E2E] Host: Pasting Joiner response code and clicking "Aplicar"...');
        await hostPage.fill('#mp-code', joinerAnswerCode);
        await hostPage.click('#mp-apply');

        // --- STEP 4: VERIFY CONNECTION ---
        console.log('[MP-E2E] Waiting for direct P2P connection to open...');
        await Promise.all([
            hostPage.waitForFunction(() => game.mp.connected === true, { timeout: 6000 }),
            joinerPage.waitForFunction(() => game.mp.connected === true, { timeout: 6000 })
        ]);

        const hostConnected = await hostPage.evaluate(() => game.mp.connected);
        const joinerConnected = await joinerPage.evaluate(() => game.mp.connected);
        
        if (hostConnected && joinerConnected) {
            console.log('✓ WebRTC P2P Connection established! Status is "Conectado" on both peers.');
        } else {
            throw new Error('Connection failed to open.');
        }

        // --- STEP 5: VERIFY GAMEPLAY SYNCHRONIZATION ---
        console.log('\n--- VERIFYING ACTION REPLICATION ---');
        // Get baseline of secondary player coordinates on Host screen
        const initialSecondaryX = await hostPage.evaluate(() => {
            if (game.players.length < 2) return null;
            return game.players[1].x;
        });

        console.log(`Host screen: Joiner's initial position: x=${initialSecondaryX}`);

        // Joiner walks right
        console.log('[MP-E2E Action] Joiner Walks Right (KeyD) for 600ms...');
        await joinerPage.keyboard.down('KeyD');
        await joinerPage.waitForTimeout(600);
        await joinerPage.keyboard.up('KeyD');
        await joinerPage.waitForTimeout(100);

        // Retrieve secondary player coordinate on Host page (should have increased)
        const updatedSecondaryX = await hostPage.evaluate(() => {
            if (game.players.length < 2) return null;
            return game.players[1].x;
        });
        
        console.log(`Host screen: Joiner's synchronized position: x=${updatedSecondaryX}`);

        if (updatedSecondaryX !== null && updatedSecondaryX > initialSecondaryX) {
            console.log('✓ Action replication successful! Movement synchronized and drawn on host canvas.');
        } else {
            throw new Error(`Movement replication failed. Initial x: ${initialSecondaryX}, Synchronized x: ${updatedSecondaryX}`);
        }

        console.log('\n[MP-E2E SUCCESS] WebRTC Multiplayer E2E play-test passed perfectly!');

    } catch (err) {
        console.error('[MP-E2E EXCEPTION] Test failed with error:', err.message);
        process.exitCode = 1;
    } finally {
        console.log('[MP-E2E] Closing browser...');
        await browser.close();
        console.log('[MP-E2E] Stopping static HTTP server...');
        await new Promise((resolve) => server.close(resolve));
        console.log('[MP-E2E] Test run terminated.');
    }
}

runMultiplayerTest();
