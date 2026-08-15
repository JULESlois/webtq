from PIL import Image

def is_fill(p, dark):
    r,g,b = p
    if dark:
        # blue bubble #3e6fa3-ish : b>g and b>120 and b-g>25
        if b > g+25 and b > 115 and b>=r: return 'blue'
        # gray/white bubble #373737-ish : 45<=val<=85 and balanced
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'white'
        return None
    else:
        if b > r+20 and b > 150: return 'blue'   # light blue outgoing
        if r>=248 and g>=248 and b>=248: return 'white'  # white incoming
        return None

def analyze(name):
    im = Image.open(f"{name}.jpg").convert("RGB")
    W,H = im.size
    dark = im.getpixel((5,200))[0] < 60
    y0,y1 = 55, 730   # bubble area, above composer
    bubbles = []  # each: dict
    rows = []
    for y in range(y0,y1):
        minx=999; maxx=-1; cols=[]
        for x in range(8,383):
            t = is_fill(im.getpixel((x,y)), dark)
            if t:
                if x<minx: minx=x
                if x>maxx: maxx=x
                cols.append(t)
        rows.append((minx,maxx,cols))
    # group into bands: a band is consecutive rows with minx<999
    bands=[]
    cur=None
    for y in range(y0,y1):
        minx,maxx,cols = rows[y-y0]
        if minx<999:
            if cur is None:
                cur={'y0':y,'y1':y,'minx':minx,'maxx':maxx,'blue':0,'white':0}
            cur['y1']=y
            cur['minx']=min(cur['minx'],minx); cur['maxx']=max(cur['maxx'],maxx)
            cur['blue']+=cols.count('blue'); cur['white']+=cols.count('white')
        else:
            if cur is not None:
                bands.append(cur); cur=None
    if cur: bands.append(cur)
    # filter noise
    bubbles=[b for b in bands if (b['maxx']-b['minx'])>18 and (b['y1']-b['y0'])>5]
    print(f"\n===== {name}  dark={dark}  bands_total={len(bands)} bubbles={len(bubbles)} =====")
    for i,b in enumerate(bubbles):
        color = 'BLUE(out)' if b['blue']>=b['white'] else 'WHITE(in)'
        side = 'R' if b['maxx']>195 else 'L'
        w = b['maxx']-b['minx']+1
        print(f"  B{i:2d} y[{b['y0']:3d}-{b['y1']:3d}] h={b['y1']-b['y0']+1:3d} x[{b['minx']:3d}-{b['maxx']:3d}] w={w:3d} side={side} {color}")
    # gaps
    print("  -- vertical gaps (next.top - prev.bottom) --")
    for i in range(1,len(bubbles)):
        gap = bubbles[i]['y0'] - bubbles[i-1]['y1']
        print(f"    gap B{i-1}->B{i} = {gap}px")
    return bubbles

for n in ["mobile-chat","mobile-chat-dark","group-chat","voice-recording","composer-reply","message-menu"]:
    analyze(n)
