#!/usr/bin/env python3
import _analyze_round12 as A

def is_blue(p):
    r,g,b=p; return b>120 and b-r>60 and b-g>30
def light_blue_bg(p):
    r,g,b=p; return b>232 and b-r>10 and b-g>5 and not is_blue(p)

def panel_span(name, white_thresh=250):
    w,h=A.dims(name)
    # find first and last white-ish rows from bottom
    top=None; bottom=None
    for y in range(h):
        b,_=A.avg_brightness_line(name,y)
        if b is not None and b>230:
            # ensure white span wide enough
            row=A.scanline(name,y)
            whites=[i for i,p in enumerate(row) if A.brightness(p)>white_thresh]
            if len(whites)>w*0.5:
                top=y; break
    for y in range(h-1,-1,-1):
        b,_=A.avg_brightness_line(name,y)
        if b is not None and b>230:
            row=A.scanline(name,y)
            whites=[i for i,p in enumerate(row) if A.brightness(p)>white_thresh]
            if len(whites)>w*0.5:
                bottom=y; break
    return top,bottom

print("===== 1. EMOJI PANEL MOBILE =====")
ep="emoji-panel.jpg"
# mask
print("MASK (emoji-panel vs group-chat avg row brightness):")
for y in [25,40,55,200,300,380]:
    b1,_=A.avg_brightness_line(ep,y)
    b2,_=A.avg_brightness_line("group-chat.jpg",y)
    d=round(b2-b1,1) if b1 and b2 else None
    print(f"  y={y:3d}: masked={b1:.1f} base={b2:.1f} delta={d}")
# panel span
top,bottom=panel_span(ep)
print(f"Panel white span y={top}..{bottom} ({bottom-top}px); input bar y={bottom+2}..844 gray")
# tab bar blue icon (most saturated in known cluster)
best=None
for y in range(730,770):
    row=A.scanline(ep,y)
    for x in range(115,155):
        p=row[x]; r,g,b=p
        if is_blue(p):
            sat=b-r
            if best is None or sat>best[0]:
                best=(sat,x,y,p)
print(f"Active tab blue icon pixel: {best[1:] if best else 'NOT FOUND'}")
# 10% bg
bg=A.pixel(ep,135,746)
print(f"Active tab bg sample (135,746): {bg}")
# full width edge check at mid panel
row=A.scanline(ep,500)
print(f"Mid-panel full-width non-white (emoji glyphs) count={sum(1 for p in row if A.brightness(p)<240)} (OK, emojis)")
# corner radius estimate
print("Top-left corner white onset:")
for x in [0,5,8,12,16,20]:
    yf=None
    for y in range(388,420):
        if A.brightness(A.pixel(ep,x,y))>248:
            yf=y; break
    print(f"  x={x}: y={yf}")

print("\n===== 2. EMOJI PANEL TABLET =====")
et="emoji-panel-tablet.jpg"
W,H=A.dims(et)
print(f"  dims {W}x{H}")
print("MASK (emoji-panel-tablet vs group-chat-tablet):")
for y in [30,60,200,400]:
    b1,_=A.avg_brightness_line(et,y)
    b2,_=A.avg_brightness_line("group-chat-tablet.jpg",y)
    d=round(b2-b1,1) if b1 and b2 else None
    print(f"  y={y:3d}: masked={b1:.1f} base={b2:.1f} delta={d}")
