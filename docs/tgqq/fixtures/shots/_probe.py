import numpy as np
from PIL import Image

files = {
  "mobile": "mobile.jpg",
  "channels": "channels-tab.jpg",
  "contacts": "contacts-tab.jpg",
  "dynamics": "dynamics-tab.jpg",
  "groupchat": "group-chat.jpg",
}

def stats(a):
    return f"mean={a.reshape(-1,3).mean(0).round(1)} std={a.reshape(-1,3).std(0).round(1)}"

for name, f in files.items():
    im = Image.open(f).convert("RGB")
    a = np.array(im)
    h, w = a.shape[:2]
    print(f"\n===== {name} ({w}x{h}) =====")
    print("global", stats(a))
    # Is it a 404 blank? check fraction near-white and black-text block upper-left
    white = (a.mean(2) > 250).mean()
    print(f"white fraction={white:.3f}")
    # coarse grid 16x12 color blocks (average)
    gx, gy = 36, 24
    blockw = w // gx; blockh = h // gy
    print("COARSE GRID (R,G,B) sample every other block (left->right, top->bottom):")
    for by in range(0, gy, 2):
        row = []
        for bx in range(0, gx, 2):
            sub = a[by*blockh:(by+1)*blockh, bx*blockw:(bx+1)*blockw].reshape(-1,3)
            r,g,b = sub.mean(0).round(0).astype(int)
            row.append(f"{r:3d},{g:3d},{b:3d}")
        print("  " + " | ".join(row))
