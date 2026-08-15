from PIL import Image
def classify(p,dark):
    r,g,b=p
    if dark:
        if b>g+25 and b>115 and b>=r: return 'B'
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'W'
        if r<40 and g<40 and b<40: return '.'
        return '#'
    else:
        if r>248 and g>248 and b>248: return 'W'
        if b>r+20 and b>150: return 'B'
        if r>230 and g>233 and b>236 and (b-r)<16: return '.'   # bg
        return '#'
def render(name,y0,y1,step=8):
    im=Image.open(f"{name}.jpg").convert("RGB")
    dark=im.getpixel((5,200))[0]<60
    print(f"\n=== {name} y[{y0}-{y1}] ===")
    y=y0
    while y<y1:
        line="".join(classify(im.getpixel((x,y)),dark) for x in range(0,390,step))
        print(f"y{y:3d}|{line}")
        y+=step

render("voice-recording",700,844,8)
render("composer-reply",700,844,8)

# ---- message-menu: find panel top + item divider lines ----
print("\n=== message-menu item analysis ===")
im=Image.open("message-menu.jpg").convert("RGB")
W,H=im.size
# panel = white majority rows
def whitefrac(y):
    c=0
    for x in range(0,W,2):
        r,g,b=im.getpixel((x,y))
        if r>245 and g>245 and b>245: c+=1
    return c/(W//2)
# find panel top
top=None
for y in range(640,844):
    if whitefrac(y)>0.85:
        top=y; break
print(f"menu panel top y={top}  (white fraction there={whitefrac(top):.2f})")
# find horizontal divider lines (gray ~ (210,210,210) and not white, spanning width)
def grayfrac(y):
    c=0
    for x in range(0,W,2):
        r,g,b=im.getpixel((x,y))
        if 150<r<245 and abs(r-g)<12 and abs(r-b)<12: c+=1
    return c/(W//2)
print("gray divider rows (grayfrac>0.5):")
divs=[]
for y in range(top,844):
    gf=grayfrac(y)
    if gf>0.5:
        divs.append(y)
print("  dividers:",divs)
# compute item heights between dividers (and panel top/bottom)
bounds=[top-1]+divs+[844]
print("panel total height:",844-top)
print("item bands (height):")
for i in range(1,len(bounds)):
    print(f"  item{y if False else bounds[i-1]+1}-{bounds[i]}: h={bounds[i]-bounds[i-1]}px")
