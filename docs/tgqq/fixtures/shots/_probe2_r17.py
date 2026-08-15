from PIL import Image
from collections import Counter

def dominant(im, x0,x1,y0,y1, exclude=None):
    c=Counter()
    for y in range(y0,y1,2):
        for x in range(x0,x1,2):
            p=im.getpixel((x,y))
            if exclude and all(abs(p[i]-exclude[i])<10 for i in range(3)):
                continue
            c[p]+=1
    return c.most_common(8)

# dark mode: find bubble fills
im=Image.open("mobile-chat-dark.jpg").convert("RGB")
print("DARK bubble-area sample (x 40-360, y 120-600), excluding bg(25,25,25):")
for col,cnt in dominant(im,40,360,120,600,exclude=(25,25,25))[:8]:
    print("  ",col,cnt)

# light: find white & blue bubbles in a strip
im=Image.open("mobile-chat.jpg").convert("RGB")
print("LIGHT bubble-area sample (x 40-360, y 120-600), excluding bg(240,243,248):")
for col,cnt in dominant(im,40,360,120,600,exclude=(240,243,248))[:8]:
    print("  ",col,cnt)
