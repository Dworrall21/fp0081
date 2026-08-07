# 🎉 0081 BREAKTHROUGH — fingerprint ridges recovered via flat-field correction (2026-08-06)

## The fix works

The banded raw output CONTAINS the fingerprint. Correction:
  corrected = row_normalize(finger_frame − uncovered_background_frame)

Vision analysis confirms: DIAGONAL ridge flow, curved parallel ridges,
regular spacing — actual fingerprint structure, not noise.

## Two correction methods tested

Method A (background subtraction): finger − same-session uncovered frame,
then row-normalize. BETTER visual quality (cleaner ridges).

Method B (calibration-matrix subtraction): finger − deblocked 0x30 matrix
(padded 64x96→64x128). HIGHER ridge energy (4291 vs 2433) but more
artifacts/banding.

## Quantitative support

- Ridge-band FFT energy: finger 3019 vs uncovered 1499 (2x)
- Finger vs uncovered: mean 131->115, var 2x, col-diff 3.4x
- The sensor + capture path work correctly; output = fixed-pattern
  carrier + fingerprint signal

## What this means

1. The 06cb:0081 sensor produces usable fingerprint data with the
   standard capture frames (017/031) + authorize 6677B + TLS
2. Host-side flat-field correction (subtract background / calibration
   reference, row-normalize) recovers the fingerprint
3. This matches Sol verdict 6's "host-side fixed-pattern correction"
   hypothesis — the driver/Windows subtracts a runtime calibration
   vector after reading the buffer
4. The stable 96x96 calibration matrix (MVWT0-equivalent) is the
   canonical reference for this correction

## Implication for the goal

The fingerprint sensor can produce readable fingerprints natively.
A Linux driver path exists: capture banded raw -> flat-field correct
with the calibration reference -> usable fingerprint image.

## Remaining questions
1. Canonical correction: background-frame vs matrix-based? (matrix =
   session-stable, no per-session bg capture needed)
2. Does the matrix need MEDOID/median across captures, or a fresh
   calibration capture per session (like the driver's CALIBRATE flow)?
3. Is row-normalize + subtract sufficient, or is the full
   process_calibration_results pipeline (scale 10/0x22, signed add)
   the canonical transform?

## Artifacts
- /tmp/0081-optical-test/finger_flatfield.png (VISIBLE RIDGES)
- /tmp/0081-optical-test/finger_matrixcorr.png
- /tmp/0081-optical-test/finger_minus_uncovered.png
- all raw frames hashed in evidence.sha256
