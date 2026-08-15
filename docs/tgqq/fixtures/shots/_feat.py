import numpy as np
from PIL import Image

def load(f):
    im = Image.open(f).convert("RGB")
    return np.array(im), im.size

def is_blue(p):  # QQ blue family: b dominant
    r,g,b = p
    return b>140 and b>r+30 and b>=g-10
def is_red(p):
    r,g,b = p
    return r>170 and g<110 and b<110
def is_green(p):
    r,g,b = p
    return g>140 and g>r+30 and g>b+20
def is_graycap(p):  # light gray ~ (240,240,240)
    r,g,b = p
    return abs(r-g)<8 and abs(g-b)<8 and 232<=r<=250
def is_darktext(p):
    r,g,b = p
    return r<90 and g<90 and b<90

def bbox_groups(a, pred, band=18, gap=6):
    """Return list of (y0,y1,x0,x1) bands where pred true for many pixels."""
    h,w = a.shape[:2]
    ys = [y for y in range(h) for x in range(w) if pred(a[y,x])]
    if not ys: return []
    xs = [x for y in range(h) for x in range(w) if pred(a[y,x])]
    return (min(ys),max(ys),min(xs),max(xs),len(ys))

for name,f in [("mobile","mobile.jpg"),("channels","channels-tab.jpg"),
               ("contacts","contacts-tab.jpg"),("dynamics","dynamics-tab.jpg"),
               ("groupchat","group-chat.jpg")]:
    a,(w,h)=load(f)
    print(f"\n##### {name} {w}x{h} #####")
    for label,pred in [("BLUE",is_blue),("RED",is_red),("GREEN",is_green),
                       ("GRAYCAP",is_graycap),("DARKTEXT",is_darktext)]:
        res = bbox_groups(a,pred)
        if res:
            y0,y1,x0,x1,n=res
            print(f"  {label}: y[{y0}..{y1}] x[{x0}..{x1}] count={n}")
        else:
            print(f"  {label}: none")
