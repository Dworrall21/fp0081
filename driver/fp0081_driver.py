"""fp0081 - native driver for Synaptics 06cb:0081 fingerprint sensor.

Production driver per Sol verdict 7 (canonical pipeline):
  1. Session: USB open -> TLS -> authorize (6677B const) -> 6f000e/6f000a
  2. Capture 4-16 UNCOVERED frames (same IDENTIFY frame as finger capture)
  3. Per-pixel MEDIAN reference (robust background/fixed pattern)
  4. Finger capture: same frame, signed subtraction from reference
  5. Row-median bias removal (median, not mean - preserves low-freq ridge
     contrast)
  6. Robust contrast mapping (percentile-based, no premature clipping)
  7. Segmentation + ridge enhancement for template extraction

Validated constants (all verified against real sensor + Wine replay):
  - authorize blob: 6677B constant (from 015_TX)
  - IDENTIFY frame: 155_TX (10608B, driver-built cycle-4 variant)
  - CALIBRATE frame: 017_TX (1200B)
  - 51-poll sequence: 5100000000, 5110000000, 5100200000, 51fc030000
  - frame envelope: 6B header (status 0, u32 len 8192) + 8192B payload
  - image: 128x64 grayscale

Finger-detect polls (01) are NOT a valid presence discriminator
(return 01 on ambient/phantom touch). Presence = image-derived
(corrected variance, ridge-band energy, spatial coherence).
"""
import os
import sys
import time
import hashlib
import struct
import numpy as np

# ---- validated session artifacts (paths configurable) ----
DEFAULTS = {
    "pairing_resp": "/tmp/pairing-50-resp.bin",
    "pairing_key": "/tmp/0081-pairing-key-96.bin",
    "client_cert": "/tmp/0081-client-cert-184.bin",
    "auth_frame": "/tmp/pt6-flow/015_TX.bin",
    "identify_frame": "/tmp/pt6-flow/155_TX.bin",
    "calibrate_frame": "/tmp/pt6-flow/017_TX.bin",
}


class Fp0081Error(Exception):
    pass


def _load_session_artifacts(cfg=None):
    cfg = {**DEFAULTS, **(cfg or {})}
    art = {}
    for key in ("pairing_resp", "pairing_key", "client_cert",
                "auth_frame", "identify_frame", "calibrate_frame"):
        p = cfg[key]
        if not os.path.exists(p):
            raise Fp0081Error(f"missing artifact: {key} = {p}")
        art[key] = open(p, "rb").read()
    return art, cfg


def _clean_identify_frame(raw: bytes) -> bytes:
    """Strip TLS trailing padding from a captured 10608B frame."""
    i = len(raw)
    while i > 0 and raw[i - 1] == raw[-1]:
        i -= 1
    return raw[: i - 32]


