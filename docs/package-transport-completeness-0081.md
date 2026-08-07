# Package-level transport-sink completeness — 0081 (r0qfp15w 2022 + 2018)

Scope: r0qfp15w WBF_Drivers package (13 binaries) + sandbox 2018 driver
(huy103af07m6-era, synaWudfBioUsb-sandbox).

## SCS/PAL transport owners

Only binaries containing the 0x938AE000-dispatch dispatcher:

| binary | dispatcher | producer types | calibration status type |
|--------|-----------|----------------|-------------------------|
| synaWudfBioUsb.dll (2018 sandbox) | 0x1800F3150 | 0x938AE004..070 (19) | 0x938AE038 |
| synaWudfBioUsbSGX.dll (2022) | 0x18003F6FB | 0x938AE004..070 (19) | 0x938AE038 |
| synaWudfBioUsb.dll (2022 main) | NONE | NONE | N/A (shell only) |

Same PAL type set in both versions — no calibration-write type exists in the
protocol layer of either driver.

## Calibration string coverage (whole package)

MVWT0 / Calibrat / WOENF / WOF2 / WOVAR markers found ONLY in:

```
synaWudfBioUsb.dll (2018)      — CalibrateDevice, deviceCalibrate, BackupCalibrationData
synaWudfBioUsbSGX.dll (2022)   — CalibrateDevice, backupCalibrationDataToFlash, WinUsb sinks
synaTEE.signed.dll             — enclave op-0x15 transform (CalibrationData)
vtp.dll                        — vtpCall → sgx_ecall transport
```

Absent from: SynapticsUtility.exe, IPTSecureFPx64/Uix64/Win32, synaAdvAdapter.dll,
sgx_capable.dll, synaDriverLoader.dll, WudfUpdate_01011.dll, SynaSmi.sys, xpfwext.
No factory/diagnostic calibration tool ships in the consumer package.

## Final verdict (package-level)

```
No host-to-device calibration-data write exists in the consumer driver
package (2018 or 2022) or its SCS/PAL protocol layer.
```

Calibration handling in host software is limited to:

```
1. status/version query      PAL 0x938AE038 (6B response, version compare)
2. device→host backup        backupCalibrationDataToFlash
3. enclave transform         CalibrationData op 0x15 (validation/envelope)
4. WPP telemetry             0x60/0x61/0x9d + event 0x2B
```

MVWT0 on working devices is therefore written by factory tooling or
firmware regeneration, not by installed host software (Sol hypothesis #5
confirmed at package level).

## Remaining unknowns (stop-criteria state)

- Exact wire frame of PAL 0x938AE038 (host-side cache fill via 0x1800F3B10;
  the observed wire `6f000e` calibration read is NOT built from any static
  constant in the 2018 DLL — no 6f/0e/0a immediates, no frame templates in
  .text/.data/.rdata; construction must be runtime-derived, likely in the
  scsCommands.c layer 0x180055xxx. Candidate for a Wine-side capture proof,
  not static.)
- Whether firmware exposes an on-device recalibrate trigger (factory mode)
- Whether a calibration donor blob could be validated by op 0x15 offline

## Wire-frame note (2018 driver)

Exhaustive constant search for the `6f000e`/`6f000a` frame bytes:

```
C6 <modrm> 6f  (mov byte [mem],0x6f):   none (only stack-disp false positives)
B0 6f         (mov al,0x6f):            1 site, non-transport helper
66 C7 imm16=0x006f/0x000e/0x000a:        none
C7 dword imm 0x0e006f/0x0a006f:          none
byte tables in .rdata/.data:             none
```

The 9-byte `6f 00 0e 00 00 00 00 00 00` calibration-read frame is therefore
assembled at runtime from non-literal values (protocol-layer field
composition in scsCommands.c / palUsbProtocol). Mapping PAL type → wire
frame requires dynamic capture, not static constants.
