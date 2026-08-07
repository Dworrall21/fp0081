# 0081 Stage 3 — matrix mapping REJECTED (2026-08-06)

## Sol verdict 7 Stage 3 directive
"Resolve the matrix: exhaustively test defensible geometric/channel
mappings. Compare on held-out empty frames and matching performance,
not FFT energy alone. Reject direct subtraction if no cross-session
mapping generalizes."

## Tests executed (deblocked 96x96 matrix vs 128x64 images)

1. Row mapping: image rows vs matrix rows, offsets 0-32 -> max corr 0.069
   (noise). REJECT.
2. Full transforms: identity/transpose/flipLR/flipUD/flipboth ->
   |corr| < 0.05 all. REJECT.
3. Resampling: upsample image 64->96, downsample M 96->64, cols 128->96
   -> |corr| < 0.03. REJECT.
4. Signatures: M-rowmeans vs img-rowmeans 0.04; M-colmeans vs
   img-colmeans 0.42 (moderate but not a mapping); M-colmeans vs
   img-rowmeans 0.03; inverse -0.32. REJECT.
5. Column-strip: M colmeans lag-4 autocorr 0.439 (strip structure
   present) vs img colmeans lag-4 -0.025 (no strip structure in image).
   Structurally different. REJECT.
6. Matching performance: matrix-as-column-gain corrections give finger
   ~3050 vs covered ~1545 (sep 1510) vs background subtraction finger
   2434 vs covered 192 (sep 2242). Matrix inflates no-finger frames
   toward false-positive territory. REJECT on matching performance.

## Conclusion

The 96x96 matrix is a CALIBRATION-GENERATION COEFFICIENT OBJECT (used
to build the 0x30 line-update program), NOT a pixel-level background
image for the 128x64 capture. No geometric/channel mapping exists.

Background subtraction (Method A) remains the canonical correction:
separation 2242 vs matrix 1510.

## Practical implication for the driver
- fp0081_driver.py uses same-session/cached background subtraction
  (canonical, validated) - correct
- The 96x96 matrix remains useful only for REPRODUCING the driver's
  frame construction (0x30/0x34), not for image correction
- Stored-matrix path: REJECTED (no generalizable mapping)

## Artifacts
- stage2-robustness-0081.md (99 evidence entries total)
- fp0081_driver.py (canonical pipeline)
