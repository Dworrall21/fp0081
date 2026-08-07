# 0081 driver Stage 2 — ROBUSTNESS VALIDATED (2026-08-06)

## Live cross-session tests (cached reference, no re-capture)

Session B (fresh open, cached ref from Session A):
  finger frame 0: presence 2578 (threshold >1500) PASS
  finger frame 1: presence 2625 PASS

## Offline cross-session reference matrix (ridge-band energy)

finger_optical (A) vs ref_optical (A): 2434
finger_optical (A) vs ref_live (B):    2423
finger_optical (A) vs ref_native (C):  3354
finger_live (B) vs ref_live (B):       2441
finger_live (B) vs ref_optical (A):    2446
finger_live (B) vs ref_native (C):     3717
covered (no finger) vs ref_optical:    192
covered (no finger) vs ref_live:       154

ALL finger references detect (>2400). ALL no-finger stay flat (<400).
Cross-session reference is STABLE - any session's background corrects
any session's finger frame.

## Conclusions (Sol verdict 7 Stage 2 acceptance direction)

"One fixed pipeline, without manual tuning, produces extractable and
repeatably matchable templates... while uncovered frames remain
non-biometric and low-structure."

- Fixed pipeline confirmed: same correction, no per-session tuning
- Cached reference works across sessions/reconnects (fresh capture
  still safer per Sol, but not strictly required)
- No-finger (opaque) stays flat: no false positives
- Finger detection robust: 2400-3700 across all cross-session combos

## Driver state
- fp0081_driver.py: session (reset+init+TLS+authorize 6677B+6f000e/a),
  median reference (n frames), capture (155_TX + 51-polls), correction
  (signed sub + row-mean + clip), presence (ridge-band FFT energy)
- Validated live: 5/5 finger detections across 3 sessions
- Artifacts: /tmp/fp0081-live-test/, /tmp/fp0081-robust-test/

## Remaining (Stage 3-4)
- Stage 3: 96x96 matrix -> 128x64 mapping (experimental, optional path)
- Stage 4: template extraction (minutiae), genuine/impostor eval
