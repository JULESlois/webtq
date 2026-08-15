#!/usr/bin/env python3
"""
Round-14 final targeted audit. Fixes known coordinate misses.
"""
from PIL import Image
import os, json, collections

SHOTS = "/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS, n)).convert("RGB")
def px(img, x, y): return img.getpixel((int(x), int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

# Color predicates
def is_qq_blue(rgb, tol=40):
    r,g,b=rgb; return abs(r-18)<=tol and abs(g-150)<=tol and abs(b-219)<=tol
def is_green_dot(rgb):
    r,g,b=rgb
    return g >= 140 and g > r + 30 and g > b + 20 and r < 200
def is_red_badge(rgb):
    r,g,b=rgb
    return r >= 200 and g < 130 and b < 130 and r > g + 70 and r > b + 70
def is_orange_avatar(rgb):
    r,g,b=rgb; return r >= 220 and 110 <= g <= 180 and 40 <= b <= 110 and r > g > b
def is_purple_avatar(rgb):
    r,g,b=rgb; return 130 <= r <= 200 and 70 <= g <= 140 and 160 <= b <= 220 and b > r > g
def is_pink_avatar(rgb):
    r,g,b=rgb; return r >= 200 and g < 130 and 100 <= b <= 180 and r > g and b > g
def is_teal_avatar(rgb):
    r,g,b=rgb; return r < 130 and g > 150 and b > 180 and b > r
def is_dark_text(rgb): return br(rgb) <= 130
def is_mid_gray(rgb): b=br(rgb); return 130 < b <= 200

def find_color_bbox(img, pred, x0, y0, x1, y1):
    pts=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            if pred(px(img,x,y)): pts.append((x,y))
    if not pts: return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return {"n":len(pts),"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
            "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
            "cx":(min(xs)+max(xs))//2,"cy":(min(ys)+max(ys))//2,
            "sample_rgb":px(img,(min(xs)+max(xs))//2,(min(ys)+max(ys))//2)}

def sample_avatar_at(img, x, y):
    """Sample multiple x offsets to find the dominant avatar color (skip text pixels)."""
    samples=[]
    for dx in [-15,-10,-5,0,5,10,15,20]:
        for dy in [-15,-10,0,10,15]:
            try:
                samples.append(px(img,x+dx,y+dy))
            except: pass
    # Filter to "colorful" pixels (not white, not too dark)
    color_samples=[s for s in samples if br(s)>=40 and br(s)<=235]
    if not color_samples:
        return None
    # Average
    n=len(color_samples)
    return (sum(s[0] for s in color_samples)//n,
            sum(s[1] for s in color_samples)//n,
            sum(s[2] for s in color_samples)//n)

def classify(rgb):
    if rgb is None: return "?"
    if is_orange_avatar(rgb): return "orange"
    if is_purple_avatar(rgb): return "purple"
    if is_pink_avatar(rgb): return "pink"
    if is_teal_avatar(rgb): return "teal"
    if is_qq_blue(rgb, 50): return "qq_blue"
    if is_green_dot(rgb): return "green"
    return "other(%d,%d,%d)"%rgb

# =============================================================
# Detailed avatar + dot + row analysis for mobile.jpg
# =============================================================
def mobile_deep():
    img=load("mobile.jpg")
    out={}
    # Page bg samples
    out["page_bg_samples"]={
        "top_header_(195,28)": px(img,195,28),
        "between_rows_(195,180)": px(img,195,180),
        "between_rows_(195,275)": px(img,195,275),
    }
    # 我 avatar — sample edge of avatar, not center
    # Avatar bbox from audit2: x0=29, y0=27, x1=66, y1=65. Sample at multiple offsets
    out["my_avatar_edge_samples"]={
        "left_edge_(30,46)": px(img,30,46),
        "right_edge_(65,46)": px(img,65,46),
        "top_edge_(47,28)": px(img,47,28),
        "bot_edge_(47,64)": px(img,47,64),
        "dom": sample_avatar_at(img,47,46),
    }
    out["my_avatar_classified"]=classify(sample_avatar_at(img,47,46))

    # Search pill — scan y=110-160 for leftmost non-bg edge of pill
    pill_top=None; pill_bot=None; pill_left=None; pill_right=None
    for y in range(100,170):
        for x in range(0,80):
            r=px(img,x,y)
            if 220<=r[2]<=255 and 220<=r[0]<=250 and 230<=r[1]<=252:
                if pill_top is None: pill_top=y
                pill_bot=y
                if pill_left is None or x<pill_left: pill_left=x
                break
        for x in range(389,300,-1):
            r=px(img,x,y)
            if 220<=r[2]<=255 and 220<=r[0]<=250 and 230<=r[1]<=252:
                if pill_right is None or x>pill_right: pill_right=x
                break
    out["search_pill_actual_bbox"]=(pill_left,pill_top,pill_right,pill_bot)
    out["search_pill_height"]=(pill_bot-pill_top+1) if pill_top else None
    out["search_pill_width"]=(pill_right-pill_left+1) if pill_left else None
    out["search_pill_sample"]=px(img,200,(pill_top+pill_bot)//2) if pill_top else None

    # Selected row detection — find rows where there's a NON-WHITE bg
    # Scan y 180-790; record every row's bg color at x=200
    selected_bands=[]
    in_band=False; b0=None
    for y in range(180,790):
        c=px(img,200,y)
        # Not white (255,255,255), but light enough to be a bg
        if 235<=br(c)<=253 and (c[0]<254 or c[1]<254 or c[2]<254):
            if not in_band:
                b0=y; in_band=True
        else:
            if in_band and y-b0>=5:
                selected_bands.append((b0,y-1))
                in_band=False
            elif in_band:
                in_band=False
    out["non_white_row_bands"]=selected_bands

    # For each row band, sample bg color
    out["row_bg_samples"]=[]
    for (y0,y1) in selected_bands:
        cy=(y0+y1)//2
        out["row_bg_samples"].append({"y_range":(y0,y1), "bg": px(img,200,cy)})

    # Find selected row distinctly — look for the one with light blue tint
    blue_selected=[]
    for (y0,y1) in selected_bands:
        cy=(y0+y1)//2
        c=px(img,200,cy)
        if c[2]>c[0] and c[2]>c[1] and 240<=c[2]<=253 and 240<=c[0]<=252:
            blue_selected.append((y0,y1,c))
    out["light_blue_tinted_rows"]=blue_selected

    # Left blue border (selected indicator) — find by scanning x=2-12, y=180-790 for blue
    out["left_border_bbox"]=find_color_bbox(img,lambda c:is_qq_blue(c,30), 0, 180, 12, 790)

    # Find green dot under 我 avatar — search x=65-90, y=60-90 (right of avatar)
    out["green_dot_under_my"]=find_color_bbox(img, is_green_dot, 60, 60, 100, 90)
    # Also try left of avatar
    out["green_dot_left_of_my"]=find_color_bbox(img, is_green_dot, 5, 60, 30, 90)
    # Search anywhere in header y=60-90
    out["green_dot_header"]=find_color_bbox(img, is_green_dot, 0, 60, 200, 90)

    # Per-row avatar colors (use corrected coords based on row_avatar_bands from audit2)
    # Audit2 found these row bands (y0,y1):
    # (208,222), (237,257), (281,298), (306,332), (356,371), (384,406), (428,481),
    # (503,503), (515,515), (525,525), (601,601), (652,667), (681,701),
    # (725,726), (739,742), (758,776)
    # Each row's avatar should be at left, x ~ 28-65
    row_y_centers=[215, 247, 289, 319, 363, 395, 454, 691]  # 8 conversation rows
    row_names=["林晚晴","陈默","产品讨论组","周子昂","前端交流群","苏小满","沈亦舟","唐雪"]
    out["row_avatars"]=[]
    for name,cy in zip(row_names, row_y_centers):
        dom = sample_avatar_at(img, 47, cy)
        out["row_avatars"].append({
            "name": name,
            "y_center": cy,
            "dominant_rgb": dom,
            "classified": classify(dom),
            "sample_left_edge": px(img, 28, cy),
            "sample_center": px(img, 47, cy),
            "sample_right_edge": px(img, 65, cy),
        })

    # Find unread red badges — aggregate clusters
    red_pts=[]
    for y in range(180,790):
        for x in range(320, 390):
            if is_red_badge(px(img,x,y)): red_pts.append((x,y))
    # Cluster
    clusters=[]
    if red_pts:
        red_pts.sort()
        cur=[red_pts[0]]
        for p in red_pts[1:]:
            if abs(p[0]-cur[-1][0])<=8 and abs(p[1]-cur[-1][1])<=8:
                cur.append(p)
            else:
                clusters.append(cur); cur=[p]
        clusters.append(cur)
    out["red_badge_clusters"]=[
        {"bbox":(min(p[0] for p in c), min(p[1] for p in c),
                 max(p[0] for p in c), max(p[1] for p in c)),
         "n":len(c)}
        for c in clusters
    ]

    # Bottom tab selected state — find blue label text
    # Tab labels at y ~ 830. Find where blue text is
    tab_y=830
    out["bottom_blue_label_clusters"]=[]
    pts=[x for x in range(0,390) if is_qq_blue(px(img,x,tab_y),35)]
    if pts:
        # cluster
        clusters=[]
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
        out["bottom_blue_label_clusters"]=clusters

    # Bottom tab icons (above labels) — find dark glyph clusters
    # Icons at y ~ 800-820
    out["bottom_tab_icons"]={}
    for label, cx in [("消息",49),("频道",147),("联系人",245),("动态",343)]:
        out["bottom_tab_icons"][label]={
            "icon_at_(%d,805)"%cx: px(img,cx,805),
            "label_at_(%d,830)"%cx: px(img,cx,830),
        }

    # Dynamics red badge ABOVE 动态 tab
    out["dynamics_red_dot_bbox"]=find_color_bbox(img, is_red_badge, 340, 770, 388, 810)

    # Header text "手机在线 WiFi" — count mid-gray pixels (text glyphs)
    out["header_text_midgray_px"]=sum(1 for y in range(60,85) for x in range(70,260)
                                      if is_mid_gray(px(img,x,y)))
    out["header_text_dark_px"]=sum(1 for y in range(60,85) for x in range(70,260)
                                   if is_dark_text(px(img,x,y)))

    return out

# =============================================================
# Channels tab detailed
# =============================================================
def channels_deep():
    img=load("channels-tab.jpg")
    out={}
    out["page_bg_samples"]={
        "(450,28)":px(img,450,28),
        "(450,400)":px(img,450,400),
        "(700,400)":px(img,700,400),
    }
    # 我 avatar — search more broadly top-right
    out["my_avatar_search_box"]=find_color_bbox(img,lambda c:is_qq_blue(c,30), 800, 5, 895, 80)
    out["my_avatar_alt_sample_(845,35)"]=px(img,845,35)

    # Search pill actual
    sb=find_color_bbox(img,lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 10, 80, 460, 130)
    out["search_pill_bbox"]=sb

    # Section header "推荐频道" sample
    out["section_text_pixels"]=sum(1 for y in range(150,180) for x in range(20,150)
                                   if is_dark_text(px(img,x,y)))
    out["section_text_sample_(40,165)"]=px(img,40,165)

    # Card 1 "腾讯新闻" — find red gradient bbox
    out["card1_red_bbox"]=find_color_bbox(img,lambda c: c[0]>=220 and c[1]<120 and c[2]<130, 25, 165, 165, 265)
    out["card1_red_sample"]=px(img,75,200)
    out["card1_text_px_count"]=sum(1 for y in range(255,290) for x in range(25,165)
                                    if is_dark_text(px(img,x,y)))
    out["card1_follow_text_px"]=sum(1 for y in range(290,330) for x in range(110,165)
                                     if is_qq_blue(px(img,x,y),50) or is_dark_text(px(img,x,y)))

    # Card 2 blue
    out["card2_blue_bbox"]=find_color_bbox(img,lambda c: c[2]>=180 and c[2]>c[0]+20 and br(c)<220, 175, 165, 320, 265)
    out["card2_blue_sample"]=px(img,245,200)

    # Card 3 purple
    out["card3_purple_bbox"]=find_color_bbox(img,lambda c: 130<=c[0]<=200 and 70<=c[1]<=140 and 160<=c[2]<=220, 325, 165, 465, 265)
    out["card3_purple_sample"]=px(img,395,200)

    # 行业频道 rows — find row avatars
    # Approximate: row centers y=425, 490, 555
    for name, cy in [("科技资讯",425),("财经观察",490),("职场成长",555)]:
        dom=sample_avatar_at(img, 47, cy)
        out[f"row_{name}_avatar"]={
            "y":cy,
            "dom":dom,
            "classified":classify(dom),
            "edge_samples":[px(img,28,cy), px(img,47,cy), px(img,65,cy)],
        }

    # Follow button blue outline — search broader range
    out["follow_button_blue_px"]=sum(1 for y in range(380,610) for x in range(360,450)
                                      if is_qq_blue(px(img,x,y), 50))
    out["follow_button_text_px"]=sum(1 for y in range(380,610) for x in range(360,450)
                                      if is_dark_text(px(img,x,y)))

    # Bottom nav — tab 频道 should be blue (selected)
    out["tab_频道_y680_blue"]=is_qq_blue(px(img,152,680), 60)
    out["tab_频道_y650_blue"]=is_qq_blue(px(img,152,650), 60)
    out["tab_频道_icon_sample"]=px(img,152,640)
    out["tab_频道_label_sample"]=px(img,152,683)
    # Scan whole bottom strip for blue
    pts=[x for x in range(0,900) if is_qq_blue(px(img,x,680),40)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["tab_blue_clusters_y680"]=clusters

    out["dynamics_red_dot_bbox"]=find_color_bbox(img, is_red_badge, 340, 630, 395, 670)

    return out

# =============================================================
# Contacts tab detailed — with letter index verification
# =============================================================
def contacts_deep():
    img=load("contacts-tab.jpg")
    out={}
    out["page_bg_samples"]={
        "(450,28)":px(img,450,28),
        "(450,400)":px(img,450,400),
        "(700,400)":px(img,700,400),
    }

    # 我 avatar
    out["my_avatar_search_box"]=find_color_bbox(img,lambda c:is_qq_blue(c,30), 800, 5, 895, 80)
    out["my_avatar_alt_sample"]=px(img,845,35)

    # Search pill
    sb=find_color_bbox(img,lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 10, 80, 470, 130)
    out["search_pill_bbox"]=sb

    # ===== A-Z LETTER INDEX — the key bug check =====
    # Visually A is at top, then B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
    # Find the x column of the letters (mid-gray text)
    az_cols={}
    for x in range(420, 520):
        col_count=sum(1 for y in range(170, 600) if is_mid_gray(px(img,x,y)))
        if col_count > 5:
            az_cols[x]=col_count
    if az_cols:
        # find max
        max_col=max(az_cols, key=az_cols.get)
        out["az_letter_max_col"]=(max_col, az_cols[max_col])
        out["az_letter_col_range"]=(min(az_cols.keys()), max(az_cols.keys()))

    # Sample a few letter positions
    out["az_samples_by_y"]={
        "y180_(?)": px(img, 489, 180),
        "y200_(?)": px(img, 489, 200),
        "y250_(?)": px(img, 489, 250),
        "y300_(?)": px(img, 489, 300),
        "y400_(?)": px(img, 489, 400),
        "y500_(?)": px(img, 489, 500),
        "y570_(?)": px(img, 489, 570),
    }
    # Count distinct y positions where the letter column has mid-gray text
    out["az_letter_y_count"]=sum(1 for y in range(170, 600) if is_mid_gray(px(img, 489, y)))

    # Find the right edge of the contacts list (before letter index)
    # Scan x=400-500 for white bg vs letter text boundary
    out["right_edge_scan"]={}
    for x in range(420, 510, 5):
        out["right_edge_scan"][x]=px(img, x, 300)

    # Group section labels
    for name, y in [("新朋友_header",195),("我的群聊_header",292),("我的好友_header",570)]:
        out[f"section_{name}_text_px"]=sum(1 for yi in range(y-15,y+15) for x in range(20,150)
                                             if is_dark_text(px(img,x,yi)))

    # Row avatars — corrected sampling
    for name, cy in [("新朋友_新",220),("产品讨论组_产",343),("前端交流群_前",413),
                     ("周末爬山小队_周",483),("林晚晴_林",615),("陈默_陈",678)]:
        dom=sample_avatar_at(img, 47, cy)
        out[f"row_{name}_avatar"]={
            "y":cy, "dom":dom, "classified":classify(dom),
            "edge_samples":[px(img,28,cy), px(img,47,cy), px(img,65,cy)],
        }

    # Green dot next to 林 avatar — check around (78, 632)
    out["lin_green_dot"]=find_color_bbox(img, is_green_dot, 60, 625, 95, 655)
    out["chen_green_dot"]=find_color_bbox(img, is_green_dot, 60, 685, 95, 700)

    # Red badge "1" for 新朋友 — find at x ~ 340-385, y ~ 200-235
    out["new_friend_red_badge"]=find_color_bbox(img, is_red_badge, 320, 200, 380, 240)

    # Bottom nav 联系人 selected blue
    out["tab_contacts_y680_blue"]=is_qq_blue(px(img,247,680), 60)
    out["tab_contacts_y650_blue"]=is_qq_blue(px(img,247,650), 60)
    pts=[x for x in range(0,900) if is_qq_blue(px(img,x,680),40)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["tab_blue_clusters_y680"]=clusters

    return out

# =============================================================
# Dynamics deep — for both images
# =============================================================
def dynamics_deep(label, is_mobile):
    img=load(label)
    W,H=img.size
    out={"file":label,"size":(W,H)}
    out["page_bg_samples"]={
        f"(200,28)": px(img,200,28),
        f"(200,400)": px(img,200,400),
        f"(W-100,400)": px(img,W-100,400),
    }

    # 我 avatar — search broadly top-right
    out["my_avatar_search"]=find_color_bbox(img,lambda c:is_qq_blue(c,30), W-90, 5, W-5, 80)

    # Camera icon
    out["camera_icon"]=find_color_bbox(img, lambda c: is_dark_text(c), W-200, 20, W-90, 70)

    # Search pill
    sb=find_color_bbox(img,lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255 and abs(c[0]-c[1])<8, 10, 80, W-20, 130)
    out["search_pill_bbox"]=sb

    # 沈亦舟 avatar — sample at multiple points to find true color
    samples=[]
    for dx in [-20,-10,0,10,20]:
        for dy in [-20,-10,0,10,20]:
            samples.append((dx,dy,px(img,45+dx,185+dy)))
    out["shen_avatar_samples"]=samples[:15]  # truncate
    out["shen_avatar_dom"]=sample_avatar_at(img, 47, 185)
    out["shen_avatar_classified"]=classify(sample_avatar_at(img, 47, 185))

    # 9-grid tiles — verify each tile has real image (not solid bg)
    if is_mobile:
        xs=[75,175,275]; ys=[325,425,525]
    else:
        xs=[90,200,310]; ys=[320,430,540]
    tiles=[]
    for r,ty in enumerate(ys):
        for c,tx in enumerate(xs):
            # Sample 5x5 around center
            samp=[px(img,tx+dx,ty+dy) for dx in [-15,0,15] for dy in [-15,0,15]]
            avg_l=sum(br(s) for s in samp)/len(samp)
            # Variance check (not solid)
            vars_=sum((br(s)-avg_l)**2 for s in samp)/len(samp)
            tiles.append({"r":r,"c":c,"center_rgb":px(img,tx,ty),
                          "avg_luma":round(avg_l,1),"variance":round(vars_,1),
                          "is_image": vars_>50})  # real image has variance
    out["nine_grid_tiles"]=tiles
    out["nine_grid_image_count"]=sum(1 for t in tiles if t["is_image"])

    # Card 1 white bbox
    out["card1_white_bbox"]=find_color_bbox(img, lambda c: br(c)>=250, 0, 140, W-5, 690)

    # Like/Comment/Share counts
    if is_mobile:
        like_x=(95,130); cm_x=(195,225); sh_x=(290,320)
    else:
        like_x=(95,145); cm_x=(200,250); sh_x=(315,360)
    out["like_count_text_px"]=sum(1 for y in range(655,680) for x in range(*like_x)
                                    if is_dark_text(px(img,x,y)))
    out["comment_count_text_px"]=sum(1 for y in range(655,680) for x in range(*cm_x)
                                      if is_dark_text(px(img,x,y)))
    out["share_count_text_px"]=sum(1 for y in range(655,680) for x in range(*sh_x)
                                    if is_dark_text(px(img,x,y)))

    # Bottom nav 动态 selected blue + red dot
    if is_mobile:
        tab_x=343; tab_y_label=825; tab_y_icon=805
        rd_x=(340,388); rd_y=(770,810)
    else:
        tab_x=348; tab_y_label=680; tab_y_icon=650
        rd_x=(340,395); rd_y=(630,670)
    out["tab_dynamics_label_blue"]=is_qq_blue(px(img,tab_x,tab_y_label),60)
    out["tab_dynamics_label_sample"]=px(img,tab_x,tab_y_label)
    out["tab_dynamics_icon_sample"]=px(img,tab_x,tab_y_icon)

    out["dynamics_red_dot_bbox"]=find_color_bbox(img, is_red_badge, rd_x[0], rd_y[0], rd_x[1], rd_y[1])

    return out

# =============================================================
# Tablet mid deep
# =============================================================
def tablet_mid_deep():
    img=load("tablet-mid.jpg")
    out={}
    out["full_avg_luma"]=round(sum(br(px(img,x,y)) for y in range(0,700,4) for x in range(0,900,4))/175000, 1)
    # Left pane bg
    out["left_pane_luma_at_(250,400)"]=br(px(img,250,400))
    out["right_pane_luma_at_(600,400)"]=br(px(img,600,400))
    # Pane divider
    out["pane_divider_samples"]={x:px(img,x,400) for x in [418,420,422,425,430,435]}

    # Right pane top bar — avatar 林 at left, then name+status, then icons right
    # Avatar bbox search
    out["chat_top_avatar"]=find_color_bbox(img,lambda c:is_qq_blue(c,30), 440, 5, 510, 70)
    out["chat_top_avatar_dom"]=sample_avatar_at(img, 475, 35)
    out["chat_top_avatar_classified"]=classify(sample_avatar_at(img, 475, 35))

    # Name "林晚晴" + status — text count
    out["chat_name_text_px"]=sum(1 for y in range(15,50) for x in range(515,620)
                                  if is_dark_text(px(img,x,y)))
    out["chat_status_text_px"]=sum(1 for y in range(50,75) for x in range(515,720)
                                    if is_mid_gray(px(img,x,y)))

    # Green dot next to chat name
    out["chat_name_green_dot"]=find_color_bbox(img, is_green_dot, 520, 55, 560, 80)

    # Top-right icons (phone, video, more)
    right_dark=set()
    for x in range(700, 890):
        for y in range(15, 55):
            if is_dark_text(px(img,x,y)): right_dark.add(x)
    right_dark=sorted(right_dark)
    clusters=[]
    if right_dark:
        cur=[right_dark[0]]
        for v in right_dark[1:]:
            if v-cur[-1]<=5: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["chat_top_right_icon_clusters"]=clusters
    out["chat_top_right_icon_count"]=len(clusters)

    # Outbound bubbles in right pane
    out["outbound_bubble_bbox"]=find_color_bbox(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200, 440, 60, 890, 600)
    # Sample multiple bubble positions
    out["outbound_bubble_samples"]={
        "bubble1_(650,100)": px(img,650,100),
        "bubble2_(700,160)": px(img,700,160),
        "bubble3_(720,470)": px(img,720,470),
        "bubble4_(700,560)": px(img,700,560),
    }

    # "已读" text in right pane — count blue text glyphs
    blue_text=[]
    for y in range(60, 700):
        for x in range(440, 890):
            r=px(img,x,y)
            if is_qq_blue(r, 30) and br(r) < 220:
                blue_text.append((x,y))
    out["blue_text_pixel_count"]=len(blue_text)
    if blue_text:
        xs=[p[0] for p in blue_text]; ys=[p[1] for p in blue_text]
        out["blue_text_bbox"]=(min(xs),min(ys),max(xs),max(ys))
    # Y bands of blue text
    y_bands=set(p[1] for p in blue_text)
    out["blue_text_y_range"]=(min(y_bands),max(y_bands)) if y_bands else None

    # Composer
    out["composer_bg"]=px(img,600,660)
    out["composer_send_btn_rgb"]=px(img,850,660)
    out["composer_send_btn_blue"]=is_qq_blue(px(img,850,660),50)
    out["composer_input_field_bbox"]=find_color_bbox(img, lambda c: br(c)>=248, 440, 640, 870, 690)

    # Left pane — verify selected row 林晚晴
    # Row 1 should have light blue tint and left blue border
    out["left_pane_row1_bg_at_x200_y220"]=px(img,200,220)
    out["left_pane_row1_left_border_at_x4_y220"]=px(img,4,220)
    out["left_pane_row1_left_border_blue"]=is_qq_blue(px(img,4,220),50)
    # Check if selected tint is present
    out["left_pane_row1_tint_check"]=[px(img,x,220) for x in [50,100,150,200,250,300,350,400]]

    # Bottom nav 消息 selected blue
    out["left_pane_tab_message_label_blue"]=is_qq_blue(px(img,74,680),60)
    out["left_pane_tab_message_icon_sample"]=px(img,74,650)

    # Mask residue check (no dark overlay)
    out["mask_check_left_pane_top"]=px(img,200,200)
    out["mask_check_left_pane_bot"]=px(img,200,600)
    out["mask_check_right_pane_top"]=px(img,600,200)
    out["mask_check_right_pane_bot"]=px(img,600,600)

    return out

# =============================================================
# Group chat regression deep
# =============================================================
def group_chat_deep():
    img=load("group-chat.jpg")
    out={}
    out["full_avg_luma"]=round(sum(br(px(img,x,y)) for y in range(0,844,4) for x in range(0,390,4))/20895, 1)

    # Top bar
    out["back_arrow_bbox"]=find_color_bbox(img, lambda c: is_dark_text(c), 5, 20, 50, 70)
    out["back_arrow_sample"]=px(img, 22, 50)

    # Top avatar — "产" on white circle
    out["top_avatar_bbox"]=find_color_bbox(img, lambda c: 230<=br(c)<=255 and abs(c[0]-c[1])>10, 50, 15, 110, 70)
    out["top_avatar_sample"]=px(img, 80, 40)

    # "产品讨论组" + "128 人" text
    out["title_text_px"]=sum(1 for y in range(20,55) for x in range(115,260)
                              if is_dark_text(px(img,x,y)))
    out["subtitle_text_px"]=sum(1 for y in range(50,80) for x in range(115,260)
                                 if is_mid_gray(px(img,x,y)))

    # More icon top right
    out["more_icon_bbox"]=find_color_bbox(img, lambda c: is_dark_text(c), 340, 20, 390, 70)

    # Inbound white bubble bg
    out["inbound_bubble_white_at_(200,200)"]=br(px(img,200,200))>=248
    out["inbound_bubble_white_at_(230,300)"]=br(px(img,230,300))>=248

    # Outbound blue bubble bbox
    out["outbound_blue_bbox"]=find_color_bbox(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200, 150, 100, 390, 800)

    # Self avatar orange (right side, beside bubble)
    out["self_avatar_samples"]=[px(img,x,y) for x,y in [(370,385),(365,415),(370,520),(365,580),(370,640)]]
    out["self_avatar_orange_count"]=sum(1 for s in out["self_avatar_samples"] if is_orange_avatar(s))

    # Inbound avatars (left, smaller)
    out["inbound_avatar_orange_count"]=sum(1 for y in range(200,800,50) for x in range(5,45)
                                            if is_orange_avatar(px(img,x,y)))

    # "已读" blue text — count and bbox
    blue_text=[]
    for y in range(150, 800):
        for x in range(220, 390):
            r=px(img,x,y)
            if is_qq_blue(r,30) and br(r)<220:
                blue_text.append((x,y))
    out["blue_read_text_count"]=len(blue_text)
    if blue_text:
        xs=[p[0] for p in blue_text]; ys=[p[1] for p in blue_text]
        out["blue_read_text_bbox"]=(min(xs),min(ys),max(xs),max(ys))

    # Composer
    out["composer_bg"]=px(img,200,808)
    out["composer_emoji_at_(22,808)"]=px(img,22,808)
    out["composer_send_btn_rgb"]=px(img,358,808)
    out["composer_send_btn_blue"]=is_qq_blue(px(img,358,808),50)

    # Mask residue check
    out["mask_check_top_bg_at_(195,90)"]=px(img,195,90)
    out["mask_check_mid_bg_at_(195,500)"]=px(img,195,500)
    out["mask_check_btm_bg_at_(195,790)"]=px(img,195,790)

    return out

# =============================================================
if __name__=="__main__":
    r={
        "mobile_deep": mobile_deep(),
        "channels_deep": channels_deep(),
        "contacts_deep": contacts_deep(),
        "dynamics_tablet_deep": dynamics_deep("dynamics-tab.jpg", False),
        "dynamics_mobile_deep": dynamics_deep("dynamics-tab-mobile.jpg", True),
        "tablet_mid_deep": tablet_mid_deep(),
        "group_chat_deep": group_chat_deep(),
    }
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))