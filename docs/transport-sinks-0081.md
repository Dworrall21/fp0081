# Transport-sink + provenance map — 0081 (2018 sandbox DLL)

Module: `~/fp-research/repos/synaWudfBioUsb-sandbox/synaWudfBioUsb.dll`
Base: 0x180000000. Companion CSV: `transport-sinks-0081.csv`.

## Terminal sinks (host→device)

WinUsb API resolved dynamically. Resolver `0x1800F4DC0` fills a 0x78-byte
function table; global singleton at `0x18022F640`.

| slot | API | sink wrapper |
|------|-----|--------------|
| +0x08 | WinUsb_Initialize | `0x1800F3D40` |
| +0x28 | WinUsb_ReadPipe | `0x1800F4550` |
| +0x30 | WinUsb_WritePipe | `0x1800F5CE0` (pre-wrapper `0x1800F45D0` selects pipe/endpoint) |
| +0x40 | WinUsb_ControlTransfer | `0x1800F4630` (pre-wrappers `0x1800F3C90`, `0x1800F3CF0`) |

Protocol dispatcher `0x1800F3150` (palUsbProtocol) is registered as a vtable
method by the transport factory `0x1800EE2C0` (palDevice, config strings
"usb"/"UMDF").

## PAL message types (0x938AE0xx) and producers

Dispatcher `0x1800F3150` switch base `0x938AE000`, byte map at
`0x1800F37DC`, jump table `0x1800F37B0`. Case index → handler:

| case | type(s) | handler |
|------|---------|---------|
| 0 | 00 | 0x1800F34D3 (req/resp exchange) |
| 1 | 04,08,14,18,48,4c,50,54,64,68,6c | 0x1800F3331 (ctrl) |
| 2 | 10 | 0x1800F35E1 (req/resp) |
| 3 | 1c | 0x1800F36A4 |
| 4 | 24 | 0x1800F3391 (ctrl) |
| 5 | 38 | 0x1800F36E7 (large req) |
| 6 | 58 | 0x1800F3531 |
| 7 | 5c | 0x1800F3691 (large req) |
| 8 | 60 | 0x1800F3426 (ctrl, obj build) |
| 9 | 84 | 0x1800F3735 (ctrl2) |
| default | — | 0x1800F3788 (error 0x6f) |

Producers (functions that set each type and call the send chain):

| type | producer | note |
|------|----------|------|
| 0x938AE038 | `0x180065860` | scs.c; calibration status/version query |
| 0x938AE024 | `0x180067450` | |
| 0x938AE034 | `0x180067A70` | |
| 0x938AE070 | `0x180067B90` | |
| 0x938AE008 | `0x18006B720` | |
| 0x938AE004 | `0x1800EE6B0` | request-builder class |
| 0x938AE010 | `0x1800EED10` | |
| 0x938AE014 | `0x1800EE750` | |
| 0x938AE018 | `0x1800EE810` | |
| 0x938AE048 | `0x1800EE5F0` | |
| 0x938AE04C | `0x1800EE8B0` | |
| 0x938AE050 | `0x1800EEF40` | |
| 0x938AE054/58 | `0x1800EEE80` | |
| 0x938AE05C | `0x1800EEC00` | |
| 0x938AE060 | `0x1800EEA90` | |
| 0x938AE064 | `0x1800EEB60` | |
| 0x938AE068 | `0x1800EE950` | |
| 0x938AE06C | `0x1800EE9F0` | |

Send chain: producer → `0x1800E1340` (scs.c) → `0x1800EE530` (palDevice.c)
→ vtable `[obj+0x10]` → dispatcher `0x1800F3150` → case handler →
WritePipe/ControlTransfer/ReadPipe.

## Calibration-relevant path (proven)

```
fcn.180046D90 (vfmDevice.c: calibration status check)
  arg3->type selects 1/2/3 (mode byte 2/3/4)
  → fcn.180065860  builds PAL msg 0x938AE038, 6-byte response buffer
  → send chain → dispatcher case 5 → 0x1800F36E7 → large-req path
  → WinUsb_WritePipe / WinUsb_ReadPipe
```

Response semantics decoded in `0x180046D90`:

```
resp[0..1]  sensor status (bits → var_20h: 0x1,0x2,0x4)
resp[4]     calibration version byte A, compared vs [dev+0x4c]
resp[5]     calibration version byte B, compared vs [dev+0x4d]
mismatch → status bits 0x4/0x8 (calibration-version drift flag)
```

This is a host→device query with device→host 6-byte answer — calibration
VERSION/status read, not a calibration-data write.

## CalibrateDevice / deviceCalibrate / OnCalibrate — closed

All three are WPP/status/backup only:

```
0x180025B00 deviceCalibrate  → WPP 0x60/0x61, loader 0x18001A644
0x18001A644 CalibrateDevice  → WPP msgs 86-89, status 0x1800459A0 (0xD7),
                               backup 0x18001A16C, fcn.0x180028A74
0x180028A74                  → ADVAPI32!TraceMessage event 0x2B (WPP)
0x18001EDF4 OnCalibrate      → work fcn.0x18001DEF4 (vtable +0x60/+0x80/
                               +0x88/+0x90 interface), WPP 0x9d
```

None of them reach a WinUsb write with a calibration-data payload.

## Result vs Sol hypotheses

Strongly supports Sol hypothesis #5: the consumer 2018 driver does NOT ship a
host-to-device calibration restore. Calibration handling = status read
(0x938AE038), version comparison, device→host backup, WPP telemetry.
Restoration is plausibly factory tooling / firmware regeneration.

## Completeness / stop-criteria state

Covered in this module:

- all WinUsb terminal sinks (resolve+table slot+pre-wrapper)
- protocol dispatcher and full 0x938AE0xx jump table
- every producer of a 0x938AE0xx type
- one calibration-specific producer/consumer pair (0x938AE038)

Not yet covered (next per Sol plan):

- full caller closure of every producer (0x1800EExxx builders' callers)
- sibling setter/restore/commit ops on the CalibrationData interface
  (vtable slots +0x60/+0x80/+0x88/+0x90 used by OnCalibrate work fn
  `0x18001DEF4`)
- whether any producer's input buffer can carry an MVWT0/calibration blob
  (0x938AE038 carries only a 1-byte mode; large-write types 0x938AE000/1c/5c
  and ctrl types need per-type payload inspection)
- version-matched siblings (SGX 2022 DLL, services, tools)

Statement: NO host-to-device calibration-data WRITE has been identified in
the 2018 module's transport sinks yet. 0x938AE038 is a read/status query.
