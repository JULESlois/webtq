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

im=Image.open("mobile-chat.jpg").convert("RGB")
dark=False
# dump per-row for y in 190..380 (covers B1,B2)
for y in range(190,375):
    minx=999;maxx=-1;cnt=0;types=[]
    for x in range(8,383):
        t=is_fill(im.getpixel((x,y)),dark)
        if t:
            cnt+=1; types.append(t)
            minx=min(minx,x);maxx=max(maxx,x)
    if cnt>0:
        blue=types.count('B');white=types.count('W')
        print(f"y{y:3d} minx={minx:3d} maxx={maxx:3d} w={maxx-minx+1:3d} n={cnt:3d} B={blue} W={white}")
