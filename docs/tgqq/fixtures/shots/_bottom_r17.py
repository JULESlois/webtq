from PIL import Image
def classify(p,dark):
    r,g,b=p
    if dark:
        if b>g+25 and b>115 and b>=r: return 'B'
        if 45<=r<=85 and abs(r-g)<12 and abs(r-b)<12: return 'W'
        if r<40 and g<40 and b<40: return '.'
        return '#'
    else:
        if b>r+20 and b>150: return 'B'
        if r>=248 and g>=248 and b>=248: return 'W'
        if r<225 and g<228 and b<232: return '.'  # bg
        return '#'
def render(name,y0,y1,step=9):
    im=Image.open(f"{name}.jpg").convert("RGB")
    dark=im.getpixel((5,200))[0]<60
    print(f"\n=== {name} y[{y0}-{y1}] (dark={dark}) ===")
    y=y0
    while y<y1:
        line=""
        x=0
        while x<390:
            line+=classify(im.getpixel((x,y)),dark)
            x+=step
        print(f"y{y:3d}|{line}")
        y+=step

render("voice-recording",690,844)
render("composer-reply",690,844)
render("message-menu",690,844)
