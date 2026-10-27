// Frame-by-frame render of index.html to MP4 (1080x1350, H.264).
// Usage: node render.js [fps] [out.mp4]   (run from this folder, server on :8766)
//        node render.js still 4.5 out.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto('http://127.0.0.1:8766/index.html?t=0');
  await page.evaluate(async () => {
    await window.ready;
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode()));
  });
  const shot = () => page.locator('.post').screenshot({ type: 'png' });

  if (process.argv[2] === 'still') {
    await page.evaluate((t) => setTime(t), parseFloat(process.argv[3]));
    require('fs').writeFileSync(process.argv[4], await shot());
    return browser.close();
  }

  const fps = parseInt(process.argv[2] || '30', 10);
  const out = process.argv[3] || 'basarab-type.mp4';
  const dur = await page.evaluate(() => DURATION);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(dur * fps);
  for (let i = 0; i < total; i++) {
    await page.evaluate((t) => setTime(t), i / fps);
    if (!ff.stdin.write(await shot())) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
  console.log(`${out}: ${total} frames @ ${fps}fps`);
})();
