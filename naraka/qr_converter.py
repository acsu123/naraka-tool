import re
from pathlib import Path
from urllib.parse import unquote

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

from .config import NARAKA_BASE, CONVERTED_SUFFIX, CONVERTED_DIR, SOURCE_HOST


def extract_share_code(url: str):
    m = re.search(r"shareCode=([A-Za-z0-9_\-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"shareCode=([A-Za-z0-9_\-]+)", unquote(url))
    return m.group(1) if m else None


def is_source_qr(url: str) -> bool:
    return SOURCE_HOST in url


def build_converted_url(code: str) -> str:
    return f"{NARAKA_BASE}?shareCode={code}{CONVERTED_SUFFIX}"


def _load_font(size: int):
    for p in ["C:/Windows/Fonts/arialuni.ttf", "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _cv2_decode(img) -> list:
    det = cv2.QRCodeDetector()
    found = []
    try:
        ok, infos, pts_arr, _ = det.detectAndDecodeMulti(img)
        if ok and pts_arr is not None:
            for data, pts in zip(infos, pts_arr):
                if data:
                    p = pts.astype(int)
                    x, y = p[:, 0].min(), p[:, 1].min()
                    w, h = p[:, 0].max() - x, p[:, 1].max() - y
                    found.append((data, x, y, w, h))
    except Exception:
        pass
    if not found:
        try:
            data, bbox, _ = det.detectAndDecode(img)
            if data and bbox is not None:
                p = bbox[0].astype(int)
                x, y = p[:, 0].min(), p[:, 1].min()
                w, h = p[:, 0].max() - x, p[:, 1].max() - y
                found.append((data, x, y, w, h))
        except Exception:
            pass
    return found


def detect_qr(cv_img) -> list:
    ih, iw = cv_img.shape[:2]
    out = _cv2_decode(cv_img)
    if out:
        return out
    long_side = max(iw, ih)
    if long_side < 2000:
        scale = max(2.0, 2000 / long_side)
        up = cv2.resize(cv_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        found = _cv2_decode(up)
        if found:
            return [(d, int(x / scale), int(y / scale), int(w / scale), int(h / scale))
                    for d, x, y, w, h in found]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw3 = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    out = _cv2_decode(bw3)
    if out:
        return out
    bw3_up = cv2.resize(bw3, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    found = _cv2_decode(bw3_up)
    return [(d, int(x / 2), int(y / 2), int(w / 2), int(h / 2))
            for d, x, y, w, h in found] if found else []


def make_qr(url: str, size: int) -> Image.Image:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=max(1, size // 40), border=2)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB").resize(
        (size, size), Image.LANCZOS)


def process_image(img_bytes: bytes, filename: str) -> dict:
    nparr = np.frombuffer(img_bytes, np.uint8)
    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if cv_img is None:
        return {"file": filename, "error": "Cannot decode image"}
    qr_list = detect_qr(cv_img)
    if not qr_list:
        return {"file": filename, "error": "No QR code detected"}
    src_qrs = [(d, x, y, w, h) for d, x, y, w, h in qr_list if is_source_qr(d)]
    if not src_qrs:
        return {"file": filename,
                "error": f"QR found but not recognised: {qr_list[0][0][:80]}"}
    pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)).convert("RGB")
    iw, ih = pil.size
    codes = []
    for data, x, y, qw, qh in src_qrs:
        code = extract_share_code(data)
        if not code:
            continue
        sz = max(qw, qh)
        new_qr = make_qr(build_converted_url(code), sz)
        px, py = max(0, x), max(0, y)
        cw, ch = min(sz, iw - px), min(sz, ih - py)
        if cw > 0 and ch > 0:
            pil.paste(new_qr.crop((0, 0, cw, ch)), (px, py))
        codes.append(code)
    if not codes:
        return {"file": filename, "error": "Could not extract shareCode"}
    total_qr = sum(w * h for _, _, _, w, h in src_qrs)
    if iw * ih > total_qr * 4:
        draw = ImageDraw.Draw(pil)
        txt = "QR Chuyen Doi Thanh Cong | from Wang with <3"
        qr_w = max(w for _, _, _, w, _ in src_qrs)
        fsz = max(12, min(28, qr_w // 14))
        font = _load_font(fsz)
        try:
            bb = draw.textbbox((0, 0), txt, font=font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
        except Exception:
            tw, th = qr_w, fsz + 4
        qr_x = min(x for _, x, _, _, _ in src_qrs)
        max_y = max(y + h for _, _, y, _, h in src_qrs)
        tx, ty = qr_x, min(max_y + 6, ih - th - 4)
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
            draw.text((tx + ox, ty + oy), txt, fill=(0, 0, 0), font=font)
        draw.text((tx, ty), txt, fill=(255, 255, 255), font=font)
    stem = Path(filename).stem
    out = f"converted_{stem}.png"
    pil.save(str(CONVERTED_DIR / out), "PNG")
    return {"file": filename, "success": True,
            "output": str(CONVERTED_DIR / out), "out_name": out, "codes": codes}
