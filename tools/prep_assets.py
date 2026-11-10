"""Phoenix animation asset builder.

Splits 'Blazing Phoenix Ascendant.png' into animatable layers:
  - assets/phoenix_base.png : original with wing fire inpainted (dark fill)
  - assets/wing_left.png    : feathered left-wing cutout  (RGBA, full canvas)
  - assets/wing_right.png   : feathered right-wing cutout (RGBA, full canvas)
  - assets/bird_mask.png    : RGBA mask (alpha=0 on the bird) so the rotating
                              ring overlay always stays behind the phoenix

Debug renders land in debug/.
"""
import os
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Blazing Phoenix Ascendant.png")
ASSETS = os.path.join(ROOT, "assets")
DEBUG = os.path.join(ROOT, "debug")
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(DEBUG, exist_ok=True)

# ring geometry measured from the source image (image pixel space)
RING_CX, RING_CY = 770, 290
RING_BANDS = [(120, 134), (171, 185), (196, 216), (217, 229), (260, 276)]

# wing root pivots (shoulders)
PIVOT_L = (660, 400)
PIVOT_R = (870, 400)

POLY_L = [(650, 340), (645, 400), (650, 470), (630, 540), (600, 600),
          (560, 640), (500, 660), (400, 665), (300, 650), (200, 620),
          (100, 590), (0, 560), (0, 45), (100, 75), (200, 115),
          (300, 165), (400, 210), (500, 255), (600, 300)]

POLY_R = [(886, 340), (880, 440), (885, 520), (910, 590), (960, 640),
          (1030, 670), (1120, 690), (1220, 700), (1330, 690), (1440, 660),
          (1536, 620), (1536, 40), (1440, 65), (1340, 110), (1240, 160),
          (1140, 210), (1040, 255), (940, 300)]

img = cv2.imread(SRC)
h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

yy, xx = np.mgrid[0:h, 0:w]
rr = np.hypot(xx - RING_CX, yy - RING_CY)
in_band = np.zeros((h, w), bool)
for a, b in RING_BANDS:
    in_band |= (rr >= a) & (rr <= b)


def poly_mask(points):
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [np.array(points, np.int32)], 1)
    return m.astype(bool)


def fire_mask():
    """All fire pixels (bright cores + dark-red feather bodies)."""
    m = (gray > 46).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE,
                         cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(m)
    out = np.zeros((h, w), np.uint8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 800:
            out[labels == i] = 1
    return out.astype(bool)


fire = fire_mask()

# ---------------------------------------------------------------- wings ---
def build_wing(poly, side):
    region = poly_mask(poly)
    mask = (fire & region & ~in_band).astype(np.uint8)
    # fill enclosed dark gaps so the cutout is a solid shape
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    out = np.zeros((h, w), np.uint8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 3000:
            out[labels == i] = 1
    mask = out
    # feathered alpha
    alpha = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 7)
    alpha = np.clip(alpha * 1.35, 0, 1)
    rgba = np.dstack([img, (alpha * 255).astype(np.uint8)])
    cv2.imwrite(os.path.join(ASSETS, f"wing_{side}.png"), rgba)
    return mask


mask_l = build_wing(POLY_L, "left")
mask_r = build_wing(POLY_R, "right")

# ----------------------------------------------------------------- base ---
wing_union = ((mask_l > 0) | (mask_r > 0)).astype(np.uint8)
base = cv2.inpaint(img, wing_union, 9, cv2.INPAINT_TELEA)
cv2.imwrite(os.path.join(ASSETS, "phoenix_base.png"), base)

# --------------------------------------------------------- bird mask ------
# thick bird body (opening removes thin ring strokes)
low = (gray > 46).astype(np.uint8)
k25 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
thick = cv2.morphologyEx(low, cv2.MORPH_OPEN, k25)
thick = cv2.morphologyEx(thick, cv2.MORPH_CLOSE, k25)
n, labels, stats, _ = cv2.connectedComponentsWithStats(thick)
body = np.zeros((h, w), np.uint8)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] > 4000:
        body[labels == i] = 1
body = cv2.dilate(body, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
# bright fire outside the ring bands (spark tips, crest flames)
bright_out = ((gray > 85) & ~in_band).astype(np.uint8)
bird = np.maximum(body, bright_out)
bird = cv2.morphologyEx(bird, cv2.MORPH_CLOSE,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
bird_f = cv2.GaussianBlur(bird.astype(np.float32), (0, 0), 3)
alpha = np.clip(1.0 - bird_f, 0, 1)          # ring visible where bird is NOT
mask_rgba = np.dstack([np.full((h, w), 255, np.uint8)] * 3 +
                      [(alpha * 255).astype(np.uint8)])
cv2.imwrite(os.path.join(ASSETS, "bird_mask.png"), mask_rgba)

# ---------------------------------------------------------------- debug ---
def tint(color, m):
    return (img.astype(np.float32) * (1 - 0.5 * m[..., None]) +
            np.array(color, np.float32) * 0.5 * m[..., None]).astype(np.uint8)


prev = cv2.resize(img, (w // 2, h // 2))
dbg = prev.copy()
dl = cv2.resize(mask_l, (w // 2, h // 2))
dr = cv2.resize(mask_r, (w // 2, h // 2))
dbg[dl > 0] = (dbg[dl > 0] * 0.4 + np.array([0, 255, 0]) * 0.6).astype(np.uint8)
dbg[dr > 0] = (dbg[dr > 0] * 0.4 + np.array([255, 0, 255]) * 0.6).astype(np.uint8)
cv2.polylines(dbg, [np.array(POLY_L) // 2], True, (255, 255, 0), 1)
cv2.polylines(dbg, [np.array(POLY_R) // 2], True, (255, 255, 0), 1)
cv2.circle(dbg, (PIVOT_L[0] // 2, PIVOT_L[1] // 2), 4, (255, 255, 255), -1)
cv2.circle(dbg, (PIVOT_R[0] // 2, PIVOT_R[1] // 2), 4, (255, 255, 255), -1)
cv2.imwrite(os.path.join(DEBUG, "wings_preview.jpg"), dbg, [cv2.IMWRITE_JPEG_QUALITY, 90])

# rest-state composite vs original
comp = base.copy()
for m in (mask_l, mask_r):
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 7)
    a = np.clip(a * 1.35, 0, 1)[..., None]
    comp = (comp * (1 - a) + img * a).astype(np.uint8)
diff = cv2.absdiff(comp, img)
print("rest max diff:", diff.max(), " mean:", round(float(diff.mean()), 3))
cv2.imwrite(os.path.join(DEBUG, "rest_diff.jpg"),
            cv2.resize(diff, (w // 2, h // 2)), [cv2.IMWRITE_JPEG_QUALITY, 90])

bm = cv2.resize(bird, (w // 2, h // 2))
dbg2 = prev.copy()
dbg2[bm > 0] = (dbg2[bm > 0] * 0.4 + np.array([0, 255, 255]) * 0.6).astype(np.uint8)
cv2.imwrite(os.path.join(DEBUG, "bird_preview.jpg"), dbg2, [cv2.IMWRITE_JPEG_QUALITY, 90])
print("done: wings L=%.1f%% R=%.1f%% bird=%.1f%%" %
      (100 * mask_l.mean(), 100 * mask_r.mean(), 100 * bird.mean()))
