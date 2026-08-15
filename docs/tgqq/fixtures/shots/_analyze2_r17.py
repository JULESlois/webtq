from PIL import Image

def is_fill(p, dark):
    r,g,b=p
    if dark:
        if b>g+25 and b>115 and b>=r: return 'B'
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'W'
        return None
    else:
        if b>r+20 and b>150: return 'B'
        if r>=248 and g>=248 and b>=248: return 'W'
        return None

def row_main_run(im,y,dark):
    # find contiguous runs of fill; return (minx,maxx,colorcount) of the largest run
    best=None
    x=8; W=383
    while x<W:
        t=is_fill(im.getpixel((x,y)),dark)
        if t:
            sx=x
            cnt={'B':0,'W':0}
            while x<W and is_fill(im.getpixel((x,y)),dark):
                tt=is_fill(im.getpixel((x,y)),dark)
                cnt[tt]+=1
                x+=1
            run_w=x-sx
            if run_w>=18:  # ignore noise
                if best is None or run_w>best[2]:
                    best=(sx,x-1,run_w,cnt)
        else:
            x+=1
    return best  # (minx,maxx,width,cnt) or None

def analyze(name, y0=55, y1=730):
    im=Image.open(f"{name}.jpg").convert("RGB")
    W,H=im.size
    dark=im.getpixel((5,200))[0]<60
    rows={}
    for y in range(y0,y1):
        r=row_main_run(im,y,dark)
        if r: rows[y]=r
    # bands
    bands=[]; cur=None
    for y in range(y0,y1):
        if y in rows:
            r=rows[y]
            if cur is None:
                cur={'y0':y,'y1':y,'minx':r[0],'maxx':r[1],'B':0,'W':0}
            cur['y1']=y
            cur['minx']=min(cur['minx'],r[0]); cur['maxx']=max(cur['maxx'],r[1])
            cur['B']+=r[3]['B']; cur['W']+=r[3]['W']
        else:
            if cur: bands.append(cur); cur=None
    if cur: bands.append(cur)
    print(f"\n===== {name} dark={dark} bubbles={len(bands)} =====")
    out=[]
    for i,b in enumerate(bands):
        color='BLUE(out)' if b['B']>=b['W'] else 'WHITE(in)'
        side='R' if b['maxx']>360 else ('L' if b['minx']<40 else '?')
        w=b['maxx']-b['minx']+1
        print(f"  B{i:2d} y[{b['y0']:3d}-{b['y1']:3d}] h={b['y1']-b['y0']+1:3d} x[{b['minx']:3d}-{b['maxx']:3d}] w={w:3d} side={side} {color}")
        out.append(b)
    print("  gaps(next.top-prev.bottom):")
    for i in range(1,len(bands)):
        g=bands[i]['y0']-bands[i-1]['y1']
        print(f"    B{i-1}->{i}: {g}px")
    return out,dark

for n in ["mobile-chat","mobile-chat-dark","group-chat","voice-recording","composer-reply"]:
    analyze(n)
