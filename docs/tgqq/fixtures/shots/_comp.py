import numpy as np
from PIL import Image
from scipy import ndimage

def load(f):
    return np.array(Image.open(f).convert("RGB")).astype(int), Image.open(f).size

def comps(mask, minsize=25):
    lab,n=ndimage.label(mask)
    out=[]
    for i in range(1,n+1):
        ys,xs=np.where(lab==i)
        if len(xs)>=minsize:
            out.append((len(xs),xs.min(),xs.max(),ys.min(),ys.max(),
                        int(xs.mean()),int(ys.mean())))
    out.sort(reverse=True)
    return out

for name,f,clip in [("mobile","mobile.jpg",390),("channels","channels-tab.jpg",360),
               ("contacts","contacts-tab.jpg",360),("dynamics","dynamics-tab.jpg",360),
               ("groupchat","group-chat.jpg",390)]:
    a,(w,h)=load(f)
    if w>400: a=a[:,:360]
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    blue=(b>120)&(b>r+25)&(b>=g-15)
    dark=(r<95)&(g<95)&(b<95)
    red=(r>165)&(g<115)&(b<115)&(r>g+50)&(r>b+50)
    print(f"\n===== {name} =====")
    print(" BLUE components (size,x0,x1,y0,y1,cx,cy):")
    for c in comps(blue)[:12]: print("   ",c)
    print(" DARK components:")
    for c in comps(dark,20)[:12]: print("   ",c)
    print(" RED components:")
    for c in comps(red,15)[:10]: print("   ",c)
