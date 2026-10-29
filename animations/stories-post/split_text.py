# Split baked-in story text into a clean background + one RGBA sprite per line.
# Usage (needs opencv-python-headless): python3 split_text.py src src/story-lines-v2
import sys, json, numpy as np, cv2
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
# story: (rows of the text block, dark text on light?, opening kernel for light text)
JOBS = {1: ((1380, 1620), True, 0), 3: ((1300, 1615), False, 71), 5: ((1430, 1610), False, 31)}
meta = {}
for i, ((y0, y1), dark, kern) in JOBS.items():
    O = np.asarray(Image.open(f'{src}/{i}.webp').convert('RGB')).astype(np.float32)
    L = O.mean(2)
    band = np.zeros(L.shape, bool); band[y0:y1] = True
    if dark:
        raw = (np.abs(O - 255).max(2) > 6) & band
    else:
        op = cv2.morphologyEx(L.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kern, kern)))
        raw = ((L - op) > 8) & band
    # keep glyph-sized components only (drops specks and floor texture)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(raw.astype(np.uint8), connectivity=8)
    keep = [c for c in range(1, n) if stats[c, cv2.CC_STAT_AREA] >= 25]
    mask = np.isin(lab, keep)
    m8 = cv2.dilate(mask.astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
    if dark:
        B = O.copy(); B[m8 > 0] = 255
    else:
        B = cv2.inpaint(O.astype(np.uint8), m8, 9, cv2.INPAINT_TELEA).astype(np.float32)
        blur = cv2.GaussianBlur(B, (0, 0), 6)
        w = cv2.GaussianBlur((m8 > 0).astype(np.float32), (0, 0), 4)[..., None]
        B = B * (1 - w) + blur * w
    Image.fromarray(np.clip(B, 0, 255).astype(np.uint8)).save(f'{out}/{i}-clean.webp', quality=92)

    # group glyph components into lines by their vertical centre
    ys = sorted((cent[c][1], c) for c in keep)
    groups, cur = [], [ys[0]]
    for y, c in ys[1:]:
        if y - cur[-1][0] > 18:
            groups.append(cur); cur = []
        cur.append((y, c))
    groups.append(cur)
    # a lone tittle (the dot of an i) joins the nearest real line
    area = lambda g: sum(stats[c, cv2.CC_STAT_AREA] for _, c in g)
    big = max(area(g) for g in groups)
    for g in [g for g in groups if area(g) < 0.05 * big]:
        groups.remove(g)
        y = np.mean([y for y, _ in g])
        min(groups, key=lambda h: abs(np.mean([yy for yy, _ in h]) - y)).extend(g)
    lines = []
    for k, g in enumerate(groups):
        own = np.isin(lab, [c for _, c in g])
        own = cv2.dilate(own.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        yy, xx = np.where(own)
        a, b, c0, c1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
        o, bg, mk = O[a:b, c0:c1], B[a:b, c0:c1], own[a:b, c0:c1]
        diff = np.abs(o - bg).sum(2)
        C = o[(diff >= np.percentile(diff[mk], 92)) & mk].mean(0)
        d = C - bg
        alpha = np.clip(((o - bg) * d).sum(2) / np.maximum((d * d).sum(2), 1e-3), 0, 1) * mk
        rgba = np.dstack([np.broadcast_to(C, o.shape), alpha * 255]).astype(np.uint8)
        name = f'{i}-line{k + 1}.png'
        Image.fromarray(rgba, 'RGBA').save(f'{out}/{name}')
        lines.append({'src': name, 'x': int(c0), 'y': int(a), 'w': int(c1 - c0), 'h': int(b - a)})
    meta[i] = lines
json.dump(meta, open(f'{out}/text-lines.json', 'w'), indent=1)
print(json.dumps(meta))
