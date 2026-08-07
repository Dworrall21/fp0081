# 0081 native calibration flow — DECODED (2026-08-06)

## Discovery: the pt6 native flow IS the complete calibration dataset

The native capture (tls_capture6_0081.py, real sensor) records 8+ full
capture cycles. Each cycle (frames 17-44, 49-76, ...):

```
6f000e (factory bits) -> 1632B TLV (calib_6f0e = factory_calibration_values)
6f000a -> ack
0x02 CAPTURE 1200B  (CALIBRATE: 0x34 zeros, 0x30 stub) -> 2272B
poll 51 00000000 x3 -> 48B each
poll 51 10000000    -> 64B  (image recon params, 0x60006000 = 96x96)
poll 51 00200000    -> 8240B RAW CAPTURE FRAME
poll 51 fc030000    -> 1072B
0x02 CAPTURE 10608B (IDENTIFY: 0x34 filled, 0x30 full) -> 2272B
polls -> image
```

## Frame structure (chunk format = same as python-validity/Rust)

- 5-byte header: cmd=0x02, bytes_per_line=0x0068 (104), req_lines=0x0000
- CALIBRATE (017): chunks 0x23,0x20,0x32,0x33,0x32,0x32, 0x34=648B ZEROS,
  0x2f(96),0x29,0x35,0x17,0x2e(28B),0x44, 0x30=20B stub, 0x43(164B gamma)
- IDENTIFY (031): same except 0x34=648B patched timeslot, 0x30=9428B
  (register-write program, 0x85 base addresses + 0xffffffff values)

Diff between CALIBRATE and IDENTIFY = EXACTLY 2 chunks change:
- 0x34: all-zeros -> patched timeslot table (key_line + line data)
- 0x30: 20B stub -> 9428B full line program

Everything else identical (0x2e image recon 28B, 0x43 gamma 164B, 0x44).

## CRITICAL: correction to Sol verdict (9b03a769)

Sol's "decisive artifact" was a DLL-emitted 0x02 with NONZERO req_lines.
The REAL 0081 driver emits req_lines=0x0000 for BOTH Calibrate and
Identify. The mode is expressed via chunk CONTENT (0x34/0x30 empty vs
filled), not the header req_lines field. The req_lines=nonzero formula
comes from the python-validity/Rust port (CALIBRATE -> frames*lines+1)
which does NOT match this driver's behavior.

Implication: Sol's stop-condition "no exact 0x0195 param path" and the
"nonzero req_lines" acceptance criterion must be revised. The Calibrate
frame ALREADY EXISTS in our native captures (017_TX.bin, 1200B).

## Raw calibration capture frames (8240B = 48B hdr + 8192B data)

Sparse (background, 90.5% nonzero, zeros at start):
  28 (head 03060100...), 60 (070a00...), 120 (020400...), 152 (020600...)
Dense (finger present, 99.8% nonzero, full pixel data 0x30-0x5f):
  42 (96979381...), 74 (8f939584...), 134 (96959081...), 166 (94968e80...)

This is the background/finger pair pattern expected by average_interleaved.

## Artifacts (work/calibration-re/artifacts/, all sha256-hashed)

raw-capture-{28,42,60,74,120,134,152,166}.bin  (8240B each)
calibrate-cmd-017.bin   (1200B, CALIBRATE frame)
identify-cmd-031.bin    (10608B, IDENTIFY frame w/ calib)
status-26.bin (64B), status-30.bin (1072B)
calib-0x30-lines.bin (9428B), calib-0x34-timeslot.bin (648B)
calib-0x2e-recon.bin (28B), calib-0x43-gamma.bin (164B)

## Parameters established for 0x0195

- bytes_per_line = 104 (0x68), line_width = 96 (0x60), lines_2d = 96
- factory_calibration_values: 6f000e subtag=3, 116B
- capture program: static blobs in 2018 DLL .rdata (0x1bdaa0 et al.),
  chunk structure matches 0x199/FM-3367 family with 0x70 geometry byte
- CALIBRATE frame = 017 (empty 0x34/0x30), IDENTIFY = 031 (filled)
- 0x30 = line program (reg writes), 0x34 = patched timeslot table
- mode byte in 0x2e chunk: 0x08 (identify) per notes.txt 0x451 diff
  (enroll=0x23, ident=0x02 for 0x00db; 0081 variant 0x08)

## Open questions

1. Is 031's calib (0x30/0x34) derived from THIS device's raw frames, or
   loaded from a stored/static source? (provenance: 155_TX pre-existed in
   pt6-flow; script replays it)
2. Where does key_calibration_line sit for 0x195 (0x38 candidate)?
3. Does 017->raw->031 processing happen driver-side (needs Wine replay
   with calib breakpoints) or can we replicate offline (python-validity
   average_interleaved)?

## UPDATE: Wine replay confirms host-side calibration (2026-08-06)

Ran 2018 driver under USB-free Wine replay (usb-pt6 script):
- OnPrepareHardware rc = 0
- deviceInit fires -> deviceCalibrate fires TWICE
- CalibrationData loader: "GetNamedValue CalibrationData" -> "Loaded 0 bytes
  of calibration data" (partition 6 EMPTY, no donor)
- Driver proceeds: 6f000e factory fetch -> capture flow -> image data
- All USB frames TLS-encrypted (17 03 03 records); plaintext = pt6-flow files

CONCLUSION: driver runs calibration with NO stored calib and succeeds.
Calibration is host-side computed from live captures. MVWT0 donor
definitively NOT required. Matches Sol verdict 2.
