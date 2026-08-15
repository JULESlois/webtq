#!/usr/bin/env python3
"""Round-13 audit — direct pixel probes for unresolved items."""
from PIL import Image
import os

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

print("="*70)
print("(A) DIRECT PROBE — sample exact pixels at visible '已读' glyph locations")
print("="*70)

# tablet-mid right pane. From visual reading, "已读" appears below bubble text on right.
# Bubble "好嘞，周六见！" with "14:23 已读" — the 已读 text glyphs should be visible.
# Let me find them by scanning for medium-blue text in the bubble area
t=load("tablet-mid.jpg")

# Scan a horizontal strip across the right-pane chat area at various y to find blue text
def scan_strip(img, y, x0, x1, label):
    line=[]
    for x in range(x0, x1):
        line.append((x, px(img,x,y)))
    # Find non-background pixels (luma != 240-256)
    interesting=[(x,r) for x,r in line if not (235<=br(r)<=256)]
    if interesting:
        # find darkest blue
        dark_blues=[(x,r) for x,r in interesting if r[2]>r[0]+30 and r[2]>120]
        if dark_blues:
            print(f" {label} y={y}: {len(dark_blues)} bluish pixels, x=[{dark_blues[0][0]}..{dark_blues[-1][0]}]")
            for x,r in dark_blues[:5]:
                print(f"     ({x},{y}) = {r}")
            return dark_blues
    return []

# Look for "已读" — small text near right edge of bubbles
# The bubbles are right-aligned. Outbound bubble right edges near x=860.
# Scan along x=820-880 at various y values
print()
print(" Scanning for 已读 text in tablet-mid right pane (x=820-890, y=20-660):")
# Strategy: find a y where we see a thin (1-3px tall) cluster of blue at the very bottom of a bubble
hits=[]
for y in range(60, 670):
    blues=[]
    for x in range(800, 895):
        r=px(t,x,y)
        # looking for blue text glyph: G < 200 and B > R+50
        if r[2]>=120 and r[2]>r[0]+40 and r[2]>r[1]+5 and br(r)<235:
            blues.append((x,r))
    if 1<=len(blues)<=20:  # text-like density
        hits.append((y, blues))
for y,blues in hits[:30]:
    print(f" y={y}: {len(blues)} bluish, x-range [{blues[0][0]}..{blues[-1][0]}]")

# Let me also look at all-blue-darkness in the right-pane chat area
print()
print(" All dark-blue (text) px in right pane:")
total=0
xs=[]; ys=[]; rs=[]
for y in range(60, 670):
    for x in range(500, 895):
        r=px(t,x,y)
        # dark blue (text), R low, G moderate, B high
        if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
            total+=1; xs.append(x); ys.append(y); rs.append(r)
print(f" total: {total}")
if xs:
    print(f" x range: {min(xs)}..{max(xs)}")
    print(f" y range: {min(ys)}..{max(ys)}")
    # Group by y to find text-line clusters
    by_y={}
    for x,y,r in zip(xs,ys,rs):
        by_y.setdefault(y,[]).append((x,r))
    # find consecutive y bands
    sorted_y=sorted(by_y.keys())
    bands=[]; cur=[]; last=None
    for y in sorted_y:
        if last is None or y-last<=2: cur.append(y)
        else: bands.append(cur); cur=[y]
        last=y
    if cur: bands.append(cur)
    print(f" y-bands of dark blue text (likely '已读' lines):")
    for b in bands:
        if len(b)>=2:
            x_in_band=[x for y in b for x,r in by_y[y]]
            print(f"  band y={b[0]}..{b[-1]} (h={len(b)}): x=[{min(x_in_band)}..{max(x_in_band)}], {len(x_in_band)} px")

# Sample color of these text pixels
if rs:
    print(f" sample RGB (mid): {rs[len(rs)//2]}")

print()
print("="*70)
print("(B) Mobile-chat avatar exact color/diameter")
print("="*70)
m=load("mobile-chat.jpg")
# Probe the orange avatar at left
# First group avatar around y=140-185, second around y=455-500
print(" mobile-chat avatar column profile (x=0..60, y=130-200):")
for y in range(130, 200, 3):
    row=[]
    for x in range(0, 60):
        r=px(m,x,y)
        # orange predicate: R high, G mid, B low, R>G>B
        if r[0]>=200 and r[1]<=180 and r[2]<=120 and r[0]>r[1]>r[2]:
            row.append((x,r))
    if row:
        print(f" y={y}: x-range [{row[0][0]}..{row[-1][0]}], w={row[-1][0]-row[0][0]+1}, sample={row[len(row)//2][1]}")
