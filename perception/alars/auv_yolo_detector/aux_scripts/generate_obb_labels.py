#!/usr/bin/env python3
"""
Create YOLO OBB labels (xyxyxyxy) from magenta-background masks.

Example:
python3 generate_obb_labels.py \
  --images-dir images \
  --labels-dir labels \
  --normal-suffix "_DR-NormalCamera.png" \
  --sam-suffix    "_DR-SamCamera.png" \
  --buoy-suffix   "_DR-BuoyCamera.png" \
  --class-map "sam=0,buoy=1" \
  --dist-thr 5 \
  --pad-px 1 \
  --debug-dir debug

In case of improve segmentation needed, add and tune those parameters: --dist-thr, --open-ksize and --close-ksize
Note: --pad-px controls how much padding to add around the detected OBB. Also, debug-dir is optional.
"""

import argparse
from pathlib import Path
import re

import cv2
import numpy as np


# Segmentation using magenta background

BG_RGB_DEFAULT = (218, 0, 207)  # exact background


def extract_foreground_fixed_bg(mask_bgr: np.ndarray,
                                bg_rgb=BG_RGB_DEFAULT,
                                dist_thr: float = 25.0) -> np.ndarray:
    """
    Foreground = pixels far from the known magenta background color.
    Returns binary mask.
    """
    mask_rgb = cv2.cvtColor(mask_bgr, cv2.COLOR_BGR2RGB).astype(np.int16)
    bg = np.array(bg_rgb, dtype=np.int16)[None, None, :]
    dist = np.linalg.norm(mask_rgb - bg, axis=2)
    return (dist > dist_thr).astype(np.uint8) * 255


def keep_largest_component(binary_255: np.ndarray) -> np.ndarray:
    num, labels, stats, _ = cv2.connectedComponentsWithStats(binary_255, connectivity=8)
    if num <= 1:
        return binary_255
    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = 1 + int(np.argmax(areas))
    return np.where(labels == largest_label, 255, 0).astype(np.uint8)

# Morphological cleanup to reduce noise
def morph_cleanup(binary_255: np.ndarray, open_ksize: int, close_ksize: int) -> np.ndarray:
    b = binary_255.copy()
    if open_ksize and open_ksize > 1:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_ksize, open_ksize))
        b = cv2.morphologyEx(b, cv2.MORPH_OPEN, k)
    if close_ksize and close_ksize > 1:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize))
        b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, k)
    return b

# OBB / YOLO formatting

# Past approach: may produce duplicates, some plots look like triangles
def order_points_tl_tr_br_bl(pts_xy: np.ndarray) -> np.ndarray:
    pts = np.asarray(pts_xy, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)[:, 0]
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    return np.stack([tl, tr, br, bl], axis=0)

# New approach: working good with all images tested
def order_points_clockwise_unique(pts_xy: np.ndarray) -> np.ndarray:
    """
    Ordering for 4 points from cv2.boxPoints:
    - Sort by angle around centroid (clockwise)
    - Rotate so the first point is the top-left (min y, then min x)
    Ensures no duplicated indices due to ties in sum/diff heuristics.
    """
    pts = np.asarray(pts_xy, dtype=np.float32)

    c = pts.mean(axis=0)

    # angles around centroid
    ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0])

    # sort by angle (descending for clockwise)
    idx = np.argsort(-ang)
    pts = pts[idx]

    # find top-left point (min y, then min x)
    tl_idx = np.lexsort((pts[:, 0], pts[:, 1]))[0]
    pts = np.roll(pts, -tl_idx, axis=0)

    return pts

