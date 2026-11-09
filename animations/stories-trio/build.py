# Splits the client's Figma story exports (2x, 480x869) into a clean background
# (no progress line, no story text) and one RGBA sprite per text line, so the
# text can rise in and the bar can fill in render.py. Clean photo under the text
# is recomposed from her raw image fills at the Figma geometry (matches the export
# to <1 level outside the text).
import json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation
W, H = 480, 869
def place(canvas, path, x, y, w, h, mode='normal'):
    im = np.asarray(Image.open(path).convert('RGB').resize((round(w), round(h)), Image.LANCZOS), np.float32)
    xi, yi = round(x), round(y)
    x0, y0 = max(0, xi), max(0, yi); x1, y1 = min(W, xi + im.shape[1]), min(H, yi + im.shape[0])
    sub = im[y0 - yi:y1 - yi, x0 - xi:x1 - xi]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * sub / 255 if mode == 'multiply' else sub
clean = {}
c = np.full((H, W, 3), 255, np.float32); place(c, 'src/s1c-109846.png', -210, -80, 714, 952); clean['1c'] = c * 0.85
c = np.full((H, W, 3), 246, np.float32); place(c, 'src/s2b-109846.png', -46.88, 78.4, 574.88, 766.51, 'multiply'); clean['2b'] = c
# text blocks (2x): story, name, colour, box (x0,y0,x1,y1), line pitch
TEXT = {
    '1c': [('big', (255, 255, 255), (10, 95, 476, 400), 90.85), ('small', (255, 255, 255), (110, 750, 370, 825), 30.72)],
    '2b': [('big', (0xAC, 0xB5, 0x9C), (10, 95, 476, 400), 90.85), ('small', (0x1A, 0x22, 0x33), (110, 710, 370, 785), 30.72)],
}
meta = {}
for k in ['1a', '1b', '1c', '2a', '2b', '2c']:
    E = np.asarray(Image.open(f'src/story-{k}.png').convert('RGBA'), np.float32)
    rgb, alpha = E[..., :3].copy(), E[..., 3]
    # progress line (y 21.7-25.2 at 2x): fill rows 19-27 by blending the rows just outside
    top, bot = rgb[18].copy(), rgb[28].copy()
    for y in range(19, 28):
        f = (y - 18) / 10; rgb[y] = top * (1 - f) + bot * f
    lines = []
    for name, col, (x0, y0, x1, y1), pitch in TEXT.get(k, []):
        C = clean[k][y0:y1, x0:x1]; Eb = E[y0:y1, x0:x1, :3]; T = np.array(col, np.float32)
        den = T - C
        wgt = np.abs(den)
        a = ((Eb - C) * np.sign(den)).sum(2) / np.maximum(wgt.sum(2), 1e-3)
        a = np.clip(a, 0, 1); a[wgt.sum(2) < 30] = 0
        a[a < 0.04] = 0
        # replace text with the clean photo, softly
        m = np.zeros((H, W), np.float32); m[y0:y1, x0:x1] = binary_dilation(a > 0.02, iterations=3)
        m = np.clip(gaussian_filter(m, 1.2) * 1.5, 0, 1)[..., None]
        rgb = rgb * (1 - m) + clean[k] * m
        # split into lines by rows with no ink, else at the pitch
        # line bands (box-relative), from the ink rows of the clean flat story 2b
        bounds = [5, 104, 197, 305] if name == 'big' else [0, 36, 75]
        for i in range(len(bounds) - 1):
            ya, yb = bounds[i], bounds[i + 1]
            spr = np.zeros((yb - ya, x1 - x0, 4), np.uint8)
            spr[..., :3] = T; spr[..., 3] = (a[ya:yb] * 255).round()
            fn = f'sprites/{k}-{name}-{i}.png'
            Image.fromarray(spr, 'RGBA').save(fn)
            lines.append({'file': fn, 'x': int(x0), 'y': int(y0 + ya)})
    out = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(f'sprites/{k}-bg.png')
    meta[k] = {'lines': lines, 'ui_light': k in ('1a', '1c', '2c')}
json.dump(meta, open('sprites/meta.json', 'w'), indent=1)
print(json.dumps({k: len(v['lines']) for k, v in meta.items()}))
