#!/usr/bin/env python3
"""Pixel/scanline analyzer for TGQQ Round-12 screenshots (ImageMagick backend)."""
import subprocess, sys, os

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"

def img(name):
    return os.path.join(SOTS if False else SHOTS, name)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout

def dims(name):
    out = run(["convert", img(name), "-format", "%w %h", "info:"])
    w, h = out.split()
    return int(w), int(h)

def pixel(name, x, y):
    """Return (r,g,b) at x,y."""
    out = run(["convert", img(name), "-crop", "1x1+%d+%d" % (x, y),
               "+repage", "-format", "%[pixel:p{0,0}]", "info:"])
    s = out.strip()
    # format like "srgb(18,150,219)" or "gray(..)"
    s = s.replace("srgb(", "").replace("rgb(", "").replace(")", "")
    parts = s.split(",")
    if len(parts) == 1:
        v = int(parts[0])
        return (v, v, v)
    return tuple(int(p.strip()) for p in parts[:3])

def scanline(name, y):
    """Return list of (r,g,b) across full width at row y."""
    w, h = dims(name)
    out = run(["convert", img(name), "-crop", "%dx1+0+%d" % (w, y),
               "+repage", "txt:-"])
    res = []
    for line in out.splitlines():
        if line.startswith("#"):
            continue
        # format: x,y: (r,g,b)  #HEX  srgb(r,g,b)
        try:
            after = line.split(":", 1)[1]
            # grab the parenthesized tuple
            tup = after[after.index("("):after.index(")")+1]
            tup = tup.strip("()")
            parts = tup.split(",")
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            res.append((r, g, b))
        except Exception:
            pass
    return res

def colscan(name, x, ys):
    return [pixel(name, x, y) for y in ys]

def brightness(p):
    r, g, b = p
    return (r * 299 + g * 587 + b * 114) / 1000

def avg_brightness_line(name, y):
    row = scanline(name, y)
    if not row:
        return None, 0
    return sum(brightness(p) for p in row) / len(row), len(row)

if __name__ == "__main__":
    names = ["emoji-panel.jpg", "emoji-panel-tablet.jpg",
             "message-menu.jpg", "message-menu-tablet.jpg", "group-chat.jpg"]
    for n in names:
        w, h = dims(n)
        print(f"{n}: {w}x{h}")
