#!/usr/bin/env python3
"""TGQQ round14 acceptance: analyze 6 screenshots of the two-row composer."""
import numpy as np
from PIL import Image

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"

# Blue thresholds (loose, per spec): blue = B>R+30 and B>140
def is_blue(r, g, b):
    r, g, b = int(r), int(g), int(b)
    return b > r + 30 and b > 140

def is_gray_icon(r, g, b):
    r, g, b = int(r), int(g), int(b)
    # #5A5A5A ~ (90,90,90) with tolerance; low saturation
    return (abs(r-g) < 30 and abs(g-b) < 30 and 55 < r < 150 and abs((r+g+b)//3 - r) < 22)

def is_light_plate(r, g, b):
    r, g, b = int(r), int(g), int(b)
    # #f7f8fa ~ (247,248,250)
    return r > 232 and g > 234 and b > 236

def is_white(r, g, b):
    r, g, b = int(r), int(g), int(b)
    return r > 245 and g > 245 and b > 245

def load(name):
    img = Image.open(f"{SHOTS}/{name}").convert("RGB")
    return np.asarray(img), img.size

def classify(r, g, b):
    r, g, b = int(r), int(g), int(b)
    if is_blue(r, g, b):
        return 'B'   # blue send button
    if is_gray_icon(r, g, b):
        return 'G'   # gray icon
    if is_white(r, g, b):
        return 'w'
    if is_light_plate(r, g, b):
        return 'L'   # light plate
    if r < 70 and g < 70 and b < 70:
        return 'D'   # dark text
    if b > r + 25 and b > 110:
        return 'b'   # faint blue
    return '.'

def region_map(arr, x0, y0, x1, y1, cw=3, ch=3):
    """Downsample region to ASCII using majority vote per cell."""
    sub = arr[y0:y1, x0:x1]
    h, w = sub.shape[:2]
    cols = max(1, w // cw)
    rows = max(1, h // ch)
    out = []
    for ry in range(rows):
        line = []
        for cx in range(cols):
            cell = sub[ry*ch:(ry+1)*ch, cx*cw:(cx+1)*cw].reshape(-1, 3)
            # pick most common label
            from collections import Counter
            labels = [classify(*p) for p in cell]
            cnt = Counter(labels)
            # prefer non-'.' if present
            best = cnt.most_common(1)[0][0]
            line.append(best if best != '.' else ' ')
        out.append(''.join(line))
    return out

def count_blue(arr, x0, y0, x1, y1):
    sub = arr[y0:y1, x0:x1].reshape(-1, 3)
    n = sum(1 for (r, g, b) in sub if is_blue(r, g, b))
    return n

def count_gray(arr, x0, y0, x1, y1):
    sub = arr[y0:y1, x0:x1].reshape(-1, 3)
    n = sum(1 for (r, g, b) in sub if is_gray_icon(r, g, b))
    return n

def sample(arr, x, y):
    r, g, b = arr[y, x]
    return (r, g, b)

def scan_row_gray_clusters(arr, y0, y1, x0, x1, step=1):
    """Find x-centers where gray-icon pixels are concentrated in a horizontal band."""
    sub = arr[y0:y1, x0:x1]
    w = sub.shape[1]
    graycols = []
    for cx in range(w):
        col = sub[:, cx]
        cnt = sum(1 for (r, g, b) in col if is_gray_icon(r, g, b))
        graycols.append(cnt)
    # find local maxima (clusters) with count above threshold
    centers = []
    min_gap = 20
    last = -100
    for cx in range(1, w-1):
        if graycols[cx] >= 8 and graycols[cx] >= graycols[cx-1] and graycols[cx] >= graycols[cx+1]:
            if cx - last >= min_gap:
                centers.append(x0 + cx)
                last = cx
    return centers, graycols

print("=" * 70)
print("TGQQ two-row composer acceptance — 6 screenshots")
print("=" * 70)

# ---------- A) mobile-chat.jpg ----------
print("\n### A) mobile-chat.jpg (390x844) — two-row composer")
arr, sz = load("mobile-chat.jpg")
print("size:", sz)
print("send-button region (x330-386,y728-788) blue px:", count_blue(arr, 330, 728, 386, 788))
print("upper plate region (x10-340,y730-788) light-plate px:",
      sum(1 for (r,g,b) in arr[730:788,10:340].reshape(-1,3) if is_light_plate(r,g,b)))
centers, _ = scan_row_gray_clusters(arr, 798, 826, 8, 382)
print("lower-row gray-icon cluster centers (y798-826):", centers)
print("sample send btn center (363,758):", sample(arr, 363, 758))
print("sample plate (180,758):", sample(arr, 180, 758))
print("-- composer ASCII (x0..390, y720..844) --")
for line in region_map(arr, 0, 720, 390, 844, cw=4, ch=4):
    print(line)

# ---------- B) group-chat.jpg ----------
print("\n### B) group-chat.jpg (390x844) — group + two-row composer")
arr, sz = load("group-chat.jpg")
print("size:", sz)
print("send-btn blue px (330-386,728-788):", count_blue(arr, 330, 728, 386, 788))
print("upper plate px (10-340,730-788):",
      sum(1 for (r,g,b) in arr[730:788,10:340].reshape(-1,3) if is_light_plate(r,g,b)))
centers, _ = scan_row_gray_clusters(arr, 798, 826, 8, 382)
print("lower-row gray-icon centers:", centers)
print("-- composer ASCII (y720..844) --")
for line in region_map(arr, 0, 720, 390, 844, cw=4, ch=4):
    print(line)
# check sender name blue in bubble area
print("scan for blue sender-name pixels in bubble band y150-500:")
nb = count_blue(arr, 0, 150, 390, 500)
print("  blue px count in y150-500:", nb)

# ---------- C) tablet-mid.jpg ----------
print("\n### C) tablet-mid.jpg (900x700) — right-window composer")
arr, sz = load("tablet-mid.jpg")
print("size:", sz)
print("-- full ASCII (cw=9,ch=7) --")
for line in region_map(arr, 0, 0, 900, 700, cw=9, ch=7):
    print(line)
# right window composer: right window x 360..900, bottom
print("right-window send-btn blue px (x838-896,y556-616):", count_blue(arr, 838, 556, 896, 616))
print("right-window upper plate px (x372-860,y560-616):",
      sum(1 for (r,g,b) in arr[560:616,372:860].reshape(-1,3) if is_light_plate(r,g,b)))
centers, _ = scan_row_gray_clusters(arr, 628, 660, 372, 896)
print("right-window lower-row gray centers (y628-660):", centers)
print("-- right window composer zoom (x360..900,y540..700) --")
for line in region_map(arr, 360, 540, 900, 700, cw=6, ch=4):
    print(line)
# left home not regressed: check 4 tabs region x10-350 y top, and that it's a phone-style home
print("left column top bar sample (x40,40):", sample(arr, 40, 40))
print("left column tab area sample (x40,700-? ) not available; sample (x175, 40):", sample(arr, 175, 40))

# ---------- D) group-chat-tablet.jpg ----------
print("\n### D) group-chat-tablet.jpg (900x700) — tablet group composer")
arr, sz = load("group-chat-tablet.jpg")
print("size:", sz)
print("right-window send-btn blue px (838-896,556-616):", count_blue(arr, 838, 556, 896, 616))
print("right-window upper plate px (372-860,560-616):",
      sum(1 for (r,g,b) in arr[560:616,372:860].reshape(-1,3) if is_light_plate(r,g,b)))
centers, _ = scan_row_gray_clusters(arr, 628, 660, 372, 896)
print("right-window lower-row gray centers:", centers)
print("-- right window composer zoom (x360..900,y540..700) --")
for line in region_map(arr, 360, 540, 900, 700, cw=6, ch=4):
    print(line)
print("scan blue sender in right window bubble band y150-520 x380-880:",
      count_blue(arr, 380, 150, 880, 520))

# ---------- E) emoji-panel.jpg ----------
print("\n### E) emoji-panel.jpg (390x844) — emoji panel above composer")
arr, sz = load("emoji-panel.jpg")
print("size:", sz)
# panel 384px tall bottom, top rounded 16px, mask darkened. bottom edge ~88px above input.
# So panel occupies y from 844-384=460 to 844. But input area below? Wait composer at y726-826.
# Panel bottom edge above input (~88px up from input top 726 => ~638?). Actually spec: panel bottom edge ~88px above input area.
# Let's detect white panel region and its top edge and the composer below.
print("-- full ASCII (cw=6,ch=7) --")
for line in region_map(arr, 0, 0, 390, 844, cw=6, ch=7):
    print(line)
# find top edge of white panel: scan upward from bottom for where white panel starts
# panel should be white (250+), mask darker above. Detect composer blue send below panel?
print("send-btn blue px (330-386,728-788):", count_blue(arr, 330, 728, 386, 788))
# detect panel top: find first row (from bottom) where white content dominates lower portion
# We'll sample columns to find panel top y.
def panel_top_y(arr, x0, x1, yscan_start, yscan_end):
    # white panel => many 'w'/'L' pixels
    for y in range(yscan_start, yscan_end, -1):
        row = arr[y, x0:x1]
        white = sum(1 for (r,g,b) in row if is_white(r,g,b) or is_light_plate(r,g,b))
        if white > (x1-x0)*0.5:
            return y
    return -1
print("panel top edge approx (x20-360, scan 460..840):", panel_top_y(arr, 20, 360, 840, 460))
print("sample panel mid (180, 700):", sample(arr, 180, 700))
print("sample mask above panel (180, 420):", sample(arr, 180, 420))
# gap check between panel bottom (844) and composer: composer should be hidden by panel, so input not visible.
# Check composer lower row gray centers in emoji panel image (should be hidden => none or shifted)
centers, _ = scan_row_gray_clusters(arr, 798, 826, 8, 382)
print("composer lower-row gray centers (should be hidden by panel):", centers)

# ---------- F) attach-panel.jpg ----------
print("\n### F) attach-panel.jpg (390x844) — attach panel 4-col grid")
arr, sz = load("attach-panel.jpg")
print("size:", sz)
print("-- full ASCII (cw=6,ch=7) --")
for line in region_map(arr, 0, 0, 390, 844, cw=6, ch=7):
    print(line)
print("mask sample above panel (180, 420):", sample(arr, 180, 420))
print("panel mid (180, 700):", sample(arr, 180, 700))
# detect colored circular icon backgrounds: count saturated (non-gray) pixels in panel
def colored_count(arr, x0, y0, x1, y1):
    sub = arr[y0:y1, x0:x1].reshape(-1, 3)
    n = sum(1 for (r,g,b) in sub if max(r,g,b)-min(r,g,b) > 60 and max(r,g,b) > 120)
    return n
print("colored (saturated) px in panel grid (y470..820,x20..370):", colored_count(arr, 20, 470, 370, 820))
# send btn below?
print("send-btn blue px (330-386,728-788):", count_blue(arr, 330, 728, 386, 788))

print("\n=== done ===")
