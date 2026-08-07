# Sol/High verdict — 0081 host-side calibration hypothesis (2026-08-06)

Request 9b03a769-3b34-4d2a-916a-050f1df5dd25, GPT-5.6 Sol High, COMPLETED.
result_sha256 fbd62d3a51e7b2889532a00c447baae02441da5caabc3f4caa0d44eaff98b3de.
Full text in bridge registry (requests.result_text).

## Verdict

Host-side 0x02 calibration-loop hypothesis is HIGHLY APPLICABLE to
06cb:0081 and is now the LEADING recovery path. Evidence substantially
weakens the MVWT0-donor theory; no evidence MVWT0 (3168B type-06/storage-03)
is a prerequisite for this sensor.

## Established for 0x0195

- sensor_type = 0x0195 (identity response)
- factory calibration source: 6f000e subtag=3, 116B factory_calibration_values
- command family: 0x02 framing, compatible capture-program structure
- wire bytes_per_line = 0x0068 (104) — from every recorded 0081 0x02 header
- full capture program: 10603B merged body after 5-byte header
  (mode-specific, likely already contains injected calibration material —
  DO NOT reuse as build_cmd_02 input; double-patching risk)
- short program: 1195B body — valuable base/setup candidate, but req_lines=0
  means NOT a Calibrate transaction
- final image: 8198B = 8192 image (128x64) + 6 framing
- MVWT0: unsupported by current evidence, unnecessary in sibling architecture

## Critical correction (Sol)

The two 1200B frames are NOT Calibrate commands under reference framing:
header `02 68 00 00 00` = cmd 0x02, bytes_per_line 104, req_lines 0.
Calibrate requires req_lines = calibration_frames × lines_per_frame + 1
(nonzero): 009a = 3×224+1 = 673 (a1 02); 0081 candidates 673 or 337 (51 01).
req_lines=0 frames = setup/identify-mode program loads only.

## Parameters still required

1. key_calibration_line (0x38 plausible for sibling; NOT safe to assume)
2. base capture/calibration program (untouched DLL-generated buffer)
3. calibration dimensions: lines_per_calibration_data, lines_per_frame,
   interleave count/ordering, raw/cooked payload lengths
4. local calibration-data format: process_calibration_results output size,
   signed/unsigned, averaging width, saturation, key-line source, where
   patch_timeslot_again applies

## Safest acquisition path (ordered)

1. STATIC: recover 0x0195 table in 2018 + 2022 DLLs side by side —
   scsCommands 0x02 builders, PAL 0x938AE004-070, 5-byte header arithmetic
   (nonzero req_lines), 0x0195 program ptr/len, key-line const, stride,
   line counts, frame count, interleave. Check MVWT0/storage-03 reachability
   (negative = strong evidence against MVWT0). Compare 0x194/0x199/0x00ed
   entries in generated_tables.py.
2. USB-free WINE REPLAY (original DLL, strict shim, no USB backend):
   recorded 0x0195 identity, exact known TLS/post-TLS responses, constant
   6677B authorize, exact 1594B 6f000e response, whitelist commands,
   terminate on unknown. DECISIVE ARTIFACT: DLL-emitted 0x02 with
   bytes_per_line=0x68 AND nonzero req_lines + mode-specific chunk changes.
   Test BOTH driver generations.
3. RECONSTRUCT command builder offline (split/merge, line_update_type_1,
   preserve Windows arithmetic + timeslot terminal-triplet behavior).
   Generate expected Calibrate/Identify frames without device.
4. VALIDATE calibration processing offline (edge vectors: all-zero,
   all-0xff, alternating lines, max sums, last timeslot triplet ± trailing).
5. ONE bounded native session ONLY after replay+builder agree: 3-pass
   calibrate, store local, one calibrated Identify/capture. No MVWT0 unless
   static evidence proves it belongs to 0x0195 path.

## Status semantics (Calibrate classification)

Accepted / Rejected / Unsupported / Inconclusive. 0xD7/0x74 remain opaque
non-success until mapped independently. ACK without async payload != accept;
timeout != unsupported (can be wrong req_lines/program/poll).

## Stop conditions (binding)

Static/replay stop: no defensible 0x0195 param path; 2018 vs 2022 disagree
materially; unknown DLL command; replay requests real USB; authorize !=
6677B const; progress needs DLL patch/branch force/fabricated success;
length overflow or req_lines×bytes_per_line mismatch; status mapped only
by assuming 0xD7/0x74 success.
Native stop: unexpected outbound cmd; header != replay-verified frame;
non-success/unknown status; wrong response length; missing/short/excess
async; poll outside verified state machine; calibration passes disagree
beyond tolerance; wrong processed length; MVWT0 request not statically
proven; any need to alter auth/force branch/continue after ambiguity.

## Net effect

Retire MVWT0 as default recovery assumption. Focus: recover 0x0195 host
calibration parameters. Decisive next artifact = USB-free DLL-generated
0x02 frame with nonzero req_lines. Until it exists, do not guess native
Calibrate transaction.
