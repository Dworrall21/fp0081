# 0081 Phase B COMPLETE — replay reproduces driver frames byte-for-byte (2026-08-06)

## Decisive result

Wine replay (usb-pt6 script, unmodified 2018 DLL) with the harness's
TLS plaintext capture extracted **6 driver-built 10608B IDENTIFY frames**:

  replay [0] sha b4a8069f24fc == 031_TX sha b4a8069f24fc  (BYTE-IDENTICAL)
  replay [1] sha 451432adcded == pt6 frame 63
  replay [2] sha 9b6fe96d986d == pt6 frame 123
  replay [3] sha 3fde9abf263b == pt6 frame 155
  replay [4] sha b846364bbc60 == pt6 frame 187
  replay [5] sha 6e82872baca6 == pt6 frame 219

The driver under replay computes the SAME per-cycle 0x30/0x34 as the
original pt6 capture. The calibration transform is DETERMINISTIC:
raw input (8240B 51-poll frames) -> driver -> IDENTIFY frame.

Phase B pass criterion (Sol): "final buffers exactly explain captured
031_TX.bin" — MET.

## Also confirmed

- No endpoint-0x82 (bulk-in) in the replay script: 0081 uses 51-polls
  exclusively for calibration data (NOT the python-validity read_82 model)
- Replay frames carry the full calib: 0x30 (9428B) + 0x34 (648B),
  key line = matrix row 46 (frame 0 exact, others 95/96 live)
- Matrix values dominant: 47 (0x2f) and 209 — 0x2f is the stripe value
  seen in images (matrix encodes the stripe pattern!)
- Matrix rows correlate with raw rows: matrix_row 29 ~ raw_row 31 (M
  crop) corr 0.950; several rows 0.82-0.95 — transform exists, mapping
  not 1:1 (row reordering/offset)

## Key insight (stripes)

The matrix's dominant value 47 = 0x2f = the same value dominating the
striped images. The matrix ENCODES the stripe pattern — meaning the
calibration captured the sensor's striped response and the "calibration"
normalizes around it. The stripes in images may be the CORRECT raw
sensor output that needs a DIFFERENT processing (the driver's
process_calibration_results: 0x80 subtract, scale, signed add) applied
at display time.

## Open

1. Full raw->matrix row mapping (corr up to 0.95, need exact mapping)
2. Whether images need post-processing (0x80-subtract/scale/signed-add)
   rather than being raw-correct
3. Native test to validate (single bounded session)

## Artifacts
- replay-identify-{0..5}.bin saved (driver-built frames from replay)
- evidence hashed: phaseA-constants-recovered-0081.md (cdb67b3d)
