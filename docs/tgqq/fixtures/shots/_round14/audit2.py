#!/usr/bin/env python3
"""
Round-14 refined audit with smart feature detection.
Finds feature locations by scanning rows/regions, then samples at the right spots.
"""
from PIL import Image
import os, json, collections

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"

def load(n):
    return Image.open(os.path.join(SHOTS, n)).convert("RGB")

def px(img, x, y):
    return img.getpixel((int(x), int(y)))

def br(rgb):
    return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]

# ===== Color predicates =====
def is_qq_blue(rgb, tol=40):
    r,g,b = rgb
    return abs(r-18)<=tol and abs(g-150)<=tol and abs(b-219)<=tol

def is_blueish(rgb):
    # broader blue family
    r,g,b = rgb
    return b > 200 and b > r + 15 and b > g - 30 and r < 240

def is_green_dot(rgb):
    r,g,b = rgb
    return g >= 140 and g > r + 30 and g > b + 20 and r < 200

def is_red_badge(rgb):
    r,g,b = rgb
    return r >= 200 and g < 130 and b < 130 and r > g + 70 and r > b + 70

def is_orange_avatar(rgb):
    r,g,b = rgb
    return r >= 220 and 110 <= g <= 180 and 40 <= b <= 110 and r > g > b

def is_purple_avatar(rgb):
    r,g,b = rgb
    return 130 <= r <= 200 and 70 <= g <= 140 and 160 <= b <= 220 and b > r > g

def is_pink_avatar(rgb):
    r,g,b = rgb
    return r >= 200 and g < 130 and 100 <= b <= 180 and r > g and b > g

def is_teal_avatar(rgb):
    r,g,b = rgb
    return r < 130 and g > 150 and b > 180 and b > r

def is_gray_avatar(rgb):
    r,g,b = rgb
    return abs(r-g) < 25 and abs(g-b) < 25 and 60 <= r <= 180

def is_dark_text(rgb):
    return br(rgb) <= 110

def is_mid_gray_text(rgb):
    b = br(rgb)
    return 110 < b <= 180

def is_light_blue_selected(rgb):
    r,g,bl = rgb
    return bl > r and bl > g and 220 <= bl <= 252 and r >= 220 and g >= 230

def classify_avatar(rgb):
    """Return the name of the avatar color."""
    if is_orange_avatar(rgb): return "orange"
    if is_purple_avatar(rgb): return "purple"
    if is_pink_avatar(rgb): return "pink"
    if is_teal_avatar(rgb): return "teal"
    if is_gray_avatar(rgb): return "gray"
    if is_qq_blue(rgb, 60): return "qq_blue"
    if is_blueish(rgb): return "blueish"
    if is_green_dot(rgb): return "green"
    return None

def is_white(rgb):
    return br(rgb) >= 248

def is_light_bg(rgb):
    return br(rgb) >= 240

