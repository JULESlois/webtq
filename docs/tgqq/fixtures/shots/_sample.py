import numpy as np
from PIL import Image

def load(f):
    return np.array(Image.open(f).convert("RGB")).astype(int), Image.open(f).size

def dom(a):  # dominant color of region (median per channel)
    return tuple(np.median(a.reshape(-1,3),0).round(0).astype(int))

def patch(a,x0,y0,x1,y1):
    return a[y0:y1, x0:x1]

def count(a, pred):
    return int(pred(a).sum())

def is_blue(p):
    r,g,b=p; return b>120 and b>r+25 and b>=g-15
def is_midgray(p):
    r,g,b=p; return abs(r-g)<25 and abs(g-b)<25 and 55<r<125
def is_red(p):
    r,g,b=p; return r>165 and g<115 and b<115 and r>g+50 and r>b+50
def is_green(p):
    r,g,b=p; return g>130 and g>r+25 and g>b+15

# ---- bottom nav tab analysis ----
def nav_tabs(a, w, h, n=4, navh=52):
    r,g,b = a[:,:,0],a[:,:,1],a[:,:,2]
    blue=(b>120)&(b>r+25)&(b>=g-15)
    mg=(np.abs(r-g)<25)&(np.abs(g-b)<25)&(r>55)&(r<125)
    y0=h-navh
    seg=w/n
    res=[]
    for i in range(n):
        cx0=int(i*seg+seg*0.2); cx1=int(i*seg+seg*0.8)
        win=blue[y0:y0+navh, cx0:cx1]
        winmg=mg[y0:y0+navh, cx0:cx1]
        res.append((i+1, int(win.sum()), int(winmg.sum()), int((r[y0:y0+navh,cx0:cx1]).mean())))
    return y0,res

print("============ BOTTOM NAV TAB COLORS ============")
for name,f in [("mobile","mobile.jpg"),("channels","channels-tab.jpg"),
               ("contacts","contacts-tab.jpg"),("dynamics","dynamics-tab.jpg"),
               ("groupchat","group-chat.jpg")]:
    a,(w,h)=load(f)
    xmax=360 if w>400 else w
    y0,res=nav_tabs(a[:,:xmax], xmax, h)
    print(f"{name}: nav band y={y0}..{h}, leftcol_w={xmax}")
    for idx,bl,mg,meanr in res:
        sel = "SELECTED(blue)" if bl>mg and bl>40 else ("gray" if mg>bl else "?")
        print(f"   tab{idx}: bluePx={bl:4d} midgrayPx={mg:4d} meanR={meanr:3d} -> {sel}")