# Ensure minimum rectangle side lengths
def minarea_rect_from_binary(binary_255: np.ndarray):
    contours, _ = cv2.findContours(binary_255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    cnt = max(contours, key=cv2.contourArea)
    if cv2.contourArea(cnt) < 1:
        return None
    return cv2.minAreaRect(cnt)  # ((cx,cy),(w,h),angle)


def pad_rect(rect, pad_px: float = 0.0, pad_frac: float = 0.0):
    (cx, cy), (w, h), ang = rect
    w = float(w)
    h = float(h)

    extra = 0.0
    if pad_frac and pad_frac > 0:
        extra += pad_frac * max(w, h)
    if pad_px and pad_px > 0:
        extra += float(pad_px)

    w2 = max(1.0, w + 2.0 * extra)
    h2 = max(1.0, h + 2.0 * extra)
    return ((cx, cy), (w2, h2), ang)


def to_yolo_obb_line(class_id: int, rect, img_w: int, img_h: int) -> str:
    box = cv2.boxPoints(rect)  # 4x2
    ordered = order_points_clockwise_unique(box)
    ordered[:, 0] /= float(img_w)
    ordered[:, 1] /= float(img_h)
    ordered = np.clip(ordered, 0.0, 1.0)
    coords = " ".join(f"{v:.6f}" for v in ordered.reshape(-1))

    return f"{class_id} {coords}"


def parse_class_map(s: str) -> dict:
    out = {}
    for item in s.split(","):
        k, v = item.split("=")
        out[k.strip()] = int(v.strip())
    return out


# Filename reading (multi-digit) 

def numeric_prefix(path: Path, normal_suffix: str) -> str | None:
    """
    Supports multi-digit prefixes:
      2_DR-NormalCamera.png
      10_DR-NormalCamera.png
    """
    name = path.name
    if not name.endswith(normal_suffix):
        return None
    prefix_part = name[: -len(normal_suffix)]
    m = re.match(r"^(\d+)$", prefix_part)
    if not m:
        return None
    return m.group(1)


def main():
    ap = argparse.ArgumentParser()

    # input/output dirs
    ap.add_argument("--images-dir", required=True, type=Path)
    ap.add_argument("--labels-dir", required=True, type=Path)

    ap.add_argument("--normal-suffix", default="_DR-NormalCamera.png")
    ap.add_argument("--sam-suffix", default="_DR-SamCamera.png")
    ap.add_argument("--buoy-suffix", default="_DR-BuoyCamera.png")

    ap.add_argument("--class-map", default="sam=0,buoy=1")

    # Background color + threshold
    ap.add_argument("--bg-rgb", default="218,0,207", help="Exact background RGB")
    ap.add_argument("--dist-thr", type=float, default=25.0, help="RGB distance threshold to bg")

    # Padding
    ap.add_argument("--pad-px", type=float, default=0.0)
    ap.add_argument("--pad-frac", type=float, default=0.0)

    # Morphology
    ap.add_argument("--open-ksize", type=int, default=0, help="Odd int. 0 disables.")
    ap.add_argument("--close-ksize", type=int, default=0, help="Odd int. 0 disables.")

    # Debug drawings
    ap.add_argument("--debug-dir", type=Path, default=None)
    args = ap.parse_args()

    images_dir = args.images_dir.expanduser()
    labels_dir = args.labels_dir.expanduser()
    labels_dir.mkdir(parents=True, exist_ok=True)

    debug_dir = args.debug_dir.expanduser() if args.debug_dir else None
    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)

    class_map = parse_class_map(args.class_map)

    bg_rgb = tuple(int(x.strip()) for x in args.bg_rgb.split(","))
    if len(bg_rgb) != 3:
        raise ValueError("--bg-rgb must be like '218,0,207'")

    normals = sorted(images_dir.glob(f"*{args.normal_suffix}"))
    if not normals:
        raise FileNotFoundError(f"No normal images found in {images_dir} matching '*{args.normal_suffix}'.")

    n_ok, n_skip = 0, 0

    for normal_path in normals:
        prefix = numeric_prefix(normal_path, args.normal_suffix)
        if prefix is None:
            n_skip += 1
            continue

        sam_path = images_dir / f"{prefix}{args.sam_suffix}"
        buoy_path = images_dir / f"{prefix}{args.buoy_suffix}"

        if not sam_path.exists() or not buoy_path.exists():
            print(f"[SKIP] Missing masks for prefix {prefix}: sam={sam_path.exists()} buoy={buoy_path.exists()}")
            n_skip += 1
            continue

        full_bgr = cv2.imread(str(normal_path), cv2.IMREAD_COLOR)
        if full_bgr is None:
            print(f"[SKIP] Could not read full image: {normal_path}")
            n_skip += 1
            continue

        img_h, img_w = full_bgr.shape[:2]
        lines = []
        debug = full_bgr.copy() if debug_dir else None

        def process_mask(mask_path: Path, class_key: str, dbg_color_bgr):
            nonlocal lines, debug
            if class_key not in class_map:
                return

            mask_bgr = cv2.imread(str(mask_path), cv2.IMREAD_COLOR)
            if mask_bgr is None:
                return

            fg = extract_foreground_fixed_bg(mask_bgr, bg_rgb=bg_rgb, dist_thr=args.dist_thr)
            fg = keep_largest_component(fg)

            if args.open_ksize or args.close_ksize:
                fg = morph_cleanup(fg, args.open_ksize, args.close_ksize)

            rect = minarea_rect_from_binary(fg)
            if rect is None:
                return

            if args.pad_px > 0 or args.pad_frac > 0:
                
                rect = pad_rect(rect, pad_px=args.pad_px, pad_frac=args.pad_frac)

            lines.append(to_yolo_obb_line(class_map[class_key], rect, img_w, img_h))

            # Only in case want to see the debug drawing (not necessary for label generation)
            if debug is not None:
                box = cv2.boxPoints(rect)
                pts = order_points_clockwise_unique(box).astype(np.int32)
                cv2.polylines(debug, [pts], True, dbg_color_bgr, 2)

        process_mask(sam_path, "sam", (255, 0, 0))        # blue
        process_mask(buoy_path, "buoy", (255, 200, 100))        # light blue

        out_txt = labels_dir / f"{normal_path.stem}.txt"
        out_txt.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

        if debug_dir:
            out_dbg = debug_dir / f"{normal_path.stem}_debug.png"
            cv2.imwrite(str(out_dbg), debug)

        n_ok += 1
        print(f"[OK] {prefix}: wrote {out_txt.name} ({len(lines)} objects)")

    print(f"\nDone. OK: {n_ok}, skipped: {n_skip}")


if __name__ == "__main__":
    main()
