#!/usr/bin/env python3
"""Analyze TGQQ attach-panel screenshots with ImageMagick pixel sampling."""
import subprocess, sys, math, os, tempfile

def load_image(path):
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
        ppm = f.name
    subprocess.check_call(["magick", path, "-depth", "8", ppm], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(ppm, "rb") as f:
        header = f.read(100)
        tokens = header.split()
        assert tokens[0] == b"P6", f"Not P6: {tokens[0]}"
        w, h = int(tokens[1]), int(tokens[2])
        header_len = header.find(tokens[3]) + len(tokens[3])
        f.seek(header_len)
        data = f.read(w*h*3)
    os.unlink(ppm)
    arr = []
    for y in range(h):
        row = []
        base = y*w*3
        for x in range(w):
            i = base + x*3
            row.append((data[i], data[i+1], data[i+2]))
        arr.append(row)
    return arr, w, h

def lum(c):
    return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]

def dist(a, b):
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))

def px(img, x, y):
    return img[y][x]

def is_white(c, thr=248):
    return c[0] >= thr and c[1] >= thr and c[2] >= thr

WHITE = (255, 255, 255)

# ---------------------------------------------------------------------------
# Panel detection
# ---------------------------------------------------------------------------
def row_mean_lum(img, y, w):
    return sum(lum(img[y][x]) for x in range(w)) / w

def detect_panel_mobile(img, w, h, lum_thr=210):
    means = [row_mean_lum(img, y, w) for y in range(h)]
    best_start = h; best_len = 0
    cur_start = h
    for y in range(h-1, -1, -1):
        if means[y] > lum_thr:
            if cur_start == h:
                cur_start = y
        else:
            if cur_start != h:
                length = cur_start - y
                if length > best_len:
                    best_len = length
                    best_start = cur_start
                cur_start = h
    if cur_start != h:
        length = cur_start + 1
        if length > best_len:
            best_len = length
            best_start = cur_start
    panel_top = best_start - best_len + 1
    panel_bottom = best_start
    y_mid = (panel_top + panel_bottom) // 2
    left = next((x for x in range(w) if is_white(img[y_mid][x], 245)), 0)
    right = next((x for x in range(w-1, -1, -1) if is_white(img[y_mid][x], 245)), w-1)
    boundary = {}
    for x in range(w):
        for y in range(panel_top, panel_bottom+1):
            if is_white(img[y][x], 245):
                boundary[x] = y
                break
    baseline = min(boundary.values()) if boundary else panel_top
    return {
        "w": w, "h": h,
        "left": left, "right": right,
        "top": panel_top, "bottom": panel_bottom,
        "height": panel_bottom - panel_top + 1,
        "boundary": boundary,
        "baseline": baseline,
    }

