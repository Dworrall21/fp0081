# 0081 Phase A COMPLETE — calibration constants recovered (2026-08-06)

## Confirmed 0x195 constants (verified across 6 native cycles)

- bytes_per_line = 104 (0x68)
- line_width = 96 (0x60)
- lines_2d = 96 (0x2f chunk)
- logical frame = 104 x 96 = 9984B; active pixels = 96 x 96 = 9216B
- **key_calibration_line = 44 (0x2c)**: fcv[44] = 0x80 = the patched
  byte at the 0x8000203c write, verified in ALL 6 cycles
- **key line = deblocked matrix row 46** -> 0x34[0:96], 96/96 exact
  (cycles 63+ = 95/96, one byte differs per cycle = live key-line data)
- 0x30 payload = 24 records x 384B (96 rows x 4 cols each) + 2 mask=0xff
  records (gamma/factory data)
- matrix deblock: M[row][col] = P[(col//4)*384 + row*4 + (col%4)]
- 0x34 = key_line(96) + patched_timeslot(552)
- 0x8000203c write at timeslot pos 52, MAIN BODY (0081 variant patches
  the main-body write, not the post-Call subroutine like 0x199)
- subst_value = factory_calibration_values[44] = 0x80

## Timeslot structure (0x34[96:], 552B)

- Calls: pos 16,19,22,25,28 -> dest 144; pos 37 -> dest 148
- Write Register 0x8000203c: pos 52, value 0x80
- Other writes: 0x80002048=0x0008 (pos 34), 0x800020b4=0x0003 (pos 55)
- decode via python-validity/Rust opcode set (verified identical)

## Key architectural finding (0081 vs 0x199)

patch_timeslot_again in 0x199 searches AFTER the last Call (subroutine);
in 0081 the 0x8000203c write sits in the MAIN body at pos 52, before
the Calls. The 0081 driver patches the main-body write. Both produce
value = fcv[key_calibration_line].

## Still open

1. matrix VALUES (9216B) provenance: captured from 6 cycles, varies
   42-44%/cycle. Transform raw(8192)+extra(1020) -> matrix(9216) not
   derived. Endpoint-0x82 bulk read (read_82) = likely true calibration
   input, NEVER recorded natively (only 51-poll frames).
2. 8192B object geometry unproven (128x64 assumed from byte count).
3. Whether the matrix + 0x34 reconstruction produces GOOD images —
   needs native test or byte-for-byte driver reproduction.

## Next (Phase B)

Wine replay breakpoints on the driver's 0x30/0x34 construction path:
observe key-line index, extracted key-line bytes, fcv byte for
0x8000203c patch, final 0x30/0x34. Pass = final buffers explain
captured 031_TX.bin byte-for-byte.
