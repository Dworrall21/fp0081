# fwext GWK seed global — writer analysis (2026-08-06)

Correction to fwext-key-results-0081.md: "axt inconclusive — verify writers" is
now RESOLVED for 2018; 2022 has NO writer in the SGX DLL.

## 2018 synaWudfBioUsb.dll — writers PROVEN

Seed struct = {dword len @0x18022F260, qword ptr @0x18022F268}.

| site | instr | meaning |
|------|-------|---------|
| 0x18004ad80 | MOV [0x18022F260], eax | len = vfmObj->field_8 |
| 0x18004ad91 | MOV [0x18022F268], rax | ptr = malloc(len) |
| 0x18004adc7..adde | memcpy(ptr, vfmObj->field_0x10, len) | seed data = VFM object buffer |
| 0x18004aee2/aeee/aef8 | zero ptr/len | deinit |
| 0x18007707c / 0x18007744d | LEA rdx, [0x18022F260] | seed arg → scsSharedSecret (GWK PRF) |

Writer function: fcn.18004ac80 (vfmInit.c), called from 0x180018f44 and
0x180019055 — a RETRY LOOP on status 0x259 ("not ready"), Sleep(1000) between
attempts (caller fcn ~0x180018e80, vfmDeviceCtl.c). The 0x18004ac80 fn:
- allocs 8B global obj at 0x18022F248, init via 0x180076670
- checks vfmObj->field_0x10 != 0 before copying (skip if empty)
- copies vfmObj->field_8 (len) + field_0x10 (data) into seed global

## 2022 synaWudfBioUsbSGX.dll — NO writer in module

Only 2 refs total: LEA @ 0x18007ea69 and 0x18007ee1a (both pass seed to
scsSharedSecret). No MOV/imm write to 0x18018B428/0x18018B430 anywhere in
.text. Seed must be populated CROSS-MODULE (main synaWudfBioUsb.dll shell /
vtp.dll / enclave) or at a different layer. Static search closed.

## Conclusion

- 2018 seed = runtime copy of VFM device object buffer (device-derived,
  populated during device-init retry loop). NOT derivable offline.
- 2022 seed populated outside SGX module. NOT derivable offline.
- Dynamic capture (Wine replay + breakpoint at PRF call 0x1800DE660 / on the
  memcpy at 0x18004adde, or at seed write 0x18004ad80) remains the only path.
  Breakpoint target refined: 0x18004ad80 (2018) fires only after vfmObj init
  succeeds — so the Wine replay must reach device-init-complete state, not
  just any scsSharedSecret call.

Script: scan_rip_refs corrected (modrm rm field, not reg; instr len 6+rex+imm).
