"""fp0081 Stage 4: template extraction + matching (minutiae-based).

Minutiae extraction: ridge skeleton via cv2, crossing-number method for
ridge endings (CN=1) and bifurcations (CN=3). Template = sorted list of
minutiae (x, y, type). Matching: minutiae count + spatial proximity
score. Genuine/impostor evaluation on captured data.

This is a PROOF-OF-CONCEPT matcher. Production-grade matching would use
a proper minutiae matcher (e.g. mindtct/bozorth3 style or libfprint's
internal matcher). The goal here is biometric qualification: do repeated
captures of the same finger score higher than different/no-finger
frames?
"""
import numpy as np
import cv2


def enhance(image, block=16):
    """Basic ridge enhancement: CLAHE + blur + adaptive binarize + skeletonize.

    Adaptive threshold (Gaussian, block 21, C=5) outperforms Otsu on the
    small low-contrast 128x64 captures (Otsu loses ridge structure).
    """
    img = np.asarray(image, dtype=np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    bin_img = cv2.adaptiveThreshold(img, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 21, 5)
    # skeleton
    skel = np.zeros_like(bin_img)
    temp = bin_img.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        eroded = cv2.erode(temp, kernel)
        if not eroded.any():
            break
        opening = cv2.morphologyEx(eroded, cv2.MORPH_OPEN, kernel)
        skel |= cv2.subtract(eroded, opening)
        temp = eroded
    return skel


def crossing_number(skel):
    """CN-based minutiae detection on a skeleton (0/255 binary).

    Uses int32 arithmetic (uint8 overflows in the CN sum).
    """
    h, w = skel.shape
    binary = (skel > 0).astype(np.int32)
    minu = []
    # 8-neighbor order
    nbr = [(0, -1), (1, -1), (1, 0), (1, 1),
           (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if binary[y, x] == 0:
                continue
            vals = [int(binary[y + dy, x + dx]) for dx, dy in nbr]
            cn = sum(abs(vals[i] - vals[(i + 1) % 8]) for i in range(8)) // 2
            if cn == 1:
                minu.append((x, y, 'end'))
            elif cn == 3:
                minu.append((x, y, 'bif'))
    return minu


def extract_template(image, border=4):
    """Extract minutiae template from a corrected image.

    Returns dict: {'minutiae': [(x,y,type)...], 'count': n,
                   'quality': mean ridge energy proxy}
    """
    skel = enhance(image)
    minu = crossing_number(skel)
    # remove border minutiae (noise at frame edge)
    h, w = skel.shape
    minu = [m for m in minu if border <= m[0] < w - border
            and border <= m[1] < h - border]
    return {
        'minutiae': sorted(minu),
        'count': len(minu),
    }


def match_templates(t1, t2, max_dist=6):
    """Minutiae-based similarity: fraction of t1 minutiae matched in t2.

    Simple spatial matching: each t1 minutia finds nearest t2 minutia of
    same type within max_dist px. Score = matched/total (greedy).
    """
    if t1['count'] == 0 or t2['count'] == 0:
        return 0.0
    m2 = t2['minutiae']
    matched = 0
    for x1, y1, typ1 in t1['minutiae']:
        best = None
        for x2, y2, typ2 in m2:
            if typ2 != typ1:
                continue
            d = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if d <= max_dist * max_dist:
                if best is None or d < best[0]:
                    best = (d, (x2, y2))
        if best is not None:
            matched += 1
    return matched / t1['count']


def evaluate(genuine_pairs, impostor_pairs):
    """Score genuine vs impostor distributions.

    genuine_pairs: list of (t1, t2) same-finger pairs
    impostor_pairs: list of (t1, t2) different/no-finger pairs
    Returns dict with mean scores + separation.
    """
    gs = [match_templates(a, b) for a, b in genuine_pairs]
    is_ = [match_templates(a, b) for a, b in impostor_pairs]
    g_mean = np.mean(gs) if gs else 0
    i_mean = np.mean(is_) if is_ else 0
    return {
        'genuine_scores': gs,
        'impostor_scores': is_,
        'genuine_mean': float(g_mean),
        'impostor_mean': float(i_mean),
        'separation': float(g_mean - i_mean),
        'genuine_count': len(gs),
        'impostor_count': len(is_),
    }


if __name__ == "__main__":
    import json, os, sys
    # Load all corrected finger images from the live + optical tests
    sys.path.insert(0, '/home/david/fp-research/work/calibration-re')
    import fp0081_driver as f

    out = '/tmp/fp0081-stage4'
    os.makedirs(out, exist_ok=True)

    images = {}
    # live test corrected PNGs (finger)
    for i in range(3):
        p = f'/tmp/fp0081-live-test/finger_{i}.png'
        if os.path.exists(p):
            images[f'live_f{i}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    # robust test corrected PNGs (finger, cached ref)
    for i in range(2):
        p = f'/tmp/fp0081-robust-test/robust_{i}.png'
        if os.path.exists(p):
            images[f'robust_f{i}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    # optical test corrected PNGs (finger + covered)
    for name in ['finger', 'covered', 'covered2']:
        p = f'/tmp/0081-optical-test/{name}_flatfield.png'
        if os.path.exists(p):
            images[f'opt_{name}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)

    print('images loaded:', list(images.keys()))
    templates = {k: extract_template(v) for k, v in images.items()}
    for k, t in templates.items():
        print(f'  {k}: {t["count"]} minutiae')

    # Genuine pairs: same finger repeated captures
    finger_keys = [k for k in images if 'finger' in k or 'robust_f' in k]
    genuine = []
    for i in range(len(finger_keys)):
        for j in range(i + 1, len(finger_keys)):
            genuine.append((templates[finger_keys[i]],
                            templates[finger_keys[j]]))

    # Impostor pairs: finger vs covered (no finger)
    impostor = []
    for fk in finger_keys:
        for ck in [k for k in images if 'covered' in k]:
            impostor.append((templates[fk], templates[ck]))

    print()
    print('=== GENUINE (same finger repeats) ===')
    for (a, b), (ka, kb) in zip(genuine, [(finger_keys[i], finger_keys[j])
                                           for i in range(len(finger_keys))
                                           for j in range(i+1, len(finger_keys))]):
        print(f'  {ka} vs {kb}: {match_templates(a, b):.3f}')

    print()
    print('=== IMPOSTOR (finger vs no-finger covered) ===')
    for (a, b), (ka, kb) in zip(impostor, [(fk, ck) for fk in finger_keys
                                            for ck in [k for k in images if 'covered' in k]]):
        print(f'  {ka} vs {kb}: {match_templates(a, b):.3f}')

    res = evaluate(genuine, impostor)
    print()
    print('=== SUMMARY ===')
    print(f'  genuine mean: {res["genuine_mean"]:.3f} (n={res["genuine_count"]})')
    print(f'  impostor mean: {res["impostor_mean"]:.3f} (n={res["impostor_count"]})')
    print(f'  separation: {res["separation"]:.3f}')
    with open(f'{out}/eval.json', 'w') as fp:
        json.dump({k: (v if not isinstance(v, np.ndarray) else v.tolist())
                   for k, v in res.items()}, fp, indent=2)
    print(f'  saved {out}/eval.json')
