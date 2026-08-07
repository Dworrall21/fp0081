"""fp0081 Stage 4b: orientation-descriptor matching (robust for low-res).

The CN minutiae matcher failed (no genuine/impostor separation at
128x64 - 0.917 vs 0.909). This uses a ridge-orientation descriptor
approach instead:

1. Compute local ridge orientation field (gradient-based, block-wise)
2. Build a global orientation histogram descriptor (FingerCode-style)
3. Match with cosine similarity + histogram intersection

FingerCode-style global descriptors are known to work reasonably at
low resolution where minutiae are unreliable.
"""
import numpy as np
import cv2


def orientation_field(img, block=8):
    """Ridge orientation per block via gradient covariance (0..pi)."""
    img = np.asarray(img, dtype=np.float32)
    gy, gx = np.gradient(img)
    h, w = img.shape
    orient = np.zeros((h // block, w // block), dtype=np.float32)
    for by in range(0, h - block, block):
        for bx in range(0, w - block, block):
            gxx = (gx[by:by+block, bx:bx+block] ** 2).sum()
            gyy = (gy[by:by+block, bx:bx+block] ** 2).sum()
            gxy = (gx[by:by+block, bx:bx+block] *
                   gy[by:by+block, bx:bx+block]).sum()
            # theta = 0.5 * atan2(2gxy, gxx-gyy)
            theta = 0.5 * np.arctan2(2 * gxy, gxx - gyy)
            orient[by // block, bx // block] = theta
    return orient


def orientation_histogram(img, bins=16):
    """Global ridge-orientation histogram (rotation-approx-invariant)."""
    orient = orientation_field(img)
    # normalize to [0, pi), histogram
    o = (orient % np.pi).flatten()
    hist, _ = np.histogram(o, bins=bins, range=(0, np.pi))
    return hist.astype(np.float32)


def frequency_descriptor(img, nbins=8):
    """Ridge-frequency descriptor: FFT radial power in ridge band."""
    img = np.asarray(img, dtype=np.float32)
    fft = np.fft.fft2(img - img.mean())
    mag = np.abs(np.fft.fftshift(fft))
    h, w = img.shape
    Y, X = np.mgrid[0:h, 0:w]
    R = np.sqrt((X - w // 2) ** 2 + (Y - h // 2) ** 2)
    # radial bands
    rmax = np.sqrt((h/2)**2 + (w/2)**2)
    edges = np.linspace(0, rmax, nbins + 1)
    desc = []
    for i in range(nbins):
        band = (R >= edges[i]) & (R < edges[i+1])
        desc.append(float(mag[band].mean()) if band.any() else 0)
    return np.array(desc, dtype=np.float32)


def extract_descriptor(image):
    """Combine orientation histogram + frequency descriptor + local stats."""
    img = np.asarray(image, dtype=np.uint8)
    oh = orientation_histogram(img)
    fd = frequency_descriptor(img)
    # normalize
    oh = oh / (oh.sum() + 1e-9)
    fd = fd / (fd.sum() + 1e-9)
    return np.concatenate([oh, fd])


def cosine_sim(a, b):
    da = np.linalg.norm(a); db = np.linalg.norm(b)
    return float((a * b).sum() / (da * db)) if da * db else 0.0


def match_descriptors(d1, d2):
    return cosine_sim(d1, d2)


def evaluate(genuine_pairs, impostor_pairs):
    gs = [match_descriptors(a, b) for a, b in genuine_pairs]
    is_ = [match_descriptors(a, b) for a, b in impostor_pairs]
    return {
        'genuine_scores': gs,
        'impostor_scores': is_,
        'genuine_mean': float(np.mean(gs)) if gs else 0,
        'impostor_mean': float(np.mean(is_)) if is_ else 0,
        'separation': float(np.mean(gs) - np.mean(is_)) if gs and is_ else 0,
        'genuine_count': len(gs),
        'impostor_count': len(is_),
    }


if __name__ == "__main__":
    import json, os, sys
    sys.path.insert(0, '/home/david/fp-research/work/calibration-re')

    out = '/tmp/fp0081-stage4'
    os.makedirs(out, exist_ok=True)

    images = {}
    for i in range(3):
        p = f'/tmp/fp0081-live-test/finger_{i}.png'
        if os.path.exists(p):
            images[f'live_f{i}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    for i in range(2):
        p = f'/tmp/fp0081-robust-test/robust_{i}.png'
        if os.path.exists(p):
            images[f'robust_f{i}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    for name in ['finger', 'covered', 'covered2']:
        p = f'/tmp/0081-optical-test/{name}_flatfield.png'
        if os.path.exists(p):
            images[f'opt_{name}'] = cv2.imread(p, cv2.IMREAD_GRAYSCALE)

    print('images:', list(images.keys()))
    descs = {k: extract_descriptor(v) for k, v in images.items()}

    finger_keys = [k for k in images if 'finger' in k or 'robust_f' in k]
    genuine = [(descs[a], descs[b])
               for i, a in enumerate(finger_keys)
               for b in finger_keys[i+1:]]
    impostor = [(descs[a], descs[b])
                for a in finger_keys
                for b in [k for k in images if 'covered' in k]]

    print()
    print('=== GENUINE ===')
    for i, a in enumerate(finger_keys):
        for b in finger_keys[i+1:]:
            print(f'  {a} vs {b}: {cosine_sim(descs[a], descs[b]):.4f}')
    print()
    print('=== IMPOSTOR (finger vs covered) ===')
    for a in finger_keys:
        for b in [k for k in images if 'covered' in k]:
            print(f'  {a} vs {b}: {cosine_sim(descs[a], descs[b]):.4f}')

    res = evaluate(genuine, impostor)
    print()
    print('=== SUMMARY ===')
    print(f'  genuine mean: {res["genuine_mean"]:.4f} (n={res["genuine_count"]})')
    print(f'  impostor mean: {res["impostor_mean"]:.4f} (n={res["impostor_count"]})')
    print(f'  separation: {res["separation"]:.4f}')
    with open(f'{out}/eval_descriptor.json', 'w') as fp:
        json.dump({k: (v if not isinstance(v, np.ndarray) else v.tolist())
                   for k, v in res.items()}, fp, indent=2)
    print(f'  saved {out}/eval_descriptor.json')
