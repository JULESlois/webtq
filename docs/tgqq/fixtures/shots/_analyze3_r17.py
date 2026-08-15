from PIL import Image
def is_fill(p,dark):
    r,g,b=p
    if dark:
        if b>g+25 and b>115 and b>=r: return 'B'
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'W'
        return None
    else:
        if b>r+20 and b>150: return 'B'
        if r>=248 and g>=248 and b>=248: return 'W'
        return None

def analyze(name,y0=55,y1=730,minxclip=45,maxxclip=378):
    im=Image.open(f"{name}.jpg").convert("RGB")
    dark=im.getpixel((5,200))[0]<60
    rows={}
    for y in range(y0,y1):
        st=0; cntB=0;cntW=0; lx=999;rx=-1
        for x in range(8,383):
            t=is_fill(im.getpixel((x,y)),dark)
            if t:
                st+=1
                if t=='B':cntB+=1
                else:cntW+=1
                if x>=minxclip and x<=maxxclip:
                    lx=min(lx,x); rx=max(rx,x)
        if st>=25 and rx>=0:   # substantial fill = real bubble row
            rows[y]=(lx,rx,cntB,cntW,st)
    bands=[];cur=None
    for y in range(y0,y1):
        if y in rows:
            lx,rx,b,w,s=rows[y]
            if cur is None:
                cur={'y0':y,'y1':y,'L':lx,'R':rx,'B':0,'W':0}
            cur['y1']=y
            cur['L']=min(cur['L'],lx); cur['R']=max(cur['R'],rx)
            cur['B']+=b; cur['W']+=w
        else:
            if cur: bands.append(cur); cur=None
    if cur: bands.append(cur)
    print(f"\n===== {name} dark={dark} bubbles={len(bands)} =====")
    for i,b in enumerate(bands):
        color='BLUE(out)' if b['B']>=b['W'] else 'WHITE(in)'
        side='R' if b['R']>=360 else ('L' if b['L']<=50 else '?')
        w=b['R']-b['L']+1
        print(f"  B{i:2d} y[{b['y0']:3d}-{b['y1']:3d}] h={b['y1']-b['y0']+1:3d} x[{b['L']:3d}-{b['R']:3d}] w={w:3d} side={side} {color}")
    print("  gaps:")
    for i in range(1,len(bands)):
        print(f"    B{i-1}->{i}: {bands[i]['y0']-bands[i-1]['y1']}px")
    return bands

for n in ["mobile-chat","mobile-chat-dark","group-chat","voice-recording","composer-reply"]:
    analyze(n)
