import numpy as np
from PIL import Image

def load(f):
    im = Image.open(f).convert("RGB")
    return np.array(im).astype(int), im.size

def analyze(name,f):
    a,(w,h)=load(f)
    xmax = 360 if w>400 else w
    a = a[:, :xmax]
    r,g,b = a[:,:,0],a[:,:,1],a[:,:,2]
    blue = (b>120)&(b>r+25)&(b>=g-15)
    red  = (r>165)&(g<115)&(b<115)&(r>g+50)&(r>b+50)
    green= (g>130)&(g>r+25)&(g>b+15)
    dark = (r<95)&(g<95)&(b<95)
    gray = (np.abs(r-g)<10)&(np.abs(g-b)<10)&(r>=225)&(r<=250)
    band=24
    print(f"\n##### {name} (analyzed x:0..{xmax}, {h} tall) #####")
    for y0 in range(0,h,band):
        y1=min(h,y0+band)
        cb=blue[y0:y1].sum(); cr=red[y0:y1].sum(); cg=green[y0:y1].sum()
        cdk=dark[y0:y1].sum(); cgrc=gray[y0:y1].sum()
        print(f" y{y0:3d}-{y1:3d}: BLUE={cb:5d} RED={cr:4d} GREEN={cg:5d} DARK={cdk:4d} GRAY={cgrc:5d}")

for name,f in [("mobile","mobile.jpg"),("channels","channels-tab.jpg"),
               ("contacts","contacts-tab.jpg"),("dynamics","dynamics-tab.jpg"),
               ("groupchat","group-chat.jpg")]:
    analyze(name,f)
