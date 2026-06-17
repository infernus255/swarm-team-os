// =====================================================
// 12. MAIN LOOP
// =====================================================
window.addEventListener('load', () => {
    game = new Game();

    const fixedDt = 1/60;
    let acc = 0, lastT = performance.now();
    let fCount = 0, fpsT = lastT;

    function loop(now) {
        let dt = (now - lastT) / 1000;
        if (dt > 0.2) dt = 0.2;
        lastT = now;

        fCount++;
        if (now - fpsT >= 1000) { game.fps = fCount * 1000 / (now - fpsT); fCount = 0; fpsT = now; }

        const t0 = performance.now();
        acc += dt;
        while (acc >= fixedDt) { game.update(fixedDt); acc -= fixedDt; }
        game.simTime = performance.now() - t0;

        const t1 = performance.now();
        game.render();
        game.drawTime = performance.now() - t1;

        requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
});
