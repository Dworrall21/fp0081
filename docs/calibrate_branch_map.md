# Calibration branch map — 0081

## Functions

```text
deviceInitAndCalibrate  0x1800264AC / RVA 0x264AC
deviceInit              0x180025E3C / RVA 0x25E3C
deviceCalibrate         0x180025B00 / RVA 0x25B00
CalibrationData loader  0x18001A644 / RVA 0x1A644
Backup path             0x18001A16C / RVA 0x1A16C
state-machine caller    0x180023738; calls deviceCalibrate at 0x180023B14
```

## Operations

```text
0x180025C04: operation selector 0x60
0x180025C14: shared dispatcher call 0x180015F50
0x180025D29: operation selector 0x61
0x180025D39: shared dispatcher call 0x180015F50
```

Static state-machine finding: `0x180023738` has switch/state cases; case 5 calls `deviceCalibrate`, while another case calls a separate path. Existing normal caller at `0x180019CF4` passes zero and explains calibration bypass in prior traces.

## Current evidence

Wine/native traces contain no transmitted 0x60/0x61 plaintext. Wine playback reaches `Loaded 0 bytes of calibration data` and the 6f calibration exchange, but does not prove entry into both calibration branches.

## Required next evidence

Map predicates controlling entry, especially object fields around `this+0x154` and `this+0x164`, caller argument/state, return/status handling, and any reset/storage calls. Force branch only in USB-disconnected replay after transport interception is verified.

## Safety classification

`0x60` and `0x61`: unresolved. Do not send natively. Static operation number alone does not establish volatile vs persistent behavior.
