#!/usr/bin/env python3
"""Round-13 final visual audit of 5 TGQQ fixture screenshots.

Verifies A-E features and produces coordinate evidence for each PASS/FAIL.
"""
from PIL import Image
import os, json, collections, math

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
TARGETS = [
    ("mobile-chat.jpg",   "mobile-chat",   390, 844),
    ("group-chat.jpg",    "group-chat",    390, 844),
    ("tablet-mid.jpg",    "tablet-mid",    900, 700),
    ("emoji-panel.jpg",   "emoji-panel",   390, 844),
    ("message-menu.jpg",  "message-menu",  390, 844),
]

def load(name):
    return Image.open(os.path.join(SHOTS, name)).convert("RGB")

def px(img, x, y):
    return img.getpixel((int(x), int(y)))

def brightness(rgb):
    return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]

def is_qq_blue(rgb, tol=35):
    """#1296DB = (18,150,219). Allow some JPEG/AA tolerance."""
    r,g,b = rgb
    return abs(r-18)<=tol and abs(g-150)<=tol and abs(b-219)<=tol

def is_dark_mask(rgb):
    """A mask overlay darkens content. Avg luma <= ~140 qualifies."""
    return brightness(rgb) <= 140

def is_orange_avatar(rgb):
    r,g,b = rgb
    # QQ-style orange avatar: roughly (255,140,60)-(250,120,50)
    return r>=230 and 90<=g<=170 and 30<=b<=110 and r>g>b

def is_purple_avatar(rgb):
    r,g,b = rgb
    return 110<=r<=180 and 70<=g<=140 and 150<=b<=210

