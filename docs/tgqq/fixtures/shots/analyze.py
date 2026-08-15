import subprocess, sys

def sample_col(path, x, h=None):
    """Return list of (r,g,b) for vertical column x over full height."""
    if h is None:
        h = int(subprocess.check_output(["magick","identify","-format","%h",path]).decode().strip())
    out = subprocess.check_output(["magick",path,"-crop","1x%d+%d+0"%(h,x),"txt:-"]).decode().splitlines()
    res=[]
    for line in out:
        # format: 0,0: (r,g,b)  #HEX  name
        if ": (" in line:
            p=line.split(": (")[1].split(")")[0]
            parts=[int(v) for v in p.split(",")[:3]]
            res.append(tuple(parts))
    return res

def sample_row(path, y, w=None):
    if w is None:
        w=int(subprocess.check_output(["magick","identify","-format","%w",path]).decode().strip())
    out=subprocess.check_output(["magick",path,"-crop","%dx1+0+%d"%(w,y),"txt:-"]).decode().splitlines()
    res=[]
    for line in out:
        if ": (" in line:
            p=line.split(": (")[1].split(")")[0]
            parts=[int(v) for v in p.split(",")[:3]]
            res.append(tuple(parts))
    return res

def get_wh(path):
    w,h=subprocess.check_output(["magick","identify","-format","%w %h",path]).decode().split()
    return int(w),int(h)

def px(path,x,y):
    out=subprocess.check_output(["magick",path,"-crop","1x1+%d+%d"%(x,y),"txt:-"]).decode()
    line=[l for l in out.splitlines() if ": (" in l][0]
    p=line.split(": (")[1].split(")")[0]
    return tuple(int(v) for v in p.split(",")[:3])

if __name__=="__main__":
    path=sys.argv[1]
    w,h=get_wh(path)
    print("SIZE",w,h)
    # detect column split by scanning rows at several y and counting distinct runs
    # find divider: scan middle row
    ymid=h//2
    row=sample_row(path,ymid,w)
    # group into runs
    runs=[]
    prev=None;start=0
    for i,c in enumerate(row):
        if c!=prev:
            if prev is not None:
                runs.append((start,i-1,prev))
            prev=c;start=i
    runs.append((start,len(row)-1,prev))
    print("RUNS_Y%d"%ymid, runs)
