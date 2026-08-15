from PIL import Image
def is_blue(p):
    r,g,b=p
    return b>r+20 and b>150

# ---- voice panel extent (blue coverage per row, y680-844) ----
im=Image.open("voice-recording.jpg").convert("RGB")
print("=== voice-recording: blue px/row y680-844 ===")
rows=[]
for y in range(680,845):
    c=sum(1 for x in range(0,390,2) if is_blue(im.getpixel((x,y))))
    rows.append((y,c))
    if c>3: print(f"  y{y:3d} blue={c}")
blue_rows=[y for y,c in rows if c>3]
if blue_rows: print(f"  voice blue region: y{blue_rows[0]}..{blue_rows[-1]} (span {blue_rows[-1]-blue_rows[0]}px)")

# ---- compare: normal composer region color (mobile-chat) vs voice ----
def band_color(name,y0,y1):
    from collections import Counter
    c=Counter()
    im2=Image.open(f"{name}.jpg").convert("RGB")
    for y in range(y0,y1,3):
        for x in range(0,390,3):
            c[im2.getpixel((x,y))]+=1
    return c.most_common(2)
print("\nnormal composer y735-844 dominant:",band_color("mobile-chat",735,844))
print("voice composer     y735-844 dominant:",band_color("voice-recording",735,844))

# ---- long message blue sample (mobile-chat B5 ~x250,y540) ----
im3=Image.open("mobile-chat.jpg").convert("RGB")
print("\nlong-msg blue sample @(250,540):",im3.getpixel((250,540)))
print("long-msg blue sample @(300,500):",im3.getpixel((300,500)))
# dark long msg
im4=Image.open("mobile-chat-dark.jpg").convert("RGB")
print("dark long-msg blue sample @(250,540):",im4.getpixel((250,540)))

# ---- group chat avatar bottom-alignment check: sample left col x16-50 at B7 (white bubble y460-569) ----
im5=Image.open("group-chat.jpg").convert("RGB")
print("\ngroup B7 white bubble y460-569, left col x[16-52] avatar check:")
for y in [460,500,540,565,569]:
    row=[im5.getpixel((x,y)) for x in range(16,53,4)]
    print(f"  y{y}: {row}")
