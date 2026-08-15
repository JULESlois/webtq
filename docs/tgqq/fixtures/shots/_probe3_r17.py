from PIL import Image

# ---- group-chat: per-row runs y55..230 ----
im=Image.open("group-chat.jpg").convert("RGB")
def is_fill(p,dark):
    r,g,b=p
    if b>r+20 and b>150: return 'B'
    if r>=248 and g>=248 and b>=248: return 'W'
    return None
def runs(y):
    res=[];x=8
    while x<383:
        t=is_fill(im.getpixel((x,y)),False)
        if t:
            sx=x
            while x<383 and is_fill(im.getpixel((x,y)),False): x+=1
            res.append((sx,x-1,x-sx,t))
        else: x+=1
    return res
print("=== group-chat per-row runs y55-230 ===")
for y in range(55,231):
    rs=runs(y)
    if rs:
        s=",".join(f"{a}-{b}({w}{c})" for a,b,w,c in rs)
        print(f"y{y:3d} {s}")
