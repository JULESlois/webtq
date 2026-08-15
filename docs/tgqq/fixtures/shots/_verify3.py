import numpy as np
from PIL import Image
def load(f): return np.array(Image.open(f).convert("RGB")).astype(int)
def avg(a,x0,y0,x1,y1): return tuple(a[y0:y1,x0:x1].reshape(-1,3).mean(0).round(0).astype(int))

print("## MOBILE selected-row tint scan (y=158) light-blue across x ##")
a=load("mobile.jpg")
def is_tint(p):
    r,g,b=p; return b>200 and g>210 and r>165 and b>=r-10 and g>=r-10
for x in range(0,390,30):
    print(f"  x{x:3d}-{x+30}: {avg(a,x,150,x+30,166)}  tint={'Y' if is_tint(avg(a,x,150,x+30,166)) else '-'}")
# left edge blue bar
print(" left edge x0..4 y150..200 colors:", [tuple(avg(a,0,y,4,y+8)) for y in range(150,200,12)])
# green dot search y40-72
green=(a[:,:,1]>130)&(a[:,:,1]>a[:,:,0]+25)&(a[:,:,1]>a[:,:,2]+15)
ys,xs=np.where(green); print(" GREEN px:", (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max()),len(xs)) if len(xs) else "none")
# + sign top-right dark y20-50 x335-378
dark=(a[:,:,0]<95)&(a[:,:,1]<95)&(a[:,:,2]<95)
ys,xs=np.where(dark[:55,330:380]); print(" +/dark top-right x335-378 y0-55:", (int(xs.min()+330),int(xs.max()+330),int(ys.min()),int(ys.max()),len(xs)) if len(xs) else "none")

print("\n## CHANNELS title '频道' + 关注 btn ##")
a=load("channels-tab.jpg")[:,:360]
print(" title @(70,30):",avg(a,55,22,120,40),"  header-left dark @(20,28):",avg(a,14,20,40,40))
print(" 关注 btn @(310,194):",avg(a,300,184,340,206))
print(" header avatar top-right @(314,29):",avg(a,307,12,344,46))
print("\n## CONTACTS title + 新朋友 badge ##")
a=load("contacts-tab.jpg")[:,:360]
print(" title @(70,30):",avg(a,55,22,120,40))
print(" 新朋友 red badge @(324,176):",avg(a,316,168,333,186))
print(" header avatar top-right @(314,29):",avg(a,307,12,344,46))
print("\n## DYNAMICS header avatar + camera ##")
a=load("dynamics-tab.jpg")[:,:360]
print(" header avatar top-right @(314,29):",avg(a,307,12,344,46))
print(" camera btn near @(330,30):",avg(a,318,20,344,44))
print("\n## GROUPCHAT externalized name color ##")
a=load("group-chat.jpg")
print(" title @(120,22):",avg(a,95,14,230,34))
print(" title @(150,22) tighter:",avg(a,140,16,210,32))
# is name blue?
nm=avg(a,140,16,210,32)
print("  -> name bluish?" , (nm[2]>nm[0]+20))
print(" back-arrow blue @(81,25):",avg(a,61,8,101,46))
