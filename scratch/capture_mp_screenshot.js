/**
 * Screenshot Capture Utility for E2E Visual Auditing
 * 
 * This script runs locally, starting a static server and capturing 
 * high-resolution screenshots of the multiplayer panel expanded 
 * under desktop and mobile viewports.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PORT = 8086;
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

async function captureScreenshots() {
    console.log(`[Screenshot] Starting server at http://${HOST}:${PORT}/`);
    await new Promise((resolve) => server.listen(PORT, HOST, resolve));

    const artifactDir = 'C:\\Users\\admin\\.gemini\\antigravity\/\/brain\\34db15de-80f6-4bfa-9ae5-71ea463aaa34';
    if (!fs.existsSync(artifactDir)) {
        fs.mkdirSync(artifactDir, { recursive: true });
    }

    console.log('[Screenshot] Launching browser...');
    const browser = await chromium.launch({ headless: true });

    // 1. Desktop Screenshot
    console.log('[Screenshot] Capturing Desktop Layout...');
    const desktopContext = await browser.newContext({ viewport: { width: 1024, height: 768 } });
    const desktopPage = await desktopContext.newPage();
    await desktopPage.goto(`http://${HOST}:${PORT}/`);
    await desktopPage.waitForTimeout(1000);
    
    // Open panel
    await desktopPage.click('#btn-mp');
    await desktopPage.click('#mp-join'); // expand
    await desktopPage.waitForTimeout(300);
    
    await desktopPage.screenshot({ path: path.join(artifactDir, 'mp_desktop.png') });
    console.log('✓ Desktop screenshot captured.');
    await desktopContext.close();

    // 2. Mobile Screenshot
    console.log('[Screenshot] Capturing Mobile Layout...');
    const mobileContext = await browser.newContext({ viewport: { width: 375, height: 667 } });
    const mobilePage = await mobileContext.newPage();
    await mobilePage.goto(`http://${HOST}:${PORT}/`);
    await mobilePage.waitForTimeout(1000);
    
    // Open panel
    await mobilePage.click('#btn-mp');
    await mobilePage.click('#mp-join'); // expand
    await mobilePage.waitForTimeout(300);
    
    await mobilePage.screenshot({ path: path.join(artifactDir, 'mp_mobile.png') });
    console.log('✓ Mobile screenshot captured.');
    await mobileContext.close();

    console.log('[Screenshot] Stopping server...');
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
    console.log('[Screenshot] Complete.');
}

captureScreenshots();
