from PIL import Image
im=Image.open("message-menu.jpg").convert("RGB")
W,H=im.size
# content = not white(>245) and not the gray scrim; i.e., dark text/icon pixels
def content(y):
    c=0
    for x in range(0,W,2):
        r,g,b=im.getpixel((x,y))
        if not (r>243 and g>243 and b>243): c+=1
    return c
print("=== message-menu vertical content profile y[635-844] (content px count) ===")
bands=[];cur=None
for y in range(635,844):
    c=content(y)
    has = c>30   # row has visible text/icon
    if has:
        if cur is None: cur=[y,y]
        else: cur[1]=y
    else:
        if cur: bands.append(tuple(cur)); cur=None
if cur: bands.append(tuple(cur))
print("content bands (text/icon rows):")
for b in bands:
    print(f"  y{b[0]}-{b[1]}  h={b[1]-b[0]+1}")
# derive item blocks: gaps between bands > some threshold separate items
print("\nItems (merge bands separated by <6px gap):")
items=[];cb=None
for b in bands:
    if cb is None: cb=[b[0],b[1]]
    elif b[0]-cb[1]<=6: cb[1]=b[1]
    else: items.append(tuple(cb)); cb=[b[0],b[1]]
if cb: items.append(tuple(cb))
for i,it in enumerate(items):
    print(f"  item{i}: y{it[0]}-{it[1]} h={it[1]-it[0]+1}")
print(f"\npanel bottom = 844; last item bottom={items[-1][1] if items else 'NA'} (should be ~844 for bottom-aligned)")
# sample colors of one item text to confirm it's dark text on white
print("sample item0 center pixel @(200,",(items[0][0]+items[0][1])//2,"):",im.getpixel((200,(items[0][0]+items[0][1])//2)))