def detect_panel_tablet(img, w, h):
    max_lum = [max(lum(img[y][x]) for x in range(w)) for y in range(h)]
    runs = []
    start = None
    for y in range(h):
        if max_lum[y] > 250:
            if start is None:
                start = y
        else:
            if start is not None:
                runs.append((start, y-1))
                start = None
    if start is not None:
        runs.append((start, h-1))
    runs = [(a,b) for a,b in runs if a > h//3]
    if not runs:
        return None
    y0, y1 = max(runs, key=lambda r: r[1]-r[0])
    y_mid = (y0 + y1) // 2
    left = next((x for x in range(w) if is_white(img[y_mid][x], 245)), 0)
    right = next((x for x in range(w-1, -1, -1) if is_white(img[y_mid][x], 245)), w-1)
    # refine: expand left/right as long as white-ish
    while left > 0 and is_white(img[y_mid][left-1], 240):
        left -= 1
    while right < w-1 and is_white(img[y_mid][right+1], 240):
        right += 1
    return {
        "w": w, "h": h,
        "left": left, "right": right,
        "top": y0, "bottom": y1,
        "width": right-left+1,
        "height": y1-y0+1,
    }

# ---------------------------------------------------------------------------
# Icon detection & measurement
# ---------------------------------------------------------------------------
def measure_icon(img, cx, cy, win_radius=35):
    """Measure icon circle diameter using centroid of background pixels."""
    h, w = len(img), len(img[0])
    win = []
    for dy in range(-win_radius, win_radius+1):
        for dx in range(-win_radius, win_radius+1):
            x, y = cx+dx, cy+dy
            if 0 <= x < w and 0 <= y < h:
                d = dist(img[y][x], WHITE)
                if 4 < d < 70:
                    win.append((x, y, img[y][x], d))
    if not win:
        return None
    # weighted average background color
    total_d = sum(c[3] for c in win)
    bg = tuple(sum(c[2][k] * c[3] for c in win) // total_d for k in range(3))
    d_bg_white = dist(bg, WHITE)
    if d_bg_white < 6:
        return None
    inside = [(x, y) for x, y, c, d in win if dist(c, bg) < d_bg_white * 0.7]
    if len(inside) < 100:
        return None
    centroid_x = sum(p[0] for p in inside) // len(inside)
    centroid_y = sum(p[1] for p in inside) // len(inside)
    thr = max(4, d_bg_white * 0.45)
    radii = []
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        for r in range(5, 70):
            x = int(centroid_x + r * math.cos(rad))
            y = int(centroid_y + r * math.sin(rad))
            if not (0 <= x < w and 0 <= y < h):
                break
            if dist(img[y][x], WHITE) < thr:
                radii.append(r)
                break
    if not radii:
        return None
    radii.sort()
    trimmed = radii[1:-1] if len(radii) >= 4 else radii
    avg_r = sum(trimmed) / len(trimmed)
    return {
        "cx": centroid_x, "cy": centroid_y,
        "bg": bg, "diam": avg_r * 2,
        "inside_count": len(inside),
    }

def detect_icon_grid(img, panel, n_cols=4, n_rows=2):
    pw = panel["right"] - panel["left"] + 1
    ph = panel["bottom"] - panel["top"] + 1
    x_margin = pw / (n_cols * 2)
    # vertical placement: two rows centered in panel, ~70px apart
    top_margin = (ph - 140) / 2
    centers = []
    for row in range(n_rows):
        cy = int(panel["top"] + top_margin + row * 70)
        for col in range(n_cols):
            cx = int(panel["left"] + x_margin + col * (pw / n_cols))
            centers.append((cx, cy))
    return centers

def classify_icon_color(c):
    r, g, b = c
    if b > r+10 and b > g and g > r: return "light blue"
    if r > g+10 and g > b+10: return "light orange"
    if g > r+15 and g > b+10: return "light green"
    if b > r+15 and b > g+10 and g > r: return "light purple"
    if r > g+10 and r > b+10 and b > g-10: return "light red/pink"
    if g > b+10 and b > r+10: return "light cyan"
    if r > g+10 and g > b+10 and b < 200: return "light yellow"
    if max(c)-min(c) < 20: return "light gray"
    return "other"

# ---------------------------------------------------------------------------
# Text / label height
# ---------------------------------------------------------------------------
def estimate_label_height(img, cx, y0, y1):
    """Estimate text height of gray label below an icon."""
    rows = []
    for y in range(y0, y1+1):
        cnt = sum(1 for x in range(cx-25, cx+26) if lum(img[y][x]) < 180 and max(img[y][x])-min(img[y][x]) < 50)
        if cnt >= 1:
            rows.append(y)
    if not rows:
        return None
    runs = []
    start = rows[0]; prev = rows[0]
    for y in rows[1:]:
        if y - prev > 2:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    best = max(runs, key=lambda r: r[1]-r[0])
    return best[0], best[1], best[1]-best[0]+1

# ---------------------------------------------------------------------------
# Mask dimming
# ---------------------------------------------------------------------------
def region_mean_lum(img, x0, y0, x1, y1):
    s = 0
    for y in range(y0, y1+1):
        for x in range(x0, x1+1):
            s += lum(img[y][x])
    return s / ((x1-x0+1)*(y1-y0+1))

def measure_dimming(masked, clean, regions):
    results = []
    for name, (x0, y0, x1, y1) in regions.items():
        ml = region_mean_lum(masked, x0, y0, x1, y1)
        cl = region_mean_lum(clean, x0, y0, x1, y1)
        results.append((name, ml, cl, ml/cl if cl else 0))
    return results

# ---------------------------------------------------------------------------
# Corner radius
# ---------------------------------------------------------------------------
def estimate_corner_radius(boundary, baseline):
    xs = sorted(boundary.keys())
    left_curve = []
    for x in xs:
        if boundary[x] > baseline:
            left_curve.append((x, boundary[x]))
        elif left_curve:
            break
    right_curve = []
    for x in reversed(xs):
        if boundary[x] > baseline:
            right_curve.append((x, boundary[x]))
        elif right_curve:
            break
    return len(left_curve), len(right_curve), left_curve[:5], right_curve[:5]

# ---------------------------------------------------------------------------
# Regression helpers
# ---------------------------------------------------------------------------
def input_bar_info(img, w, h):
    y = h - 30
    row = img[y]
    nonwhite = [(x, row[x]) for x in range(w) if lum(row[x]) < 248]
    if not nonwhite:
        return None
    return nonwhite[0][0], nonwhite[-1][0], nonwhite[-1][0]-nonwhite[0][0]+1

def find_text_height(img, w, h):
    rows = []
    for y in range(180, h-120):
        cnt = sum(1 for x in range(20, w-20) if lum(img[y][x]) < 75 and max(img[y][x])-min(img[y][x]) < 50)
        if cnt >= 4:
            rows.append(y)
    if not rows:
        return None
    runs = []
    start = rows[0]; prev = rows[0]
    for y in rows[1:]:
        if y - prev > 3:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    best = max(runs, key=lambda r: r[1]-r[0])
    return best[0], best[1], best[1]-best[0]+1, len(runs)

def find_avatar_blobs(img, w, h):
    """Find green-ish circular avatars on left side."""
    avatars = []
    for y in range(120, h-100):
        c = img[y][40]
        # green/teal avatar: high G, moderate R/B, saturated
        if c[1] > 200 and c[0] < 150 and c[2] < 150 and max(c)-min(c) > 80:
            avatars.append(y)
    if not avatars:
        return []
    blobs = []
    start = avatars[0]; prev = avatars[0]
    for y in avatars[1:]:
        if y - prev > 6:
            blobs.append((start, prev))
            start = y
        prev = y
    blobs.append((start, prev))
    return blobs

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    base = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
    print("Loading images via ImageMagick PPM conversion...")
    imgs = {}
    for name, fn in [
        ("mobile_panel", "attach-panel.jpg"),
        ("tablet_panel", "attach-panel-tablet.jpg"),
        ("mobile_chat", "mobile-chat.jpg"),
        ("group_chat", "group-chat.jpg"),
    ]:
        path = os.path.join(base, fn)
        img, w, h = load_image(path)
        imgs[name] = (img, w, h)
        print(f"  {fn}: {w}x{h}")

    print("\n" + "="*70)
    print("## 1. attach-panel.jpg (mobile, panel open)")
    print("="*70)
    img, w, h = imgs["mobile_panel"]
    p = detect_panel_mobile(img, w, h)
    print(f"Panel bounds: x=[{p['left']},{p['right']}], y=[{p['top']},{p['bottom']}]")
    print(f"Panel width: {p['right']-p['left']+1}px (spec: full width {w}px) -> {'PASS' if p['right']-p['left']+1 >= w-4 else 'FAIL'}")
    print(f"Panel height: {p['height']}px")
    lr, rr, lc, rc = estimate_corner_radius(p["boundary"], p["baseline"])
    print(f"Panel top flat baseline y≈{p['baseline']}, top corner radius left≈{lr}px, right≈{rr}px (spec: 16px)")
    print(f"  left curve samples: {lc[:5]}, right curve samples: {rc[:5]}")

    print("\nPanel white samples (panel must remain opaque white):")
    for x, y in [(w//2, h-10), (10, h-10), (w-10, h-10), (w//2, (p['top']+h)//2)]:
        c = px(img, x, y)
        ok = min(c) >= 248
        print(f"  ({x},{y}) RGB={c} -> {'PASS' if ok else 'FAIL'}")

    icons = detect_icon_grid(img, p)
    print(f"\n4x2 icon grid measurement (spec: 52px diameter circles):")
    icon_results = []
    for i, (cx, cy) in enumerate(icons):
        m = measure_icon(img, cx, cy)
        if m:
            color_name = classify_icon_color(m["bg"])
            ok = 45 <= m["diam"] <= 58
            icon_results.append({"cx": m["cx"], "cy": m["cy"], "diam": m["diam"], "bg": m["bg"], "color": color_name})
            print(f"  Icon {i+1}: center=({m['cx']},{m['cy']}) bg={m['bg']} color={color_name} measured_diam={m['diam']:.1f}px -> {'PASS' if ok else 'FAIL (close)'}")
        else:
            print(f"  Icon {i+1}: measurement failed at grid ({cx},{cy})")

    if len(icon_results) == 8:
        row1, row2 = icon_results[:4], icon_results[4:]
        gaps = [row1[i+1]["cx"]-row1[i]["cx"] for i in range(3)]
        row_gap = row2[0]["cy"] - row1[0]["cy"]
        print(f"\nGrid column x: row1={[r['cx'] for r in row1]}  row2={[r['cx'] for r in row2]}")
        print(f"Column gaps: {gaps}px (avg {sum(gaps)/len(gaps):.1f}, max-min={max(gaps)-min(gaps)}) -> {'PASS' if max(gaps)-min(gaps) <= 8 else 'FAIL'}")
        print(f"Row gap: {row_gap}px")

    print("\nLabel text height estimates (per icon column):")
    label_heights = []
    for i, ic in enumerate(icon_results):
        y0 = ic["cy"] + 30
        y1 = min(p["bottom"] - 4, ic["cy"] + 60)
        lh = estimate_label_height(img, ic["cx"], y0, y1)
        if lh:
            label_heights.append(lh[2])
            ok = 9 <= lh[2] <= 13
            print(f"  Icon {i+1} label at x={ic['cx']}: y={lh[0]}..{lh[1]} height={lh[2]}px (spec 11px) -> {'PASS' if ok else 'FAIL'}")
    if label_heights:
        print(f"  Average label height: {sum(label_heights)/len(label_heights):.1f}px")

    regions = {
        "chat_bg_top": (20, 180, 100, 260),
        "left_bubble": (20, 320, 160, 400),
        "right_bubble": (220, 450, 360, 530),
    }
    print("\nMask dimming vs mobile-chat.jpg (spec: brightness ~-35%):")
    for name, ml, cl, ratio in measure_dimming(img, imgs["mobile_chat"][0], regions):
        pct = (1-ratio)*100
        print(f"  {name}: masked L={ml:.1f}, clean L={cl:.1f}, ratio={ratio:.2%}, dimming={pct:.1f}% -> {'PASS' if 25 <= pct <= 45 else 'FAIL'}")

    print("\n" + "="*70)
    print("## 2. attach-panel-tablet.jpg (tablet, panel open)")
    print("="*70)
    img_t, wt, ht = imgs["tablet_panel"]
    pt = detect_panel_tablet(img_t, wt, ht)
    if pt:
        print(f"Floating panel: x=[{pt['left']},{pt['right']}], y=[{pt['top']},{pt['bottom']}]")
        print(f"Panel width: {pt['width']}px (spec: ~416px) -> {'PASS' if 390 <= pt['width'] <= 450 else 'FAIL'}")
        print(f"Panel height: {pt['height']}px")
        center = (pt['left']+pt['right'])//2
        print(f"Panel center x={center}, image center={wt//2} -> {'PASS' if abs(center-wt//2) <= 10 else 'FAIL'}")
        print("Panel white samples (all four corners):")
        for x, y in [(pt["left"]+10, pt["top"]+10), (pt["right"]-10, pt["top"]+10),
                     (pt["left"]+10, pt["bottom"]-10), (pt["right"]-10, pt["bottom"]-10)]:
            c = px(img_t, x, y)
            ok = min(c) >= 245
            print(f"  ({x},{y}) RGB={c} -> {'PASS' if ok else 'FAIL'}")
        icons_t = detect_icon_grid(img_t, pt)
        print(f"\nTablet 4x2 icon grid:")
        tablet_icons = []
        for i, (cx, cy) in enumerate(icons_t):
            m = measure_icon(img_t, cx, cy)
            if m:
                color_name = classify_icon_color(m["bg"])
                ok = 45 <= m["diam"] <= 58
                tablet_icons.append({"cx": m["cx"], "cy": m["cy"], "diam": m["diam"], "bg": m["bg"], "color": color_name})
                print(f"  Icon {i+1}: center=({m['cx']},{m['cy']}) bg={m['bg']} color={color_name} measured_diam={m['diam']:.1f}px -> {'PASS' if ok else 'FAIL (close)'}")
            else:
                print(f"  Icon {i+1}: measurement failed at grid ({cx},{cy})")
        if len(tablet_icons) == 8:
            row1, row2 = tablet_icons[:4], tablet_icons[4:]
            gaps = [row1[i+1]["cx"]-row1[i]["cx"] for i in range(3)]
            row_gap = row2[0]["cy"] - row1[0]["cy"]
            print(f"Column gaps: {gaps}px (avg {sum(gaps)/len(gaps):.1f}, max-min={max(gaps)-min(gaps)}) -> {'PASS' if max(gaps)-min(gaps) <= 12 else 'FAIL'}")
            print(f"Row gap: {row_gap}px")
    else:
        print("Tablet panel detection failed.")

    print("\n" + "="*70)
    print("## 3. mobile-chat.jpg (regression: no panel)")
    print("="*70)
    img_mc, wmc, hmc = imgs["mobile_chat"]
    ib = input_bar_info(img_mc, wmc, hmc)
    if ib:
        print(f"Input bar bottom y={hmc-30}: span x=[{ib[0]},{ib[1]}], width={ib[2]}px")
    th = find_text_height(img_mc, wmc, hmc)
    if th:
        print(f"Bubble text height estimate: {th[2]}px (spec: 16px), found {th[3]} text runs -> {'PASS' if 13 <= th[2] <= 19 else 'FAIL'}")
    # Bubble colors: sample known regions
    print("Bubble color samples:")
    for label, x, y in [("left bubble body", 80, 300), ("right bubble body", 244, 480), ("chat bg", 30, 200)]:
        c = px(img_mc, x, y)
        print(f"  {label} ({x},{y}): RGB={c}")

    print("\n" + "="*70)
    print("## 4. group-chat.jpg (regression: group chat, no panel)")
    print("="*70)
    img_gc, wgc, hgc = imgs["group_chat"]
    ibg = input_bar_info(img_gc, wgc, hgc)
    if ibg:
        print(f"Input bar bottom y={hgc-30}: span x=[{ibg[0]},{ibg[1]}], width={ibg[2]}px")
    thg = find_text_height(img_gc, wgc, hgc)
    if thg:
        print(f"Bubble text height estimate: {thg[2]}px (spec: 16px), found {thg[3]} text runs -> {'PASS' if 13 <= thg[2] <= 19 else 'FAIL'}")
    blobs = find_avatar_blobs(img_gc, wgc, hgc)
    print(f"Detected {len(blobs)} green avatar blob(s): {[(b[0], b[1], b[1]-b[0]+1) for b in blobs[:5]]}")
    print("Bubble/avatar color samples:")
    for label, x, y in [("left bubble", 170, 290), ("right bubble", 244, 480), ("avatar", 50, 550), ("chat bg", 100, 100)]:
        c = px(img_gc, x, y)
        print(f"  {label} ({x},{y}): RGB={c}")

if __name__ == "__main__":
    main()
