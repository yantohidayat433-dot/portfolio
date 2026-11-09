# Splits the client's Instagram-post frames (Figma section 72:252, frames
# 14.1-14.3, exported at 2x = 2030x1240) into a clean background per frame (post
# text replaced by her raw image fills recomposed at the Figma geometry) and one
# flat-colour RGBA sprite per text line, for render.py.
import json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation
FW, FH = 2030, 1240
def layer(path, box, canvas_rgb, mode='normal'):
    """Draw an image fill whose box (x, y, w, h) is in frame 2x px, fractional."""
    im = Image.open(path).convert('RGBA'); x, y, w, h = box
    sx, sy = im.width / w, im.height / h
    t = im.transform((FW, FH), Image.AFFINE, (sx, 0, -x * sx, 0, sy, -y * sy), Image.BICUBIC)
    a = np.asarray(t, np.float32) / 255
    al = a[..., 3:4]
    canvas_rgb[:] = canvas_rgb * (1 - al) + a[..., :3] * al
def post(px, py, bg, layers):
    """Clean post in frame coords: post frame at (px, py) (1x Figma px), layers in post-relative 1x px."""
    c = np.zeros((FH, FW, 3), np.float32) + np.array(bg, np.float32) / 255
    for path, (x, y, w, h) in layers:
        layer(path, ((px + x) * 2, (py + y) * 2, w * 2, h * 2), c)
    return c
hexc = lambda s: tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
# frame -> posts with text: (clean builder, [(colour, box x0,y0,x1,y1 in 2x frame px, line pitch 2x, n lines)])
POSTS = {
    1: [
        (lambda: post(97, 154.26, (255, 255, 255), [('src/f1p1-109838.png', (-9.03, 156.25 - 181.25, 272.569, 363.426))]),
         [('#131926', (300, 828, 590, 900), 30, 2)]),
        (lambda: post(669, 154.19, hexc('#cfd2b5'), [('src/f1p3-tex8.png', (-325, -35.19, 630, 382))]),
         [('#ffffff', (1345, 425, 1830, 805), 72.5, 5), ('#ffffff', (1460, 860, 1720, 895), 30, 1)]),
    ],
    2: [
        (lambda: post(97, 154.19, hexc('#401a22'), [('src/f2p1-85.png', (0, -49.19, 249.424, 397))]),
         [('#ffffff', (210, 782, 640, 900), 53.2, 2)]),
        (lambda: post(383, 154.19, hexc('#eae9f0'), [('src/f2p2-pattern.png', (-213, -119.19, 635.225, 517.207))]),
         [('#131926', (800, 340, 1240, 530), 83.1, 2), ('#131926', (860, 828, 1180, 900), 30, 2)]),
    ],
    3: [
        (lambda: post(383, 154.19, hexc('#131926'), [('src/f3p2-tex3.png', (-154, -60.19, 655, 398))]),
         [('#eae9f0', (800, 528, 1240, 712), 83.1, 2), ('#eae9f0', (860, 828, 1180, 900), 30, 2)]),
        (lambda: post(669, 154.19, (255, 255, 255), [('src/f3p3-42.png', (0, -40.87, 250.08, 393.182))]),
         [('#141620', (1350, 340, 1820, 440), 43, 2)]),
    ],
}
if __name__ == '__main__':
    import sys
    meta = {}
    for f, posts in POSTS.items():
        E = np.asarray(Image.open(f'src/frame-{f}.png').convert('RGB'), np.float32) / 255
        if f == 1:  # first post's white header box starts 1px lower in Figma: take 14.2's edge
            E[230:246, 186:702] = np.asarray(Image.open('src/frame-2.png').convert('RGB'), np.float32)[230:246, 186:702] / 255
        out = E.copy(); lines = []
        for build, texts in posts:
            C = build()
            for col, (x0, y0, x1, y1), pitch, n in texts:
                T = np.array(hexc(col), np.float32) / 255
                Cb, Eb = C[y0:y1, x0:x1], E[y0:y1, x0:x1]
                if 'check' in sys.argv:
                    ring = np.ones((y1 - y0, x1 - x0), bool)
                    print(f, col, 'clean vs export in box (incl. text):', np.abs(Cb - Eb).mean().round(4))
                den = T - Cb; w = np.abs(den)
                a = ((Eb - Cb) * np.sign(den)).sum(2) / np.maximum(w.sum(2), 1e-3)
                a = np.clip(a, 0, 1); a[w.sum(2) < 0.12] = 0; a[a < 0.04] = 0
                m = np.zeros((FH, FW), np.float32); m[y0:y1, x0:x1] = binary_dilation(a > 0.02, iterations=3)
                m = np.clip(gaussian_filter(m, 1.2) * 1.5, 0, 1)[..., None]
                out = out * (1 - m) + C * m
                # split rows at the least-inked row near each expected line boundary
                ink = a.sum(1); top = np.argmax(ink > 0.5)
                cuts = [0]
                for i in range(1, n):
                    e = int(top + i * pitch); lo, hi = max(1, e - int(pitch * .35)), min(len(ink) - 1, e + int(pitch * .25))
                    cuts.append(lo + int(np.argmin(ink[lo:hi])))
                cuts.append(len(ink))
                for i in range(n):
                    ya, yb = cuts[i], cuts[i + 1]
                    spr = np.zeros((yb - ya, x1 - x0, 4), np.uint8)
                    spr[..., :3] = np.array(hexc(col)); spr[..., 3] = (a[ya:yb] * 255).round()
                    fn = f'sprites/{f}-{x0}-{y0}-{i}.png'
                    Image.fromarray(spr, 'RGBA').save(fn)
                    lines.append({'file': fn, 'x': x0, 'y': int(y0 + ya)})
        Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)).save(f'sprites/{f}-bg.png')
        meta[f] = lines
    json.dump(meta, open('sprites/meta.json', 'w'), indent=1)
    print({k: len(v) for k, v in meta.items()})
