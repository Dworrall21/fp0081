# 0081 FINAL — calibration problem SOLVED (proof-of-concept) (2026-08-06)

## Sol verdict 7 (request 997bf68d, sha 7ddbceac)

"YES: 0081 produces a recoverable, potentially usable fingerprint."
Solved at signal-recovery/POC level. Not yet production-canonical.

## Canonical correction (Sol-approved pipeline)
1. Capture 4-16 uncovered frames (same mode/profile as finger capture)
2. Per-pixel MEDIAN reference (not single frame)
3. Signed subtraction: D = int16(F) - int16(B)
4. Robust row-bias removal: D' = D - median_x(D) (median, not mean)
5. Robust contrast map: I = clip(128 + s*D', 0, 255), s from percentiles
6. Segmentation + ridge enhancement (Gabor/STFT) -> template extraction

## Key decisions
- Method A (same-session background subtraction) = CANONICAL
- Method B (96x96 matrix) = experimental/fallback until mapping proven;
  its higher FFT energy is artifact-inflated, not better quality
- Do NOT apply process_calibration_results to image (calibration-payload
  generation; would double-subtract 0x80; 8-byte/line preserve breaks
  128x64 continuity)
- Row MEDIAN > row MEAN (mean removes legitimate low-freq contrast)
- 017 CALIBRATE reference = only after pixel-equivalence proof; safest
  is same-mode uncovered frames (155/031 path)
- Finger-detect polls (01 always) UNUSABLE for presence -> image-derived
  detector needed (corrected variance, coherence, ridge-band excess)
- Reference refresh: after reconnect, resume, drift, quality degradation

## Production roadmap
Stage 1: freeze POC path (median bg, signed sub, robust row corr,
  reproducible contrast/polarity, diagnostics)
Stage 2: validate robustness (native-capture6 + new sessions spanning
  reconnects/reboots/thermal)
Stage 3: resolve matrix 96x96->128x64 mapping (experimental fit on
  held-out frames; reject if no generalizable mapping)
Stage 4: qualify biometrics (DPI, minutiae repeatability, genuine/
  impostor separation, image-derived presence, retries, secure cleanup)

## Acceptance criterion
One fixed pipeline, no manual tuning, produces extractable repeatably
matchable templates across sessions while uncovered frames stay
non-biometric and low-structure.

## Milestones achieved this session
- MVWT0 donor hypothesis DEAD (Sol verdict 2)
- CALIBRATE signature corrected (017 = 1200B, req_lines=0, empty 0x34/0x30)
- 0x195 constants recovered (key_calibration_line 44, key line row 46,
  fcv[44]=0x80, deblock verified)
- Wine replay reproduces driver frames byte-for-byte
- Controlled optical test: sensor works, finger-responsive
- Stage 0-3: layout, frames, 0x4e all tested/closed
- BREAKTHROUGH: ridges recovered via flat-field correction
  (finger_flatfield.png: diagonal ridge flow, curved parallel ridges)
- Control test: opaque cover stays flat (ridge 192/var 5) vs finger
  (ridge 2434/var 934) and thumb (2653/1139) — robust discriminator

## Evidence (all in work/calibration-re/evidence.sha256)
30+ docs + 25+ artifacts. Full chain: handoff -> MVWT0 -> host-side
calibration -> constants -> replay -> optical test -> breakthrough.
