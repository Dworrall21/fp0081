# 0081 Sol verdict 5 + Stage 0 layout results (2026-08-06)

## Sol verdict 5 (request 4b8b42ac, sha 20ca3d09)

1. Sensor + capture program FUNCTION (optical test decisive)
2. Leading hypothesis: incomplete device-side correction:
   - partition-6 missing clean-slate calibration (strongest state suspect)
   - capture-program/mode mismatch (safest to test first, read-only)
3. Host layout/deinterleave error = credible second hypothesis
4. Host-side matrix subtraction / missing gamma = UNLIKELY (reference
   paths have no post-capture pixel correction; 0x43 is "Line Update
   Transform" for the device, not a host LUT)
5. Confidence ranking: device-side correction absent (partition 6 or
   mode) > unrecognized stride/ROI > wrong 96->128 coeff mapping >
   host applies 0x30 > missing gamma

## Stage 0 (offline layout) results — EXECUTED

Layouts tested: 128x64, 64x128, 96-wide crop, 104x78, row-even-odd.
Metric (finger): col-diff 16.0, row-diff 47.2, rowMV 528, colMV 9.6.
Uncovered: col-diff 4.7, row-diff 27.3, rowMV 389, colMV 1.6.

FINDING: row-mean variance (rowMV) dominates colMV in ALL layouts;
banding survives every transform. Finger-vs-uncovered discriminator
(col-diff 16 vs 4.7) persists. => NOT a host layout/stide error.
Points to device-side row fixed-pattern (row timing/ADC or missing
blank-frame subtraction).

## Next per Sol
- Stage 1 (read-only): repeat 155, test 031 cycle-1, medoid if complete
  frame; randomized trials; compare band power + finger separation
- Stage 2 (read-only): full ENROLL frame (not byte patch) if available
- Stage 3 (partition-6 write): LAST — only after 0x195 format proof,
  partition backup, known success response, recovery plan, explicit
  consent. Format from 0x199 reference: u16 0x5002 + u16 len + sha256
  (32B) + pad (32B) + payload[u16 raw_blank_len + blank image + u16 0],
  0x44B header. NOT format proof for 0x195.

## Artifacts
- optical-test-results-0081.md (sha in evidence.sha256)
- /tmp/0081-optical-test/*.bin + PNGs
