# send_helper ABI — 0081

Binary: `~/fp-research/repos/synaWudfBioUsb-sandbox/synaWudfBioUsb.dll`
Base: `0x180000000`; RVA = VA - base.

## Dispatcher

- VA `0x180015F50`, RVA `0x15F50`: generic dispatcher/helper.
- ANSI variant: VA `0x180015FEC`, RVA `0x15FEC`.
- Static caller inventory: `send_helper_callers.csv`.
- Inventory contains 397 lines including header; helper has many non-calibration callers.

## Calibration call sites

```text
0x180025C04, RVA 0x25C04: mov edx, 0x60; later call 0x180015F50 at 0x180025C14
0x180025D29, RVA 0x25D29: mov edx, 0x61; later call 0x180015F50 at 0x180025D39
```

Known static call context: `0x180025B00` prepares a 0x60-byte local/heap structure, operation selector in `EDX`, descriptor/context reference through the remaining ABI arguments, then calls shared helper. Exact pointer ownership and serialized length remain dynamic-analysis items.

## Known/observed

- Descriptor reference observed in static analysis: `0x18011A000`, 96 bytes. It is not proven to be wire bytes.
- `0x180015F50` is shared; operation/WPP values in caller CSV are not automatically protocol opcodes.
- No TLS record headers, MACs, or padding belong in a future `tls.cmd()` body.

## Unknown / gate

Need capture at helper entry and transport boundary: RCX/RDX/R8/R9, stack args `[RSP+0x20...]`, allocation bounds, input/output lengths, return site, and descriptor pre/post bytes. No native replay until this is known.
