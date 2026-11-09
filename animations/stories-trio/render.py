# Renders the 3-stories slide clip from build.py's sprites: two slides (Figma
# section 68:106, frames 68:44 and 4:686), hard cut between them, looping. Each
# story's progress bar has one segment per slide and fills the current one; its
# text lines fade in one after another with a slight rise, no blur (same timing
# as the Instagram posts clip).
# Usage: python3 render.py out.mp4 [seconds per slide] [start offset]
# The site file opens 1s into slide 1 (text settled) so its poster still matches.
import json, subprocess, sys, numpy as np
from PIL import Image
from scipy.ndimage import shift as subshift
OUT = sys.argv[1]; PER = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
START = float(sys.argv[3]) if len(sys.argv) > 3 else 0
FPS, W, H = 30, 2030, 1200
X = [230, 774, 1318]; Y = 166          # Figma 115/387/659, 83 (x2)
SLIDES = [['1a', '1b', '1c'], ['2a', '2b', '2c']]
TEXT_AT, TEXT_STEP, TEXT_DUR = 0.05, 0.08, 0.8   # same gentle fade as the Instagram posts clip
RISE = 8 * 480 / 500                              # its 8px rise, scaled to this story width; no blur
BAR_X, BAR_W, BAR_Y0, BAR_Y1 = 23.4, 433.2, 21.65, 25.16
meta = json.load(open('sprites/meta.json'))
bg = {k: np.asarray(Image.open(f'sprites/{k}-bg.png'), np.float32) / 255 for k in meta}
spr = {k: [(np.asarray(Image.open(l['file']), np.float32) / 255, l['x'], l['y']) for l in v['lines']] for k, v in meta.items()}
def ease(x):  # ease-in-out (cubic)
    x = min(1, max(0, x)); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
GAP = 4  # between the two segments (2x px; stories-post's 4px at its 540px story)
def bar_cov(seg, p):
    """Coverage of the filled part and of the whole track; one segment per slide."""
    h, w = bg['1a'].shape[:2]
    rows = np.arange(h)
    rc = np.clip(np.minimum(rows + 1, BAR_Y1) - np.maximum(rows, BAR_Y0), 0, 1)
    cols = np.arange(w)
    span = lambda a, b: np.clip(np.minimum(cols + 1, b) - np.maximum(cols, a), 0, 1)
    sw = (BAR_W - GAP * (len(SLIDES) - 1)) / len(SLIDES)
    fill = np.zeros(w, np.float32); track = np.zeros(w, np.float32)
    for i in range(len(SLIDES)):
        a = BAR_X + i * (sw + GAP)
        track += span(a, a + sw)
        fill += span(a, a + sw * (1 if i < seg else p if i == seg else 0))
    return rc[:, None] * fill[None, :], rc[:, None] * track[None, :]
def story(k, seg, u, p):
    s = bg[k].copy(); rgb = s[..., :3]
    col = np.ones(3) if meta[k]['ui_light'] else np.full(3, 0x33 / 255)
    fill, track = bar_cov(seg, p)
    a = track * 0.3; rgb[:] = rgb * (1 - a[..., None]) + col * a[..., None]
    rgb[:] = rgb * (1 - fill[..., None]) + col * fill[..., None]
    for j, (sp, x, y) in enumerate(spr[k]):
        e = ease((u - TEXT_AT - j * TEXT_STEP) / TEXT_DUR)
        if e <= 0: continue
        al = sp[..., 3]
        pad = 16; al = np.pad(al, pad)
        if e < 1: al = subshift(al, ((1 - e) * RISE, 0), order=1, mode='constant')
        al = al * e
        y0, x0 = y - pad, x - pad
        hh, ww = al.shape
        ys, xs = max(0, y0), max(0, x0); ye, xe = min(s.shape[0], y0 + hh), min(s.shape[1], x0 + ww)
        A = al[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
        rgb[ys:ye, xs:xe] = rgb[ys:ye, xs:xe] * (1 - A) + sp[0, 0, :3] * A  # sprites are one flat colour
    return s
N = int(round(PER * len(SLIDES) * FPS))
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    # BT.709 conversion + tags: untagged HD H.264 is read as BT.709 by browsers but
    # ffmpeg converts with BT.601 by default, which shifted warm tones vs the poster.
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-an', '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
base = np.zeros((H, W, 3), np.float32) + 7 / 255  # Figma's #060606, lifted so the H.264 decodes to 6
for n in range(N):
    t = (n / FPS + START) % (PER * len(SLIDES)); si = int(t // PER); u = t - si * PER
    frame = base.copy()
    for k, x in zip(SLIDES[si], X):
        s = story(k, si, u, u / PER)
        h, w = s.shape[:2]; A = s[..., 3:4]
        frame[Y:Y + h, x:x + w] = frame[Y:Y + h, x:x + w] * (1 - A) + s[..., :3] * A
    ff.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait(); print(OUT, N, 'frames')
