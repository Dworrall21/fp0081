# fwext dynamic key capture — RESULTS (2026-08-06)

## What was done

Rebuilt the a.exe harness with a stub `wudfddi.h` (WDK headers were deleted;
reconstructed from ground-truth vtables extracted from the last working build
a.exe.pre-fwext-bp). Added 4 breakpoints:

- GWK PRF entry 0x1800DE660 (dumps args, label, seed desc + bytes)
- GWK PRF return 0x1800777F0
- seed write 0x18004AD80 (vfmInit)
- seed memcpy 0x18004ADDE

Verified all 8 harness class vtables match the old build structurally
(MyNamedPropertyStore 13, MyPropertyStoreFactory 9, MyMem 14, MyQueue 20,
MyDevice 43, MyDriver 14, MyDevInit 11, MyRequest 31 — only cosmetic
CreateSymbolicLinkA/W name diff on slot 24 of MyDevice).

## Replay runs (USB-free, USB_PLAYBACK=1, no device)

1. usb-pt6 (post-TLS capture flow): OnPrepareHardware rc=0, deviceInit +
   deviceInitAndCalibrate + CalibrationData loader hit (calib bps fired),
   BUT no PRF/seed breakpoints. Flow replays an ALREADY-PAIRED device.
2. usb-live7 (fresh pairing flow): full pairing incl. TLS encrypt/decrypt.
   **PRF_ENTRY FIRED ONCE.**

## CAPTURED: PRF call, label "HS_KEY_PAIR_GEN"

```
PRF_ENTRY: rip=0x1800de660 rcx=out_desc(len=16,ptr=0x5e1f930)
           rdx=label 0x1801e8578  r8=seed_desc(len=18,ptr=0x33c30)  r9=0x20
label:  "HS_KEY_PAIR_GEN"
seed:   25 12 a7 64 07 06 5f 38 38 46 13 9d 4b ec 20 33 aa aa   (18 bytes)
        = factory_key[16:32] (2512a76407065f383846139d4bec2033) + 0xaa 0xaa
```

Wine crypto log shows the TLS-PRF chain:
```
Hash input: 474ae11b3f548a7c1e7025bb8d1a122f 363636...  (ipad block, 16B key)
Hash input: 48535f4b45595f504149525f47454e2512a76407065f383846139d4bec2033aaaa
Hash out: 94267aaaceda8346f2e3c4389185109737050615815f2dde939d65c219f233ad  (inner)
Hash input: 2d208b71553ee016741a4fd1e7707845 5c5c5c...  (opad block)
Hash input: 94267aac...
Hash out: 18054d97cd6f10ca4cda53775cde4f7f3ee37700dfc93ed75338856d18c4d21b  = A(1)
Hash input: 474ae1... (ipad)
Hash input: 18054d97... + 48535f... (A1 || label || seed)
Hash out: db5d25152bde5af55d8fb3c0b83eb82fe6018e875583d3073026cbfb3b4bd422  (inner)
Hash input: 2d208b71... (opad)
Hash input: db5d2515...
Hash out: 866ab3019c09d4352e643fdb60e2e8c74041ae9c47efb0acd6546265b6a2a2e8  = P(1)
```

## Verification (OFFLINE, PASS)

```
key = HMAC-SHA256  (HMAC key = factory_key[0:16] = 717cd72d0962bc4a2846138dbb2c2419
                    recovered from ipad block: 474ae11b... = fk[0:16] ^ 0x36)
A(1) = HMAC(fk16, label || seed)          = 18054d97...  MATCH log
P(1) = HMAC(fk16, A(1) || label || seed)  = 866ab301...  MATCH log
derived 32B key = P(1) = 866ab3019c09d4352e643fdb60e2e8c74041ae9c47efb0acd6546265b6a2a2e8
```

Artifact: /tmp/hs_key_pair_gen_key_32.bin

## Interpretation

- This is the TEE "HS_KEY_PAIR_GEN" (hardware security key pair gen) PRF —
  NOT the fwext "GWK" key. Same palCrypto PRF entry (0x1800DE660), different
  label and seed.
- Seed = factory_key[16:32] + 0xaaaa marker → the runtime seed is derived
  from the static factory key half + tag. This explains why offline seeds
  (DMI/product/serial) never matched.
- **GWK/fwext PRF NEVER FIRED**: the driver never opens the xpfwext file
  (CreateFileW trace shows only c:\usb.txt; no system32\xpfwext open) and
  never triggers UpdateFirmwareExtension. Consistent with handoff:
  "xpfwext ABSENT from 0081 drivers (INF has it commented out); fwext
  upload was the wrong path."
- vfmInit seed write (0x18004AD80) never fired either — the paired-device
  flows don't populate the 0x18022F260 global in these replays.

## Verdict

Fwext dynamic-key capture: **NOT REACHABLE via 0081 consumer driver flows**
(GWK PRF / UpdateFirmwareExtension / vfmInit seed write all absent from
natural replay paths). The PRF boundary capture toolchain is PROVEN working
(one real capture + exact offline reproduction). HS_KEY_PAIR_GEN key
recovered as a side product.

Firmware gate remains CLOSED for the consumer-driver route. Remaining
routes per Sol plan: factory/service tooling, or MVWT0 donor, or accept
limitation.
