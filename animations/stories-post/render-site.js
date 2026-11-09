// Usage (from this folder, a server rooted here): PORT=8766 node render-site.js ../../videos/basarab-stories.mp4
// One-pass render of animations/stories-post straight to the site file:
// 960x1200 story post padded to 1016x1200, BT.709-tagged, field lifted 6->7 so it decodes to #060606.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [out, dur] = [process.argv[2], parseFloat(process.argv[3] || '0')];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/index.html?t=0`);
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.decode())); });
  const fps = 30, D = dur || await page.evaluate(() => DURATION), total = Math.round(D * fps);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-vf', "scale=960:1200:flags=lanczos,format=rgb24,lutrgb=r='if(eq(val,6),7,val)':g='if(eq(val,6),7,val)':b='if(eq(val,6),7,val)',pad=1016:1200:28:0:color=0x070707,scale=out_color_matrix=bt709:out_range=tv",
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < total; i++) {
    await page.evaluate((t) => setTime(t), i / fps);
    if (!ff.stdin.write(await page.locator('.post').screenshot({ type: 'png' }))) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise((r) => ff.on('close', r)); await browser.close();
  console.log(out, total, 'frames');
})();
