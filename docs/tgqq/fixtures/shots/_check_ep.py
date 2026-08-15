#!/usr/bin/env python3
import _analyze_round12 as A

def is_blue(p, tol=60):
    r, g, b = p
    return b > 120 and b - r > 60 and b - g > 30

def blue_hits(row):
    return [(i, p) for i, p in enumerate(row) if is_blue(p)]

print("===== EMOJI PANEL MOBILE (emoji-panel.jpg, 390x844) =====")
# 1) full-width white at mid panel
y = 500
row = A.scanline("emoji-panel.jpg", y)
nonwhite = [(i, p) for i, p in enumerate(row) if A.brightness(p) < 240]
print(f"[Full-width white @ y={y}] non-white px={len(nonwhite)} -> "
      f"{'PASS' if len(nonwhite)==0 else 'FAIL ('+str(nonwhite[:5])+')'}")

# 2) Tab bar blue highlight: scan rows with scanline
print("\n[Tab-bar blue highlight y=720..775]")
for y in range(720, 776, 2):
    row = A.scanline("emoji-panel.jpg", y)
    hits = blue_hits(row)
    if hits:
        xs = [h[0] for h in hits]
        print(f"  y={y}: n={len(xs)} x={xs}")

# 3) Tab/input boundary
print("\n[Tab bar / input bar boundary y=700..845]")
for y in range(700, 846, 2):
    b, n = A.avg_brightness_line("emoji-panel.jpg", y)
    if b is None: continue
    tag = " (white panel)" if b > 250 else (" (gray/input)" if b < 200 else "")
    print(f"  y={y:3d} avgBright={b:6.1f}{tag}")