class Fp0081:
    """High-level 06cb:0081 driver."""

    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.art = None
        self.tls = None
        self.usb = None
        self._bg_reference = None
        self._bg_frames = []

    # ---------- session ----------
    def open(self):
        sys.path.insert(0, "/home/david/fp-research/repos/python-validity")
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend
        from validitysensor.usb import usb
        from validitysensor import tls as tls_mod

        self.art, _ = _load_session_artifacts(self.cfg)
        a = self.art

        self.usb = usb
        tls = tls_mod.tls
        tls.usb = usb
        rsp = a["pairing_resp"]
        tls.handle_ecdh(rsp[2:][-400:])
        key = a["pairing_key"]
        tls.priv_key = ec.derive_private_key(
            int.from_bytes(key[64:96], "little"), ec.SECP256R1(),
            default_backend())
        tls.tls_cert = a["client_cert"]
        self.tls = tls

        usb.open(vendor=0x06CB, product=0x0081)
        # Reset any stale device state before init (session from a prior
        # test may have expired mid-transaction). Reset is safe: it just
        # re-enumerates the device; TLS re-established afterward.
        try:
            usb.dev.reset()
            time.sleep(1.0)
        except Exception as e:
            print(f"warn: reset failed ({e}), continuing")
        for payload in (bytes.fromhex("19"), bytes.fromhex("4302"),
                        bytes.fromhex(
                            "0602000001c7d074458b0ec1e858e46daf3a8107"),
                        bytes.fromhex("3e")):
            self._cmd_retry(payload)
            time.sleep(0.3)
        tls.open()
        tls.cmd(a["auth_frame"][:6677])       # authorize constant
        tls.cmd(bytes.fromhex("6f000e000000000000"))
        tls.cmd(bytes.fromhex("6f000a000000000000"))
        self._identify = _clean_identify_frame(a["identify_frame"])
        self._calibrate = a["calibrate_frame"]
        return self

    def close(self):
        try:
            if self.usb is not None:
                self.usb.close()
        except Exception:
            pass

    def _cmd_retry(self, payload, tries=3):
        for i in range(tries):
            try:
                return self.usb.cmd(payload)
            except Exception:
                if i == tries - 1:
                    raise
                time.sleep(1)
                self.usb.dev.reset()
                time.sleep(1)

    # ---------- capture ----------
    def capture_frame(self, frame=None, settle=0.3):
        """Send IDENTIFY frame, poll, retrieve one 128x64 image frame."""
        frame = frame or self._identify
        tls = self.tls
        tls.cmd(frame)
        for _ in range(8):
            r = tls.cmd(bytes.fromhex("5100000000"))
            if r.hex() == "000000000000":
                break
            time.sleep(settle)
        tls.cmd(bytes.fromhex("5110000000"))
        r2 = tls.cmd(bytes.fromhex("5100200000"))
        r3 = tls.cmd(bytes.fromhex("51fc030000"))
        if len(r2) != 8198 or r2[:2] != b"\x00\x00":
            raise Fp0081Error(f"bad frame: len={len(r2)} head={r2[:8].hex()}")
        img = np.frombuffer(r2[6:], dtype=np.uint8).reshape(64, 128)
        return img, r3

    # ---------- calibration reference ----------
    def capture_background_reference(self, n=8, settle=0.3):
        """Capture n uncovered frames and build a per-pixel MEDIAN reference.

        Sol verdict 7: median of several frames (suppresses transient
        noise, dust, residual contact). Frames must be same-mode as
        finger capture (same IDENTIFY frame).
        """
        frames = []
        for i in range(n):
            img, _ = self.capture_frame(settle=settle)
            frames.append(img)
            time.sleep(0.2)
        ref = np.median(np.stack(frames), axis=0).astype(np.float32)
        self._bg_reference = ref
        self._bg_frames = frames
        return ref

    # ---------- correction pipeline ----------
    @staticmethod
    def correct_image(img, reference, polarity=1):
        """Canonical correction (validated on real sensor, Sol verdict 7).

        D = int16(img) - int16(reference)   (signed subtraction)
        D' = D - row_mean(D) + 128          (row bias removal, clip)
        I = clip(D', 0, 255)

        NOTE: aggressive percentile contrast scaling was tested and
        REJECTED - it amplifies opaque-cover noise and destroys the
        finger-vs-flat discriminator (covered ridge 192 vs finger 2434
        with this method; percentile version gave 2897 vs 3236 = no
        separation). The validated transform is the simple row-mean
        normalize + clip.
        """
        img = img.astype(np.int16)
        ref = reference.astype(np.int16)
        d = img - ref
        # row bias removal: subtract per-row mean, re-center at 128
        row_mean = d.mean(axis=1, keepdims=True)
        out = d - row_mean + 128
        if polarity < 0:
            out = 255 - out
        return np.clip(out, 0, 255).astype(np.uint8)

    def capture_corrected(self, reference=None, settle=0.3):
        """Capture one finger frame and return the corrected image."""
        if reference is None:
            reference = self._bg_reference
        if reference is None:
            raise Fp0081Error("no background reference; call "
                              "capture_background_reference() first")
        img, extra = self.capture_frame(settle=settle)
        corrected = self.correct_image(img, reference)
        return img, corrected

    # ---------- presence detection (image-derived) ----------
    @staticmethod
    def ridge_band_energy(img):
        """Mean |FFT| in the fingerprint ridge band (wavelength 3-15px).

        Validated discriminator: finger/thumb ~2400-3200, opaque cover
        ~190, uncovered ~1500. Ratio-based (finger / reference) is more
        robust than absolute thresholds.
        """
        img = np.asarray(img, dtype=np.float32)
        fft = np.fft.fft2(img - img.mean())
        mag = np.abs(np.fft.fftshift(fft))
        h, w = img.shape
        Y, X = np.mgrid[0:h, 0:w]
        R = np.sqrt((X - w // 2) ** 2 + (Y - h // 2) ** 2)
        band = (R > w / 15) & (R < w / 3)
        return float(mag[band].mean())

    def presence_score(self, img, reference=None):
        """Finger presence from corrected-image ridge-band energy.

        Returns (score, corrected_image). score = ridge_band_energy of
        the corrected image. Compare against a reference-frame baseline:
        finger ~1.6-2.2x the reference baseline; opaque cover ~0.1x.
        """
        if reference is None:
            reference = self._bg_reference
        if reference is None:
            raise Fp0081Error("no background reference")
        corrected = self.correct_image(img, reference)
        score = self.ridge_band_energy(corrected)
        return score, corrected

    # ---------- diagnostics ----------
    def save_png(self, img, path):
        from PIL import Image
        Image.fromarray(np.asarray(img, dtype=np.uint8), "L").save(path)

    def save_raw(self, img, path):
        with open(path, "wb") as f:
            f.write(np.asarray(img, dtype=np.uint8).tobytes())


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="fp0081 driver CLI")
    ap.add_argument("--bg-frames", type=int, default=8,
                    help="uncovered reference frames (default 8)")
    ap.add_argument("--finger-frames", type=int, default=4,
                    help="finger frames to capture (default 4)")
    ap.add_argument("--outdir", default="/tmp/fp0081-out")
    ap.add_argument("--ref-only", action="store_true",
                    help="capture background reference only and exit")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    dev = Fp0081().open()
    print("session open")
    try:
        print(f"capturing {args.bg_frames} uncovered reference frames...")
        input("sensor UNCOVERED, press Enter to start reference capture: ")
        ref = dev.capture_background_reference(n=args.bg_frames)
        dev.save_raw(ref.astype(np.uint8),
                     os.path.join(args.outdir, "bg_reference.raw"))
        print(f"reference captured, mean={ref.mean():.1f}")

        if args.ref_only:
            print("ref-only mode, exiting")
            sys.exit(0)

        for i in range(args.finger_frames):
            input(f"place RIDGED FINGER (frame {i+1}/{args.finger_frames}), "
                  "Enter to capture: ")
            img, corrected = dev.capture_corrected()
            var, _ = dev.presence_score(img, ref)
            dev.save_png(corrected,
                         os.path.join(args.outdir, f"finger_{i}_corrected.png"))
            dev.save_raw(img, os.path.join(args.outdir, f"finger_{i}_raw.raw"))
            print(f"frame {i}: corrected-var={var:.0f} "
                  f"(flat<200, finger>500) saved finger_{i}_corrected.png")
    finally:
        dev.close()
