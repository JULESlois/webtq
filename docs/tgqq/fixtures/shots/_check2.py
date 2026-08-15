#!/usr/bin/env python3
import _analyze_round12 as A

def blue_icon(p):
    r,g,b = p
    return b>120 and b-r>60 and b-g>30
def light_blue_bg(p):
    r,g,b = p
    # 10% #1296DB over white => ~(232,235,245); distinguish from pure white
    return b>232 and b-r>10 and b-g>5 and not blue_icon(p)

print("== blue icon exact value & 10% bg in tab bar (emoji-panel.jpg) ==")
print(" pixel(135,750) =", A.pixel("emoji-panel.jpg",135,750))
# scan tab bar rows for light-blue bg patches
print(" light-blue-bg pixels per row (y=724..772):")
for y in range(724,773,2):
    row=A.scanline("emoji-panel.jpg",y)
    bg=[i for i,p in enumerate(row) if light_blue_bg(p)]
    if bg:
        print(f"  y={y}: x={bg[0]}..{bg[-1]} (n={len(bg)})")

print("\n== panel top corners / full width at top of panel ==")
for y in [388,390,392,400]:
    row=A.scanline("emoji-panel.jpg",y)
    if not row: 
        print(y,"EMPTY"); continue
    left=row[0]; right=row[-1]
    # find first non-white from left and from right
    fw=next((i for i,p in enumerate(row) if A.brightness(p)>250),None)
    rw=next((i for i in range(len(row)-1,-1,-1) if A.brightness(row[i])>250),None)
    print(f" y={y}: firstWhite x={fw}  lastWhite x={rw}  leftEdge={left} rightEdge={right}")

print("\n== MASK: header brightness compare emoji-panel vs group-chat ==")
for y in [25,40,55]:
    b1,_=A.avg_brightness_line("emoji-panel.jpg",y)
    b2,_=A.avg_brightness_line("group-chat.jpg",y)
    print(f" header y={y}: emoji-panel avg={b1}  group-chat avg={b2}  delta={None if (b1 is None or b2 is None) else round(b2-b1,1)}")

print("\n== MASK: chat-area darkening (y=200 & y=300) ==")
for y in [200,300]:
    b1,_=A.avg_brightness_line("emoji-panel.jpg",y)
    b2,_=A.avg_brightness_line("group-chat.jpg",y)
    print(f" y={y}: emoji-panel avg={b1}  group-chat avg={b2}  delta={None if (b1 is None or b2 is None) else round(b2-b1,1)}")
