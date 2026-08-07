# 0081 calibration — CRITICAL NEGATIVE RESULT (2026-08-06)

## The striped-image puzzle

EVERY captured image from the 06cb:0081 sensor is striped/banded noise:
- Native captures with driver-built IDENTIFY frame (155_TX/031): striped
- pt6 flow images (42, 74, 134, 166): striped
- bg + finger captures all identical pattern (row means 64-221, no
  fingerprint structure)
- vision_analyze confirms: horizontal bands, no ridge flow, no minutiae

The 0x30 calib matrix in the IDENTIFY frames does NOT fix it. The
matrix exists (96x96, 9216B), the frame is structurally valid (10608B,
validated chunks), yet the resulting image is striped.

## What we know works vs not

WORKS:
- TLS + authorize (6677B const)
- 6f000e factory bits (TLV, subtag=3, 116B factory_calibration_values)
- CALIBRATE frame (017) accepted, raw frames returned (8240B)
- IDENTIFY frame (031) accepted, image frames returned (8240B)
- All 51-polls, geometry (0x60006000), status frames
- Wine replay: driver calibrates with "Loaded 0 bytes", rc=0, 3x
  CALIBRATE_DEVICE, SetNamedValue CalibrationData=65 (status int)

DOES NOT WORK:
- Image content: always striped, never a fingerprint
- The 0x30 matrix in 031 doesn't produce good images

## Hypotheses for striped images

1. The matrix is correct but the IMAGE CAPTURE needs the key_line
   substitution applied at capture time (the driver computes key_line
   from calib_data and patches the frame per-capture; our replayed
   031 lacks the dynamic key_line patch).
2. The raw sensor needs a DIFFERENT capture program (the 0x30/0x34
   we have are from an INCOMPLETE calibration — "Loaded 0 bytes" means
   the driver computed a default/zero-based matrix).
3. The striped pattern is a sensor hardware state (device needs a
   different init sequence before capture).
4. The image IS being captured correctly but the RENDERING is wrong
   (e.g. image needs column reordering / de-interleaving / transpose).
5. The 0x30 matrix requires the raw calibration captures (read_82
   bulk-in) which we never recorded — the matrix in 031 was computed
   from the driver's own state, possibly default.

## Key evidence tension

- Driver "Loaded 0 bytes of calibration data" -> computed SOMETHING ->
  SetNamedValue CalibrationData=65 (just status!) -> matrix in 031
- The matrix in 031 differs per cycle (42-44%) = NOT a static default
- But images are striped in ALL cases -> matrix present but ineffective

## Questions for Sol

1. Why do images stay striped despite a valid calib matrix in the frame?
2. Is the 0x30 matrix in 031 the COMPLETE calibration, or is the
   per-capture key_line patch (dynamic) also required?
3. Is the striped pattern possibly a RENDERING issue (column
   reorder/de-interleave needed for 128x64 from 96x96 calib)?
4. Does the capture require the bulk-in read_82 (never recorded) for
   the calibration to take effect?
5. What is the minimal next experiment: replay with key_line patch
   breakpoint? render-rotate test? bulk-in capture?
