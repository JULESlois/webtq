import numpy as np
from PIL import Image

def load(f):
    return np.array(Image.open(f).convert("RGB")).astype(int), Image.open(f).size
def avg(a,x0,y0,x1,y1):
    return tuple(a[y0:y1,x0:x1].reshape(-1,3).mean(0).round(0).astype(int))
def colrun(a, x, y0, y1, pred):
    ys=[y for y in range(y0,y1) if pred(a[y,x])]
    return (ys[0],ys[-1],len(ys)) if ys else None
def rowrun(a, y, x0, x1, pred):
    xs=[x for x in range(x0,x1) if pred(a[y,x])]
    return (xs[0],xs[-1],len(xs)) if xs else None
def is_graycap(p):
    r,g,b=p; return abs(r-g)<10 and abs(g-b)<10 and 225<=r<=250
def is_blue(p):
    r,g,b=p; return b>120 and b>r+25 and b>=g-15
def is_tint(p):
    r,g,b=p; return b>200 and g>215 and r>170 and b>=r and g>=r  # light blue selected-row
def is_dark(p):
    r,g,b=p; return r<95 and g<95 and b<95

print("===== MOBILE search capsule + header + rows =====")
a,(w,h)=load("mobile.jpg")
# search capsule: scan center column x=195 for graycap run
cx=195
run=colrun(a,cx,40,140,is_graycap)
print(" search capsule vertical run @x=195:",run)
if run:
    yc=(run[0]+run[1])//2
    rr=rowrun(a,yc,20,370,is_graycap)
    print(" search capsule height:",run[1]-run[0]," width x:",rr)
# header blue avatar + green dot
print(" header avatar @(38,45):",avg(a,30,38,50,55))
print(" header green dot @(66,58):",avg(a,60,52,74,66))
print(" + sign dark @(360,46):",avg(a,352,38,368,56))
# selected row tint + left bar
print(" selected-row tint @(30,180):",avg(a,20,160,120,210))
lb=colrun(a,1,150,215,is_blue)
print(" left 3px blue-bar run @x=1:",lb, " color@(0,180):",avg(a,0,175,3,185))
# row height: detect avatar column x=40 gray/tint boundaries
print(" conv-row1 avatar @(40,170):",avg(a,28,150,52,176))
# unread red badge location
red=(a[:,:,0]>165)&(a[:,:,1]<115)&(a[:,:,2]<115)&(a[:,:,0]>a[:,:,1]+50)&(a[:,:,0]>a[:,:,2]+50)
ys,xs=np.where(red)
if len(xs): print(" RED pixels bbox: y",ys.min(),"-",ys.max()," x",xs.min(),"-",xs.max()," n=",len(xs))

print("\n===== CHANNELS header/search/cards =====")
a,(w,h)=load("channels-tab.jpg"); a=a[:,:360]
print(" header avatar @(38,36):",avg(a,30,28,50,46))
print(" header title text @(90,36):",avg(a,80,28,160,46))
run=colrun(a,180,40,140,is_graycap); print(" search capsule run @x=180:",run)
if run:
    yc=(run[0]+run[1])//2; rr=rowrun(a,yc,20,340,is_graycap); print("  capsule h/bbox:",run[1]-run[0],rr)
# recommended cards gradient + 关注 button: scan for blue on right side y144-240
blue=(a[:,:,2]>120)&(a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>=a[:,:,1]-15)
print(" 关注 blue btn at y200 right @(320,200):",avg(a,300,190,340,212))
# group list follow buttons blue at y384-456
print(" group follow btn @(320,420):",avg(a,300,408,345,432))

print("\n===== CONTACTS header/search/badge/green/index =====")
a,(w,h)=load("contacts-tab.jpg"); a=a[:,:360]
print(" header avatar @(38,36):",avg(a,30,28,50,46))
red=(a[:,:,0]>165)&(a[:,:,1]<115)&(a[:,:,2]<115)&(a[:,:,0]>a[:,:,1]+50)&(a[:,:,2]>a[:,:,0]-200)
ys,xs=np.where(red)
if len(xs): print(" RED badge bbox: y",ys.min(),"-",ys.max()," x",xs.min(),"-",xs.max()," n=",len(xs), " sample@(min):",avg(a,max(0,xs.min()-4),max(0,ys.min()-4),xs.min()+6,ys.min()+6))
green=(a[:,:,1]>130)&(a[:,:,1]>a[:,:,0]+25)&(a[:,:,1]>a[:,:,2]+15)
ys,xs=np.where(green)
if len(xs): print(" GREEN online dot bbox: y",ys.min(),"-",ys.max()," x",xs.min(),"-",xs.max()," n=",len(xs))
# A-Z index: right column x=350 dark/gray text vertical
idxcol=a[40:680,348:358]
print(" A-Z index col x=348..358 non-white px:",int(((idxcol.mean(2)<240).sum())))

print("\n===== DYNAMICS header/camera/9grid/actions =====")
a,(w,h)=load("dynamics-tab.jpg"); a=a[:,:360]
print(" header avatar @(38,36):",avg(a,30,28,50,46))
print(" camera btn @(330,36):",avg(a,318,28,342,50))
# 9-grid: locate photo region. sample 3x3 over y216-528 x20-340
gy0,gy1,gx0,gx1=216,528,20,340
print(" 9-grid cell-center colors:")
for ry in range(3):
    rowc=[]
    for rx in range(3):
        cy=gy0+(ry+0.5)*(gy1-gy0)/3; cx=gx0+(rx+0.5)*(gx1-gx0)/3
        cy,cx=int(cy),int(cx)
        rowc.append(avg(a,cx-18,cy-18,cx+18,cy+18))
    print("  ",rowc)
# like/comment/share action row: below grid y~540
print(" actions @(60,540):",avg(a,30,532,120,556)," @(180,540):",avg(a,150,532,250,556))

print("\n===== GROUPCHAT top/name/bubbles/read =====")
a,(w,h)=load("group-chat.jpg")
print(" top bar @(0,20,390,48) avg:",avg(a,0,8,390,48))
print(" title name externalized @(170,22):",avg(a,120,14,260,34))
# no mask: center screen should be light
print(" center @(195,420):",avg(a,170,400,220,440))
# blue bubbles region
blue=(a[:,:,2]>120)&(a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>=a[:,:,1]-15)
ys,xs=np.where(blue)
if len(xs): print(" BLUE (bubbles) bbox: y",ys.min(),"-",ys.max()," x",xs.min(),"-",xs.max())
# read receipts small blue near y380-420 right
print(" read receipt area @(300,400):",avg(a,270,388,360,412))
