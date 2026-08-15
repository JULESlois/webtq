#!/usr/bin/env python3
"""Targeted re-verification based on visual reading."""
from PIL import Image
import os

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"

def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

# === A) Check actual "已读" text at known outbound bubble time stamps ===
# group-chat: visual "14:15 已读" near y=270-280, x ~310-340
# group-chat: visual "14:23 已读" near y=595-605
g=load("group-chat.jpg")
print("=== group-chat outbound bubble time/已读 sampling ===")
for y in range(260, 290):
    row=[]
    for x in range(280, 380):
        r=px(g,x,y)
        # mark any bluish (B>R, B>G)
        if r[2]>=140 and r[2]>r[0]+15 and r[2]>r[1]+5:
            row.append((x,r))
    if row:
        print(f" y={y}: bluish x-range [{row[0][0]}..{row[-1][0]}], sample={row[len(row)//2][1]}")

print()
print("=== group-chat at 14:23 已读 region ===")
for y in range(585, 615):
    row=[]
    for x in range(280, 380):
        r=px(g,x,y)
        if r[2]>=140 and r[2]>r[0]+15 and r[2]>r[1]+5:
            row.append((x,r))
    if row:
        print(f" y={y}: bluish x-range [{row[0][0]}..{row[-1][0]}], sample={row[len(row)//2][1]}")

# === mobile-chat: look near 14:13, 14:15, 14:16, 14:23, 14:25 outbound bubbles ===
m=load("mobile-chat.jpg")
print()
print("=== mobile-chat outbound bubble time region scanning (right side y=190-790) ===")
total_bluish_text=0
for y in range(190, 800, 1):
    bluish_in_row=0
    for x in range(280, 380):
        r=px(m,x,y)
        # exclude bubble fill (which is very light blue/white), look for medium blue text
        if 60<=r[0]<=80 and 130<=r[1]<=170 and r[2]>=180:
            bluish_in_row+=1
    total_bluish_text += bluish_in_row
print(f" total candidate blue text pixels in outbound area (RGB~70,150,200): {total_bluish_text}")

# Compare with group-chat
print()
print("=== group-chat outbound bubble same scan ===")
gtot=0
for y in range(190, 800, 1):
    for x in range(280, 380):
        r=px(g,x,y)
        if 60<=r[0]<=80 and 130<=r[1]<=170 and r[2]>=180:
            gtot+=1
print(f" total candidate blue text pixels (group-chat): {gtot}")

# tablet-mid
t=load("tablet-mid.jpg")
print()
print("=== tablet-mid outbound bubble same scan (right pane x=750-895) ===")
ttot=0
for y in range(50, 660, 1):
    for x in range(750, 895):
        r=px(t,x,y)
        if 60<=r[0]<=80 and 130<=r[1]<=170 and r[2]>=180:
            ttot+=1
print(f" total candidate blue text pixels (tablet-mid): {ttot}")

# === Sample exact "已读" RGB in group-chat ===
print()
print("=== exact pixel at center of visible '已读' on group-chat ===")
# From visual: "14:15 已读" — text '已读' appears at approx x=345-365, y=270-278
# Try a few
for (x,y,label) in [(330,272,"after 14:15 area"),(345,273,"likely 已 字"),(360,273,"likely 读 字"),
                    (350,600,"14:23 area"),(345,600,"14:23 已")]:
    print(f" {label} ({x},{y}) = {px(g,x,y)}")

# === Tablet-mid icons: count actual distinct icon clusters in chat pane top bar ===
# The pane starts at x=445ish. Icons appear to the right of name.
print()
print("=== tablet-mid: scan x>=600 y=15-60 for dark icon glyphs ===")
# Use column-density of dark pixels
dark_cols={}
for x in range(600, 900):
    c=0
    for y in range(15,60):
        if br(px(t,x,y))<=160: c+=1
    if c>=2: dark_cols[x]=c
# group consecutive
xs=sorted(dark_cols.keys())
clusters=[]
cur=[]
for x in xs:
    if not cur or x-cur[-1]<=5: cur.append(x)
    else:
        clusters.append(cur); cur=[x]
if cur: clusters.append(cur)
print(f" dark glyph clusters in tablet topbar (x>=600): {len(clusters)}")
for cl in clusters:
    print(f"  cluster x={cl[0]}..{cl[-1]}, center={sum(cl)//len(cl)}, avg-dark-count={sum(dark_cols[x] for x in cl)/len(cl):.1f}")

# Sample icon color
if clusters:
    for cl in clusters:
        cx=sum(cl)//len(cl); cy=37
        print(f"  sample color at ({cx},{cy}) = {px(t,cx,cy)}")

# === emoji-panel: scan bottom tab row for blue highlight ===
ep=load("emoji-panel.jpg")
print()
print("=== emoji-panel bottom tab scan ===")
# Tabs are at approx y=798-815, distributed across 5 icons
# Find columns with blue-ish color
for y in [800, 805, 810]:
    print(f" y={y}:")
    for x in range(0, 390, 2):
        r=px(ep,x,y)
        if r[2]>=180 and r[2]>r[0]+40:  # blueish
            print(f"   blue at x={x}: {r}")

# === message-menu: scan rows in lower panel ===
mm=load("message-menu.jpg")
print()
print("=== message-menu row scan (lower panel y=460-830) ===")
# Detect transitions: each row has consistent light bg separated by ~6px gaps
# Sample center column for vertical luminance profile
profile=[]
for y in range(450, 830):
    samples=[px(mm,x,y) for x in (30, 100, 200, 300, 360)]
    profile.append((y, sum(br(s) for s in samples)/len(samples)))

# find peaks (rows) — local max above threshold 230
in_row=False; row_start=0; rows=[]
for y, l in profile:
    if l>=235:
        if not in_row: row_start=y; in_row=True
    else:
        if in_row:
            rows.append((row_start,y-1)); in_row=False
if in_row: rows.append((row_start, profile[-1][0]))
# merge close (<8px)
merged=[]
for r in rows:
    if merged and r[0]-merged[-1][1]<=8: merged[-1]=(merged[-1][0], r[1])
    else: merged.append(list(r))
print(f" detected rows: {merged}")
print(f" row count: {len(merged)}")
# Compute gap heights between rows
gaps=[merged[i+1][0]-merged[i][1] for i in range(len(merged)-1)]
print(f" inter-row gaps: {gaps}")
print(f" row heights: {[r[1]-r[0]+1 for r in merged]}")

# Sample row bg color
print()
print(" row bg samples:")
for r in merged:
    y=(r[0]+r[1])//2
    print(f"  row y={y}: {px(mm,200,y)}")
