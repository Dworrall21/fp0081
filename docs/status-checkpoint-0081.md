# 0081 calibration — status checkpoint (2026-08-06, end of round)

## What is definitively established (evidence-backed)

1. **MVWT0 donor NOT needed.** Sol verdict 2 (8187e540, sha 41349aa7):
   corrected CALIBRATE signature = 02 68 00 00 00 + empty 0x34/0x30 +
   1200B total. 017_TX.bin IS the decisive CALIBRATE artifact.

2. **Calibration is host-side computed, per-cycle.** 6 paired cycles in
   pt6 flow; IDENTIFY frames differ 42-44% in the 0x30 calib matrix per
   cycle; CALIBRATE frames identical. Provenance test: filled 0x30/0x34
   NOT present in 2018 or 2022 DLL (only static gamma 0x43 tail matches)
   -> computed, not static.

3. **Wine replay proves driver calibrates with NO stored calib:**
   "GetNamedValue CalibrationData" -> "Loaded 0 bytes of calibration
   data" -> proceeds -> OnPrepareHardware rc=0, deviceCalibrate fires
   twice, image data flows. USB frames TLS-encrypted (17 03 03).

4. **0x30 chunk format decoded** (python-validity line_update):
   u32 count(26) + 26x8B(mask,flags) + 9216B data = 96x96 matrix.
   2 records mask=0xff (calibration_blob gamma + factory), 24 records
   mask=0xffffffff flags=0x85000000+4n (register write addresses).

5. **0x0195 params**: bpl=104, line_width=96, lines_2d=96, sensor 0x195.

6. **Raw capture structure**: 8240B = 48B envelope (status+len u32) +
   8192B (128x64). Extra frame 1072B = 8B hdr + 1020B data (len field
   says 1020; 0x0d padding). 8+ raw + 12 extra frames captured.

## Geometry blocker (Sol #1) — RESOLVED partially

calib matrix = 96x96 = 9216B. raw = 128x64 = 8192B. Transform
raw->matrix NOT yet matched (crop/interleave tests failed correlation).
2*96*48 = 9216 exactly = interesting but unproven.
8192+1020 = 9212, +4 = 9216 (4-byte gap unexplained).

## Remaining work

1. Resolve raw(8192)+extra(1020) -> matrix(9216) transform.
   Options: (a) interleave hypothesis 2x96x48; (b) Wine replay with
   breakpoint at scale/average function in 2018 DLL (0x180093FC8 area
   = handle_avg from 0097 table, need 0081 equivalent); (c) 2022 DLL
   PAL 0x938AE004 chain (0x18003EB4B).
2. key_calibration_line for 0x195 (0x38 candidate unproven).
3. scaling factor for 0x195 (0x199 uses 10/0x22, device-dependent).
4. Build candidate IDENTIFY (replace 0x30/0x34 only) + offline validate.

## Artifacts (all hashed in work/calibration-re/evidence.sha256)

- work/calibration-re/artifacts/ (raw captures, frames, chunks)
- work/calibration-re/reconstruct_0081_calib.py (pipeline skeleton)
- work/calibration-re/static/native-calib-flow-decoded-0081.md
- work/calibration-re/static/sol-verdict2-calib-signature-0081.md
- /tmp/calib-replay1-typescript (Wine replay log)
