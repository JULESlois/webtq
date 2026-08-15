#!/usr/bin/env python3
import _analyze_round12 as A

def is_blue(p):
    r,g,b=p
    return b>120 and b-r>60 and b-g>30
def light_blue_bg(p):
    r,g,b=p
    return b>232 and b-r>10 and b-g>5 and not is_blue(p)

N="emoji-panel-tablet.jpg"
W,H=A.dims(N)
print(f"== {N} {W}x{H} ==")
# vertical profile at center (x=W//2=450)
print("center column brightness (sampled):")
for y in range(380,701,6):
    p=A.pixel(N,450,y)
    b=A.brightness(p)
    print(f" y={y:3d} bright={b:6.1f} {p}{'  <dark' if b<150 else ''}")

print("\nfull-width white of panel @ y=560 (find panel x-span):")
row=A.scanline(N,560)
# find white span
whites=[i for i,p in enumerate(row) if A.brightness(p)>250]
if whites:
    print(f" white x={whites[0]}..{whites[-1]} (n={len(whites)})  W={W}")
    print(f" leftEdge px={row[0]}  rightEdge px={row[-1]}")

print("\nblue highlight in tab bar (scan y=600..680):")
for y in range(600,681,3):
    row=A.scanline(N,y)
    hits=[i for i,p in enumerate(row) if is_blue(p)]
    if hits:
        print(f" y={y}: blue x={hits[0]}..{hits[-1]} n={len(hits)}")

print("\nlight-blue bg (active tab) y=600..680:")
for y in range(600,681,3):
    row=A.scanline(N,y)
    bg=[i for i,p in enumerate(row) if light_blue_bg(p)]
    if bg:
        print(f" y={y}: bg x={bg[0]}..{bg[-1]} n={len(bg)}")

print("\nMASK header compare (emoji-panel-tablet vs group-chat-tablet):")
for y in [30,60]:
    b1,_=A.avg_brightness_line(N,y)
    b2,_=A.avg_brightness_line("group-chat-tablet.jpg",y)
    print(f" y={y}: panel={b1}  grp={b2}  delta={None if b1 is None or b2 is None else round(b2-b1,1)}")
