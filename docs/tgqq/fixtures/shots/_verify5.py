import numpy as np
from PIL import Image
def load(f): return np.array(Image.open(f).convert("RGB")).astype(int)

# definitive 关注 button hue = mean of blue-flagged pixels only
a=load("channels-tab.jpg")[:,:360]
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
blue=(b>120)&(b>r+25)&(b>=g-15)
m=blue[161:227,283:341]
px=a[161:227,283:341][m]
print("channels 关注 button BLUE-px hue mean:", tuple(px.mean(0).round(0).astype(int)), "n=",len(px))

# dynamics header: locate title text (dark or blue) excluding avatar x300-345 & camera
a=load("dynamics-tab.jpg")[:,:360]
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
dark=(r<110)&(g<110)&(b<110)
blue=(b>120)&(b>r+25)&(b>=g-15)
print("dynamics header DARK px y14-44:", [(int(xs.min()),int(xs.max()),int(ys.min()+14),int(ys.max()+14),len(xs)) for xs,ys in [(np.where(dark[14:44])[1],np.where(dark[14:44])[0])] if len(xs)])
print("dynamics header BLUE px y14-44 (excl x300-345):")
ys,xs=np.where(blue[14:44])
xs2=xs[(xs<295)]
if len(xs2):
    print("   x",int(xs2.min()),"-",int(xs2.max()),"y",int(ys.min()+14),"-",int(ys.max()+14),"n=",len(xs2))
    # mean color of those blue px
    print("   hue:",tuple(a[14:44, :][blue[14:44]][:, :][np.where(blue[14:44])[0]][:len(xs2)].mean(0).round(0).astype(int)) if False else "see below")
    sub=a[14:44][blue[14:44]]
    print("   hue mean:",tuple(sub.mean(0).round(0).astype(int)))
else:
    print("   none")

# contacts header title: scan for dark text y14-44 x40-200
a=load("contacts-tab.jpg")[:,:360]
dark=(a[:,:,0]<110)&(a[:,:,1]<110)&(a[:,:,2]<110)
ys,xs=np.where(dark[14:44,30:200])
if len(xs): print("contacts title DARK x30-200 y14-44: x",int(xs.min()+30),"-",int(xs.max()+30)," n=",len(xs))
else: print("contacts title DARK: none in x30-200")

# channels header title
a=load("channels-tab.jpg")[:,:360]
dark=(a[:,:,0]<110)&(a[:,:,1]<110)&(a[:,:,2]<110)
ys,xs=np.where(dark[14:44,30:200])
if len(xs): print("channels title DARK x30-200 y14-44: x",int(xs.min()+30),"-",int(xs.max()+30)," n=",len(xs))
else: print("channels title DARK: none in x30-200")
