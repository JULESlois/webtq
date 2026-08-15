#!/usr/bin/env python3
"""Round-13 audit — focused re-checks on the spots that looked ambiguous."""
from PIL import Image
import os

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

print("="*70)
print("(A) Exact pixel probe at visible '已读' text on tablet-mid")
print("="*70)
t=load("tablet-mid.jpg")
# Visually the bubbles are in the right pane.
# Outbound bubbles: 14:15 已读 at approx (840, 90)
#                    14:23 已读 at approx (835, 365)
#                    14:25 已读 at approx (840, 565)
# Walk a horizontal band of y ±5 around suspected y and find darkest blue pixels (text glyphs)
def find_dark_blue_in_band(img, yc, x0, x1, step=1):
    pts=[]
    for y in range(yc-6, yc+7, step):
        for x in range(x0, x1, step):
            r=px(img,x,y)
            # darkish blue (text glyph color), exclude very-light bubble fill (B>240)
            if 5<=r[0]<=70 and 90<=r[1]<=180 and 180<=r[2]<=235 and r[2]>r[0]+90:
                pts.append((x,y,r))
    return pts

for label,yc,x0,x1 in [
    ("14:15 已读", 90, 760, 880),
    ("14:23 已读", 365, 760, 880),
    ("14:25 已读", 565, 760, 880),
]:
    pts=find_dark_blue_in_band(t, yc, x0, x1)
    print(f" {label} y~{yc}: {len(pts)} dark-blue text pixels")
    if pts:
        print(f"   x range: {min(p[0] for p in pts)}..{max(p[0] for p in pts)}")
        print(f"   sample rgb at center: {pts[len(pts)//2][2]}")

# Same scan on group-chat
print()
print("="*70)
print("(A) group-chat 已读 text color probe")
print("="*70)
g=load("group-chat.jpg")
for label,yc,x0,x1 in [
    ("14:15 已读 (group)", 275, 295, 380),
    ("14:23 已读 (group)", 600, 295, 380),
]:
    pts=find_dark_blue_in_band(g, yc, x0, x1)
    print(f" {label} y~{yc}: {len(pts)} dark-blue text pixels")
    if pts:
        print(f"   x range: {min(p[0] for p in pts)}..{max(p[0] for p in pts)}")
        print(f"   sample rgb at center: {pts[len(pts)//2][2]}")

# Same scan on mobile-chat (should also have 已读 if A is uniform)
print()
print("="*70)
print("(A) mobile-chat outbound 已读 probe — expect same as tablet if A uniform")
print("="*70)
m=load("mobile-chat.jpg")
# outbound bubbles in mobile-chat: 14:13 (~y=210), 14:15 (~y=295), 14:16 (~y=370),
# 14:23 (~y=600), 14:25 (~y=665), 14:25 (~y=720)
for label,yc,x0,x1 in [
    ("14:13 area", 215, 295, 380),
    ("14:15 area", 295, 295, 380),
    ("14:16 area", 370, 295, 380),
    ("14:23 area", 600, 295, 380),
    ("14:25 area", 665, 295, 380),
    ("14:25-2 area", 720, 295, 380),
]:
    pts=find_dark_blue_in_band(m, yc, x0, x1)
    print(f" {label} y~{yc}: {len(pts)} dark-blue text pixels")

print()
print("="*70)
print("(B) Avatar color/diameter check on tablet-mid")
print("="*70)
# Right pane "林" orange avatar around x=540-580, y=200-240
# Sample center pixel and bbox
def find_color_bbox(img, x0, x1, y0, y1, predicate):
    xs=[]; ys=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            if predicate(px(img,x,y)):
                xs.append(x); ys.append(y)
    if not xs: return None
    return (min(xs),min(ys),max(xs),max(ys), max(xs)-min(xs)+1, max(ys)-min(ys)+1)

# orange predicate: R>=230, 90<=G<=170, 30<=B<=110
bbox=find_color_bbox(t, 520, 600, 180, 260, lambda r: r[0]>=230 and 90<=r[1]<=170 and 30<=r[2]<=110)
print(f" tablet-mid '林' orange bbox: {bbox}")
if bbox:
    x0,y0,x1,y1,w,h=bbox
    print(f"   center px: {px(t,(x0+x1)//2,(y0+y1)//2)}")
    # also sample avatar border color
    print(f"   edge px (x=x0+1): {px(t,x0+1,(y0+y1)//2)}")

# mobile-chat "林" avatar bbox (should be ~40x40)
print()
print(" mobile-chat inbound avatar bbox (top group):")
bbox_m=find_color_bbox(m, 0, 80, 200, 290, lambda r: r[0]>=230 and 90<=r[1]<=170 and 30<=r[2]<=110)
print(f"  bbox: {bbox_m}")
# Check bubble x-offset — find first non-background pixel right of avatar
print(" mobile-chat top-group bubble left edge:")
for x in range(80, 250):
    r=px(m,x,250)
    if br(r)<250 and not (r[0]>=230 and 90<=r[1]<=170 and 30<=r[2]<=110):
        # could be bubble edge
        print(f"  x={x}: {r}")
        break

