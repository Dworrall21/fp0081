# 0081 gamma + structural analysis complete — native test needed (2026-08-06)

## Gamma (0x43) verified
- 0x43 chunk = `0f000000` + 100B descending gamma curve + 38B trailing
  (74000000 = metadata/signature + TLS MAC)
- Gamma = 0x93,0x92,0x91,0x8f,0x8e,0x89,... descending — same family as
  0x199 (9392918f8e8d8b8a...), 60/100 bytes overlap, 0x195-specific
  ordering. Plausible correct luminance curve.
- The gamma is in the SAME position in CALIBRATE (017) and IDENTIFY
  (031) frames — static per sensor type.

## Everything structurally correct, yet images banded
- Gamma: correct family, present
- Calib matrix: stable, extracted (MVWT0-equivalent)
- Constants: key line 46, fcv[44], deblock verified
- Frames: driver-built, replay reproduces byte-for-byte
- Finger detect: WORKS (51-polls return 01)
- Images: banded, non-optical, identical with/without finger

## Remaining hypotheses (in order)
1. 0x30 register-write program (0x85 registers) not executing on-device
   — the sensor runs unconfigured -> banded output
2. Device needs calibration STORED (partition 6) for capture to apply it
3. Hardware/sensor optical path issue (finger detect works via separate
   mechanism; optical capture path broken/defective)
4. Wrong capture variant (this 0x02 frame is identify-mode; image mode
   needs different program)

## Next: native controlled optical test (needs device + consent)
Per Sol verdict 4: covered sensor, uncovered sensor, finger contact.
A real optical frame must change materially. If invariant banding ->
program-not-executed or hardware. This is the decisive discriminator
between "program not applied" and "sensor defective".

Requires: device access (USB), TLS authorize (6677B), 6f000e, 017/031
frames — all already working natively. The test sends the SAME frames
we've validated. No new commands, no writes.
