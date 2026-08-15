#!/usr/bin/env python3
import _analyze_round12 as A

def vprofile(name, x, y0, y1, step=4):
    out = []
    for y in range(y0, y1, step):
        p = A.pixel(name, x, y)
        out.append((y, A.brightness(p), p))
    return out

def bright_band(name, y0, y1, x_center=None, step=4, thresh=120):
    """Find y-range where average brightness of full row is below thresh (mask-darkened)."""
    w, h = A.dims(name)
    xs = x_center if x_center else w // 2
    res = []
    for y in range(y0, y1, step):
        b, n = A.avg_brightness_line(name, y)
        if b is not None:
            res.append((y, b))
    return res

if __name__ == "__main__":
    name = "emoji-panel.jpg"
    print("=== emoji-panel.jpg vertical brightness at x=195 (center) ===")
    for y, b, p in vprofile(name, 195, 350, 844, 6):
        mark = "  <-- dark" if b < 120 else ""
        print(f"y={y:3d}  bright={b:6.1f}  {p}{mark}")