top,bottom=panel_span(et)
print(f"Panel white span y={top}..{bottom} ({bottom-top}px)")
row=A.scanline(et,(top+bottom)//2)
whites=[i for i,p in enumerate(row) if A.brightness(p)>250]
print(f"Mid-panel white x-span={whites[0] if whites else None}..{whites[-1] if whites else None}  W={W}")
# active tab icon (the real one, left of center)
best=None
for y in range(580,615):
    row=A.scanline(et,y)
    for x in range(350,420):
        p=row[x]
        if is_blue(p):
            sat=b-r
            if best is None or sat>best[0]:
                best=(sat,x,y,p)
        elif light_blue_bg(p):
            if best is None or (b-r)>best[0]:
                best=(b-r,x,y,p)
print(f"Active tab icon sample (tablet): {best[1:] if best else 'NOT FOUND'}")
# bottom-right blue send button (saturated)
best=None
for y in range(620,670):
    row=A.scanline(et,y)
    for x in range(800,890):
        p=row[x]
        if is_blue(p):
            sat=b-r
            if best is None or sat>best[0]:
                best=(sat,x,y,p)
print(f"Send button blue sample: {best[1:] if best else 'NOT FOUND'}")

print("\n===== 3. MESSAGE MENU MOBILE =====")
mm="message-menu.jpg"
print("MASK (message-menu vs group-chat):")
for y in [25,40,55,200,300,700]:
    b1,_=A.avg_brightness_line(mm,y)
    b2,_=A.avg_brightness_line("group-chat.jpg",y)
    d=round(b2-b1,1) if b1 and b2 else None
    print(f"  y={y:3d}: masked={b1:.1f} base={b2:.1f} delta={d}")
# find white action sheet
row=A.scanline(mm,700)
# find bottom-most bright white strip
top,bottom=panel_span(mm)
print(f"Action sheet white span y={top}..{bottom} ({bottom-top}px)")
# full width at mid sheet
row=A.scanline(mm,(top+bottom)//2)
whites=[i for i,p in enumerate(row) if A.brightness(p)>250]
print(f"Sheet full-width: x={whites[0] if whites else None}..{whites[-1] if whites else None}  W=390")
# detect rows (dark text/gray icons): scan avg brightness inside sheet per y
print("Sheet row brightness profile (y=top..bottom):")
for y in range(top,bottom+1,3):
    b,n=A.avg_brightness_line(mm,y)
    if b is not None:
        print(f"  y={y:3d} avg={b:.1f}")

print("\n===== 4. MESSAGE MENU TABLET =====")
mt="message-menu-tablet.jpg"
W,H=A.dims(mt)
print(f"  dims {W}x{H}")
# find white floating card
top,bottom=panel_span(mt)
print(f"Floating card white span y={top}..{bottom} ({bottom-top}px)")
row=A.scanline(mt,(top+bottom)//2)
whites=[i for i,p in enumerate(row) if A.brightness(p)>250]
print(f"Card width={whites[-1]-whites[0]+1 if whites else None}px  center≈{W//2}  left={whites[0] if whites else None}")
# check all corners rounded: find left white onset at various y, etc
print("Top-left and bottom-left corner onset:")
for x in [290,300,310,320]:
    for y0 in [top,bottom]:
        yf=None
        for y in range(y0-15,y0+15):
            if 0<=y<H and A.brightness(A.pixel(mt,x,y))>248:
                yf=y; break
        print(f"  x={x} @ {'top' if y0==top else 'bottom'}: y={yf}")

print("\n===== 5. GROUP-CHAT REGRESSION =====")
gc="group-chat.jpg"
print("No-mask check (header avg brightness):")
for y in [25,40,55]:
    b,_=A.avg_brightness_line(gc,y)
    print(f"  y={y:3d} avg={b:.1f} (should be bright ~230-250)")
# sample blue name text "周子昂"
print(f"Name text sample (66,420 expected blue): {A.pixel(gc,66,420)}")
print(f"Another name sample (66,602 '陈默'): {A.pixel(gc,66,602)}")
# avatar bottom vs bubble bottom - sample avatar bottom row and bubble bottom
for name,y_avatar,y_bubble in [("周子昂",348,338),("陈默",532,522),("陈_2",716,706)]:
    print(f"{name}: avatar sample y={y_avatar} {A.pixel(gc,45,y_avatar)}  bubble-bottom y={y_bubble} {A.pixel(gc,120,y_bubble)}")
