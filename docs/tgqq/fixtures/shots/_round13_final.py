#!/usr/bin/env python3
"""Round-13 — final focused probes at corrected y coordinates."""
from PIL import Image
import os

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

print("="*70)
print("(D) Emoji panel TAB STRIP — locate blue active halo at correct y range")
print("="*70)
ep=load("emoji-panel.jpg")
# Visually confirmed tab strip is at y~735-765. Tabs roughly at:
#   🔍 x≈40, 😊 x≈115 (highlighted), 💬 x≈190, +a x≈265, 🗑 x≈345
# Scan for any non-grey color in y=720-770 strip
print(" y=735..760 scanning for blue halo pixels (active tab highlight):")
hits={}
for y in range(720, 770):
    for x in range(0, 390):
        r=px(ep,x,y)
        # blueish, not white
        if r[2]>=180 and r[2]>r[0]+20 and br(r)<240:
            hits.setdefault(y,[]).append((x,r))
# Print summary by y
for y in sorted(hits.keys()):
    pts=hits[y]
    if pts:
        # find x-clusters
        xs=sorted(set(p[0] for p in pts))
        # cluster consecutive xs
        clusters=[]
        cur=[xs[0]]
        for v in xs[1:]:
            if v-cur[-1]<=5: cur.append(v)
            else: clusters.append(cur); cur=[v]
        clusters.append(cur)
        cluster_summary=[(min(c),max(c)) for c in clusters]
        print(f" y={y}: {len(pts)} blue px in clusters {cluster_summary}, sample={pts[len(pts)//2][1]}")

# Centroid of blue pixels in tab strip
print()
print(" Tab strip blue centroid:")
all_x=[]; all_y=[]; all_r=[]
for y in range(720, 770):
    for x in range(0, 390):
        r=px(ep,x,y)
        if r[2]>=180 and r[2]>r[0]+20 and br(r)<240:
            all_x.append(x); all_y.append(y); all_r.append(r)
if all_x:
    cx=sum(all_x)//len(all_x); cy=sum(all_y)//len(all_y)
    print(f"  centroid=({cx},{cy}), N={len(all_x)}, x-range [{min(all_x)}..{max(all_x)}], y-range [{min(all_y)}..{max(all_y)}]")
    print(f"  sample rgb: {all_r[len(all_r)//2]}")

print()
print("="*70)
print("(B) Tablet-mid right-pane '林' avatar — search correct y range")
print("="*70)
t=load("tablet-mid.jpg")
# Visually the orange '林' avatar is in middle of right pane, beside the '林晓晴 那就周六...' reply bubble.
# The reply bubble '林晓晴 那就周六早上九点老...' is around y=380-460. The avatar should align at bottom.
# Let me scan ALL orange circles in the right pane (x>=440)
print(" tablet-mid right-pane orange avatar scan (x=440-700, y=0-700):")
all_o=[]
for y in range(0, 700, 1):
    for x in range(440, 700):
        r=px(t,x,y)
        if r[0]>=200 and r[1]<=180 and r[2]<=120 and r[0]>r[1]>r[2]:
            all_o.append((x,y,r))
if all_o:
    print(f"  N={len(all_o)} orange pixels")
    print(f"  x-range: {min(p[0] for p in all_o)}..{max(p[0] for p in all_o)}")
    print(f"  y-range: {min(p[1] for p in all_o)}..{max(p[1] for p in all_o)}")
    # Find bbox of connected orange region
    xs=[p[0] for p in all_o]; ys=[p[1] for p in all_o]
    print(f"  bbox: x[{min(xs)}..{max(xs)}] (w={max(xs)-min(xs)+1}), y[{min(ys)}..{max(ys)}] (h={max(ys)-min(ys)+1})")
    print(f"  sample color (center): {all_o[len(all_o)//2][2]}")
else:
    print("  NO orange in right pane — try broader search")
    for y in range(0, 700, 10):
        for x in range(440, 900, 10):
            r=px(t,x,y)
            if r[0]>=180 and r[1]<=200 and r[2]<=150 and r[0]>r[1] and r[0]>r[2]:
                print(f"  candidate ({x},{y}) = {r}")
                break

print()
print("="*70)
print("(A) group-chat 已读 text scan (similar to tablet-mid method)")
print("="*70)
g=load("group-chat.jpg")
# Scan whole outbound area for dark blue text glyphs
all_dark_blue=[]
for y in range(150, 800, 1):
    for x in range(220, 380):
        r=px(g,x,y)
        if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
            all_dark_blue.append((x,y,r))
print(f" group-chat outbound area dark-blue pixels: {len(all_dark_blue)}")
if all_dark_blue:
    xs=[p[0] for p in all_dark_blue]; ys=[p[1] for p in all_dark_blue]
    print(f"  x range: {min(xs)}..{max(xs)}")
    print(f"  y range: {min(ys)}..{max(ys)}")
    # Group by y to find text-line clusters
    by_y={}
    for x,y,r in all_dark_blue:
        by_y.setdefault(y,[]).append((x,r))
    sorted_y=sorted(by_y.keys())
    bands=[]; cur=[]; last=None
    for y in sorted_y:
        if last is None or y-last<=2: cur.append(y)
        else: bands.append(cur); cur=[y]
        last=y
    if cur: bands.append(cur)
    print(f"  y-bands of dark blue text:")
    for b in bands:
        if len(b)>=2:
            x_in_band=[x for y in b for x,r in by_y[y]]
            xs_in=min(x_in_band); xe_in=max(x_in_band)
            mid_r=by_y[(b[0]+b[-1])//2][len(by_y[(b[0]+b[-1])//2])//2][1]
            print(f"   band y={b[0]}..{b[-1]} (h={len(b)}, n={len(x_in_band)}): x=[{xs_in}..{xe_in}], sample={mid_r}")
    # Print sample RGB
    print(f"  sample RGB (mid): {all_dark_blue[len(all_dark_blue)//2][2]}")

print()
print("="*70)
print("(A) mobile-chat outbound 已读 scan — same method, compare counts")
print("="*70)
m=load("mobile-chat.jpg")
mb=[]
for y in range(150, 800, 1):
    for x in range(220, 380):
        r=px(m,x,y)
        if r[0]<80 and 80<r[1]<200 and r[2]>r[0]+60:
            mb.append((x,y,r))
print(f" mobile-chat outbound dark-blue pixels: {len(mb)}")
if mb:
    ys=[p[1] for p in mb]
    print(f"  y range: {min(ys)}..{max(ys)}")
    by_y={}
    for x,y,r in mb:
        by_y.setdefault(y,[]).append((x,r))
    sorted_y=sorted(by_y.keys())
    bands=[]; cur=[]; last=None
    for y in sorted_y:
        if last is None or y-last<=2: cur.append(y)
        else: bands.append(cur); cur=[y]
        last=y
    if cur: bands.append(cur)
    for b in bands:
        if len(b)>=2:
            x_in_band=[x for y in b for x,r in by_y[y]]
            print(f"   band y={b[0]}..{b[-1]} (h={len(b)}, n={len(x_in_band)}): x=[{min(x_in_band)}..{max(x_in_band)}]")
