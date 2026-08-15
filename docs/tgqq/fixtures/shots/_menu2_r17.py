from PIL import Image
im=Image.open("message-menu.jpg").convert("RGB")
W,H=im.size
def nonwhite(y):
    c=0
    for x in range(0,W,2):
        r,g,b=im.getpixel((x,y))
        if not (r>240 and g>240 and b>240): c+=1
    return c
print("non-white px/row  y500-735:")
profile=[]
for y in range(500,736):
    c=nonwhite(y)
    profile.append((y,c))
    if c>0:
        print(f"  y{y:3d} nw={c}")
# bands
bands=[];cur=None
for y,c in profile:
    if c>5:
        if cur is None: cur=[y,y]
        else: cur[1]=y
    else:
        if cur: bands.append(tuple(cur)); cur=None
if cur: bands.append(tuple(cur))
print("\ncontent bands (merged if gap<=8):")
items=[];cb=None
for b in bands:
    if cb is None: cb=[b[0],b[1]]
    elif b[0]-cb[1]<=8: cb[1]=b[1]
    else: items.append(tuple(cb)); cb=[b[0],b[1]]
if cb: items.append(tuple(cb))
for i,it in enumerate(items):
    print(f"  item{i}: y{it[0]}-{it[1]} h={it[1]-it[0]+1}")
print("panel region non-white spans y", profile[0][0], "to", profile[-1][0])
# what color is the menu text? sample a content row
if items:
    yy=(items[0][0]+items[0][1])//2
    # find a non-white x
    for x in range(0,W,3):
        r,g,b=im.getpixel((x,yy))
        if not(r>240 and g>240 and b>240):
            print(f"  sample text color @({x},{yy}) = ({r},{g},{b})"); break
