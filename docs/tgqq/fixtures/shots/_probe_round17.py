from PIL import Image

def px(im,x,y):
    return im.getpixel((x,y))

for name in ["mobile-chat","mobile-chat-dark","group-chat","voice-recording","composer-reply","message-menu"]:
    im = Image.open(f"{name}.jpg").convert("RGB")
    W,H = im.size
    print(f"\n===== {name} {W}x{H} =====")
    # sample a column in bubble area far from bubbles (left margin x=8) to get bg
    bg = px(im, 5, 200)
    bg2 = px(im, 5, 400)
    print(f"  left-margin bg @(5,200)={bg} @(5,400)={bg2}")
    # top bar
    print(f"  top @(5,10)={px(im,5,10)} @(200,10)={px(im,200,10)}")
    # bottom composer region
    print(f"  bottom @(5,{H-10})={px(im,5,H-10)} @(200,{H-10})={px(im,200,H-10)}")
    print(f"  bottom @(5,{H-60})={px(im,5,H-60)} @(200,{H-60})={px(im,200,H-60)}")
    # is dark mode?
    r,g,b = bg
    dark = (r<60)
    print(f"  DARK_MODE={dark}")
