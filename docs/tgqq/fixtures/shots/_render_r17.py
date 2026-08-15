from PIL import Image

def classify(p, dark):
    r,g,b=p
    if dark:
        if b>g+25 and b>115 and b>=r: return 'B'   # blue
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'W' # gray bubble
        if r<40 and g<40 and b<40: return '.'     # bg
        return '#'  # text/other
    else:
        if b>r+20 and b>150: return 'B'
        if r>=248 and g>=248 and b>=248: return 'W'
        if r<225 and g<228 and b<232: return '.'  # bg ~ (240,243,248)
        return '#'

def render(name, step=10, maxw=None):
    im=Image.open(f"{name}.jpg").convert("RGB")
    W,H=im.size
    dark=im.getpixel((5,200))[0]<60
    print(f"\n=== {name} (dark={dark})  each char={step}px ===")
    y=0
    while y<H:
        line=""
        x=0
        while x<W:
            c=classify(im.getpixel((x,y)),dark)
            line+=c
            x+=step
        print(line)
        y+=step

for n in ["mobile-chat","mobile-chat-dark","group-chat"]:
    render(n, step=11)
