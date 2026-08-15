#!/usr/bin/env python3
"""
Round-14 visual audit of 7 TGQQ fixture screenshots.
Produces coordinate-anchored PASS/FAIL evidence per spec A-F.
"""
from PIL import Image
import os, json, collections

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"

def load(n):
    p = os.path.join(SHOTS, n)
    return Image.open(p).convert("RGB")

def px(img, x, y):
    return img.getpixel((int(x), int(y)))

def br(rgb):
    return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]

# Color predicates (with JPEG/AA tolerance)
def is_qq_blue(rgb, tol=40):
    # #1296DB = (18,150,219)
    r,g,b = rgb
    return abs(r-18)<=tol and abs(g-150)<=tol and abs(b-219)<=tol

def is_green_dot(rgb):
    # QQ green ~ #21BA45 / #4ECB73
    r,g,b = rgb
    return g >= 130 and g > r + 30 and g > b + 20 and r < 200

def is_red_badge(rgb):
    # QQ red ~ #FA5151 / #E74C3C
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

def is_dark_text(rgb):
    return br(rgb) <= 110

def is_mid_gray_text(rgb):
    b = br(rgb)
    return 110 < b <= 180

def is_light_blue_selected(rgb):
    # selected row background ~ #EAF3FB / #F0F7FC / #ECF5FB
    r,g,bl = rgb
    return bl > r and bl > g and 220 <= bl <= 250 and r >= 220 and g >= 230

def is_page_bg_light(rgb):
    # light neutral page background ~ #F4F5F7
    r,g,b = rgb
    return 235 <= r <= 252 and 235 <= g <= 252 and 235 <= b <= 252 and abs(r-g)<10 and abs(g-b)<10

def is_card_white(rgb):
    return br(rgb) >= 248

