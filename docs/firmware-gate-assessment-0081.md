# Firmware research gate assessment — 0081 (Sol step 1)

Date: 2026-08-05. Static-only; no device access.

## Firmware artifact inventory (all local)

| artifact | sensor family | encryption | payload entropy | executable code? |
|----------|--------------|-----------|-----------------|------------------|
| 6_07f_lenovo_mis_qm.xpfwext (r0qfp15w, nz3gf09w, inno) | 0081 (MIS) | 0x0002 | 7.999 | NO (encrypted) |
| 6_07f_lenovo_sm_qm.xpfwext (r0yfp10w FM3380) | SM | 0x0002 | 7.999 | NO |
| 6_07f_lenovo_sm_qm.xefwext (r0yfp10w FM3380) | SM | 0x0003 | 7.999 | NO |

No bootloader/recovery images, no full firmware dumps, no decrypted
firmware anywhere on disk.

## xpfwext format

First 20,208 bytes are a readable INI-style header:

```
FirmwareVersion = 6.07.0164
Encryption = 0x0002
Target = 0x0001
Product = 0x0030
StartAddress = 0x51002000
Signed = 0x0001
SignatureLength = 0x0100
FwextType = 0x2000
FwextMajorver/Minorver/Buildnum/Buildtime
```

Payload (198,274 B) entropy 7.999 = fully encrypted. No key/IV in header.

## Sol gate status

Gate "image contains executable code": NOT MET — all firmware payloads
encrypted, no static decode path identified yet.

## NEW: host-side decrypt path discovered (static)

The 2022 SGX driver contains a complete fwext decrypt chain:

```
scsHostPart 0x18005AB50
  → fcn.18007E990 (decrypt orchestrator, 2 call sites)
    → fcn.1800C7D20 (decrypt entry)
      → fcn.1800CA150 / fcn.1800CAA30
        → fcn.1800C2580 / fcn.1800C2720 (palCrypto dispatcher,
           algorithms 1/2/3)
          → fcn.1800C8200 / fcn.1800C8520 / fcn.1800C88C0
            → ADVAPI32!CryptDecrypt / CryptImportKey (CryptoAPI)
```

CryptoAPI imports: CryptAcquireContextA, CryptImportKey, CryptDecrypt,
CryptDestroyKey, CryptDestroyHash.

Also present: AES S-boxes in synaTEE.signed.dll @ 0x188140 / 0x189A60
(enclave-side AES) and synaWudfBioUsbSGX.dll @ 0xE4DE0.

Upload-path strings in SGX DLL: CBiometricDevice::OnUpdateFirmware,
CBiometricDevice::UpdateFirmwareExtension (0x18000C430, WPP+counters).

## Key source

Key NOT found as a literal in the wrapper chain (palCryptoCommon.c is
generic). Key is passed from upper callers; likely embedded in the enclave
(synaTEE AES) or derived at runtime. Extracting it requires either:

- locating the key blob in the fwext-upload caller (0x18005AB50 area or
  fcn.1800CA150's stack setup before the 0x1800CA43D call), or
- enclave key extraction (synaTEE .data near AES code).

## Implication

If the fwext AES key is recovered, the 0081 firmware extension payload
decrypts offline → executable sensor firmware code → Sol step-1 firmware
research (factory-calibrate trigger / MVWT0 regeneration search) OPENS.
This is now the single highest-value static target.

## MVWT0 donor gate (Sol step 2) — still NOT MET

Scanned all 234 capture files in /tmp/pt6-flow + /tmp/calib-flow (all
RX/TX): ZERO hits for MVWT0 magic, zero type-06/storage-03/0x0c60 record
headers. The only "fragment" is /tmp/mvwt0-record-notes.txt.bin = 2 bytes
`0000` — unusable. No complete 3168B sample exists locally.
