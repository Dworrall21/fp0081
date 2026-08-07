# fp0081 — Native Linux driver for Synaptics 06cb:0081 fingerprint sensor

Working native driver + solved calibration. The 06cb:0081's banded raw
output CONTAINS the fingerprint — recovered via flat-field correction
(background subtraction + row-bias removal). Verified live on real
hardware.

## Status

| Stage | Result |
|---|---|
| Calibration problem | SOLVED (proof-of-concept, Sol-reviewed) |
| Driver (session/capture/correction/presence) | Working, live-validated |
| Robustness (cached ref, cross-session) | PASSED |
| Matrix (96x96) mapping to image | REJECTED (coefficient object) |
| Biometrics (POC) | Extract + same-finger match 0.97 |

## Quick start

```python
from fp0081_driver import Fp0081

dev = Fp0081().open()                    # USB reset -> TLS -> authorize
ref = dev.capture_background_reference(n=8)   # sensor uncovered
img, corr = dev.capture_corrected()      # finger on sensor
score, _ = dev.presence_score(img)       # ridge-band energy
# >1500 finger present, <400 none, opaque cover ~190
```

Prereqs: python-validity (validitysensor), cryptography, numpy, PIL.
Session artifacts (pairing key/cert, validated frames) via DEFAULTS.

## Key facts (0x195 / 06cb:0081)

- authorize = 6677B constant; IDENTIFY frame = 155_TX (10608B)
- CALIBRATE frame = 017_TX (1200B, req_lines=0, empty 0x34/0x30)
- frame = 6B env + 8192B = 128x64 grayscale
- key_calibration_line = 44, key line = matrix row 46, fcv[44] = 0x80
- 96x96 matrix = calibration-generation object, NOT image background
- 0x4e chunk = 0x199-specific, rejected by 0081 device

## Evidence

Full hash-verified trail: `evidence.sha256` (106 entries) + docs/.

## License

Research/experimental. No warranty. Use at your own risk.