def find_blue_clusters(img, x0, y0, x1, y1):
    """Return list of (cx, cy, count) for connected-ish blue regions in rect."""
    seen=set()
    clusters=[]
    for y in range(y0,y1,2):
        for x in range(x0,x1,2):
            if (x,y) in seen: continue
            if is_qq_blue(px(img,x,y),tol=40):
                # BFS small region
                stack=[(x,y)]; pts=[]
                while stack:
                    cx,cy=stack.pop()
                    if (cx,cy) in seen: continue
                    seen.add((cx,cy))
                    if not is_qq_blue(px(img,cx,cy),tol=40): continue
                    pts.append((cx,cy))
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx,ny=cx+dx,cy+dy
                        if x0<=nx<x1 and y0<=ny<y1 and (nx,ny) not in seen:
                            stack.append((nx,ny))
                if len(pts)>=3:
                    cxs=[p[0] for p in pts]; cys=[p[1] for p in pts]
                    clusters.append((sum(cxs)//len(cxs), sum(cys)//len(cys), len(pts)))
    return clusters

def sample_brightness_band(img, y0, y1, x0=None, x1=None):
    w,h=img.size
    x0=0 if x0 is None else x0
    x1=w if x1 is None else x1
    total=0; n=0
    for y in range(y0,y1,3):
        for x in range(x0,x1,3):
            total += brightness(px(img,x,y))
            n+=1
    return total/n if n else 0

def detect_avatar_columns(img, y0, y1):
    """Walk every row band; find columns where there's a colored (orange/purple) circular fill."""
    w,h=img.size
    band_colors=collections.Counter()
    band_left={}
    for y in range(y0,y1,4):
        for x in range(0,min(70,w),2):
            r=px(img,x,y)
            if is_orange_avatar(r) or is_purple_avatar(r):
                key=(x//12)
                band_colors[key]+=1
    return band_colors

def find_orange_blocks(img, y_range, x_max=80):
    """Find vertical extents of orange/purple circular avatar columns."""
    w,h=img.size
    cols={}
    for y in range(*y_range,2):
        for x in range(0,x_max,2):
            r=px(img,x,y)
            if is_orange_avatar(r) or is_purple_avatar(r):
                cols.setdefault(x,[]).append(y)
    # group adjacent x into blocks
    sorted_x=sorted(cols.keys())
    blocks=[]
    cur=[]; last_x=None
    for x in sorted_x:
        if last_x is None or x-last_x<=3:
            cur.append(x)
        else:
            ys=[]
            for cx in cur:
                ys.extend(cols[cx])
            if ys:
                blocks.append({"x_min":min(cur),"x_max":max(cur),
                               "y_min":min(ys),"y_max":max(ys),
                               "w":max(cur)-min(cur)+1,"h":max(ys)-min(ys)+1,
                               "n":len(ys)})
            cur=[x]
        last_x=x
    if cur:
        ys=[]
        for cx in cur:
            ys.extend(cols[cx])
        if ys:
            blocks.append({"x_min":min(cur),"x_max":max(cur),
                           "y_min":min(ys),"y_max":max(ys),
                           "w":max(cur)-min(cur)+1,"h":max(ys)-min(ys)+1,
                           "n":len(ys)})
    return blocks

def find_topbar_icon_centers(img, y0, y1, x_start):
    """Detect dark glyphs (icon shapes) in top-right corner.
    Returns centers (cx, cy) by finding columns with many dark pixels (luma<140)."""
    w,h=img.size
    dark=collections.Counter()
    for y in range(y0,y1):
        for x in range(x_start, w):
            if brightness(px(img,x,y)) <= 140:
                dark[x//3]+=1
    # group consecutive buckets with hits >=2 into clusters
    buckets=[(bx*3, c) for bx,c in sorted(dark.items()) if c>=2]
    clusters=[]
    cur=[]; last=None
    for x,c in buckets:
        if last is None or x-last<=9:
            cur.append((x,c))
        else:
            if cur:
                tot=sum(v for _,v in cur); cx=sum(x*v for x,v in cur)//tot
                clusters.append(cx)
            cur=[(x,c)]
        last=x
    if cur:
        tot=sum(v for _,v in cur); cx=sum(x*v for x,v in cur)//tot
        clusters.append(cx)
    # merge within 18 px
    merged=[]
    for c in clusters:
        if merged and c-merged[-1]<=18:
            merged[-1]=(merged[-1]+c)//2
        else:
            merged.append(c)
    return merged

def detect_rounded_rows(img, y0, y1, x0=20, x1=None):
    """Count horizontal rounded panels (action sheet rows) by detecting
    rows of consistent light fill separated by gaps."""
    w,h=img.size
    x1 = w-20 if x1 is None else x1
    rows=[]
    in_row=False; row_start=0
    for y in range(y0,y1):
        light=0; total=0
        for x in range(x0,x1,4):
            total+=1
            if brightness(px(img,x,y))>=235:
                light+=1
        if light/total>=0.92:
            if not in_row:
                row_start=y; in_row=True
        else:
            if in_row:
                rows.append((row_start,y-1))
                in_row=False
    if in_row:
        rows.append((row_start,y1-1))
    # merge close rows
    merged=[]
    for r in rows:
        if merged and r[0]-merged[-1][1]<=4:
            merged[-1]=(merged[-1][0], r[1])
        else:
            merged.append(list(r))
    return merged

def main():
    out={}
    for fname, key, W, H in TARGETS:
        img=load(fname)
        out[key]={"size":[W,H]}

    # --- A) "已读" blue text: scan outbound bubble area (right side) ---
    # mobile-chat: outbound bubbles at x ~225-385
    # group-chat: same
    # tablet-mid: right pane outbound area (x ~530-895)
    for key, x0, x1 in [
        ("mobile-chat",  225, 385),
        ("group-chat",   225, 385),
        ("tablet-mid",   520, 895),
    ]:
        img=load([t[0] for t in TARGETS if t[1]==key][0])
        clusters=find_blue_clusters(img, x0, 0, x1, 700)
        # filter to text-like small clusters (n<=80) — large ones are bubble fills
        text_clusters=[c for c in clusters if c[2]<=90]
        out[key]["blue_text_clusters"]=len(text_clusters)
        out[key]["blue_cluster_sample"]=text_clusters[:8]

    # Sample the actual color at the "已读" location in group-chat (we saw 14:15 已读)
    g=load("group-chat.jpg")
    # around 14:15 已读 — visually bubble ends around y=275 with "14:15 已读" — sample
    samples=[]
    # we'll scan near right bubble bottom rows for blue-ish text-like pixels
    for y in range(250, 650, 2):
        for x in range(290, 380, 1):
            r=px(g,x,y)
            if is_qq_blue(r,tol=45):
                samples.append((x,y,r))
    out["group-chat"]["blue_pixel_samples"]={
        "n":len(samples),
        "first":samples[0] if samples else None,
        "example_rgb":samples[0][2] if samples else None,
        "y_range":(min(s[1] for s in samples), max(s[1] for s in samples)) if samples else None,
        "x_range":(min(s[0] for s in samples), max(s[0] for s in samples)) if samples else None,
    }
    # mobile-chat outbound scan (no 已读 seen) — record 0 cluster
    m=load("mobile-chat.jpg")
    ms=[]
    for y in range(150, 800, 2):
        for x in range(290, 380, 1):
            r=px(m,x,y)
            if is_qq_blue(r,tol=45) and brightness(r)<200:
                # restrict to text-thin: only near bubble edges? Just collect
                ms.append((x,y,r))
    out["mobile-chat"]["blue_pixel_samples"]={
        "n":len(ms),
        "y_range":(min(s[1] for s in ms), max(s[1] for s in ms)) if ms else None,
    }

    # --- B) inbound avatar geometry ---
    for fname, key in [("mobile-chat.jpg","mobile-chat"),
                       ("group-chat.jpg","group-chat"),
                       ("tablet-mid.jpg","tablet-mid")]:
        img=load(fname)
        if key=="tablet-mid":
            blocks=find_orange_blocks(img,(80,680), x_max=620)
            # tablet inbound area only — restrict to left of chat pane (x<540)
            blocks=[b for b in blocks if b["x_min"]>=440]
        else:
            blocks=find_orange_blocks(img,(80,800), x_max=70)
        # only sizable blocks (real avatars)
        avatars=[b for b in blocks if b["w"]>=20 and b["h"]>=20]
        out[key]["inbound_avatars"]=avatars

    # --- C) top bar icon count ---
    for fname, key in [("mobile-chat.jpg","mobile-chat"),
                       ("group-chat.jpg","group-chat"),
                       ("tablet-mid.jpg","tablet-mid"),
                       ("emoji-panel.jpg","emoji-panel"),
                       ("message-menu.jpg","message-menu")]:
        img=load(fname)
        # top bar y range ~20-70
        if key=="tablet-mid":
            # chat pane top bar only: x>=450
            centers=find_topbar_icon_centers(img, 10, 70, 450)
        else:
            centers=find_topbar_icon_centers(img, 10, 70, 300)
        out[key]["topbar_icon_centers"]=centers
        out[key]["topbar_icon_count"]=len(centers)

    # --- D) emoji-panel dark mask ---
    ep=load("emoji-panel.jpg")
    # Above panel: y 0-440 (chat area). Panel: y 440-820.
    above_lum=sample_brightness_band(ep, 50, 420)
    panel_lum=sample_brightness_band(ep, 480, 760)
    out["emoji-panel"]["above_avg_luma"]=round(above_lum,1)
    out["emoji-panel"]["panel_avg_luma"]=round(panel_lum,1)
    out["emoji-panel"]["mask_ratio"]=round(above_lum/panel_lum,3) if panel_lum else None
    # sample a point on a dimmed bubble (we saw bubble "听说郊区..." near y=120)
    out["emoji-panel"]["bubble_pixel_sample"]=px(ep, 230, 120)

    # bottom tab active color
    # emoji tabs at very bottom ~ y 800-820
    # sample colors along y=805 across full width
    tab_line=[]
    for x in range(0,390,4):
        tab_line.append((x, px(ep,x,808)))
    out["emoji-panel"]["tab_row_sample"]=[(x,c) for x,c in tab_line if brightness(c)<210 and (c[2]>150 or (c[0]<80 and c[2]>80))][:10]

    # --- E) message-menu rows ---
    mm=load("message-menu.jpg")
    rows=detect_rounded_rows(mm, 450, 830)
    out["message-menu"]["rows"]=rows
    out["message-menu"]["row_count"]=len(rows)
    out["message-menu"]["row_avg_height"]=round((sum(r[1]-r[0]+1 for r in rows)/len(rows)),1) if rows else 0
    # background mask brightness sample above panel
    out["message-menu"]["above_mask_luma"]=round(sample_brightness_band(mm, 30, 440),1)
    out["message-menu"]["panel_luma"]=round(sample_brightness_band(mm, 470, 800),1)

    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))

if __name__=="__main__":
    main()
