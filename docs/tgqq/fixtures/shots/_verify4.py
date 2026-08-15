import numpy as np
from PIL import Image
def load(f): return np.array(Image.open(f).convert("RGB")).astype(int)
def avg(a,x0,y0,x1,y1): return tuple(a[y0:y1,x0:x1].reshape(-1,3).mean(0).round(0).astype(int))

# channels recommended-card 关注 button (lower part of card)
a=load("channels-tab.jpg")[:,:360]
print("channels 关注 btn glyph @(300,208,338,226):",avg(a,300,208,338,226))
print("channels group follow btn @(290,470,334,492):",avg(a,290,470,334,492))
# contacts title core (tight on chars) + 新朋友 badge core
a=load("contacts-tab.jpg")[:,:360]
print("contacts title core @(60,24,110,40):",avg(a,60,24,110,40))
print("contacts 新朋友 badge core @(320,170,332,182):",avg(a,320,170,332,182))
# dynamics title core
a=load("dynamics-tab.jpg")[:,:360]
print("dynamics title core @(60,24,110,40):",avg(a,60,24,110,40))
# groupchat name core (search for blue/dark text in header y10-44 excluding x55-110 back arrow)
a=load("group-chat.jpg")
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
blue=(b>120)&(b>r+25)&(b>=g-15)
dark=(r<95)&(g<95)&(b<95)
hdr=a[10:44]
ys,xs=np.where(blue[10:44])
print("groupchat header BLUE px (excl back-arrow):", (int(xs.min()),int(xs.max()),int(ys.min()+10),int(ys.max()+10),len(xs)) if len(xs) else "none")
ys,xs=np.where(dark[10:44])
print("groupchat header DARK px:", (int(xs.min()),int(xs.max()),int(ys.min()+10),int(ys.max()+10),len(xs)) if len(xs) else "none")
# sample the central name band tightly
print("groupchat name band @(120,18,250,34):",avg(a,120,18,250,34))
