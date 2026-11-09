# Renders the 3-stories slide clip from build.py's sprites: two slides (Figma
# section 68:106, frames 68:44 and 4:686), hard cut between them, looping; each
# story's progress bar fills over the slide and its text lines rise, sharpen and
# fade in one after another, with the timings of animations/stories-post.
# Usage: python3 render.py out.mp4 [seconds per slide] [start offset]
# The site file opens 1s into slide 1 (text settled) so its poster still matches.
import json, subprocess, sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, shift as subshift
OUT = sys.argv[1]; PER = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
START = float(sys.argv[3]) if len(sys.argv) > 3 else 0
FPS, W, H = 30, 2030, 1200
X = [230, 774, 1318]; Y = 166          # Figma 115/387/659, 83 (x2)
SLIDES = [['1a', '1b', '1c'], ['2a', '2b', '2c']]
TEXT_AT, TEXT_STEP, TEXT_DUR = 0.075, 0.075, 0.47
RISE, BLUR = 28 * 480 / 540, 6 * 480 / 540   # stories-post values, scaled to this story width
BAR_X, BAR_W, BAR_Y0, BAR_Y1 = 23.4, 433.2, 21.65, 25.16
meta = json.load(open('sprites/meta.json'))
bg = {k: np.asarray(Image.open(f'sprites/{k}-bg.png'), np.float32) / 255 for k in meta}
spr = {k: [(np.asarray(Image.open(l['file']), np.float32) / 255, l['x'], l['y']) for l in v['lines']] for k, v in meta.items()}
ease = lambda x: 1 - (1 - min(1, max(0, x))) ** 3
def bar_cov(p):
    h, w = bg['1a'].shape[:2]
    c = np.zeros((h, w), np.float32)
    rows = np.arange(h)
    rc = np.clip(np.minimum(rows + 1, BAR_Y1) - np.maximum(rows, BAR_Y0), 0, 1)
    cols = np.arange(w)
    end = BAR_X + BAR_W * p
    cc = np.clip(np.minimum(cols + 1, end) - np.maximum(cols, BAR_X), 0, 1)
    full = np.clip(np.minimum(cols + 1, BAR_X + BAR_W) - np.maximum(cols, BAR_X), 0, 1)
    return rc[:, None] * cc[None, :], rc[:, None] * full[None, :]
def story(k, u, p):
    s = bg[k].copy(); rgb = s[..., :3]
    col = np.ones(3) if meta[k]['ui_light'] else np.full(3, 0x33 / 255)
    fill, track = bar_cov(p)
    a = track * 0.3; rgb[:] = rgb * (1 - a[..., None]) + col * a[..., None]
    rgb[:] = rgb * (1 - fill[..., None]) + col * fill[..., None]
    for j, (sp, x, y) in enumerate(spr[k]):
        e = ease((u - TEXT_AT - j * TEXT_STEP) / TEXT_DUR)
        if e <= 0: continue
        al = sp[..., 3]
        pad = 16; al = np.pad(al, pad)
        if e < 1:
            al = subshift(al, ((1 - e) * RISE, 0), order=1, mode='constant')
            al = gaussian_filter(al, (1 - e) * BLUR) if (1 - e) * BLUR > 0.05 else al
        al = al * e
        y0, x0 = y - pad, x - pad
        hh, ww = al.shape
        ys, xs = max(0, y0), max(0, x0); ye, xe = min(s.shape[0], y0 + hh), min(s.shape[1], x0 + ww)
        A = al[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
        rgb[ys:ye, xs:xe] = rgb[ys:ye, xs:xe] * (1 - A) + sp[0, 0, :3] * A  # sprites are one flat colour
    return s
N = int(round(PER * len(SLIDES) * FPS))
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-an', '-c:v', 'libx264', '-crf', '22', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
base = np.zeros((H, W, 3), np.float32) + 6 / 255
for n in range(N):
    t = (n / FPS + START) % (PER * len(SLIDES)); si = int(t // PER); u = t - si * PER
    frame = base.copy()
    for k, x in zip(SLIDES[si], X):
        s = story(k, u, u / PER)
        h, w = s.shape[:2]; A = s[..., 3:4]
        frame[Y:Y + h, x:x + w] = frame[Y:Y + h, x:x + w] * (1 - A) + s[..., :3] * A
    ff.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait(); print(OUT, N, 'frames')
