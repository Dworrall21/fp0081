# 0081 Phase C — Sol verdict 4 + offline tests (2026-08-06)

## Sol verdict 4 (request 0f10ee64, sha 51902859)

KEY INSIGHT: 0x2f (47) and 0xd1 (209) are symmetric around 0x80:
0x2f = 0x80-0x51, 0xd1 = 0x80+0x51. Signed/bias-centered coefficients,
NOT ordinary luminance. (NOTE: this analysis was on the MATRIX, which
dominates in these values — the image does NOT actually have long runs.)

Verdicts:
- Stable matrix = runtime calibration-program component, "logical
  MVWT0-equivalent coefficient field", but NOT proven to be the
  partition-6 persistent record. DO NOT write naked matrix to partition 6.
- GetNamedValue "Loaded 0 bytes" does NOT contradict stable matrix —
  named-value store = host cache; driver constructs runtime program
  from stable sensor/factory inputs. Flash persistence NOT a prerequisite.
- Striped 8192B output is UNLIKELY to be raw image needing host-side
  correction (reference implementations return device image without
  matrix-based correction). scale() is calibration-generation, not
  image correction.
- Leading fault class: CAPTURE/PROGRAM CONTRACT FAILURE (wrong stream/
  mode, program staged but not executed, internal program overrides,
  wrong coefficient layout/capture variant).
- Phase B proves HOST-SIDE determinism, NOT device-side correctness.

## Sol's experiment order
1. Resolve provenance/format offline (which cmd/endpoint produced 8240B?
   is 8192B the image payload? named-value contents?)
2. Exact n-gram test: image vs program components
3. Validate normal capture pipeline (reference implementation oracle)
4. Prove program consumption/execution (status/readback, not just ack)
5. Firmware-override cases (inline vs staged vs partition vs wrong variant)
6. Partition-6 write ONLY after: format proof, full backup, readback,
   rollback plan, explicit consent. Use a real cycle's MEDOID, not median.

## Offline test results (executed)

Test #2 (n-gram): image vs serialized 0x30 = 0B match; vs keyline = 0B;
vs timeslot = 5B (zeros, coincidence); vs gamma = 4B (coincidence).
=> NO program-buffer leakage. Image is its own data.

Test #3 (cross-cycle): images change 85-86% per cycle (live sensor data,
not stale buffer); programs change 42-44% (mostly +/-1 noise, matrix
stable). Images respond to live captures but always banded.
=> Consistent with program staged-but-not-executed OR wrong capture
variant OR inherent playback banding.

## Remaining decisive evidence needed
- Provenance of 8192B buffer (which command produces it)
- Reference 0081 capture flow (python-validity/Rust oracle for 0x195)
- Program execution proof (status/readback, register changes)
- Controlled optical challenges (covered/uncovered/finger) native test
- Partition-6 A/B only after format+backup+consent

## Artifacts
- master-calib-matrix-96x96.bin (9216B, sha 64bd4ed6) — the MVWT0-equiv
  coefficient field (MEDOID version still to build from cycle data)
- All offline tests recorded in evidence.sha256
