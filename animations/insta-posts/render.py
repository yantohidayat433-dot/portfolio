# Renders the Instagram-posts clip from build.py's sprites: frames 14.1-14.3 in
# turn, hard cut every PER seconds; after each cut every post's text lines fade in
# one after another with a slight rise, no blur (client: opacity only, gentler
# than the stories).
# Usage: python3 render.py out.mp4 [seconds per frame] [start offset]
# The site file opens 1s into frame 1 (text settled) so its poster still matches.
import json, subprocess, sys, numpy as np
from PIL import Image
from scipy.ndimage import shift as subshift
OUT = sys.argv[1]
PER = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
START = float(sys.argv[3]) if len(sys.argv) > 3 else 0
FPS, W, H = 30, 2030, 1240
TEXT_AT, TEXT_STEP, TEXT_DUR = 0.05, 0.08, 0.8
RISE = 8
meta = json.load(open('sprites/meta.json'))
FRAMES = ['1', '2', '3']
bg = {f: np.asarray(Image.open(f'sprites/{f}-bg.png').convert('RGB'), np.float32) / 255 for f in FRAMES}
# H.264 can't hold #0A0B0D exactly; (11,13,15) is what decodes closest to it,
# (10,11,14), in this BT.709-tagged stream (found by round-tripping this frame).
FIELD = np.array([10, 11, 13], np.float32) / 255
for f in FRAMES:
    m = np.all(np.abs(bg[f] - FIELD) < 0.5 / 255, axis=2)
    bg[f][m] = np.array([11, 13, 15], np.float32) / 255
# lines grouped per post (sprites of one post share a text-block x) in reading order
spr = {}
for f in FRAMES:
    posts = {}
    for l in meta[f]:
        posts.setdefault(l['x'] // 500, []).append((np.asarray(Image.open(l['file']), np.float32) / 255, l['x'], l['y']))
    spr[f] = [sorted(v, key=lambda s: s[2]) for v in posts.values()]
def ease(x):  # ease-in-out (cubic)
    x = min(1, max(0, x)); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def frame_at(f, u):
    img = bg[f].copy()
    for lines in spr[f]:
        for j, (sp, x, y) in enumerate(lines):
            e = ease((u - TEXT_AT - j * TEXT_STEP) / TEXT_DUR)
            if e <= 0: continue
            pad = 16; al = np.pad(sp[..., 3], pad)
            if e < 1: al = subshift(al, ((1 - e) * RISE, 0), order=1, mode='constant')
            al = al * e
            y0, x0 = y - pad, x - pad; hh, ww = al.shape
            ys, xs = max(0, y0), max(0, x0); ye, xe = min(H, y0 + hh), min(W, x0 + ww)
            A = al[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
            img[ys:ye, xs:xe] = img[ys:ye, xs:xe] * (1 - A) + sp[0, 0, :3] * A  # sprites are one flat colour
    return img
N = int(round(PER * len(FRAMES) * FPS))
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-an', '-c:v', 'libx264', '-crf', '22', '-x264-params', 'chroma-qp-offset=-6', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for n in range(N):
    t = (n / FPS + START) % (PER * len(FRAMES)); fi = int(t // PER); u = t - fi * PER
    ff.stdin.write((np.clip(frame_at(FRAMES[fi], u), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait(); print(OUT, N, 'frames')
