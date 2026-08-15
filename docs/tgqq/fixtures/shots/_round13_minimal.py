#!/usr/bin/env python3
"""Round-13 — minimal targeted checks."""
from PIL import Image
import os

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

# === Compare 已读 text pixel counts uniformly ===
print("="*70)
print("(A) UNIFORM 已读 pixel count comparison")
print("="*70)
for name, x0, x1, y0, y1 in [
    ("mobile-chat.jpg", 220, 380, 150, 800),
    ("group-chat.jpg",  220, 380, 150, 800),
    ("tablet-mid.jpg",  500, 895, 60, 670),
]:
    im=load(name)
    n=0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r=px(im,x,y)
            if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
                n+=1
    print(f" {name}: dark-blue text px in outbound area = {n}")

# === Tablet-mid right-pane avatar: scan whole image for ANY orange ===
print()
print("="*70)
print("(B) Tablet-mid — find ALL orange/purple avatar circles (whole image)")
print("="*70)
t=load("tablet-mid.jpg")
# Find connected orange regions
visited=set()
def flood(x0,y0):
    stack=[(x0,y0)]; pts=[]
    while stack:
        x,y=stack.pop()
        if (x,y) in visited: continue
        if not (0<=x<900 and 0<=y<700): continue
        visited.add((x,y))
        r=px(t,x,y)
        # accept orange OR purple-ish (multiple people in list)
        is_avatar=r[0]>=200 and r[1]<=200 and r[2]<=130 and r[0]>r[2]
        if not is_avatar: continue
        pts.append((x,y))
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            stack.append((x+dx,y+dy))
    return pts

regions=[]
for y in range(0, 700, 4):
    for x in range(0, 900, 4):
        if (x,y) in visited: continue
        r=px(t,x,y)
        if r[0]>=200 and r[1]<=200 and r[2]<=130 and r[0]>r[2]:
            pts=flood(x,y)
            if len(pts)>=20:
                xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                regions.append({"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
                                "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,"n":len(pts),
                                "center_x":sum(xs)//len(xs),"center_y":sum(ys)//len(ys)})
# Sort by x to see distribution
for r in sorted(regions, key=lambda r: r["center_x"]):
    side = "sidebar" if r["center_x"]<440 else "RIGHT pane"
    print(f" {side}: center=({r['center_x']},{r['center_y']}), bbox x[{r['x0']}..{r['x1']}] y[{r['y0']}..{r['y1']}] (w={r['w']}, h={r['h']}, n={r['n']})")

# === Confirm bubble offset on tablet-mid right pane (after finding avatar) ===
print()
print("="*70)
print("(B) Tablet-mid right pane — bubble left edge vs avatar alignment")
print("="*70)
# Pick the right-pane avatar
rp = [r for r in regions if r["center_x"]>=440]
if rp:
    a = rp[0]
    print(f" right-pane avatar: bbox x[{a['x0']}..{a['x1']}] y[{a['y0']}..{a['y1']}]")
    print(f" avatar diameter: w={a['w']}, h={a['h']}")
    # Bubble left edge — find first white bubble pixel right of avatar
    cy = (a['y0']+a['y1'])//2
    print(f" avatar center y={cy}, scanning rightward from x={a['x1']+1}")
    for x in range(a['x1']+1, a['x1']+50):
        r=px(t,x,cy)
        if br(r)>=240 and not (r[0]>=200 and r[1]<=200 and r[2]<=130):
            print(f"  bubble edge at x={x}, gap from avatar={x-a['x1']-1} px")
            break
else:
    print(" No right-pane avatar found — fallback sample at expected coords")

# === group-chat: confirm 已读 appears, count bands at 14:15 and 14:23 ===
print()
print("="*70)
print("(A) group-chat — verify 已读 appears at expected bubble positions")
print("="*70)
g=load("group-chat.jpg")
# Visually bubbles 14:15 (y~270-290), 14:16 (y~330-360), 14:23 (y~590-620)
# Check for dark blue pixels (text) in the time-row band x=295-380
for label, y_range in [
    ("14:15 row (expect 已读)", range(263, 290)),
    ("14:16 row (NO 已读?)", range(323, 350)),
    ("14:23 row (expect 已读)", range(590, 615)),
]:
    n_dark_blue=0
    samples=[]
    for y in y_range:
        for x in range(295, 380):
            r=px(g,x,y)
            if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
                n_dark_blue+=1
                if len(samples)<3: samples.append((x,y,r))
    print(f" {label}: dark-blue text px = {n_dark_blue}")
    for s in samples: print(f"   {s}")

# === mobile-chat: same check ===
print()
print("="*70)
print("(A) mobile-chat — same outbound time-row check")
print("="*70)
m=load("mobile-chat.jpg")
# Visually bubbles 14:13 (y~205-225), 14:15 (y~285-305), 14:16 (y~360-380),
# 14:23 (y~590-610), 14:25 (y~655-680), 14:25-2 (y~715-735)
for label, y_range in [
    ("14:13 row", range(195, 230)),
    ("14:15 row", range(280, 310)),
    ("14:16 row", range(355, 385)),
    ("14:23 row", range(590, 615)),
    ("14:25 row", range(650, 685)),
    ("14:25-2 row", range(710, 740)),
]:
    n_dark_blue=0
    samples=[]
    for y in y_range:
        for x in range(295, 380):
            r=px(m,x,y)
            if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
                n_dark_blue+=1
                if len(samples)<3: samples.append((x,y,r))
    print(f" {label}: dark-blue text px = {n_dark_blue}")
    for s in samples: print(f"   {s}")
