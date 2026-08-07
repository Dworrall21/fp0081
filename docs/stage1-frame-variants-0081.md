# 0081 Stage 1 results — frame variants identical, TLS expired trial 6 (2026-08-06)

## Setup
3 IDENTIFY frame variants tested natively (read-only, validated cmds):
f031 (cycle 1), f155 (cycle 4), f187 (medoid). Randomized order,
uncovered + ridged finger conditions.

## Results

Frame | uncovered mean/var/col-d | finger mean/var/col-d
f031  | 131.8/931/4.62           | 114.0/3168/16.19
f155  | 131.2/942/4.69           | 113.0/2882/17.65
f187  | 131.1/944/4.70           | (TLS expired mid-trial)

## Finding
ALL frame variants behave IDENTICALLY. Finger response (mean 131->114,
var 2-3x, col-d 4.7->16-17) is consistent across frames; banded output
persists with every variant.

=> Rules out "wrong IDENTIFY frame variant" (Sol Stage 1 hypothesis).
The capture program choice is not the discriminator.

## Note
Trial 6 (f187 + finger) failed: "Unexpected TLS version 4 0" — the
TLS session expired after ~2.3 hours of device interaction. The
optical-test + stage-1 sessions ran long; the device/session timed out.
This is a session-lifetime limitation, not a protocol error.

## Implication (per Sol verdict 5)
Remaining leading hypothesis: DEVICE-SIDE correction incomplete —
partition 6 clean-slate missing (strongest state suspect). The 0x199
reference stores a blank calibration image in partition 6 for
"fine-grained after-capture adjustments" — exactly the fixed-pattern
row correction our banded output lacks.

Stage 2 (ENROLL frame): not executable — we only have driver-built
IDENTIFY frames (017/031/155/187); no complete ENROLL capture frame
was observed in the pt6 flow.

Stage 3 (partition-6 write): conditional + last. Needs 0x195 format
proof, partition backup, known success response, recovery plan, and
explicit user consent.

## Artifacts
- /tmp/0081-stage1/t{0-4}_*.bin (hashed into evidence.sha256)
