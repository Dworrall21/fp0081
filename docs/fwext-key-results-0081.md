# fwext key extraction — results (2026-08-05)

## Extracted & verified

The 0081 drivers embed the SAME 32-byte factory key as Validity90:

```
717cd72d0962bc4a2846138dbb2c24192512a76407065f383846139d4bec2033
```

Recovered from synaWudfBioUsbSGX.dll (2022) as 4 inline byte-store
functions writing 8 bytes each:

```
0x18007F200: 71 7c d7 2d 09 62 bc 4a
0x18007F2F0: 28 46 13 8d bb 2c 24 19
0x18007F3E0: 25 12 a7 64 07 06 5f 38
0x18007F4D0: 38 46 13 9d 4b ec 20 33
```

2018 driver equivalent: fcn.180077830 (byte-store `c6 04 01 71` @
0x18007784F + 3 siblings), parent fcn.1800776F0 (scsSharedSecret.c).

Byte-identical to Validity90 prototype/validity90/validity90.c factory_key
+ utils-test.c.

## Key derivation (both drivers)

```
key = TLS-PRF(factory_key, "GWK", seed, 0x20)
2018: fcn.1800776F0 -> fcn.1800DE660 ; seed = *0x18022F260 (global)
2022: fcn.18007F0C0 -> fcn.1800C9790 ; seed = *0x18018B428 (global)
labels also present: "GWK_SIGN" (2018 @0x1801F11A0)
AES decrypt: palCrypto dispatcher (algos 1/2/3) -> CryptDecrypt (CryptoAPI)
```

## Seed NOT statically recoverable

Both seed globals (0x18022F260 / 0x18018B428) are ZERO or table-valued in
the static file and are populated at runtime. Offline attempts with:

```
labels:   GWK, GWK_SIGN, GWKVirtualBox
seeds:    DMI product/serial/vendor combos (81JS\0MP1MT8MF\0 etc.),
          empty, VirtualBox, zeros
keys:     PRF outputs (AES-128/256), factory key forms
layouts:  whole payload ±16B, minus 256B sig, IV variants
```

→ ZERO padding-valid low-entropy decrypts. The fwext AES key is
runtime/session-derived (likely enclave/vtp-mediated), NOT derivable
offline from static constants + known machine strings.

## Implication

Firmware gate (Sol step 1) remains NOT MET for static decryption.
The decrypt path IS fully mapped, so the seed can be captured DYNAMICALLY:

```
Wine USB-free replay of the 2018 driver
  + a.exe breakpoint at PRF call fcn.1800DE660 (2018)
  + xpfwext present + update path triggered
  → capture seed, derived key, and decrypted fwext payload
```

This is the established read-only Wine-replay method (no device, no USB
write). It converts the firmware gate from "blocked" to "dynamic-only".

## Files

```
notes/fwext_decrypt_0081.py   (round 1: DMI seeds, GWK)
notes/fwext_decrypt2_0081.py  (round 2: broad keys/layouts)
notes/fwext_decrypt3_0081.py  (round 3: log-derived seed formats)
```
