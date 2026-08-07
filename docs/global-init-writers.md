# Static Global-Initialization Writer Trace

Target: `synaWudfBioUsb.dll` (PE image base `0x180000000`, file timestamp `0x5b356890`).

## Result

`0x1801cf000` is the first 8-byte slot in `.data`, initially containing the image-relative self-pointer `0x1801cf000`. The only direct code writers found are:

| VA | Instruction | Predicate / path | Caller | Confidence |
|---|---|---|---|---|
| `0x180017728` | `mov qword [0x1801cf000], rax`, where `rax = 0x18022f0c8` | `fcn.1800176cc` switch: `arg2 == 1` (`DLL_PROCESS_ATTACH`) | `entry0` at `0x1800ff29d` | High |
| `0x180017965` | `mov qword [0x1801cf000], rax`, where `rax = 0x1801cf000` | `fcn.1800178ec`: only after the slot is not the self-pointer; unregister loop has completed | `fcn.1800176cc` at `0x180017761` | High |

`fcn.1800176cc` is reached from `entry0` at `0x1800ff29d` for attach and `0x1800ff2b9` for detach. Its other switch cases call TLS setup/cleanup routines and do not write the target slot. The attach sequence is:

1. `entry0` receives `edx == 1` and first calls `fcn.180106030` at `0x1800ff1f4`; that routine initializes the security/random-cookie state at `0x18022d7d0`, not the target global.
2. `entry0` optionally calls the indirect function pointer at `[0x180141cf0]` (`0x1800ff25d`), then calls `fcn.1800176cc`.
3. `fcn.1800176cc` calls `fcn.180017840`, `fcn.1800178c8`, writes the target slot at `0x180017728`, registers trace metadata through `fcn.180017a68`, stores the module argument at `0x18022f0f0`, and calls `fcn.180040f64`.

## Gate Record

After attach, the target slot points to `0x18022f0c8`. The relevant record fields are therefore:

| Effective address | Field | Static initialization | Used by calibration |
|---|---|---|---|
| `0x18022f0e1` | `record + 0x19` | `mov byte [rax + 0x19], 0` at `0x180017890` | `movzx` at `0x180025cf5`; gate `cmp eax, 5` at `0x180025cfa`, `jl` at `0x180025cfd` |
| `0x18022f0dc` | `record + 0x1c` | `mov dword [rcx + rax + 0x1c], 0` at `0x1800178ad` (`rax` is zero) | load at `0x180025cda`; `and eax, 4` at `0x180025cde`; `test` at `0x180025ce1`; gate `je` at `0x180025ce3` |

The same record initializer at `fcn.180017840` also sets `record + 0x10` to zero, `record + 0x18` to one, and `record + 0x1a` to zero. The `cmp eax, 1` at `0x180017858` follows `xor eax, eax`, so the alternate `record + 0` assignment path is not taken in this function’s observed flow.

The full `deviceCalibrate` function is `fcn.180025b00`. Its callers are:

- `fcn.180023738` calls it at `0x180023b14`.
- `fcn.1800264ac` calls it at `0x1800265ea`.

The requested gates are conditional on all of the following in the second branch of that function: the global slot is not the self-pointer (`0x180025cae`/`0x180025cb5`), `record + 0x1c` has bit `0x4` (`0x180025cda` through `0x180025ce3`), and `record + 0x19 >= 5` (`0x180025cf5` through `0x180025cfd`).

## Indirect Registration / Table Paths

`fcn.1800178c8` writes the first table/vtable pointer at `0x18022f0c0` (`mov qword [rax], 0x180119928` at `0x1800178d9`) and advances the table cursor by 8 bytes. `fcn.180017a68` then walks the list beginning at `record + 0x28`, writes each registration handle at list-entry `+0x20` (`0x180017aeb`), and calls imported `ADVAPI32!RegisterTraceGuidsW` at `0x180017b29`.

The callback/list machinery contains indirect calls, including `fcn.180017374` calling `[entry + 0x38]` at `0x1800173c6` and `fcn.1800170a8` calling `[object + 0x10]` at `0x180017212` or the decoded callback at `0x180017278`. These paths write registration/list pointers and encoded callbacks, but static inspection found no additional in-module store to the exact `record + 0x19` or `record + 0x1c` locations. Consequently, nonzero gate values are most plausibly supplied by the external trace-control/registration mechanism represented by `RegisterTraceGuidsW` and its callbacks, not by another direct DLL writer. Confidence in that external-writer attribution is medium; the absence of another in-module writer is high.

## CRT / Constructor Findings

The PE has only `.text`, `.rdata`, `.data`, `.pdata`, `.rsrc`, and `.reloc`; no `.CRT` or TLS section is present in the section table. The image entrypoint is `0x1800ff1d8` (`entry0`), and it directly implements the DLL attach/detach dispatch. No separate C++ constructor array or CRT initializer was identified. The attach-only call to `fcn.180106030` is cookie initialization and does not initialize the target global.

## Static-Only Caveat

This report is based on `r2`, `rabin2`, and `objdump` disassembly/metadata only. No Wine/native execution, device access, or binary modification was performed. Runtime writes performed by Windows/ETW after `RegisterTraceGuidsW` cannot be assigned an exact DLL VA from static code alone.
