# Renders the Instagram-posts clip from build.py's sprites: frames 14.1-14.3 in
# turn, hard cut every PER seconds; after each cut every post's text lines rise,
# sharpen and fade in one after another, with the timings of
# animations/stories-post (rise/blur scaled to the 250px post).
# Usage: python3 render.py out.mp4 [seconds per frame] [start offset]
# The site file opens 1s into frame 1 (text settled) so its poster still matches.
import json, subprocess, sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as subshift
OUT = sys.argv[1]
PER = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
START = float(sys.argv[3]) if len(sys.argv) > 3 else 0
FPS, W, H = 30, 2030, 1240
TEXT_AT, TEXT_STEP, TEXT_DUR = 0.075, 0.075, 0.47
RISE, BLUR = 28 * 500 / 540, 6 * 500 / 540
meta = json.load(open('sprites/meta.json'))
FRAMES = ['1', '2', '3']
bg = {f: np.asarray(Image.open(f'sprites/{f}-bg.png').convert('RGB'), np.float32) / 255 for f in FRAMES}
# lines grouped per post (sprites of one post share a text-block x) in reading order
spr = {}
for f in FRAMES:
    posts = {}
    for l in meta[f]:
        posts.setdefault(l['x'] // 500, []).append((np.asarray(Image.open(l['file']), np.float32) / 255, l['x'], l['y']))
    spr[f] = [sorted(v, key=lambda s: s[2]) for v in posts.values()]
ease = lambda x: 1 - (1 - min(1, max(0, x))) ** 3
def frame_at(f, u):
    img = bg[f].copy()
    for lines in spr[f]:
        for j, (sp, x, y) in enumerate(lines):
            e = ease((u - TEXT_AT - j * TEXT_STEP) / TEXT_DUR)
            if e <= 0: continue
            pad = 16; al = np.pad(sp[..., 3], pad)
            if e < 1:
                al = subshift(al, ((1 - e) * RISE, 0), order=1, mode='constant')
                if (1 - e) * BLUR > 0.05: al = gaussian_filter(al, (1 - e) * BLUR)
            al = al * e
            y0, x0 = y - pad, x - pad; hh, ww = al.shape
            ys, xs = max(0, y0), max(0, x0); ye, xe = min(H, y0 + hh), min(W, x0 + ww)
            A = al[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
            img[ys:ye, xs:xe] = img[ys:ye, xs:xe] * (1 - A) + sp[0, 0, :3] * A  # sprites are one flat colour
    return img
N = int(round(PER * len(FRAMES) * FPS))
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-an', '-c:v', 'libx264', '-crf', '22', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for n in range(N):
    t = (n / FPS + START) % (PER * len(FRAMES)); fi = int(t // PER); u = t - fi * PER
    ff.stdin.write((np.clip(frame_at(FRAMES[fi], u), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait(); print(OUT, N, 'frames')
