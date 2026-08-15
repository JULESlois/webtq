#!/usr/bin/env python3
import _analyze_round12 as A

print("===== 1. message-menu mobile mask =====")
for y in [25,40,55,300,700]:
    b1,_=A.avg_brightness_line("message-menu.jpg",y)
    b2,_=A.avg_brightness_line("group-chat.jpg",y)
    print(f" y={y}: menu={b1:.1f} base={b2:.1f} delta={round(b2-b1,1)}")

print("\n===== 2. message-menu mobile sheet y-span (center x=195) =====")
for y in range(500,844,3):
    p=A.pixel("message-menu.jpg",195,y)
    b=A.brightness(p)
    if b>230:
        print(f" first white row y={y} {p}")
        break
for y in range(843,500,-3):
    p=A.pixel("message-menu.jpg",195,y)
    b=A.brightness(p)
    if b>230:
        print(f" last  white row y={y} {p}")
        break

print("\n===== 3. message-menu tablet card width =====")
W,H=A.dims("message-menu-tablet.jpg")
print(f"dims {W}x{H}")
# find white mid-height
for y in range(H//2-50,H//2+50):
    row=A.scanline("message-menu-tablet.jpg",y)
    whites=[i for i,p in enumerate(row) if A.brightness(p)>250]
    if whites:
        print(f" y={y}: card x={whites[0]}..{whites[-1]} width={whites[-1]-whites[0]+1}")
        break

print("\n===== 4. group-chat regression =====")
for y in [25,40,55]:
    b,_=A.avg_brightness_line("group-chat.jpg",y)
    print(f" header y={y} bright={b:.1f}")
print("name text pixels:")
# approximate positions from visual: '周子昂' around x=66 y=410 ; '陈默' x=66 y=590
for x,y,label in [(66,410,"周子昂"),(66,590,"陈默")]:
    print(f"  {label} @({x},{y}): {A.pixel('group-chat.jpg',x,y)}")
print("avatar bottom vs bubble bottom:")
for x,y,label in [(45,353,"周头像底"),(45,536,"陈默头像底"),(45,732,"陈头像底")]:
    print(f"  {label} @({x},{y}): {A.pixel('group-chat.jpg',x,y)}")
# bubble bottom around x=120,y=348 etc
for x,y,label in [(150,348,"周气泡底"),(150,532,"陈默气泡底"),(150,730,"陈气泡底")]:
    print(f"  {label} @({x},{y}): {A.pixel('group-chat.jpg',x,y)}")

print("\n===== 5. tablet emoji active icon sample =====")
# active emoji tab: visually 2nd icon from left, in tab bar ~y=580-610 x~370-410
print(f" active tab bg sample (390,600): {A.pixel('emoji-panel-tablet.jpg',390,600)}")
print(f" active tab icon sample (390,596): {A.pixel('emoji-panel-tablet.jpg',390,596)}")
print(f" inactive tab icon sample (sticker, 520,596): {A.pixel('emoji-panel-tablet.jpg',520,596)}")
