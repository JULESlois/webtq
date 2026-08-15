import subprocess, sys, collections, json

def get_wh(path):
    w,h=subprocess.check_output(["magick","identify","-format","%w %h",path]).decode().split()
    return int(w),int(h)

def px(path,x,y):
    out=subprocess.check_output(["magick",path,"-crop","1x1+%d+%d"%(x,y),"txt:-"]).decode()
    line=[l for l in out.splitlines() if ": (" in l][0]
    p=line.split(": (")[1].split(")")[0]
    return tuple(int(v) for v in p.split(",")[:3])

def sample_row(path,y,w=None,h=None):
    if w is None: w=get_wh(path)[0]
    out=subprocess.check_output(["magick",path,"-crop","%dx1+0+%d"%(w,y),"txt:-"]).decode().splitlines()
    res=[]
    for line in out:
        if ": (" in line:
            p=line.split(": (")[1].split(")")[0]
            res.append(tuple(int(v) for v in p.split(",")[:3]))
    return res

def sample_col(path,x,w=None,h=None):
    if h is None: h=get_wh(path)[1]
    out=subprocess.check_output(["magick",path,"-crop","1x%d+%d+0"%(h,x),"txt:-"]).decode().splitlines()
    res=[]
    for line in out:
        if ": (" in line:
            p=line.split(": (")[1].split(")")[0]
            res.append(tuple(int(v) for v in p.split(",")[:3]))
    return res

def color_cluster(row):
    runs=[]; prev=None; start=0
    for i,c in enumerate(row):
        if c!=prev:
            if prev is not None: runs.append((start,i-1,prev))
            prev=c; start=i
    runs.append((start,len(row)-1,prev))
    return runs

def is_green(c):
    r,g,b=c
    return g>120 and r<g-40 and b<g-30 and g>r+30 and g>b+20
def is_blue(c):
    r,g,b=c
    return b>120 and b>r+40 and g<b and g>r
def is_lightblue(c):
    r,g,b=c
    # #A6E3FF ~ (166,227,255): high b, high g, mid r
    return b>210 and g>180 and r>120 and b>=g>=r
def is_white(c):
    r,g,b=c
    return r>235 and g>235 and b>235

def count_colors(path):
    """Count green/blue/lightblue/white-ish pixels over whole image (sampled)."""
    w,h=get_wh(path)
    # sample grid every 2px using -resize downscale for speed
    small="%dx%d"%(w//4 or 1, h//4 or 1)
    out=subprocess.check_output(["magick",path,"-resize",small,"-depth","8","txt:-"]).decode().splitlines()
    cnt=collections.Counter()
    n=0
    for line in out:
        if ": (" in line:
            p=line.split(": (")[1].split(")")[0]
            c=tuple(int(v) for v in p.split(",")[:3])
            n+=1
            if is_green(c): cnt['green']+=1
            if is_blue(c): cnt['blue']+=1
            if is_lightblue(c): cnt['lightblue']+=1
            if is_white(c): cnt['white']+=1
    tot=n or 1
    return {k:round(v/tot*100,2) for k,v in cnt.items()}

def blank_regions(path, x0,x1,y0,y1, step=4):
    """Detect uniform-color rectangles (possible blank/empty areas) in a region."""
    w,h=get_wh(path)
    x0=max(0,x0); y0=max(0,y0); x1=min(w,x1); y1=min(h,y1)
    # sample region to a small grid and look for large single-color blocks
    sw=max(1,(x1-x0)//40); sh=max(1,(y1-y0)//40)
    out=subprocess.check_output(["magick",path,"-crop","%dx%d+%d+%d"%(x1-x0,y1-y0,x0,y0),"-resize","%dx%d"%(40,40),"txt:-"]).decode().splitlines()
    cells={}
    for line in out:
        if ": (" in line:
            head=line.split(":")[0]
            a,b=head.split(",")
            p=line.split(": (")[1].split(")")[0]
            c=tuple(int(v) for v in p.split(",")[:3])
            cells[(int(a),int(b))]=c
    return cells

def main():
    files=sys.argv[1:]
    for path in files:
        w,h=get_wh(path)
        print("="*60)
        print("FILE",path,"SIZE",w,h)
        # divider detection: scan middle row runs
        for frac in (0.12,0.5,0.88):
            y=int(h*frac)
            row=sample_row(path,y,w)
            runs=color_cluster(row)
            # collapse near-identical colors
            print("  Y%d runs(n=%d):"%(y,len(runs)), [(s,e) for s,e,c in runs])
        # color stats
        stats=count_colors(path)
        print("  COLOR%%:",stats)
        # left third / middle / right third average bg
        for label,(xa,xb) in [("LEFT",(0,w//3)),("MID",(w//3,2*w//3)),("RIGHT",(2*w//3,w))]:
            col=sample_col(path,(xa+xb)//2,w,h)
            # average
            ar=sum(c[0] for c in col)//len(col); ag=sum(c[1] for c in col)//len(col); ab=sum(c[2] for c in col)//len(col)
            print("  %s col avg (%d,%d,%d)"%(label,ar,ag,ab))

if __name__=="__main__":
    main()
