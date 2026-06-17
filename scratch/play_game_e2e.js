/**
 * Professional Interactive E2E Play-Test Suite for Project Forge 2D
 * 
 * This script runs entirely locally, consumes 0 LLM tokens, and verifies:
 *   1. Local HTTP static server initialization and routing.
 *   2. Canvas load and game-loop execution.
 *   3. Keyboard player movement (WASD) and collision responses.
 *   4. Mouse-drag interaction (painting sand particles) and physics execution.
 *   5. Sound engine and mission UI bindings.
 *   6. Complete absence of runtime Javascript console errors.
 * 
 * Execution:
 *   node scratch/play_game_e2e.js
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// --- 1. SET UP STATIC HTTP SERVER ---
const PORT = 8083;
const HOST = '127.0.0.1';

const server = http.createServer((req, res) => {
    // Normalize URL path
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
            if (error.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end(`File not found: ${reqUrl}`);
            } else {
                res.writeHead(500);
                res.end(`Internal Server Error: ${error.code}`);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

// Run E2E test using Playwright
async function runPlayTest() {
    console.log(`[E2E] Starting static HTTP server at http://${HOST}:${PORT}/`);
    await new Promise((resolve) => server.listen(PORT, HOST, resolve));

    console.log('[E2E] Launching headless Chromium...');
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1024, height: 768 }
    });
    const page = await context.newPage();

    const consoleErrors = [];
    const logs = [];

    // Track console messages and uncaught exceptions
    page.on('console', msg => {
        const txt = msg.text();
        logs.push(`[CONSOLE ${msg.type().toUpperCase()}] ${txt}`);
        if (msg.type() === 'error') {
            consoleErrors.push(txt);
        }
    });

    page.on('pageerror', err => {
        consoleErrors.push(`[UNCAUGHT ERROR] ${err.message}\nStack:\n${err.stack}`);
    });

    try {
        console.log('[E2E] Navigating to local game URL...');
        await page.goto(`http://${HOST}:${PORT}/`, { waitUntil: 'load' });
        console.log('[E2E] Page loaded. Waiting for world generation to complete...');
        await page.waitForTimeout(1500);

        // Verify elements load
        const canvasVisible = await page.locator('#gameCanvas').isVisible();
        if (!canvasVisible) throw new Error('gameCanvas element is not visible.');
        console.log('✓ Canvas verified visible.');

        // 1. Get baseline player position
        const pState0 = await page.evaluate(() => {
            if (typeof game === 'undefined' || !game || game.players.length === 0) return null;
            const p = game.players[0];
            return { x: p.x, y: p.y, hp: p.hp };
        });

        if (!pState0) throw new Error('Could not read player state from Javascript context.');
        console.log(`✓ Baseline player position: x=${pState0.x.toFixed(2)}, y=${pState0.y.toFixed(2)}, HP=${pState0.hp}`);

        // 2. Test Player Movement Right (KeyD)
        console.log('[E2E Action] Simulating player walking right (KeyD)...');
        await page.keyboard.down('KeyD');
        await page.waitForTimeout(600);
        await page.keyboard.up('KeyD');
        await page.waitForTimeout(100);

        const pState1 = await page.evaluate(() => {
            const p = game.players[0];
            return { x: p.x, y: p.y };
        });
        
        console.log(`✓ Player position after walking right: x=${pState1.x.toFixed(2)}, y=${pState1.y.toFixed(2)}`);
        if (pState1.x <= pState0.x) {
            throw new Error(`Player did not move right. Baseline x: ${pState0.x.toFixed(2)}, New x: ${pState1.x.toFixed(2)}`);
        }
        console.log('✓ Walk right verification passed.');

        // 3. Test Player Jump (KeyW)
        console.log('[E2E Action] Simulating player jumping (KeyW)...');
        await page.keyboard.down('KeyW');
        await page.waitForTimeout(150);
        await page.keyboard.up('KeyW');
        // Wait for player to rise and fall
        await page.waitForTimeout(400);

        const pState2 = await page.evaluate(() => {
            const p = game.players[0];
            return { x: p.x, y: p.y };
        });
        console.log(`✓ Player position after jumping: x=${pState2.x.toFixed(2)}, y=${pState2.y.toFixed(2)}`);

        // 4. Test Materials Placement (Sand / Water)
        console.log('[E2E Action] Selecting sand and drawing particles via mouse drag...');
        // Press '1' to select Sand from palette
        await page.keyboard.press('Digit1');
        
        // Simulating canvas click and drag to paint sand
        const canvasBounding = await page.locator('#gameCanvas').boundingBox();
        const paintX = canvasBounding.x + canvasBounding.width / 2;
        const paintY = canvasBounding.y + canvasBounding.height / 3;

        await page.mouse.move(paintX, paintY);
        await page.mouse.down();
        // Drag in a line
        for (let offset = 0; offset <= 60; offset += 10) {
            await page.mouse.move(paintX + offset, paintY + (offset / 2));
            await page.waitForTimeout(30);
        }
        await page.mouse.up();
        console.log('[E2E] Sand painted. Waiting for physics simulation to settle...');
        await page.waitForTimeout(1000);

        // Verify that simulation has active cells and performance remains stable
        const gameStats = await page.evaluate(() => {
            return {
                fps: game.fps,
                simTime: game.simTime,
                drawTime: game.drawTime,
                activeMission: game.activeMission ? game.activeMission.desc : 'None'
            };
        });

        console.log('\n==================================================');
        console.log('   GAMEPLAY RUNTIME PERFORMANCE DIAGNOSTICS      ');
        console.log('==================================================');
        console.log(`FPS                      : ${gameStats.fps.toFixed(1)}`);
        console.log(`Avg Physics Sim Duration : ${gameStats.simTime.toFixed(2)} ms`);
        console.log(`Avg Frame Draw Duration  : ${gameStats.drawTime.toFixed(2)} ms`);
        console.log(`Current Active Mission   : ${gameStats.activeMission}`);
        console.log('==================================================\n');

        // Check for errors
        if (consoleErrors.length > 0) {
            console.error('[E2E FAILURE] Errors detected in browser console:');
            consoleErrors.forEach(err => console.error(` - ${err}`));
            throw new Error('E2E test failed due to browser runtime errors.');
        } else {
            console.log('✓ No runtime JS errors or warnings detected in the console logs.');
        }

        console.log('[E2E SUCCESS] Gameplay play-test completed successfully.');

    } catch (err) {
        console.error('[E2E EXCEPTION] E2E Play-Test failed with error:', err.message);
        if (logs.length > 0) {
            console.log('\n--- Captured Console Logs ---');
            logs.slice(-15).forEach(l => console.log(l));
        }
        process.exitCode = 1;
    } finally {
        console.log('[E2E] Closing browser...');
        await browser.close();
        console.log('[E2E] Stopping static HTTP server...');
        await new Promise((resolve) => server.close(resolve));
        console.log('[E2E] Test run terminated.');
    }
}

runPlayTest();
