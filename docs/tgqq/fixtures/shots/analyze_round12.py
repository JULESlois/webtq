#!/usr/bin/env python3
"""Analyze TGQQ Round 12 screenshots: emoji panel & message menu."""
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

def lum(c): return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]
def dist(a, b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
def px(img, x, y): return img[y][x]

def is_white(c, thr=248): return c[0] >= thr and c[1] >= thr and c[2] >= thr
def is_light(c, thr=245): return c[0] >= thr and c[1] >= thr and c[2] >= thr

def row_mean_lum(img, y, w):
    return sum(lum(img[y][x]) for x in range(w)) / w

# ---------------------------------------------------------------------------
# Panel detection (bottom sheet)
# ---------------------------------------------------------------------------
def is_bright_row(img, y, w, thr=200):
    return row_mean_lum(img, y, w) > thr

def find_panel_top(img, w, h, min_panel_height=150):
    """Find the top of the bottom bright sheet by bright-fraction contrast."""
    bright = [is_bright_row(img, y, w) for y in range(h)]
    best_y = 0; best_score = -999
    for y in range(h - min_panel_height, h//2, -1):
        below = sum(bright[y:h]) / (h - y)
        above = sum(bright[max(0, y-40):y]) / 40
        if below < 0.75:
            continue
        score = below - above
        if score > best_score:
            best_score = score
            best_y = y
    return best_y, best_score

def find_input_bar_top(img, w, h, region_top, region_bottom):
    blue_rows = []
    for y in range(region_top, region_bottom+1):
        for x in range(w*2//3, w):
            c = img[y][x]
            if c[2] > c[0]+15 and c[2] > c[1]+15 and c[2] > 150:
                blue_rows.append(y)
                break
    if not blue_rows:
        return None
    top_blue = min(blue_rows)
    for y in range(top_blue, max(region_top-5, 0), -1):
        dark = sum(1 for x in range(w) if lum(img[y][x]) < 220)
        if dark < w * 0.03:
            return y
    return top_blue

def detect_bottom_panel(img, w, h, min_height=120, expect_input_bar=True):
    panel_top, edge_score = find_panel_top(img, w, h)
    if panel_top == 0:
        return None
    region_bottom = h - 1
    panel_bottom = region_bottom
    if expect_input_bar:
        ib_top = find_input_bar_top(img, w, h, max(0, h-140), h-1)
        if ib_top and panel_top <= ib_top - 2 <= h - 1:
            panel_bottom = ib_top - 1
            region_bottom = h - 1
    ph = panel_bottom - panel_top + 1
    if ph < min_height:
        return None
    y_mid = (panel_top + panel_bottom) // 2
    left = next((x for x in range(w) if is_light(img[y_mid][x], 245)), 0)
    right = next((x for x in range(w-1, -1, -1) if is_light(img[y_mid][x], 245)), w-1)
    return {
        "left": left, "right": right,
        "top": panel_top, "bottom": panel_bottom,
        "width": right-left+1, "height": ph,
        "region_top": panel_bottom + 1, "region_bottom": h - 1,
        "y_mid": y_mid,
        "edge_score": edge_score,
    }

def detect_floating_panel(img, w, h):
    """Detect a bright centered card inside a dimmed overlay."""
    card_rows = []
    for y in range(h//6, 5*h//6):
        # Find contiguous bright span around center
        left = None; right = None
        for x in range(w//2, -1, -1):
            if is_light(img[y][x], 200):
                left = x
            else:
                if left is not None and x < w//2 - 140:
                    break
        for x in range(w//2, w):
            if is_light(img[y][x], 200):
                right = x
            else:
                if right is not None and x > w//2 + 140:
                    break
        if left is None or right is None:
            continue
        span = right - left + 1
        center = (left + right) // 2
        # Check surrounding area is darker (overlay)
        dark_left = sum(1 for x in range(max(0, left-60), left) if is_light(img[y][x], 200)) < 5
        dark_right = sum(1 for x in range(right+1, min(w, right+60)) if is_light(img[y][x], 200)) < 5
        if 240 <= span <= 400 and abs(center - w//2) <= 80 and (dark_left or dark_right):
            card_rows.append((y, left, right, span, center))
    if not card_rows:
        return None
    # Use the largest contiguous run of candidate rows (allow small gaps)
    rows = [r[0] for r in card_rows]
    runs = []; start = rows[0]; prev = rows[0]
    for y in rows[1:]:
        if y - prev > 8:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    best = None
    for y0, y1 in runs:
        if y1 - y0 < 120:
            continue
        mid_rows = [r for r in card_rows if y0 <= r[0] <= y1]
        left = min(r[1] for r in mid_rows)
        right = max(r[2] for r in mid_rows)
        width = right - left + 1
        center = (left + right) // 2
        if best is None or (y1-y0, abs(center-w//2)) > (best[1]-best[0], abs(best[4]-w//2)):
            best = (y0, y1, left, right, center, width)
    if not best:
        return None
    y0, y1, left, right, center, width = best
    return {
        "left": left, "right": right,
        "top": y0, "bottom": y1,
        "width": width, "height": y1 - y0 + 1,
        "y_mid": (y0 + y1) // 2,
    }

# ---------------------------------------------------------------------------
# Top boundary & corner radius
# ---------------------------------------------------------------------------
def find_top_boundary(img, panel):
    boundary = {}
    for x in range(panel["left"], panel["right"]+1):
        for y in range(panel["top"], min(panel["top"]+35, panel["bottom"]+1)):
            if is_light(img[y][x], 245):
                boundary[x] = y
                break
    return boundary

def estimate_top_corner_radius(boundary, panel):
    xs = sorted(boundary.keys())
    if not xs:
        return 0, 0, 0, 0, 0, [], []
    baseline = min(boundary.values())
    left_curve = []
    for x in xs:
        y = boundary[x]
        if y > baseline + 1:
            left_curve.append((x, y))
        elif left_curve:
            break
    right_curve = []
    for x in reversed(xs):
        y = boundary[x]
        if y > baseline + 1:
            right_curve.append((x, y))
        elif right_curve:
            break

    def radius_from_curve(curve):
        if len(curve) < 3:
            return 0
        best = (99999, 0)
        for r in range(6, 33):
            cx = curve[0][0] + r
            cy = baseline + r
            err = 0
            for x, y in curve:
                err += abs(math.sqrt((x-cx)**2 + (y-cy)**2) - r)
            avg_err = err / len(curve)
            if avg_err < best[0]:
                best = (avg_err, r)
        return best[1]

    lr_est = radius_from_curve(left_curve)
    rr_est = radius_from_curve(right_curve)
    return len(left_curve), len(right_curve), lr_est, rr_est, baseline, left_curve[:8], right_curve[:8]

# ---------------------------------------------------------------------------
# Separators
# ---------------------------------------------------------------------------
def find_horizontal_separator(img, panel, y_start, y_end, thr=200):
    best_y = None; best_score = 0
    y_start = max(panel["top"], y_start)
    y_end = min(panel["bottom"], y_end)
    for y in range(y_start, y_end+1):
        dark = sum(1 for x in range(panel["left"], panel["right"]+1) if lum(img[y][x]) < thr)
        if dark > best_score:
            best_score = dark
            best_y = y
    return best_y, best_score

def detect_category_bar_bottom(img, panel):
    return find_horizontal_separator(img, panel, panel["top"]+25, panel["top"]+90, thr=200)

def detect_tab_bar_top(img, panel):
    return find_horizontal_separator(img, panel, panel["bottom"]-75, panel["bottom"]-10, thr=220)

# ---------------------------------------------------------------------------
# Tab bar icons
# ---------------------------------------------------------------------------
def sample_tab_icons(img, panel, tab_top):
    tab_h = panel["bottom"] - tab_top
    y = tab_top + tab_h // 2
    span = panel["right"] - panel["left"]
    centers = [int(panel["left"] + span * (i+1) / 6) for i in range(5)]
    samples = []
    for cx in centers:
        r = g = b = n = 0
        for dx in range(-8, 9):
            for dy in range(-8, 9):
                xx, yy = cx+dx, y+dy
                if panel["left"] <= xx <= panel["right"] and tab_top <= yy <= panel["bottom"]:
                    c = px(img, xx, yy)
                    if not is_light(c, 250):
                        r += c[0]; g += c[1]; b += c[2]; n += 1
        if n:
            avg = (r//n, g//n, b//n)
            if avg[2] > avg[0]+25 and avg[2] > avg[1]+20 and avg[2] > 150:
                label = "blue"
            elif max(avg)-min(avg) < 45:
                label = "gray"
            else:
                label = "other"
            samples.append((cx, y, avg, label))
        else:
            samples.append((cx, y, (255,255,255), "empty"))
    return samples, tab_h

# ---------------------------------------------------------------------------
# Emoji grid
# ---------------------------------------------------------------------------
def detect_emoji_grid_rows(img, panel, cat_bottom, tab_top):
    region_top = cat_bottom + 8 if cat_bottom else panel["top"] + 50
    region_bottom = tab_top - 8 if tab_top else panel["bottom"] - 50
    if region_bottom <= region_top:
        return []
    rows = []
    for y in range(region_top, region_bottom+1):
        dark = sum(1 for x in range(panel["left"], panel["right"]+1) if lum(img[y][x]) < 210)
        if dark > (panel["right"]-panel["left"]+1) * 0.12:
            rows.append(y)
    if not rows:
        return []
    runs = []; start = rows[0]; prev = rows[0]
    for y in rows[1:]:
        if y - prev > 3:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    return [(s, e, e-s+1) for s, e in runs if e-s+1 >= 3]

# ---------------------------------------------------------------------------
# Message menu rows
# ---------------------------------------------------------------------------
def detect_message_menu_rows(img, panel, n_rows=6):
    """Detect evenly-spaced menu rows by cross-correlation with expected spacing."""
    y0 = panel["top"] + 8
    y1 = panel["bottom"]
    signal = []
    for y in range(y0, y1+1):
        cnt = sum(1 for x in range(panel["left"]+15, panel["right"]-15) if lum(img[y][x]) < 180)
        signal.append(cnt)
    # Try candidate spacings (36..52) and offsets
    best = (0, 0, [], -1)
    for spacing in range(26, 53):
        for off in range(0, spacing):
            rows = []
            valid = True
            for i in range(n_rows):
                idx = off + i*spacing
                if idx >= len(signal):
                    valid = False
                    break
                rows.append(idx)
            if not valid:
                continue
            score = sum(signal[idx] for idx in rows)
            last_y = y0 + rows[-1]
            if last_y + spacing//2 > y1:
                continue
            if score > best[3] or (score == best[3] and abs(spacing-48) < abs(best[1]-48)):
                best = (off, spacing, rows, score)
    if not best[3]:
        return []
    off, spacing, row_indices, _ = best
    rows = []
    for idx in row_indices:
        cy = y0 + idx
        s = max(panel["top"]+2, cy - spacing//2)
        e = min(panel["bottom"]-2, cy + spacing//2 - 1)
        rows.append((s, e, e - s + 1))
    return rows

# ---------------------------------------------------------------------------
# Mask dimming
# ---------------------------------------------------------------------------
def region_mean_lum(img, x0, y0, x1, y1):
    s = 0; n = 0
    for y in range(y0, y1+1):
        for x in range(x0, x1+1):
            s += lum(img[y][x]); n += 1
    return s / n if n else 0

def measure_dimming(masked, clean, regions):
    results = []
    for name, (x0, y0, x1, y1) in regions.items():
        ml = region_mean_lum(masked, x0, y0, x1, y1)
        cl = region_mean_lum(clean, x0, y0, x1, y1)
        results.append((name, ml, cl, ml/cl if cl else 0))
    return results

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

def find_text_runs(img, x0, x1, y0, y1, dark_thr=80):
    rows = []
    for y in range(y0, y1+1):
        cnt = sum(1 for x in range(x0, x1+1) if lum(img[y][x]) < dark_thr)
        if cnt >= 3:
            rows.append(y)
    if not rows: return []
    runs = []; start = rows[0]; prev = rows[0]
    for y in rows[1:]:
        if y - prev > 2:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    return runs

def find_names_blue(img, w, h):
    blue_rows = []
    for y in range(140, h-120):
        cnt = sum(1 for x in range(30, w-30) if img[y][x][2] > img[y][x][0]+30 and img[y][x][2] > img[y][x][1]+20 and 80 < lum(img[y][x]) < 200)
        if cnt >= 3:
            blue_rows.append(y)
    if not blue_rows: return []
    runs = []; start = blue_rows[0]; prev = blue_rows[0]
    for y in blue_rows[1:]:
        if y - prev > 2:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    return [r for r in runs if r[1]-r[0]+1 >= 8]

def fmt_px(c):
    return f"RGB=({c[0]},{c[1]},{c[2]})"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    base = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
    print("Loading images via ImageMagick PPM conversion...")
    imgs = {}
    for name, fn in [
        ("emoji_m", "emoji-panel.jpg"),
        ("emoji_t", "emoji-panel-tablet.jpg"),
        ("menu_m", "message-menu.jpg"),
        ("menu_t", "message-menu-tablet.jpg"),
        ("group", "group-chat.jpg"),
        ("mobile", "mobile-chat.jpg"),
        ("tablet", "tablet-mid.jpg"),
        ("group_t", "group-chat-tablet.jpg"),
    ]:
        path = os.path.join(base, fn)
        img, w, h = load_image(path)
        imgs[name] = (img, w, h)
        print(f"  {fn}: {w}x{h}")

    # ============================================================
    print("\n" + "="*70)
    print("## 1. emoji-panel.jpg (mobile emoji panel)")
    print("="*70)
    img, w, h = imgs["emoji_m"]
    clean, wc, hc = imgs["mobile"]
    p = detect_bottom_panel(img, w, h, min_height=120, expect_input_bar=True)
    if not p:
        print("ERROR: mobile emoji panel not detected")
        return
    print(f"Panel bounds: x=[{p['left']},{p['right']}], y=[{p['top']},{p['bottom']}]")
    print(f"Panel width: {p['width']}px (spec: full width {w}px) -> {'PASS' if p['width'] >= w-4 else 'FAIL'}")
    print(f"Panel height: {p['height']}px")
    print(f"Input bar region below panel: y=[{p['region_top']},{p['region_bottom']}]")
    gap = max(0, p['region_top'] - (p['bottom'] + 1))
    print(f"Panel bottom={p['bottom']}, input bar top={p['region_top']}, gap={gap}px (spec: 0) -> {'PASS' if gap <= 2 else 'FAIL'}")

    boundary = find_top_boundary(img, p)
    lr, rr, lr_est, rr_est, baseline, lc, rc = estimate_top_corner_radius(boundary, p)
    print(f"Top rounded corners: baseline y={baseline}, extent L={lr}px R={rr}px, radius L≈{lr_est}px R≈{rr_est}px (spec: 16px) -> {'PASS' if 12 <= lr_est <= 22 and 12 <= rr_est <= 22 else 'FAIL'}")
    print(f"  left curve: {lc}")
    print(f"  right curve: {rc}")

    cat_y, cat_score = detect_category_bar_bottom(img, p)
    tab_y, tab_score = detect_tab_bar_top(img, p)
    print(f"Category bar separator y≈{cat_y}, coverage={cat_score}/{p['width']}")
    print(f"Tab bar separator y≈{tab_y}, coverage={tab_score}/{p['width']}")
    if cat_y:
        cat_h = cat_y - p['top']
        print(f"Category bar height: {cat_h}px")
    if tab_y:
        tab_h = p['bottom'] - tab_y
        print(f"Tab bar height: {tab_h}px (spec: 48px) -> {'PASS' if 42 <= tab_h <= 55 else 'FAIL'}")
        samples, _ = sample_tab_icons(img, p, tab_y)
        print(f"Tab bar icon colors: {[(cx, fmt_px(c), label) for cx,_,c,label in samples]}")
        active_blue = any(label == "blue" for _,_,_,label in samples)
        print(f"Active tab blue highlight -> {'PASS' if active_blue else 'FAIL (no blue)'}")
    else:
        print("Tab bar not detected")

    rows = detect_emoji_grid_rows(img, p, cat_y, tab_y)
    print(f"Detected emoji grid row clusters: {rows[:10]}")
    if len(rows) >= 4:
        row_heights = [r[2] for r in rows]
        print(f"Emoji row heights: {row_heights}")
        gaps = [rows[i+1][0] - rows[i][1] for i in range(min(6, len(rows)-1))]
        print(f"Row gaps: {gaps} (spec: 8px)")

    # Mask dimming samples above the panel
    regions = {
        "chat_bg_top": (20, 120, 100, 220),
        "left_bubble": (20, 250, 140, 340),
        "right_bubble": (250, 420, 360, 520),
    }
    print("Mask dimming vs mobile-chat.jpg:")
    for name, ml, cl, ratio in measure_dimming(img, clean, regions):
        pct = (1-ratio)*100
        print(f"  {name}: masked L={ml:.1f}, clean L={cl:.1f}, dimming={pct:.1f}% -> {'PASS' if 25 <= pct <= 55 else 'FAIL'}")

    # ============================================================
    print("\n" + "="*70)
    print("## 2. emoji-panel-tablet.jpg (tablet emoji panel)")
    print("="*70)
    img_t, wt, ht = imgs["emoji_t"]
    clean_t, wct, hct = imgs["tablet"]
    pt = detect_bottom_panel(img_t, wt, ht, min_height=120, expect_input_bar=True)
    if not pt:
        print("ERROR: tablet emoji panel not detected; trying fallback...")
        pt = detect_bottom_panel(img_t, wt, ht, min_height=80, expect_input_bar=False)
    if not pt:
        print("ERROR: tablet emoji panel still not detected")
    else:
        print(f"Panel bounds: x=[{pt['left']},{pt['right']}], y=[{pt['top']},{pt['bottom']}]")
        print(f"Panel width: {pt['width']}px")
        print(f"Panel height: {pt['height']}px")
        print(f"Panel spans full chat area -> {'PASS' if pt['left'] <= 10 and pt['right'] >= wt-10 else 'FAIL'}")
        print(f"Input bar region below: y=[{pt['region_top']},{pt['region_bottom']}]")
        gap_t = max(0, pt['region_top'] - (pt['bottom'] + 1))
        print(f"Panel-input bar gap={gap_t}px -> {'PASS' if gap_t <= 2 else 'FAIL'}")
        boundary_t = find_top_boundary(img_t, pt)
        lr_t, rr_t, lr_est_t, rr_est_t, baseline_t, lc_t, rc_t = estimate_top_corner_radius(boundary_t, pt)
        print(f"Top corner radius L≈{lr_est_t}px R≈{rr_est_t}px (spec: 16px) -> {'PASS' if 12 <= lr_est_t <= 22 and 12 <= rr_est_t <= 22 else 'FAIL'}")
        cat_y_t, _ = detect_category_bar_bottom(img_t, pt)
        tab_y_t, _ = detect_tab_bar_top(img_t, pt)
        if cat_y_t:
            print(f"Category bar height: {cat_y_t-pt['top']}px")
        if tab_y_t:
            print(f"Tab bar height: {pt['bottom']-tab_y_t}px (spec: 48px) -> {'PASS' if 42 <= pt['bottom']-tab_y_t <= 55 else 'FAIL'}")
            samples_t, _ = sample_tab_icons(img_t, pt, tab_y_t)
            print(f"Tab icon colors: {[(cx, fmt_px(c), label) for cx,_,c,label in samples_t]}")
            active_blue_t = any(label == "blue" for _,_,_,label in samples_t)
            print(f"Active tab blue highlight -> {'PASS' if active_blue_t else 'FAIL'}")
        regions_t = {
            "chat_bg_top": (250, 120, 450, 180),
            "left_bubble_area": (250, 180, 450, 260),
        }
        print("Tablet mask dimming vs tablet-mid.jpg:")
        for name, ml, cl, ratio in measure_dimming(img_t, clean_t, regions_t):
            pct = (1-ratio)*100
            print(f"  {name}: masked L={ml:.1f}, clean L={cl:.1f}, dimming={pct:.1f}% -> {'PASS' if 20 <= pct <= 55 else 'FAIL'}")

    # ============================================================
    print("\n" + "="*70)
    print("## 3. message-menu.jpg (mobile long-press menu)")
    print("="*70)
    img_mm, wmm, hmm = imgs["menu_m"]
    clean_m, wcm, hcm = imgs["group"]
    pm = detect_bottom_panel(img_mm, wmm, hmm, min_height=120, expect_input_bar=False)
    if not pm:
        print("ERROR: mobile message menu not detected")
    else:
        print(f"Menu bounds: x=[{pm['left']},{pm['right']}], y=[{pm['top']},{pm['bottom']}]")
        print(f"Menu width: {pm['width']}px (spec: full width {wmm}px) -> {'PASS' if pm['width'] >= wmm-4 else 'FAIL'}")
        print(f"Menu height: {pm['height']}px")
        boundary_m = find_top_boundary(img_mm, pm)
        lr_m, rr_m, lr_est_m, rr_est_m, baseline_m, lc_m, rc_m = estimate_top_corner_radius(boundary_m, pm)
        print(f"Top corner radius L≈{lr_est_m}px R≈{rr_est_m}px (spec: 16px) -> {'PASS' if 12 <= lr_est_m <= 22 and 12 <= rr_est_m <= 22 else 'FAIL'}")
        rows_m = detect_message_menu_rows(img_mm, pm)
        print(f"Detected menu rows: {rows_m}")
        if len(rows_m) >= 6:
            heights = [r[2] for r in rows_m[:6]]
            print(f"Row heights: {heights} (spec: 48px each) -> {'PASS' if all(42 <= h <= 55 for h in heights) else 'FAIL'}")
            gaps = [rows_m[i+1][0] - rows_m[i][1] for i in range(5)]
            print(f"Row gaps: {gaps} (spec: 0) -> {'PASS' if all(g <= 2 for g in gaps) else 'FAIL'}")
        else:
            print(f"FAIL: only {len(rows_m)} rows detected (expected 6)")
        if rows_m:
            y_mid = (rows_m[0][0] + rows_m[0][1]) // 2
            icon_x = pm["left"] + 25
            text_x = pm["left"] + 75
            icon_c = px(img_mm, icon_x, y_mid)
            text_c = px(img_mm, text_x, y_mid)
            print(f"Row 1 icon ({icon_x},{y_mid}): {fmt_px(icon_c)} -> {'PASS (gray)' if max(icon_c)-min(icon_c) < 70 else 'FAIL'}")
            print(f"Row 1 text ({text_x},{y_mid}): {fmt_px(text_c)} -> {'PASS (dark)' if lum(text_c) < 130 else 'FAIL'}")
        regions_mm = {
            "chat_bg_top": (20, 120, 120, 220),
            "bubble_area": (40, 250, 160, 350),
        }
        print("Mobile menu mask dimming vs group-chat.jpg:")
        for name, ml, cl, ratio in measure_dimming(img_mm, clean_m, regions_mm):
            pct = (1-ratio)*100
            print(f"  {name}: masked L={ml:.1f}, clean L={cl:.1f}, dimming={pct:.1f}% -> {'PASS' if 25 <= pct <= 55 else 'FAIL'}")

    # ============================================================
    print("\n" + "="*70)
    print("## 4. message-menu-tablet.jpg (tablet long-press menu)")
    print("="*70)
    img_mt, wmt, hmt = imgs["menu_t"]
    clean_mt, wcmt, hcmt = imgs["group_t"]
    pmt = detect_floating_panel(img_mt, wmt, hmt)
    if not pmt:
        print("ERROR: tablet message menu not detected")
    else:
        print(f"Menu card bounds: x=[{pmt['left']},{pmt['right']}], y=[{pmt['top']},{pmt['bottom']}]")
        print(f"Menu width: {pmt['width']}px (spec: ~320px) -> {'PASS' if 280 <= pmt['width'] <= 360 else 'FAIL'}")
        print(f"Menu height: {pmt['height']}px")
        center = (pmt['left'] + pmt['right']) // 2
        print(f"Card center x={center}, image center={wmt//2} -> {'PASS' if abs(center - wmt//2) <= 30 else 'FAIL'}")
        boundary_mt = find_top_boundary(img_mt, pmt)
        lr_mt, rr_mt, lr_est_mt, rr_est_mt, baseline_mt, lc_mt, rc_mt = estimate_top_corner_radius(boundary_mt, pmt)
        print(f"Corner radius L≈{lr_est_mt}px R≈{rr_est_mt}px (spec: 16px) -> {'PASS' if 12 <= lr_est_mt <= 22 and 12 <= rr_est_mt <= 22 else 'FAIL'}")
        rows_mt = detect_message_menu_rows(img_mt, pmt)
        print(f"Detected menu rows: {rows_mt}")
        if len(rows_mt) >= 6:
            heights = [r[2] for r in rows_mt[:6]]
            print(f"Row heights: {heights}")
        else:
            print(f"FAIL: only {len(rows_mt)} rows detected (expected 6)")
        regions_mt = {
            "chat_bg_top": (200, 120, 400, 200),
            "left_bubble_area": (50, 180, 180, 260),
        }
        print("Tablet menu mask dimming vs group-chat-tablet.jpg:")
        for name, ml, cl, ratio in measure_dimming(img_mt, clean_mt, regions_mt):
            pct = (1-ratio)*100
            print(f"  {name}: masked L={ml:.1f}, clean L={cl:.1f}, dimming={pct:.1f}% -> {'PASS' if 20 <= pct <= 55 else 'FAIL'}")

    # ============================================================
    print("\n" + "="*70)
    print("## 5. group-chat.jpg (regression)")
    print("="*70)
    img_g, wg, hg = imgs["group"]
    ibg = input_bar_info(img_g, wg, hg)
    if ibg:
        print(f"Input bar bottom y={hg-30}: x=[{ibg[0]},{ibg[1]}], width={ibg[2]}px")
    sample_text_regions = [(70, 230, 170, 270), (240, 370, 330, 410), (230, 530, 330, 570), (100, 680, 280, 720)]
    heights = []
    for x0,y0,x1,y1 in sample_text_regions:
        runs = find_text_runs(img_g, x0, x1, y0, y1, dark_thr=90)
        if runs:
            best = max(runs, key=lambda r: r[1]-r[0])
            heights.append(best[1]-best[0]+1)
    if heights:
        avg = sum(heights)/len(heights)
        print(f"Bubble text height samples: {heights}, avg={avg:.1f}px (spec: 16px) -> {'PASS' if 13 <= avg <= 20 else 'FAIL'}")
    names = find_names_blue(img_g, wg, hg)
    print(f"Blue name labels: {[(s,e,e-s+1) for s,e in names]} -> {'PASS' if len(names) >= 2 else 'FAIL'}")
    samples = [
        ("chat_bg", 120, 80),
        ("left_bubble", 80, 220),
        ("right_bubble", 280, 360),
        ("name_周子昂", 80, 332),
        ("name_陈默", 80, 450),
    ]
    for label, x, y in samples:
        c = px(img_g, x, y)
        print(f"  {label} ({x},{y}): {fmt_px(c)}")
    mean_lum = region_mean_lum(img_g, 0, 0, wg-1, hg-1)
    print(f"Overall mean luminance: {mean_lum:.1f} -> {'PASS (no overlay dimming)' if mean_lum > 230 else 'FAIL'}")

if __name__ == "__main__":
    main()
