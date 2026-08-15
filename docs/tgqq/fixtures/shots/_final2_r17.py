from PIL import Image
from collections import Counter
def band_color(name,y0,y1):
    c=Counter()
    im=Image.open(f"{name}.jpg").convert("RGB")
    for y in range(y0,y1,3):
        for x in range(0,390,3):
            c[im.getpixel((x,y))]+=1
    return c.most_common(2)
print("normal composer y735-844 dominant:",band_color("mobile-chat",735,844))
print("voice  composer y735-844 dominant:",band_color("voice-recording",735,844))
print("reply  composer y735-844 dominant:",band_color("composer-reply",735,844))

im3=Image.open("mobile-chat.jpg").convert("RGB")
print("\nlong-msg blue @(250,540):",im3.getpixel((250,540))," @(300,500):",im3.getpixel((300,500)))
im4=Image.open("mobile-chat-dark.jpg").convert("RGB")
print("dark long-msg blue @(250,540):",im4.getpixel((250,540)))
# avatar check group: sample x16-52 across B7 white bubble (y460-569) and above
im5=Image.open("group-chat.jpg").convert("RGB")
print("\ngroup B7 white bubble left col avatar (x16-52 step4) at several y:")
for y in [455,470,500,540,565,569]:
    print(f"  y{y}:",[im5.getpixel((x,y)) for x in range(16,53,4)])
