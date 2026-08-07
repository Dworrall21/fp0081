# Calibration storage map — 0081

## Loader

`0x18001A644` / RVA `0x1A644` is called from `deviceCalibrate` at:

```text
0x180025C7B
0x180025D77
```

Static analysis shows a named-property interaction using the string `CalibrationData`; the loader path can receive zero bytes. Prior Wine evidence: `Loaded 0 bytes of calibration data`.

## Backup path

`0x18001A16C` / RVA `0x1A16C` is the related backup/persistence path. Direction is not yet proven: name alone cannot distinguish device-to-host backup from host-to-device restore. Must inspect property/file/registry APIs, length checks, and transport calls.

## Evidence

Observed 6f000e response: 1594 bytes after TLS framing removal. It is a candidate input to host-side calibration assembly, not yet proven MVWT0. Existing device read for MVWT0 returns absent (`b304`). No complete MVWT0 record exists locally.

Descriptor table: `0x18011A000`, 96 bytes, SHA-256:

```text
5bacc3a54ae4ffad4ddbaed9063480abf4e2772b0ed70d13f2c9fc3c77c55bdc
```

## Required dumps

Capture, in order:

1. raw 6f000e response
2. decoded response after shared helper
3. post-processing destination buffer
4. BackupCalibrationData input
5. persistence boundary bytes
6. loader reload bytes

Record size, SHA-256, header/length fields, MVWT0 offset, and provenance. Truncated fragment must not be padded or written.

## Safety

Any path touching flash, erase, partition writes, factory reset, firmware update, or device-side persistent storage is prohibited from native testing until fully characterized.