print()
print("="*70)
print("(C) Tablet top bar icon glyph color check")
print("="*70)
# Find dark pixels in each cluster center
clusters_x=[761, 779, 836]
for cx in clusters_x:
    # search ±15 around cx, y=10..60 for darkest pixel
    darkest=(255,255,255)
    for y in range(10,60):
        for x in range(cx-15, cx+15):
            r=px(t,x,y)
            if br(r)<br(darkest): darkest=r
    print(f" cluster center x={cx}: darkest px found = {darkest}")

# Also check cluster width vs expected ~20px
print()
print(" tablet top bar dark pixel column profile (x=700..900):")
profile=[]
for x in range(700,900):
    dark_n=sum(1 for y in range(10,60) if br(px(t,x,y))<=130)
    if dark_n>0: profile.append((x,dark_n))
# Print columns with dark pixels >=3
print(" x : dark count (>3 only):")
for x,c in profile:
    if c>=3: print(f"  {x}: {c}")

print()
print("="*70)
print("(D) Emoji panel — locate blue-highlighted tab")
print("="*70)
ep=load("emoji-panel.jpg")
# Scan y=790..820 across full width for blueish color
for y in range(790, 825):
    blues=[]
    for x in range(0,390):
        r=px(ep,x,y)
        # blue-ish (not light grey bg)
        if r[2]>=170 and r[2]>r[0]+30 and r[2]>r[1]+10:
            blues.append((x,r))
    if blues:
        print(f" y={y}: {len(blues)} blue-ish px, x-range [{blues[0][0]}..{blues[-1][0]}]")
# Find center of blue mass on the tab row
print()
print(" Centroid of blue pixels at tab row:")
xs=[]; ys=[]; rs=[]
for y in range(795, 820):
    for x in range(0,390):
        r=px(ep,x,y)
        if 0<=r[0]<=80 and 110<=r[1]<=180 and r[2]>=200:
            xs.append(x); ys.append(y); rs.append(r)
if xs:
    print(f"  N={len(xs)}; centroid=({sum(xs)//len(xs)},{sum(ys)//len(ys)}); sample={rs[len(rs)//2]}")
    print(f"  x range: {min(xs)}..{max(xs)}")

print()
print("="*70)
print("(E) Message menu — count actual rows by detecting text/icon glyphs")
print("="*70)
mm=load("message-menu.jpg")
# Each row has an icon at left + text. Scan left column x=15..50 for dark icons per row.
# Also check for the rounded panel — find top y of white panel
# Look for first row of consistent luma >=235 starting from bottom
top_panel=None
for y in range(440, 600):
    samples=[br(px(mm,x,y)) for x in (50,150,250,350)]
    if all(s>=240 for s in samples):
        top_panel=y; break
print(f" message-menu top panel y ≈ {top_panel}")
# Now scan downward, detecting rows by icon-glyph density at x=15..50
icon_density=[]
for y in range(top_panel or 460, 830):
    dark=sum(1 for x in range(15,50) if br(px(mm,x,y))<=140)
    icon_density.append((y,dark))
# Find peaks (rows with dark pixels)
in_row=False; rows=[]; start=0
for y,d in icon_density:
    if d>=3:
        if not in_row: start=y; in_row=True
    else:
        if in_row:
            rows.append((start,y-1)); in_row=False
if in_row: rows.append((start,icon_density[-1][0]))
# merge close (<15)
merged=[]
for r in rows:
    if merged and r[0]-merged[-1][1]<=15: merged[-1]=(merged[-1][0], r[1])
    else: merged.append(list(r))
print(f" icon-glyph rows (action items): {merged}")
print(f" count: {len(merged)}")

# Also detect inter-row gaps (light separator or padding)
# Use luma profile at x=200 (center)
luma_prof=[]
for y in range((top_panel or 460), 830):
    luma_prof.append((y, br(px(mm,200,y))))
# find local minima (darkest = gaps, separators)
# but gaps here are likely just whitespace — find low-luma zones
print()
print(" Luma at x=200, y range:", [(y,l) for y,l in luma_prof if l<250][::5][:30])

# Count rows by panel-bg white bands at x=15..375 separated by grey borders
# Actually the simplest: detect text-baseline rows by finding dark glyph presence at x=70..200 (text area)
text_rows=[]
in_row=False; start=0
for y in range(top_panel or 460, 830):
    dark=sum(1 for x in range(70,250) if br(px(mm,x,y))<=140)
    if dark>=2:
        if not in_row: start=y; in_row=True
    else:
        if in_row:
            text_rows.append((start,y-1)); in_row=False
if in_row: text_rows.append((start,luma_prof[-1][0]))
merged2=[]
for r in text_rows:
    if merged2 and r[0]-merged2[-1][1]<=15: merged2[-1]=(merged2[-1][0], r[1])
    else: merged2.append(list(r))
print(f" text rows in panel: {merged2}")
print(f" text row count: {len(merged2)}")
print(f" text row heights: {[r[1]-r[0]+1 for r in merged2]}")
print(f" inter-row gaps: {[merged2[i+1][0]-merged2[i][1] for i in range(len(merged2)-1)]}")
