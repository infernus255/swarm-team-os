/**
 * Professional-Grade Game Performance Benchmark using Playwright & Chrome DevTools Protocol (CDP)
 * 
 * This script automates a headless Chromium instance, simulates user drag interactions 
 * to spawn cellular automata particles, and reads low-level engine metrics (CPU task duration, 
 * layout, scripting, and JS heap memory) with microsecond precision.
 * 
 * To run:
 *   1. Initialize a node environment: npm init -y
 *   2. Install playwright: npm install playwright
 *   3. Execute: node scratch/playwright_benchmark.js
 */

const { chromium } = require('playwright');

async function runBenchmark() {
    const url = 'https://project-forge-2d.vercel.app/';
    console.log(`Launching Chromium to benchmark: ${url}...`);

    // 1. Launch Browser
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1024, height: 768 },
        deviceScaleFactor: 1
    });
    const page = await context.newPage();

    // 2. Track Console Messages and Uncaught Errors
    const consoleLogs = [];
    page.on('console', msg => {
        consoleLogs.push(`[${msg.type().toUpperCase()}] ${msg.text()}`);
    });
    page.on('pageerror', err => {
        consoleLogs.push(`[UNCAUGHT ERROR] ${err.message}`);
    });

    // 3. Connect to Chrome DevTools Protocol (CDP)
    const client = await page.context().newCDPSession(page);
    await client.send('Performance.enable');

    // 4. Navigate to the game
    console.log('Navigating to game and waiting for load...');
    await page.goto(url, { waitUntil: 'load' });
    console.log('Page loaded. Letting simulation settle for 2 seconds...');
    await page.waitForTimeout(2000);

    // Helper to extract CDP metrics
    async function getCDPMetrics() {
        const response = await client.send('Performance.getMetrics');
        const metrics = {};
        for (const metric of response.metrics) {
            metrics[metric.name] = metric.value;
        }
        return metrics;
    };

    // Capture baseline metrics
    const baseline = await getCDPMetrics();

    // 5. Simulate Heavy Game Interaction (drag to paint particles)
    console.log('Simulating mouse drags to spawn particles and trigger physics loops...');
    const startX = 500;
    const startY = 400;
    
    // Mouse down
    await page.mouse.move(startX, startY);
    await page.mouse.down();
    
    // Drag in a circle to paint sand/liquids
    const steps = 30;
    const radius = 80;
    for (let i = 0; i <= steps; i++) {
        const angle = (i / steps) * Math.PI * 4; // 2 full circles
        const x = startX + Math.cos(angle) * radius;
        const y = startY + Math.sin(angle) * radius;
        await page.mouse.move(x, y);
        await page.waitForTimeout(50); // 50ms intervals
    }
    await page.mouse.up();
    console.log('Interaction complete. Letting physics run for 3 seconds...');
    await page.waitForTimeout(3000);

    // Capture post-interaction metrics
    const target = await getCDPMetrics();

    // 6. Read Game-State directly from JS runtime context
    const gameRuntimeStats = await page.evaluate(() => {
        if (typeof game !== 'undefined' && game) {
            return {
                fps: game.fps,
                simTimeMs: game.simTime,
                drawTimeMs: game.drawTime,
                playersCount: game.players.length,
                floatingTextsCount: game.floatingTexts.length,
                score: game.score,
                activeMissionDesc: game.activeMission ? game.activeMission.desc : 'None'
            };
        }
        return null;
    });

    // Close browser
    await browser.close();

    // 7. Calculate Deltas
    const taskDuration = target.TaskDuration - baseline.TaskDuration;
    const scriptDuration = target.ScriptDuration - baseline.ScriptDuration;
    const layoutDuration = target.LayoutDuration - baseline.LayoutDuration;
    const layoutCount = target.LayoutCount - baseline.LayoutCount;
    const styleRecalcDuration = target.RecalculateStyleDuration - baseline.RecalculateStyleDuration;
    const styleRecalcCount = target.RecalculateStyleCount - baseline.RecalculateStyleCount;
    
    // Heap Memory
    const heapUsedMB = (target.JSHeapUsedSize / 1024 / 1024).toFixed(2);
    const heapTotalMB = (target.JSHeapTotalSize / 1024 / 1024).toFixed(2);

    // 8. Generate Benchmark Report
    console.log('\n==================================================');
    console.log('    PROJECT FORGE 2D - PERFORMANCE BENCHMARK      ');
    console.log('==================================================');
    console.log(`JS Heap memory used      : ${heapUsedMB} MB / ${heapTotalMB} MB`);
    console.log(`Total CPU Task Duration  : ${(taskDuration * 1000).toFixed(1)} ms`);
    console.log(`  - Scripting execution  : ${(scriptDuration * 1000).toFixed(1)} ms`);
    console.log(`  - Layout calculation   : ${(layoutDuration * 1000).toFixed(1)} ms (Count: ${layoutCount})`);
    console.log(`  - Style recalculations : ${(styleRecalcDuration * 1000).toFixed(1)} ms (Count: ${styleRecalcCount})`);
    
    if (gameRuntimeStats) {
        console.log('\n--- INTERNAL GAME LOGIC METRICS ---');
        console.log(`Renderer FPS             : ${gameRuntimeStats.fps.toFixed(1)}`);
        console.log(`Avg Physics Sim Time     : ${gameRuntimeStats.simTimeMs.toFixed(2)} ms`);
        console.log(`Avg Frame Draw Time      : ${gameRuntimeStats.drawTimeMs.toFixed(2)} ms`);
        console.log(`Active Entities (Players): ${gameRuntimeStats.playersCount}`);
        console.log(`Floating Text Elements   : ${gameRuntimeStats.floatingTextsCount}`);
        console.log(`Current Player Score     : ${gameRuntimeStats.score}`);
        console.log(`Active Mission           : ${gameRuntimeStats.activeMissionDesc}`);
    } else {
        console.log('\n[WARNING] Could not read game runtime stats.');
    }

    if (consoleLogs.length > 0) {
        console.log('\n--- CONSOLE LOGS & ERRORS DETECTED ---');
        consoleLogs.forEach(log => console.log(log));
    } else {
        console.log('\nNo console errors or logs detected.');
    }
    console.log('==================================================\n');
}

runBenchmark().catch(err => {
    console.error('Benchmark execution failed:', err);
});