def find_color_bbox(img, pred, x0, y0, x1, y1):
    pts = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px(img, x, y)):
                pts.append((x, y))
    if not pts:
        return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return {
        "n": len(pts),
        "x0": min(xs), "y0": min(ys),
        "x1": max(xs), "y1": max(ys),
        "w": max(xs)-min(xs)+1, "h": max(ys)-min(ys)+1,
        "cx": (min(xs)+max(xs))//2, "cy": (min(ys)+max(ys))//2,
        "sample_rgb": px(img, (min(xs)+max(xs))//2, (min(ys)+max(ys))//2),
    }

def find_row_y_extent(img, x_center, y_start, y_end, fg_pred):
    """Find vertical extent where the row contains fg_pred pixels at x_center or near."""
    # Walk y; a row is "active" where x_center column has any color
    bands = []
    cur = None
    for y in range(y_start, y_end):
        c = px(img, x_center, y)
        if fg_pred(c):
            if cur is None:
                cur = [y, y]
            else:
                cur[1] = y
        else:
            if cur and y - cur[1] > 2:
                bands.append(tuple(cur)); cur = None
            elif cur is None:
                pass
    if cur:
        bands.append(tuple(cur))
    return bands

# ==============================================================
# A+E : mobile.jpg  (390x844) — Messages list + bottom nav
# ==============================================================
def audit_mobile():
    img = load("mobile.jpg")
    out = {"file": "mobile.jpg", "size": img.size}

    # ---- Top personal row (header) ----
    # 我 avatar is at top-left. Sample its center
    out["my_avatar_center_rgb"] = px(img, 37, 47)
    out["my_avatar_is_qq_blue"] = is_qq_blue(px(img, 37, 47), 60)
    # Green dot under "我"
    out["green_dot_rgb"] = px(img, 32, 71)
    out["green_dot_present"] = is_green_dot(px(img, 32, 71))
    # "+" icon top right
    out["plus_icon_rgb"] = px(img, 360, 47)
    out["plus_icon_is_dark"] = is_dark_text(px(img, 360, 47))
    # Header bg
    out["header_bg_rgb"] = px(img, 200, 30)
    # "手机在线 WiFi" text presence — find some dark text in header (y ~60-80)
    out["header_text_pixels"] = sum(1 for y in range(55,90) for x in range(70,260) if is_dark_text(px(img,x,y)))

    # ---- Search bar ----
    # Search pill bg ~ y=110-150
    out["search_pill_bg_rgb"] = px(img, 195, 135)
    out["search_pill_is_light"] = br(px(img, 195, 135)) >= 230
    # Search icon
    out["search_icon_rgb"] = px(img, 50, 135)
    # Search pill rounded corners — check that pill spans full width with margin
    # Top edge of pill
    search_top = None; search_bot = None
    for y in range(100, 170):
        # Check leftmost pixel that's NOT page bg
        for x in range(20, 80):
            r = px(img, x, y)
            if br(r) > 240 and not is_page_bg_light(r):
                # found pill left edge
                if search_top is None: search_top = y
                search_bot = y
                break
    out["search_pill_y_range"] = (search_top, search_bot)

    # ---- Conversation rows (selected first row) ----
    # Row 1 "林晚晴" — selected
    # Selected bg: very light blue
    out["row1_bg_rgb"] = px(img, 200, 215)
    out["row1_selected_bg"] = is_light_blue_selected(px(img, 200, 215))
    # Selected left blue border
    out["row1_left_border_rgb"] = px(img, 8, 215)
    out["row1_left_border_blue"] = is_qq_blue(px(img, 8, 215), 50)
    # Avatar "林" center — should be blue
    out["row1_avatar_rgb"] = px(img, 50, 215)
    out["row1_avatar_blue"] = is_qq_blue(px(img, 50, 215), 80)
    # Time "14:23" — gray text
    out["row1_time_rgb"] = px(img, 350, 200)
    # Unread "3" red badge
    out["row1_badge_rgb"] = px(img, 360, 240)
    out["row1_badge_red"] = is_red_badge(px(img, 360, 240))

    # Row geometry — detect avatar centers
    # Avatar left margin ~30, size ~52px, so x_center ~ 56
    avatar_y_bands = []
    in_band = False; b0 = 0
    for y in range(110, 800):
        c = px(img, 56, y)
        # An avatar has colored fill; check if not white bg
        if (is_qq_blue(c, 80) or is_orange_avatar(c) or is_purple_avatar(c)
                or is_pink_avatar(c) or is_teal_avatar(c)):
            if not in_band:
                b0 = y; in_band = True
        else:
            if in_band and y - b0 > 5:
                avatar_y_bands.append((b0, y-1, br(px(img, 56, (b0+y-1)//2))))
                in_band = False
            elif in_band and y - b0 <= 5:
                in_band = False
    if in_band:
        avatar_y_bands.append((b0, y, br(px(img, 56, (b0+y)//2))))
    out["avatar_y_bands"] = avatar_y_bands
    # Compute row heights
    if len(avatar_y_bands) >= 2:
        heights = [b[1]-b[0]+1 for b in avatar_y_bands]
        out["avatar_heights"] = heights
        out["row_gaps"] = [avatar_y_bands[i+1][0]-avatar_y_bands[i][1] for i in range(len(avatar_y_bands)-1)]

    # Row 4 "周子昂" purple + unread 12
    out["row4_avatar_rgb"] = px(img, 56, 535)
    out["row4_avatar_purple"] = is_purple_avatar(px(img, 56, 535))
    out["row4_badge_rgb"] = px(img, 360, 565)
    out["row4_badge_red"] = is_red_badge(px(img, 360, 565))

    # "陈默" row 已读 dot (small green check)
    # 陈 row avatar at y ~325
    out["row2_avatar_rgb"] = px(img, 56, 325)
    out["row2_avatar_orange"] = is_orange_avatar(px(img, 56, 325))
    # Right side small mark
    out["row2_right_mark_rgb"] = px(img, 360, 350)

    # ---- Bottom navigation ----
    # Bottom tab strip ~ y=790-844
    # Find tab icons by scanning dark pixels at y=810,820
    # Tab x centers: 消息~49, 频道~147, 联系人~245, 动态~343
    out["tab_y_text_label"] = (815, 838)
    out["tab_message_icon"] = px(img, 49, 805)
    out["tab_message_label_rgb"] = px(img, 49, 830)
    out["tab_message_selected_blue"] = is_qq_blue(px(img, 49, 830), 60)
    out["tab_channels_label_rgb"] = px(img, 147, 830)
    out["tab_contacts_label_rgb"] = px(img, 245, 830)
    out["tab_dynamics_label_rgb"] = px(img, 343, 830)
    out["tab_dynamics_selected_blue"] = is_qq_blue(px(img, 343, 830), 60)
    # Red dot badge above 动态 tab
    # Sample around (370, 778)
    out["tab_dynamics_badge_rgb"] = px(img, 372, 778)
    out["tab_dynamics_badge_red"] = is_red_badge(px(img, 372, 778))
    # Scan for red badge above 动态 icon
    badge_pts = []
    for y in range(770, 800):
        for x in range(340, 390):
            if is_red_badge(px(img, x, y)):
                badge_pts.append((x, y))
    out["tab_dynamics_badge_bbox"] = (
        (min(p[0] for p in badge_pts), min(p[1] for p in badge_pts),
         max(p[0] for p in badge_pts), max(p[1] for p in badge_pts))
        if badge_pts else None)

    return out

# ==============================================================
# B : channels-tab.jpg (900x700) — Channels tab (tablet left)
# ==============================================================
def audit_channels():
    img = load("channels-tab.jpg")
    out = {"file": "channels-tab.jpg", "size": img.size}

    # Page bg
    out["page_bg_rgb"] = px(img, 600, 400)
    # Header "频道" — sample where text would be
    out["header_text_pixels"] = sum(1 for y in range(25,55) for x in range(20,100) if is_dark_text(px(img,x,y)))
    # 我 avatar top-right
    out["my_avatar_rgb"] = px(img, 838, 35)
    out["my_avatar_blue"] = is_qq_blue(px(img, 838, 35), 70)
    # Search "搜索频道"
    out["search_bg_rgb"] = px(img, 300, 100)
    out["search_pill_light"] = br(px(img, 300, 100)) >= 235
    # 推荐频道 title
    out["section_recommend_text_px"] = sum(1 for y in range(155,175) for x in range(20,150) if is_dark_text(px(img,x,y)))
    # First card "腾讯新闻" red gradient cover
    out["card1_cover_rgb"] = px(img, 85, 215)
    out["card1_cover_red"] = px(img, 85, 215)[0] >= 200 and px(img, 85, 215)[1] < 100
    out["card1_name_rgb"] = px(img, 100, 280)
    # "+关注" pill — should have blue outline
    out["card1_follow_text_px"] = sum(1 for y in range(305,325) for x in range(120,180) if is_qq_blue(px(img,x,y), 60))

    # Card geometry: find red gradient bbox in card 1 (x ~ 30-160, y ~ 175-260)
    bbox = find_color_bbox(img, lambda c: c[0]>=200 and c[1]<110 and c[2]<120, 25, 170, 165, 265)
    out["card1_red_cover_bbox"] = bbox

    # Card 2 "科技前沿" — blue gradient
    bbox2 = find_color_bbox(img, lambda c: c[2]>=180 and c[2]>c[0]+20 and br(c)<220, 175, 170, 315, 265)
    out["card2_blue_cover_bbox"] = bbox2

    # Card 3 "影视热播" — purple gradient
    bbox3 = find_color_bbox(img, lambda c: 130<=c[0]<=200 and 70<=c[1]<=140 and 160<=c[2]<=220, 325, 170, 465, 265)
    out["card3_purple_cover_bbox"] = bbox3

    # 行业频道 — find row avatars (blue/orange/green)
    # Row 1 "科技资讯" — blue avatar at (45, 420)
    out["row_sci_avatar_rgb"] = px(img, 45, 425)
    out["row_sci_avatar_blue"] = is_qq_blue(px(img, 45, 425), 80)
    # Row 2 "财经观察" — orange at (45, 485)
    out["row_fin_avatar_rgb"] = px(img, 45, 490)
    out["row_fin_avatar_orange"] = is_orange_avatar(px(img, 45, 490))
    # Row 3 "职场成长" — green at (45, 550)
    out["row_car_avatar_rgb"] = px(img, 45, 555)
    out["row_car_avatar_green"] = px(img, 45, 555)[1] > 150 and px(img, 45, 555)[0] < 200 and px(img, 45, 555)[2] < 150

    # "+关注" buttons in 行业频道 — blue outlines
    out["row_follow_buttons_blue_px"] = sum(1 for y in range(400,620) for x in range(370,440)
                                              if is_qq_blue(px(img,x,y), 60))

    # Bottom nav: 频道 selected blue
    out["tab_message_label_rgb"] = px(img, 74, 680)
    out["tab_channels_label_rgb"] = px(img, 152, 680)
    out["tab_channels_selected_blue"] = is_qq_blue(px(img, 152, 680), 70)
    out["tab_contacts_label_rgb"] = px(img, 247, 680)
    out["tab_dynamics_label_rgb"] = px(img, 348, 680)

    return out

# ==============================================================
# C : contacts-tab.jpg (900x700) — Contacts tab
# ==============================================================
def audit_contacts():
    img = load("contacts-tab.jpg")
    out = {"file": "contacts-tab.jpg", "size": img.size}

    out["page_bg_rgb"] = px(img, 600, 400)
    out["header_text_pixels"] = sum(1 for y in range(25,55) for x in range(20,120) if is_dark_text(px(img,x,y)))
    out["my_avatar_rgb"] = px(img, 838, 35)
    out["my_avatar_blue"] = is_qq_blue(px(img, 838, 35), 70)

    out["search_pill_rgb"] = px(img, 300, 100)
    out["search_pill_light"] = br(px(img, 300, 100)) >= 235

    # 新朋友 row + red badge "1"
    # 新 avatar orange at (45, 217)
    out["new_friend_avatar_rgb"] = px(img, 45, 220)
    out["new_friend_avatar_orange"] = is_orange_avatar(px(img, 45, 220))
    # Red badge "1" at right
    out["new_friend_badge_rgb"] = px(img, 357, 218)
    out["new_friend_badge_red"] = is_red_badge(px(img, 357, 218))

    # 产 avatar green
    out["group_prod_avatar_rgb"] = px(img, 45, 343)
    # 前 avatar blue
    out["group_qian_avatar_rgb"] = px(img, 45, 413)
    # 周 avatar pink
    out["group_zhou_avatar_rgb"] = px(img, 45, 483)

    # 林 (我的好友) — blue avatar + green dot
    out["friend_lin_avatar_rgb"] = px(img, 45, 615)
    out["friend_lin_green_dot_rgb"] = px(img, 78, 632)
    out["friend_lin_green_dot"] = is_green_dot(px(img, 78, 632))
    # 陈 (我的好友) — orange avatar + green dot
    out["friend_chen_avatar_rgb"] = px(img, 45, 678)
    out["friend_chen_green_dot_rgb"] = px(img, 78, 695)
    out["friend_chen_green_dot"] = is_green_dot(px(img, 78, 695))

    # **The infamous A-Z letter index** — Telegram artifact on right side
    # Sample letter column — should be around x=485
    az_text_px = 0
    for y in range(170, 600):
        for x in range(480, 510):
            if is_mid_gray_text(px(img, x, y)):
                az_text_px += 1
    out["az_letter_index_text_px"] = az_text_px

    # Sample a few specific letter locations to confirm
    out["az_A_rgb"] = px(img, 489, 178)
    out["az_B_rgb"] = px(img, 489, 188)
    out["az_M_rgb"] = px(img, 489, 378)
    out["az_Z_rgb"] = px(img, 489, 568)

    # Bottom nav
    out["tab_contacts_label_rgb"] = px(img, 247, 680)
    out["tab_contacts_selected_blue"] = is_qq_blue(px(img, 247, 680), 70)

    return out

# ==============================================================
# D : dynamics-tab.jpg (900x700) + dynamics-tab-mobile.jpg (390x844)
# ==============================================================
def audit_dynamics_tablet():
    img = load("dynamics-tab.jpg")
    out = {"file": "dynamics-tab.jpg", "size": img.size}

    out["page_bg_rgb"] = px(img, 700, 400)
    out["header_text_pixels"] = sum(1 for y in range(25,55) for x in range(20,90) if is_dark_text(px(img,x,y)))

    # 📷 camera icon — sample where camera button would be (right side, before avatar)
    out["camera_icon_rgb"] = px(img, 745, 35)
    out["camera_icon_dark"] = is_dark_text(px(img, 745, 35))

    out["my_avatar_rgb"] = px(img, 838, 35)
    out["my_avatar_blue"] = is_qq_blue(px(img, 838, 35), 70)

    out["search_pill_rgb"] = px(img, 250, 100)
    out["search_pill_light"] = br(px(img, 250, 100)) >= 235

    # First card "沈亦舟" — orange avatar + name + time
    out["card_shen_avatar_rgb"] = px(img, 45, 185)
    out["card_shen_avatar_orange"] = is_orange_avatar(px(img, 45, 185))

    # 9-grid 3x3 images — sample center of each tile to verify they're loaded images not blanks
    # Tile centers ~ x: 90, 200, 310 ; y: 320, 430, 540
    tiles = []
    for r in range(3):
        for c in range(3):
            tx = 90 + c*110
            ty = 320 + r*110
            tiles.append((r, c, px(img, tx, ty)))
    out["nine_grid_tiles"] = tiles

    # Like/Comment/Share buttons — sample around bottom of card
    # Heart icon ~ x=100, y=665; Comment ~ x=210, y=665; Share ~ x=320, y=665
    out["like_button_icon_rgb"] = px(img, 100, 660)
    out["like_count_text_px"] = sum(1 for y in range(655,680) for x in range(115,140) if is_dark_text(px(img,x,y)))
    out["comment_count_text_px"] = sum(1 for y in range(655,680) for x in range(225,250) if is_dark_text(px(img,x,y)))
    out["share_count_text_px"] = sum(1 for y in range(655,680) for x in range(335,355) if is_dark_text(px(img,x,y)))

    # Card geometry — find white card bbox
    bbox = find_color_bbox(img, lambda c: br(c) >= 250, 10, 145, 450, 690)
    out["dynamics_card1_bbox"] = bbox

    # Right side empty area
    out["right_empty_luma"] = br(px(img, 600, 400))
    out["right_empty_width_px"] = sum(1 for x in range(450, 900) if br(px(img, x, 400)) >= 235)

    # Bottom nav — 动态 selected blue, with red badge
    out["tab_dynamics_label_rgb"] = px(img, 348, 680)
    out["tab_dynamics_selected_blue"] = is_qq_blue(px(img, 348, 680), 70)
    # Red badge above 动态
    badge_pts = []
    for y in range(630, 670):
        for x in range(355, 395):
            if is_red_badge(px(img, x, y)):
                badge_pts.append((x, y))
    out["tab_dynamics_badge_bbox"] = (
        (min(p[0] for p in badge_pts), min(p[1] for p in badge_pts),
         max(p[0] for p in badge_pts), max(p[1] for p in badge_pts))
        if badge_pts else None)

    return out

def audit_dynamics_mobile():
    img = load("dynamics-tab-mobile.jpg")
    out = {"file": "dynamics-tab-mobile.jpg", "size": img.size}

    out["page_bg_rgb"] = px(img, 200, 400)
    out["header_text_pixels"] = sum(1 for y in range(25,55) for x in range(20,90) if is_dark_text(px(img,x,y)))
    out["camera_icon_rgb"] = px(img, 305, 35)
    out["camera_icon_dark"] = is_dark_text(px(img, 305, 35))
    out["my_avatar_rgb"] = px(img, 360, 35)
    out["my_avatar_blue"] = is_qq_blue(px(img, 360, 35), 70)

    out["search_pill_rgb"] = px(img, 195, 100)
    out["search_pill_light"] = br(px(img, 195, 100)) >= 235

    out["card_shen_avatar_rgb"] = px(img, 45, 185)
    out["card_shen_avatar_orange"] = is_orange_avatar(px(img, 45, 185))

    # 9-grid on mobile — tile centers
    tiles = []
    for r in range(3):
        for c in range(3):
            tx = 75 + c*100
            ty = 325 + r*100
            tiles.append((r, c, px(img, tx, ty)))
    out["nine_grid_tiles"] = tiles

    out["like_count_text_px"] = sum(1 for y in range(655,680) for x in range(95,115) if is_dark_text(px(img,x,y)))
    out["comment_count_text_px"] = sum(1 for y in range(655,680) for x in range(200,225) if is_dark_text(px(img,x,y)))
    out["share_count_text_px"] = sum(1 for y in range(655,680) for x in range(295,320) if is_dark_text(px(img,x,y)))

    bbox = find_color_bbox(img, lambda c: br(c) >= 250, 10, 145, 380, 690)
    out["dynamics_card1_bbox"] = bbox

    out["tab_dynamics_label_rgb"] = px(img, 343, 825)
    out["tab_dynamics_selected_blue"] = is_qq_blue(px(img, 343, 825), 70)
    badge_pts = []
    for y in range(775, 815):
        for x in range(355, 388):
            if is_red_badge(px(img, x, y)):
                badge_pts.append((x, y))
    out["tab_dynamics_badge_bbox"] = (
        (min(p[0] for p in badge_pts), min(p[1] for p in badge_pts),
         max(p[0] for p in badge_pts), max(p[1] for p in badge_pts))
        if badge_pts else None)

    return out

# ==============================================================
# F : tablet-mid.jpg (900x700) — Left home + right chat
# ==============================================================
def audit_tablet_mid():
    img = load("tablet-mid.jpg")
    out = {"file": "tablet-mid.jpg", "size": img.size}

    # Split into left pane (0-420) and right pane (420-900)
    # Left pane bg
    out["left_pane_bg_rgb"] = px(img, 250, 350)
    out["left_pane_luma"] = br(px(img, 250, 350))
    # Right pane bg — should be very light (chat bg)
    out["right_pane_bg_rgb"] = px(img, 600, 350)
    out["right_pane_luma"] = br(px(img, 600, 350))

    # Right pane top bar
    # Avatar 林
    out["chat_avatar_lin_rgb"] = px(img, 470, 35)
    out["chat_avatar_lin_blue"] = is_qq_blue(px(img, 470, 35), 80)
    # Green dot under avatar
    out["chat_green_dot_rgb"] = px(img, 500, 56)
    out["chat_green_dot"] = is_green_dot(px(img, 500, 56))
    # Right side icons (phone/video/more) — count dark glyph centers in y=25-50, x=700-880
    icon_centers = []
    for x in range(680, 890):
        col_dark = sum(1 for y in range(15, 55) if is_dark_text(px(img, x, y)))
        if col_dark > 3:
            icon_centers.append(x)
    # cluster consecutive
    clusters = []
    if icon_centers:
        cur = [icon_centers[0]]
        for v in icon_centers[1:]:
            if v - cur[-1] <= 6:
                cur.append(v)
            else:
                clusters.append((cur[0], cur[-1])); cur = [v]
        clusters.append((cur[0], cur[-1]))
    out["chat_top_right_icon_clusters"] = clusters

    # Outbound bubble — find blue bubble in right pane
    # Sample around (650, 100) which should be a blue outbound bubble
    # Look in y=80-200, x=440-880 for blue pixels
    bbox = find_color_bbox(img, lambda c: c[2]>=200 and c[2]>c[0]+15 and c[0]<230 and br(c)>200, 440, 60, 890, 600)
    out["right_pane_blue_bubble_bbox"] = bbox

    # "已读" text in right pane — sample for blue text
    blue_text_pts = []
    for y in range(60, 600):
        for x in range(440, 890):
            r = px(img, x, y)
            if is_qq_blue(r, 35) and br(r) < 230 and r[0] < 80:
                blue_text_pts.append((x, y))
    if blue_text_pts:
        out["right_pane_blue_text_count"] = len(blue_text_pts)
        xs = [p[0] for p in blue_text_pts]; ys = [p[1] for p in blue_text_pts]
        out["right_pane_blue_text_bbox"] = (min(xs), min(ys), max(xs), max(ys))
    else:
        out["right_pane_blue_text_count"] = 0

    # Mask residue check — average luma should be high (no dark overlay)
    # Sample whole image luma
    avg_luma = 0; n = 0
    for y in range(50, 650, 4):
        for x in range(0, 900, 4):
            avg_luma += br(px(img, x, y)); n += 1
    out["full_avg_luma"] = avg_luma / n

    # Composer — sample
    out["composer_bg_rgb"] = px(img, 600, 660)
    out["composer_emoji_rgb"] = px(img, 480, 660)
    out["composer_send_btn_rgb"] = px(img, 850, 660)

    # Left pane — first conversation row (林晚晴 selected)
    out["left_pane_row1_bg_rgb"] = px(img, 250, 215)
    out["left_pane_row1_selected_bg"] = is_light_blue_selected(px(img, 250, 215))
    out["left_pane_row1_left_border_rgb"] = px(img, 8, 215)
    out["left_pane_row1_left_border_blue"] = is_qq_blue(px(img, 8, 215), 50)
    out["left_pane_row1_avatar_rgb"] = px(img, 56, 215)
    out["left_pane_row1_avatar_blue"] = is_qq_blue(px(img, 56, 215), 80)

    # Left pane bottom nav — verify 消息 selected
    out["left_pane_tab_message_label_rgb"] = px(img, 74, 680)
    out["left_pane_tab_message_selected_blue"] = is_qq_blue(px(img, 74, 680), 70)

    return out

# ==============================================================
# Regression : group-chat.jpg (390x844)
# ==============================================================
def audit_group_chat():
    img = load("group-chat.jpg")
    out = {"file": "group-chat.jpg", "size": img.size}

    # Mask residue check — full image average luma (no dark overlay)
    avg_luma = 0; n = 0
    for y in range(0, 844, 4):
        for x in range(0, 390, 4):
            avg_luma += br(px(img, x, y)); n += 1
    out["full_avg_luma"] = avg_luma / n

    # Top bar — < back arrow + avatar "产" + name "产品讨论组" + "128 人" + ⋯
    out["back_arrow_rgb"] = px(img, 22, 50)
    out["back_arrow_dark"] = is_dark_text(px(img, 22, 50))
    out["top_avatar_white"] = br(px(img, 60, 35)) >= 240  # avatar sits on white pill
    out["more_icon_rgb"] = px(img, 365, 50)
    out["more_icon_dark"] = is_dark_text(px(img, 365, 50))

    # Inbound bubble white
    out["inbound_bubble_bg_rgb"] = px(img, 230, 200)
    out["inbound_bubble_white"] = br(px(img, 230, 200)) >= 248

    # Outbound bubble blue
    bbox = find_color_bbox(img, lambda c: c[2]>=200 and c[2]>c[0]+15 and c[0]<230 and br(c)>200, 150, 100, 390, 800)
    out["outbound_blue_bubble_bbox"] = bbox

    # "已读" text
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
    out["composer_emoji_rgb"] = px(img, 22, 808)
    out["composer_send_btn_rgb"] = px(img, 358, 808)
    out["composer_send_blue"] = is_qq_blue(px(img, 358, 808), 50)

    # Self avatar "我" (orange) appears beside outbound bubble
    # First outbound is around y=380
    out["self_avatar_orange"] = is_orange_avatar(px(img, 370, 385))
    out["self_avatar_rgb"] = px(img, 370, 385)

    # Inbound avatars (陈, 周, 陈) at left
    out["inbound_avatar_chen_rgb"] = px(img, 22, 222)
    out["inbound_avatar_zhou_rgb"] = px(img, 22, 480)

    return out

# ==============================================================
# Main
# ==============================================================
if __name__ == "__main__":
    results = {
        "mobile": audit_mobile(),
        "channels": audit_channels(),
        "contacts": audit_contacts(),
        "dynamics_tablet": audit_dynamics_tablet(),
        "dynamics_mobile": audit_dynamics_mobile(),
        "tablet_mid": audit_tablet_mid(),
        "group_chat": audit_group_chat(),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))