# ===== Scanners =====
def find_color_bbox_in(img, pred, x0, y0, x1, y1):
    pts = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px(img, x, y)):
                pts.append((x, y))
    if not pts:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return {"n": len(pts), "x0": min(xs), "y0": min(ys),
            "x1": max(xs), "y1": max(ys),
            "w": max(xs)-min(xs)+1, "h": max(ys)-min(ys)+1,
            "cx": (min(xs)+max(xs))//2, "cy": (min(ys)+max(ys))//2,
            "sample_rgb": px(img, (min(xs)+max(xs))//2, (min(ys)+max(ys))//2)}

def find_red_regions(img, x0, y0, x1, y1):
    return find_color_bbox_in(img, is_red_badge, x0, y0, x1, y1)

def find_green_dots(img, x0, y0, x1, y1):
    return find_color_bbox_in(img, is_green_dot, x0, y0, x1, y1)

def find_blue_badge(img, x0, y0, x1, y1):
    """Find small blue clusters (could be selected text / icons)."""
    return find_color_bbox_in(img, lambda c: is_qq_blue(c, 30) and br(c) < 220, x0, y0, x1, y1)

def find_avatar_in_row(img, y_center, x_search=(15, 90)):
    """Detect the avatar center color in a row by scanning x range at y_center.
    Returns (cx, cy, color_name, rgb)."""
    for x in range(x_search[0], x_search[1]):
        c = px(img, x, y_center)
        name = classify_avatar(c)
        if name:
            return (x, y_center, name, c)
    return None

def find_row_starts(img, y_start, y_end, x_col=56):
    """Find vertical bands of avatar-colored content at x_col."""
    bands = []
    in_band = False; b0 = 0
    for y in range(y_start, y_end):
        c = px(img, x_col, y)
        is_avatar = classify_avatar(c) is not None
        if is_avatar:
            if not in_band:
                b0 = y; in_band = True
            last = y
        else:
            if in_band:
                if y - last >= 1:
                    bands.append((b0, last))
                in_band = False
                last = None
    if in_band:
        bands.append((b0, last))
    # merge close
    merged = []
    for b in bands:
        if merged and b[0]-merged[-1][1] <= 3:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    return merged

# =============================================================
# 1. mobile.jpg — comprehensive scan
# =============================================================
def audit_mobile():
    img = load("mobile.jpg")
    out = {"file": "mobile.jpg", "size": img.size}

    # Page bg — sample between rows
    out["page_bg_rgb"] = px(img, 200, 800)
    # Header bg (top personal row strip)
    out["header_strip_rgb"] = px(img, 200, 28)

    # Search pill region: scan for light-blue tint
    # Find by scanning a horizontal slice at y=130
    sb = find_color_bbox_in(img, lambda c: 220<=c[2]<=255 and 230<=c[0]<=245 and 235<=c[1]<=250, 0, 105, 390, 165)
    out["search_pill_bbox"] = sb

    # Find "我" avatar (blue) at top-left
    # Scan top 90px for blue avatar
    my_a = find_color_bbox_in(img, lambda c: is_qq_blue(c, 30), 5, 5, 80, 85)
    out["my_avatar_bbox"] = my_a
    if my_a:
        # green dot would be just below the avatar
        green_below = find_color_bbox_in(img, is_green_dot,
                                          my_a["x0"], my_a["y1"],
                                          my_a["x1"]+5, my_a["y1"]+25)
        out["green_dot_bbox_below_my_avatar"] = green_below

    # Find "+" icon top right — should be a darker glyph at x ~ 355-370, y ~ 30-65
    plus_bbox = find_color_bbox_in(img, lambda c: br(c) <= 160 and not is_qq_blue(c, 60) and not is_red_badge(c) and not is_green_dot(c),
                                    340, 20, 390, 70)
    out["plus_icon_bbox"] = plus_bbox

    # Find selected row (light blue bg)
    # Selected bg would span full width of left pane minus borders
    # Scan y range 100-790 for rows where the bg is light blue
    selected_rows = []
    for y in range(180, 790):
        c = px(img, 200, y)
        if is_light_blue_selected(c):
            selected_rows.append(y)
    if selected_rows:
        # group consecutive
        bands = []
        cur = [selected_rows[0], selected_rows[0]]
        for v in selected_rows[1:]:
            if v - cur[1] <= 2:
                cur[1] = v
            else:
                bands.append(tuple(cur)); cur = [v, v]
        bands.append(tuple(cur))
        # only keep big bands
        big = [b for b in bands if b[1]-b[0] >= 30]
        out["selected_row_bands"] = big
    else:
        out["selected_row_bands"] = []

    # Find LEFT-BORDER blue strip — narrow blue vertical line on far-left edge of selected row
    left_blue_pts = []
    for y in range(180, 790):
        c = px(img, 6, y)
        if is_qq_blue(c, 50):
            left_blue_pts.append(y)
    if left_blue_pts:
        # group consecutive
        bands = []
        cur = [left_blue_pts[0]]
        for v in left_blue_pts[1:]:
            if v - cur[-1] <= 2:
                cur.append(v)
            else:
                if len(cur) >= 10:
                    bands.append((cur[0], cur[-1]))
                cur = [v]
        if len(cur) >= 10:
            bands.append((cur[0], cur[-1]))
        out["left_blue_border_bands"] = bands

    # Find all conversation rows by scanning avatar column (x=20-80) for colored regions
    # Use a wider scan and merge
    row_starts = find_row_starts(img, 130, 800, x_col=50)
    out["row_avatar_bands"] = row_starts

    # For each row band, sample avatar center color and find right-side elements
    rows = []
    for (y0, y1) in row_starts:
        cy = (y0+y1)//2
        # sample multiple x to find avatar color reliably
        avatar_c = None
        for x in range(20, 90):
            c = px(img, x, cy)
            n = classify_avatar(c)
            if n and n not in ("qq_blue",) or (n == "qq_blue" and y0 < 200):
                # avoid mistaking search bar
                avatar_c = (x, cy, n, c)
                break
            if n in ("orange","purple","pink","teal","gray","blueish","qq_blue","green"):
                avatar_c = (x, cy, n, c)
                break
        rows.append({"y0": y0, "y1": y1, "h": y1-y0+1, "avatar": avatar_c})
    out["rows_detected"] = rows

    # Find unread red badges anywhere on the right side
    red_pts_all = []
    for y in range(180, 790):
        for x in range(320, 390):
            if is_red_badge(px(img, x, y)):
                red_pts_all.append((x, y))
    # cluster
    red_clusters = []
    if red_pts_all:
        # cluster by proximity
        red_pts_all.sort()
        cur = [red_pts_all[0]]
        for p in red_pts_all[1:]:
            if abs(p[0]-cur[-1][0])<=5 and abs(p[1]-cur[-1][1])<=5:
                cur.append(p)
            else:
                red_clusters.append(cur)
                cur = [p]
        red_clusters.append(cur)
    out["red_badge_clusters"] = [{"x0": min(p[0] for p in c), "y0": min(p[1] for p in c),
                                  "x1": max(p[0] for p in c), "y1": max(p[1] for p in c),
                                  "n": len(c)} for c in red_clusters]

    # Bottom tab strip — y range 780-844
    # Find selected tab (blue) by scanning y=820 for blue label
    bottom_blue = []
    for x in range(0, 390):
        c = px(img, x, 820)
        if is_qq_blue(c, 40):
            bottom_blue.append(x)
    if bottom_blue:
        # cluster
        clusters = []
        cur = [bottom_blue[0]]
        for v in bottom_blue[1:]:
            if v - cur[-1] <= 4:
                cur.append(v)
            else:
                clusters.append((cur[0], cur[-1])); cur = [v]
        clusters.append((cur[0], cur[-1]))
        out["bottom_tab_blue_clusters"] = clusters

    # Find red badge ABOVE the 动态 tab (around x=355-385, y=770-800)
    red_top = find_color_bbox_in(img, is_red_badge, 340, 770, 390, 810)
    out["dynamics_red_dot_bbox"] = red_top

    # Top-bar status text "手机在线 WiFi" — should be mid-gray
    out["header_text_gray_px"] = sum(1 for y in range(60,85) for x in range(70,260)
                                     if is_mid_gray_text(px(img,x,y)))

    return out

# =============================================================
# 2. channels-tab.jpg
# =============================================================
def audit_channels():
    img = load("channels-tab.jpg")
    out = {"file": "channels-tab.jpg", "size": img.size}

    out["page_bg_rgb"] = px(img, 700, 400)
    out["header_strip_rgb"] = px(img, 450, 28)

    # 我 avatar top-right (blue)
    my_a = find_color_bbox_in(img, lambda c: is_qq_blue(c, 30), 810, 5, 890, 85)
    out["my_avatar_bbox"] = my_a

    # Search pill (light bg)
    sb = find_color_bbox_in(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 0, 85, 900, 130)
    out["search_pill_bbox"] = sb

    # 3 卡片 (recommended channels): red, blue, purple gradient covers
    card1 = find_color_bbox_in(img, lambda c: c[0]>=200 and c[1]<110 and c[2]<120, 20, 165, 165, 265)
    card2 = find_color_bbox_in(img, lambda c: c[2]>=180 and c[2]>c[0]+20 and br(c)<220, 175, 165, 320, 265)
    card3 = find_color_bbox_in(img, lambda c: 130<=c[0]<=200 and 70<=c[1]<=140 and 160<=c[2]<=220, 325, 165, 465, 265)
    out["card1_red_bbox"] = card1
    out["card2_blue_bbox"] = card2
    out["card3_purple_bbox"] = card3

    # 行业频道 avatars (3 rows: 科技资讯 blue, 财经观察 orange, 职场成长 green)
    # Search at x=20-80, y=400-620
    for name, y_sample, color_name in [
        ("row_sci", 425, "qq_blue"),
        ("row_fin", 490, "orange"),
        ("row_car", 555, "green"),
    ]:
        av = find_avatar_in_row(img, y_sample, (20, 80))
        out[f"{name}_avatar"] = av

    # "+关注" pill buttons — should have blue outline at x ~ 380-440
    out["follow_blue_outline_px"] = sum(1 for y in range(400,620) for x in range(370,445)
                                         if is_qq_blue(px(img,x,y), 50))

    # Bottom nav — 频道 selected blue at x~152, y=680
    out["tab_channels_label_blue"] = is_qq_blue(px(img, 152, 680), 60)
    out["tab_channels_icon_blue"] = is_qq_blue(px(img, 152, 650), 60)

    # Bottom nav red badge above 动态 at x~370, y~640
    out["dynamics_red_dot_bbox"] = find_color_bbox_in(img, is_red_badge, 340, 630, 395, 670)

    return out

# =============================================================
# 3. contacts-tab.jpg
# =============================================================
def audit_contacts():
    img = load("contacts-tab.jpg")
    out = {"file": "contacts-tab.jpg", "size": img.size}

    out["page_bg_rgb"] = px(img, 700, 400)

    my_a = find_color_bbox_in(img, lambda c: is_qq_blue(c, 30), 810, 5, 890, 85)
    out["my_avatar_bbox"] = my_a

    sb = find_color_bbox_in(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 0, 85, 470, 130)
    out["search_pill_bbox"] = sb

    # Row avatars — 新朋友(orange), 产(green), 前(blue/teal), 周(pink), 林(blue+green), 陈(orange+green)
    for name, y_sample in [
        ("new_friend", 220),
        ("group_prod", 343),
        ("group_qian", 413),
        ("group_zhou", 483),
        ("friend_lin", 615),
        ("friend_chen", 678),
    ]:
        av = find_avatar_in_row(img, y_sample, (20, 80))
        out[f"{name}_avatar"] = av

    # Green dot on 林/陈 avatars (slightly below-right of avatar)
    out["lin_green_dot_bbox"] = find_color_bbox_in(img, is_green_dot, 60, 625, 95, 660)
    out["chen_green_dot_bbox"] = find_color_bbox_in(img, is_green_dot, 60, 685, 95, 700)

    # Red badge "1" next to 新朋友 — should be at x ~ 340-380, y ~ 205-235
    out["new_friend_red_badge"] = find_color_bbox_in(img, is_red_badge, 320, 200, 380, 240)

    # A-Z letter index — this is the QQ9 anti-feature. Sample mid-gray text in the right column
    # It's narrow vertical text on the right side around x=480-510, y=170-580
    out["az_letter_text_px"] = sum(1 for y in range(170, 600) for x in range(478, 515)
                                   if is_mid_gray_text(px(img, x, y)))
    # Sample a few specific points
    out["az_sample_ABCDEFG_px"] = [px(img, 489, y) for y in range(170, 280, 5)]
    out["az_sample_MNO_px"] = [px(img, 489, y) for y in range(370, 410, 5)]
    out["az_sample_XYZ_px"] = [px(img, 489, y) for y in range(540, 580, 5)]

    # Bottom nav 联系人 selected blue at x~247
    out["tab_contacts_label_blue"] = is_qq_blue(px(img, 247, 680), 60)
    out["tab_contacts_icon_blue"] = is_qq_blue(px(img, 247, 650), 60)

    return out

# =============================================================
# 4. dynamics-tab.jpg + dynamics-tab-mobile.jpg
# =============================================================
def audit_dynamics(img, label, is_mobile):
    out = {"file": label, "size": img.size}
    W, H = img.size

    out["page_bg_rgb"] = px(img, W-100, 400)

    my_a = find_color_bbox_in(img, lambda c: is_qq_blue(c, 30), W-80, 5, W-5, 85)
    out["my_avatar_bbox"] = my_a

    # Camera icon — should be a dark glyph between center and avatar
    cam_x_max = W-85
    cam_x_min = W-200
    cam_bbox = find_color_bbox_in(img, lambda c: br(c) <= 100,
                                  cam_x_min, 20, cam_x_max, 70)
    out["camera_icon_bbox"] = cam_bbox

    sb = find_color_bbox_in(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 0, 85, W-5, 130)
    out["search_pill_bbox"] = sb

    # First card "沈亦舟" avatar orange at x ~ 45, y ~ 185
    out["card1_shen_avatar"] = find_avatar_in_row(img, 185, (20, 80))

    # 9-grid images — verify tiles contain non-white content
    # Tablet: tiles around (90,200,310) × (320,430,540), ~110px apart
    # Mobile: tiles around (75,175,275) × (325,425,525), ~100px apart
    if is_mobile:
        xs = [75, 175, 275]; ys = [325, 425, 525]
    else:
        xs = [90, 200, 310]; ys = [320, 430, 540]
    tiles = []
    for r, ty in enumerate(ys):
        for c, tx in enumerate(xs):
            r_c = px(img, tx, ty)
            tiles.append({"r": r, "c": c, "x": tx, "y": ty, "rgb": r_c,
                          "luma": round(br(r_c), 1),
                          "non_white": br(r_c) < 220})
    out["nine_grid_tiles"] = tiles
    out["nine_grid_filled_count"] = sum(1 for t in tiles if t["non_white"])

    # Card bbox — find white card region
    out["card1_white_bbox"] = find_color_bbox_in(img, lambda c: br(c) >= 250, 0, 140, W-5, 690)

    # Like/Comment/Share buttons text counts — find dark text glyphs near y=665
    if is_mobile:
        like_x_range = (95, 130)
        comment_x_range = (195, 230)
        share_x_range = (290, 320)
    else:
        like_x_range = (95, 145)
        comment_x_range = (200, 250)
        share_x_range = (315, 365)
    out["like_count_px"] = sum(1 for y in range(655, 680) for x in range(*like_x_range) if is_dark_text(px(img,x,y)))
    out["comment_count_px"] = sum(1 for y in range(655, 680) for x in range(*comment_x_range) if is_dark_text(px(img,x,y)))
    out["share_count_px"] = sum(1 for y in range(655, 680) for x in range(*share_x_range) if is_dark_text(px(img,x,y)))

    # Right-side empty area (tablet issue)
    if not is_mobile:
        # Check empty white area to the right of card
        empty_luma_samples = [br(px(img, x, 400)) for x in range(450, 880, 30)]
        out["right_empty_avg_luma"] = round(sum(empty_luma_samples)/len(empty_luma_samples), 1)
        out["right_empty_px"] = sum(1 for x in range(450, 880) if br(px(img, x, 400)) >= 235)

    # Bottom nav 动态 selected blue + red dot
    if is_mobile:
        tab_x = 343; tab_y = 825
        red_y0, red_y1 = 775, 815
        red_x0, red_x1 = 355, 388
    else:
        tab_x = 348; tab_y = 680
        red_y0, red_y1 = 630, 670
        red_x0, red_x1 = 355, 395
    out["tab_dynamics_label_blue"] = is_qq_blue(px(img, tab_x, tab_y), 60)
    out["tab_dynamics_icon_blue"] = is_qq_blue(px(img, tab_x, tab_y-30), 60)
    out["dynamics_red_dot_bbox"] = find_color_bbox_in(img, is_red_badge, red_x0, red_y0, red_x1, red_y1)

    return out

# =============================================================
# 5. tablet-mid.jpg — left home + right chat
# =============================================================
def audit_tablet_mid():
    img = load("tablet-mid.jpg")
    out = {"file": "tablet-mid.jpg", "size": img.size}

    # Left pane bg (0-420)
    out["left_pane_bg_rgb"] = px(img, 250, 350)
    out["left_pane_luma"] = br(px(img, 250, 350))

    # Right pane bg (chat area)
    out["right_pane_bg_rgb"] = px(img, 600, 350)
    out["right_pane_luma"] = br(px(img, 600, 350))

    # Vertical divider between panes — find by looking for column with darker gray
    div_x = None
    for x in range(420, 460):
        col_l = [br(px(img, x, y)) for y in range(100, 600, 50)]
        avg = sum(col_l)/len(col_l)
        if avg < 240 and avg > 200:
            div_x = x
            break
    out["pane_divider_x"] = div_x

    # Right pane top bar: avatar (blue) at x ~ 450-490, y ~ 15-60
    chat_avatar = find_color_bbox_in(img, lambda c: is_qq_blue(c, 30), 440, 5, 520, 65)
    out["chat_top_avatar_bbox"] = chat_avatar

    # Green dot under chat avatar
    out["chat_top_green_dot"] = find_color_bbox_in(img, is_green_dot, 470, 55, 510, 80)

    # Top right icons (phone/video/more) — find dark glyph clusters
    right_icons = []
    for x in range(700, 890):
        col_dark = sum(1 for y in range(15, 55) if is_dark_text(px(img, x, y)))
        if col_dark >= 3:
            right_icons.append(x)
    clusters = []
    if right_icons:
        cur = [right_icons[0]]
        for v in right_icons[1:]:
            if v - cur[-1] <= 6:
                cur.append(v)
            else:
                clusters.append((cur[0], cur[-1])); cur = [v]
        clusters.append((cur[0], cur[-1]))
    out["chat_top_right_icon_clusters"] = clusters
    out["chat_top_right_icon_count"] = len(clusters)

    # Outbound blue bubbles — find big blue regions in right pane (x >= 440)
    bubble_bbox = find_color_bbox_in(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200,
                                     440, 60, 890, 600)
    out["outbound_bubble_bbox"] = bubble_bbox

    # "已读" text — find blue text glyphs (small blue, br < 230)
    blue_text = []
    for y in range(60, 700):
        for x in range(440, 890):
            r = px(img, x, y)
            if is_qq_blue(r, 35) and br(r) < 230 and r[0] < 80:
                blue_text.append((x, y))
    out["blue_text_pixel_count"] = len(blue_text)

    # Mask residue check — full average luma (no dark overlay)
    avg_luma = 0; n = 0
    for y in range(50, 650, 4):
        for x in range(0, 900, 4):
            avg_luma += br(px(img, x, y)); n += 1
    out["full_avg_luma"] = round(avg_luma / n, 1)

    # Composer
    out["composer_bg_rgb"] = px(img, 600, 660)
    out["composer_send_btn_blue"] = is_qq_blue(px(img, 850, 660), 50)
    out["composer_send_btn_rgb"] = px(img, 850, 660)

    # Left pane row 1 selected state
    out["left_pane_row1_bg_rgb"] = px(img, 200, 215)
    out["left_pane_row1_selected_bg"] = is_light_blue_selected(px(img, 200, 215))
    out["left_pane_row1_left_border"] = px(img, 6, 215)
    out["left_pane_row1_left_border_blue"] = is_qq_blue(px(img, 6, 215), 50)

    # Left pane bottom nav 消息 selected blue
    out["left_pane_tab_message_label_blue"] = is_qq_blue(px(img, 74, 680), 60)

    return out

# =============================================================
# 6. group-chat.jpg regression
# =============================================================
def audit_group_chat():
    img = load("group-chat.jpg")
    out = {"file": "group-chat.jpg", "size": img.size}

    # Full luma (no mask)
    avg_luma = 0; n = 0
    for y in range(0, 844, 4):
        for x in range(0, 390, 4):
            avg_luma += br(px(img, x, y)); n += 1
    out["full_avg_luma"] = round(avg_luma / n, 1)

    # Back arrow at top-left
    out["back_arrow_bbox"] = find_color_bbox_in(img, lambda c: br(c) <= 130, 5, 20, 50, 70)

    # Top avatar (白底) — group chat avatar is on a white pill
    out["top_avatar_white_bg_rgb"] = px(img, 60, 35)
    out["top_avatar_white_bg"] = br(px(img, 60, 35)) >= 245

    # More icon top right
    out["more_icon_bbox"] = find_color_bbox_in(img, lambda c: br(c) <= 130, 340, 20, 390, 70)

    # Inbound white bubble — sample at known inbound area
    out["inbound_bubble_white"] = br(px(img, 200, 200)) >= 245
    out["inbound_bubble_rgb"] = px(img, 200, 200)

    # Outbound blue bubble area
    out["outbound_blue_bbox"] = find_color_bbox_in(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200,
                                                   150, 100, 390, 800)

    # 已读 blue text
    blue_text = []
    for y in range(150, 800):
        for x in range(220, 380):
            r = px(img, x, y)
            if is_qq_blue(r, 35) and br(r) < 230 and r[0] < 80:
                blue_text.append((x, y))
    out["blue_read_text_count"] = len(blue_text)
    if blue_text:
        xs = [p[0] for p in blue_text]; ys = [p[1] for p in blue_text]
        out["blue_read_text_bbox"] = (min(xs), min(ys), max(xs), max(ys))

    # Composer
    out["composer_bg_rgb"] = px(img, 200, 808)
    out["composer_send_btn_blue"] = is_qq_blue(px(img, 358, 808), 50)

    # Self avatar orange (right side)
    out["self_avatar_orange"] = is_orange_avatar(px(img, 370, 385))
    out["self_avatar_rgb"] = px(img, 370, 385)

    # Inbound avatars (left)
    out["inbound_avatar_chen_bbox"] = find_color_bbox_in(img, lambda c: is_orange_avatar(c), 0, 200, 50, 260)

    return out

# =============================================================
if __name__ == "__main__":
    results = {
        "mobile":        audit_mobile(),
        "channels":      audit_channels(),
        "contacts":      audit_contacts(),
        "dynamics_tablet": audit_dynamics(load("dynamics-tab.jpg"), "dynamics-tab.jpg", False),
        "dynamics_mobile":  audit_dynamics(load("dynamics-tab-mobile.jpg"), "dynamics-tab-mobile.jpg", True),
        "tablet_mid":    audit_tablet_mid(),
        "group_chat":    audit_group_chat(),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))