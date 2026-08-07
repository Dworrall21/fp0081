# 0081 Stage 3 result — 0x4e hybrid frame REJECTED by device (2026-08-06)

## Test (Sol verdict 6: exact 0x4e-only A/B/A)
- A1: 031 baseline, uncovered -> 8198B image, mean 131.8 (normal)
- A2: 031 baseline, finger -> 8198B image, mean 116.8 (normal, finger-responsive)
- B1: 031 + reference IDENTIFY 0x4e chunk (hybrid), uncovered ->
  **6-byte error response, NO image** (division by zero in stats)

## Result
The device REJECTED the 0x4e-augmented frame. Per Sol verdict 6
interpretation: "Rejected command: the exact blob is incompatible with
0081 or with its current state."

## Conclusions
1. Reference 0x4e chunk = 0x199-specific, INCOMPATIBLE with 0x195/0081.
   Not a reconstruction-enable switch for this device.
2. Missing 0x4e does NOT explain banding (device rejects it entirely;
   no partial effect to observe).
3. 0081 frame format is genuinely its own (0x08 profile, no 0x4e/0x26).
   The driver-built frames (017/031/155/187) are the correct and only
   valid capture frames.
4. Frame-construction hypothesis CLOSED. All native frame variants
   produce the same banded-but-finger-responsive output.

## What remains (per Sol verdict 6 decision sequence)
- Step 3 of Sol's sequence: "If unchanged, stop modifying capture fields
  and treat the 0x4e hypothesis as not sufficient." -> DONE.
- Next: "Feed or trace the authentic banded raw through the same
  downstream extraction path used by Windows, or intercept the buffer
  immediately before that boundary." -> The banded raw may be the
  EXPECTED pre-template representation that Windows feeds to template
  extraction (WBF never displays it). The "Windows gets good images"
  premise is UNPROVEN — WBF may successfully match on the banded raw.
- Also: "Test calibration subtraction and row/lane normalization
  against actual CALIBRATE data — not generic contrast enhancement."
- Also: "Analyze the 0x2e constructor and obtain an authentic 0081
  ENROLL frame before assigning names to 0x08."

## Artifacts
- /tmp/0081-stage3-4e/A1_base_uncovered.bin, A2_base_finger.bin (8198B)
- /tmp/0081-stage3-4e/B1_hyb_uncovered.bin (6B error response)
- script: notes/tls_stage3_4e_0081.py
