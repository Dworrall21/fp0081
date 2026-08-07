# 0081 CONTROLLED OPTICAL TEST — DEFINITIVE RESULTS (2026-08-06)

## Setup
Real 06cb:0081 sensor (Bus 001 Device 015). Validated commands only:
authorize 6677B, 6f000e/6f000a, 155_TX IDENTIFY frame, 51-polls. NO writes.
4 phases with user-controlled optical conditions.

## Results

Phase | Condition      | frame mean | var   | col-diff | sha
A     | uncovered      | 131.1      | 939   | 4.66     | a419e8b6
B     | covered        | 130.1      | 941   | 4.68     | 7c85e31e
C     | RIDGED FINGER  | 115.4      | 1912  | 16.01    | e4452422
D     | covered2       | 114.9      | 2330  | 16.53    | 7dd84129

## DECISIVE FINDINGS

1. THE SENSOR OPTICAL PATH WORKS. Finger contact changes the image
   materially: mean drops 131->115 (12%), variance doubles (939->1912),
   column-diff 3.4x (4.7->16.0). NOT defective, NOT program-not-executed.

2. The response is a BANDED pattern, not a readable fingerprint.
   Vision analysis (raw + enhanced + row-normalized): horizontal banding
   dominates; no clear ridge flow/minutiae visible. But the finger
   signature IS present in the statistics (structure responds).

3. Phase D (covered again) matched finger-level stats (114.9, var 2330)
   — user likely covered with thumb; repeatable finger response.

4. Re-examined native-capture6: bg AND f1 both have var 2316-2354,
   col-diff 13.5 — consistent with finger-contact captures. My earlier
   "identical bg/f1" conclusion was a measurement artifact (row means
   alone don't discriminate; var + col-diff do).

## INTERPRETATION (hypothesis)

The sensor outputs RAW pre-correction data. The 0x30/0x34 program
coefficients (the stable calibration matrix) must be APPLIED to the
output to produce a fingerprint — the device does NOT auto-apply them,
or applies them only when the calibration is properly stored/active.

The banded pattern = row-gain variation that the calibration matrix
compensates. The finger response is visible in stats but hidden by the
row-gain bands. Correct processing = apply matrix-based row/column
correction (the inverse of the gain pattern).

## This REOPENS Sol's "no host post-processing" claim

Sol verdict 4 said reference implementations return device-corrected
images. Our controlled test shows the 0081 returns BANDED data that
responds to finger. Either:
(a) 0081 differs from 0x199 (host must apply the calibration matrix),
(b) the calibration must be STORED (partition 6) for the device to
   apply it automatically, or
(c) the capture program variant is wrong (we send IDENTIFY-mode; the
   device applies coefficients only for the correct mode).

## Artifacts (hashed)
- /tmp/0081-optical-test/{uncovered,covered,finger,covered2}_{frame,extra}.bin
- /tmp/0081-optical-test/*_enh.png, *_unbanded.png
- script: notes/tls_optical_test_0081.py