# Find leftmost and rightmost orange columns and vertical extent
print()
print(" Bounding box of first-group avatar:")
ox=[]; oy=[]
for y in range(100, 230):
    for x in range(0,80):
        r=px(m,x,y)
        if r[0]>=200 and r[1]<=180 and r[2]<=120 and r[0]>r[1]>r[2]:
            ox.append(x); oy.append(y)
if ox:
    print(f"  x:[{min(ox)}..{max(ox)}] (w={max(ox)-min(ox)+1}), y:[{min(oy)}..{max(oy)}] (h={max(oy)-min(oy)+1})")

# Bubble x-offset (right edge of avatar to left edge of bubble)
print()
print(" Bubble left edge in mobile-chat top group (looking at row y=155 — inside avatar row):")
# At y=155 we should see avatar. Check x=60..200 to find first white bubble pixel
for x in range(60, 250):
    r=px(m,x,155)
    if br(r)>=245 and not (r[0]>=200 and r[1]<=180 and r[2]<=120):
        print(f"  bubble interior at x={x}: {r}")
        print(f"  gap from avatar edge (max avatar x=54): {x - 54 - 1} px")
        break

print()
print("="*70)
print("(B) Tablet-mid avatar check (right pane '林' orange)")
print("="*70)
# Right pane avatar at approx x=540-580, y=200-240
print(" tablet-mid right-pane avatar column scan (x=520-600, y=190-260):")
for y in range(190, 260, 3):
    row=[]
    for x in range(520, 600):
        r=px(t,x,y)
        if r[0]>=200 and r[1]<=180 and r[2]<=120 and r[0]>r[1]>r[2]:
            row.append((x,r))
    if row:
        print(f" y={y}: x-range [{row[0][0]}..{row[-1][0]}], w={row[-1][0]-row[0][0]+1}, sample={row[len(row)//2][1]}")
ox=[]; oy=[]
for y in range(150, 280):
    for x in range(500,620):
        r=px(t,x,y)
        if r[0]>=200 and r[1]<=180 and r[2]<=120 and r[0]>r[1]>r[2]:
            ox.append(x); oy.append(y)
if ox:
    print(f"  bbox: x:[{min(ox)}..{max(ox)}] (w={max(ox)-min(ox)+1}), y:[{min(oy)}..{max(oy)}] (h={max(oy)-min(oy)+1})")
else:
    print("  NO orange avatar found in expected zone — sampling pixels directly:")
    for y in [195, 200, 205, 210, 215, 220]:
        for x in [540, 545, 550, 555, 560, 565, 570]:
            print(f"    ({x},{y}) = {px(t,x,y)}")

print()
print("="*70)
print("(D) Emoji panel: which tab is highlighted?")
print("="*70)
ep=load("emoji-panel.jpg")
# Tabs are at y~795-820. 5 tabs: x_centers ≈ 40, 117, 195, 273, 351
# Sample 8x8 area around each center, look for non-grey colors
for cx in [40, 117, 195, 273, 351]:
    samples=[]
    for dy in range(-12, 13):
        for dx in range(-15, 16):
            r=px(ep,cx+dx, 808+dy)
            samples.append(r)
    # Find any pixel that's blue-ish (active highlight)
    blues=[r for r in samples if r[2]>r[0]+40 and r[2]>150]
    avg=(
        sum(s[0] for s in samples)//len(samples),
        sum(s[1] for s in samples)//len(samples),
        sum(s[2] for s in samples)//len(samples))
    print(f" tab cx={cx}: avg color = {avg}, blue pixels in 26x26 region = {len(blues)}, sample blue = {blues[0] if blues else None}")

# Direct sample at smile-face halo area (if there's a circle around smile)
print()
print(" Direct sampling at smile icon (cx~117, y~798-815):")
for y in range(795, 822, 2):
    for x in range(95, 145, 3):
        r=px(ep,x,y)
        if (r[0]+r[1]+r[2])<700 or r[2]>r[0]+15:  # not light grey
            print(f"  ({x},{y}) = {r}")

print()
print("="*70)
print("(D) Mask brightness at multiple points")
print("="*70)
# Above the panel: y=100-430. Sample 5 evenly spaced points
print(" above-panel (chat area under mask):")
for y in [80, 150, 250, 350, 430]:
    samples=[br(px(ep,x,y)) for x in (60, 130, 220, 310, 380)]
    print(f"  y={y}: avg luma = {sum(samples)/len(samples):.1f}")
print(" within emoji panel (y=480-770):")
for y in [490, 560, 640, 720, 770]:
    samples=[br(px(ep,x,y)) for x in (60, 130, 220, 310, 380)]
    print(f"  y={y}: avg luma = {sum(samples)/len(samples):.1f}")