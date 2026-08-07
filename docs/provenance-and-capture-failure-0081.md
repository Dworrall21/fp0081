# 0081 PROVENANCE + CAPTURE-CONTRACT FAILURE PROOF (2026-08-06)

## 8192B buffer provenance — RESOLVED

- Both native (real device) and pt6 (replay) capture paths produce the
  same envelope: `00 00 | 00 20 00 00 | [8192B data]`
  (status=0, u32 len=8192, then payload)
- native: 6B hdr + 8192 = 8198B total
- pt6: 8B hdr (2 extra bytes = per-capture marker) + 8192 = 8240B total
- Same command (51 00200000 poll) produces it; payload = live data
  (changes 85-86% per cycle)
- => The 8192B region IS the image payload (128x64)

## DECISIVE: capture-program contract failure (real-device proof)

Native session (tls_capture6_0081.py, REAL sensor):
- bg (no finger) vs f1/f2/f3 (finger HELD): nearly identical stats
  row means 64-216, col means 111-124, variance ~1590
- A real fingerprint MUST change the image dramatically. It doesn't.
- Finger DETECTION works: 51 00000000 polls return `01 00000000`
  (finger present) every cycle, then `00` (released)
- But image output is identical banded pattern with/without finger

CONCLUSION: the sensor detects fingers but the captured image does not
respond to optical input. The 0x02 capture program (or its variant/
mode) is NOT producing valid optical output. This is a capture-program
contract failure, not a calibration-data problem.

## Implication

- The calibration matrix (extracted, stable, MVWT0-equivalent) is
  likely CORRECT — but the capture program that USES it is wrong
- The frame we send (017/031) may be the CALIBRATE/IDENTIFY variant,
  not the IMAGE-capture variant
- The 0x2e chunk (image recon params) or the capture mode byte may
  need a different value for image mode vs identify mode
- Or the device needs a different command sequence to enter image
  capture (vs identify/template matching)

## Next hypotheses

1. Wrong capture variant: the 031 frame = IDENTIFY mode; image capture
   may need ENROLL mode or a distinct program (0x2e byte 08 vs 23?)
2. The image may require the CAPTURE command (not IDENTIFY) — maybe a
   separate 0x02 mode or different poll sequence
3. The device may need an explicit "start capture" after detect that
   differs from what we send
4. Sensor hardware may genuinely be defective (finger detect works via
   a different mechanism than optical capture)
