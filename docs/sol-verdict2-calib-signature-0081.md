# Sol verdict 2 — CALIBRATE signature corrected, offline reconstruction path (2026-08-06)

Request 8187e540-0a22-4f9d-98ec-37b642b26ce7, GPT-5.6 Sol High, COMPLETED.
result_sha256 41349aa7b8718dfa12721a2a9036ae49d38be4bb0b80f0f813f1feb216593a09.
Full text in bridge registry (requests.result_text).

## Corrected CALIBRATE signature (replaces req_lines!=0 criterion)

is_0081_calibrate =
    cmd == 0x02 and bytes_per_line == 104 and req_lines == 0
    and packet_length == 1200
    and chunk_order == canonical_0195_order
    and chunk_0x34.length == 648 and chunk_0x34.payload == all_zero
    and chunk_0x30.length == 20 and chunk_0x30.payload == known_stub
    and every_other_chunk == canonical_017_value

017_TX.bin (1200B) IS the decisive native CALIBRATE artifact. MVWT0
donor hypothesis displaced as the gating requirement.

## Structural identity (exact)

CALIBRATE 1200B, IDENTIFY 10608B, diff 9408B = 0x30 expansion
(9428 - 20 = 9408). 0x34 stays 648B (zeros -> filled). All else identical.

## Provenance of filled 031/155

UNRESOLVED. 155_TX was pre-existing replay input in pt6 — loaded, not
computed from that run's raws. Could be: driver-generated from earlier
raws, derived from 116B factory TLV, loaded from cache/storage, static
tables + small derived key line, or fully static. Neither "device-derived"
nor "static" is proven. Classification: host-sent, replay-loaded, source
unknown.

## Ordered provenance tests (least -> most invasive)

1. Exact static search: full filled 0x30/0x34 + long interior subsequences
   in 2018 DLL + driver files. Full match => static storage.
2. Cross-session equality: identical 0x30/0x34 across sessions/raws =>
   static/cached; small changes => scaffolding + derived fields.
3. Compare vs partition/calibration records + 116B factory TLV for exact
   or transformed matches.
4. Invert 0x30 line program -> canonical line records -> implied
   calibration matrix (offline target).
5. Infer key line: match measurement-bearing 0x34 portion vs reconstructed
   matrix rows.
6. Paired driver vector (Wine replay): driver receives known raws, emits
   NEW identify in same run, no preloaded calib. Decisive provenance.

## Offline reconstruction plan (immediate path)

1. Parse 8240B raws: 48B envelope + 8192B body. Validate headers.
2. RESOLVE 8192-vs-9984 discrepancy FIRST (96x104 != 8192). Do not guess
   reshape/stride. Most immediate blocker.
3. Classify frames: nonzero fraction, leading-zero extent, histogram,
   saturation, row/col energy, correlation. Confirm (28,42) + (60,74) are
   comparable background/finger pairs.
4. Pin exact python-validity/Rust revision. Port stages separately:
   0x80 subtract, scale (10/0x22 device-dependent!), signed clipping,
   first-8-bytes-per-line preserve, saturating add of passes,
   bit-packing, line encoding, timeslot patching.
5. Candidate groupings: pairwise (28,42)+(60,74); bg/finger controls;
   4-frame aggregate; 3-frame only if reference contract allows.
6. Build candidate IDENTIFY from canonical 031, replace ONLY 0x30+0x34.
   Reparse: header 02 68 00 00 00, total 10608, chunk order unchanged,
   0x30 = 9428, 0x34 = 648, every other byte identical to 031.
7. Compare candidate vs native 031: structural, then byte-for-byte when
   paired vector exists.

## Native test (future spec, NOT authorized by this verdict)

After offline gates: 4 captures as 2 bg/finger pairs (or 3 only if 0x0195
proven 3-frame), process offline, send at most ONE candidate IDENTIFY,
evaluate capture quality only (geometry, dynamic range, saturation,
banding, contrast, phantom-touch). No retry/mutation. Note: sending is
itself a USB write / volatile state change — conflicts with literal
"no USB writes" constraint; verdict authorizes OFFLINE phase only.

## Stop conditions (binding)

identity/ROM mismatch; TLS MAC/padding/sequence failure; factory-TLV
structure change; authorize mismatch; 0x02 ack != captured 2272B form;
missing/reordered polls; geometry != 0x60006000; raw != 8240B expected
envelope; malformed 1072B response; timeout; unexpected interrupt; raw
statistical anomaly; unbalanced frame classes; offline dimension/packing
failure; generated length/chunk mismatch; any byte change outside
0x30/0x34; unconfirmed key line; phantom-touch sentinel; saturated/banded
image; any unknown recovery command.

## Four principal evidence gaps

1. Raw layout (8192 vs 9984)
2. Scaling factor for 0x0195 (0x199's 10/0x22 is device-dependent)
3. Pass count / pairing (3 vs 2 pairs)
4. key_calibration_line (0x38 from 0x199 NOT transferable without proof)
