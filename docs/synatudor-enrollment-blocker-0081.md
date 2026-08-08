# 06cb:0081 — synaTudor relinking: enrollment blocker identified (Sol-verified)

Date: 2026-08-07
Status: FINDING COMPLETE — blocker identified precisely; packaging per Sol/High verdict

## Executive summary

The exact 2018 Lenovo driver (`synaWudfBioUsb.dll` v5.5.2731.1050) is loaded and
driven natively on Linux via the rstar000/synaTudor dynamic relinker. The WDF
wall is crossed (OnD0Entry=0), USB re-enumeration is handled, calibration
ioctl `0x442058` completes `0`, and the CLI menu is reached. Fingerprint
ENROLLMENT remains blocked at `0x44200c` (CreateEnrollment): the native driver
crashes on a NULL virtual call because the security-management object behind
`CBiometricDevice+0x1c0` is **never created** — the setup routine that creates
it is **never invoked** by the relinked open/enrollment flow.

## Verified milestones

- DLL loads; `OnPrepareHardware = 0`; `OnD0Entry = 0`.
- USB re-enumeration during calibration handled (libusb close/re-find/reclaim
  + retry-on-`LIBUSB_ERROR_NO_DEVICE`).
- Calibrate `0x442058` → `Complete: 0` (TLS traffic: authorize 6677B,
  send 1157/read 2238, send 5/read 6).
- Pipeline initializes; CLI menu reached (`e/v/i/q/w/s`).
- Property store: CalibrationData, timestamps, PairingContext/PairingData/
  UnpairingContext wired through the datastore callback.
- Local in-memory storage adapter + `storage_OpenDatabase()`.
- `PROPVARIANT` layout corrected (DECIMAL inside union; 40-byte overwrite fixed).
- Engine/storage context fallback handles populated.
- `0x44202c` (OnGetDatabaseRecordsCount) short-circuited to zero records
  (native handler corrupts relink host; request plumbing verified correct).

## The blocker — instrumentation evidence (gdb, ASLR off, deterministic base 0x7ffff5676000)

Run: `cli/tudor_cli /tmp/tudor-datastore.bin` + `e / 0 / 1` enrollment.

| Observation | Result |
|---|---|
| Setup function RVA `0x18006e900` (scsSecMgmt.c security setup) | **NEVER ENTERED** (0 hits) |
| Allocator `0x1800da200` type `0x91` (security object alloc) | **NEVER REQUESTED** (0x91 absent; many other types observed) |
| 184-byte interface read / `0x1800e7000` state helper | never reached (setup not entered) |
| Crash PC | RVA `0x33479` |
| Crash instructions | `mov 0x1c0(%rcx),%ecx` → `mov (%rax),%rax` with `rax=0` → SIGSEGV |
| Field | `CBiometricDevice+0x1c0` stays NULL (constructor zeroes it; only assignment is inside the never-entered setup) |
| Static xrefs to setup | **zero** direct calls, zero rdata pointers, zero lea refs → dispatched indirectly (runtime table/interface) |

## Conclusion (causal chain)

1. Windows-side security initialization (scsSecMgmt) is a lifecycle step the
   relinked flow never issues (dispatched indirectly — no static caller).
2. `CBiometricDevice+0x1c0` is never assigned → stays NULL.
3. CreateEnrollment native code assumes setup succeeded → NULL vtable deref
   at RVA `0x33479` → SIGSEGV.
4. Supplying PairingContext/PairingData blobs cannot help: the routine that
   consumes them is never called.

## Sol/High verdict (GPT-5.6 Sol, High — request 8884af1a)

Run exactly ONE final diagnostic (done above), then package. The instrumentation
identified the blocker: security-setup never invoked. Record as identified
blocker and package. Do NOT continue open-ended debugging.

## What is NOT claimed

- No successful enrollment / identification / login on Linux.
- No matcher validation (embedded vcsMatcher unreachable in this path).
- No firmware or partition-6 writes; no mode-byte forcing; no field forcing.

## What IS claimed

- Native driver loads and runs substantially beyond the unsupported-device
  baseline; WDF/PROPVARIANT/storage issues isolated and fixed.
- TLS activity reached during enrollment; crash localized to missing native
  security-object initialization (RVA 0x33479, `CBiometricDevice+0x1c0` NULL).
- Blocker is a missing lifecycle/ioctl trigger, not request plumbing.

## Files

- Worktree: `/tmp/synaTudor-0081` (patched clone; patches listed in tar manifest)
- GDB scripts: `/tmp/tudor-instr.gdb`, `/tmp/tudor-crash.gdb`
- Sol context: `/tmp/sol-next-step.md`, `/tmp/sol-context.md`
