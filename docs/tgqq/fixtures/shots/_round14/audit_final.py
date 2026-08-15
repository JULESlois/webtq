#!/usr/bin/env python3
"""
Round-14 final audit based on CURRENT file content (post 03:38 regeneration).
PIL is ground truth — Read tool cache is stale.
"""
from PIL import Image
import os, json
from collections import Counter

SHOTS="/data/data/com.termux/files/home/tg-web/tweb/docs/tgqq/fixtures/shots"
def load(n): return Image.open(os.path.join(SHOTS,n)).convert("RGB")
def px(img,x,y): return img.getpixel((int(x),int(y)))
def br(rgb): return 0.299*rgb[0]+0.587*rgb[1]+0.114*rgb[2]

def is_qq_blue(rgb,tol=40):
    r,g,b=rgb; return abs(r-18)<=tol and abs(g-150)<=tol and abs(b-219)<=tol
def is_blueish(rgb):
    r,g,b=rgb; return b>=200 and b>r+10 and r<240
def is_green_dot(rgb):
    r,g,b=rgb
    return g>=140 and g>r+30 and g>b+20 and r<200
def is_red_badge(rgb):
    r,g,b=rgb
    return r>=200 and g<130 and b<130 and r>g+70 and r>b+70
def is_orange(rgb):
    r,g,b=rgb; return r>=220 and 100<=g<=185 and 30<=b<=110 and r>g>b
def is_purple(rgb):
    r,g,b=rgb; return 130<=r<=210 and 60<=g<=140 and 150<=b<=225 and b>r>g
def is_pink(rgb):
    r,g,b=rgb; return r>=200 and g<130 and 100<=b<=180 and r>g and b>g
def is_teal(rgb):
    r,g,b=rgb; return r<130 and g>150 and b>170 and b>=r
def is_gray(rgb):
    r,g,b=rgb; return abs(r-g)<25 and abs(g-b)<25 and 50<=r<=180
def is_dark(rgb): return br(rgb)<=130
def is_midgray(rgb): b=br(rgb); return 130<b<=200

def find_bbox(img, pred, x0,y0,x1,y1):
    pts=[]
    for y in range(y0,y1):
        for x in range(x0,x1):
            if pred(px(img,x,y)): pts.append((x,y))
    if not pts: return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return {"n":len(pts),"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
            "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
            "cx":(min(xs)+max(xs))//2,"cy":(min(ys)+max(ys))//2}

def sample_avatar(img, x, y, dx_list=(-18,-12,-6,0,6,12,18)):
    """Get dominant colored pixel in a small ring around (x,y) to skip text."""
    samps=[]
    for dx in dx_list:
        for dy in (-15,-8,0,8,15):
            try: samps.append(px(img,x+dx,y+dy))
            except: pass
    fil=[s for s in samps if 30<br(s)<=235]
    if not fil: return None
    return tuple(sum(s[i] for s in fil)//len(fil) for i in range(3))

def classify(rgb):
    if rgb is None: return "?"
    if is_orange(rgb): return "orange"
    if is_purple(rgb): return "purple"
    if is_pink(rgb): return "pink"
    if is_teal(rgb): return "teal"
    if is_gray(rgb): return "gray"
    if is_qq_blue(rgb,50): return "qq_blue"
    if is_blueish(rgb): return "blueish"
    if is_green_dot(rgb): return "green"
    return "other(%d,%d,%d)"%rgb

# =============================================================
# 1. mobile.jpg (390x844) — current truth
# =============================================================
def mobile():
    img=load("mobile.jpg"); W,H=img.size
    out={"file":"mobile.jpg","size":[W,H]}

    # Page bg — sample 9 points
    out["page_bg"]=[px(img,x,y) for x,y in [(20,28),(195,28),(370,28),
                                              (20,170),(195,170),(370,170),
                                              (20,500),(195,500),(370,500)]]

    # 我 avatar — bbox of blue in top-left
    out["my_avatar_bbox"]=find_bbox(img, lambda c: is_qq_blue(c,35), 5, 5, 80, 80)
    # Green dot — anywhere in header y=60-90
    out["green_dot_bbox"]=find_bbox(img, is_green_dot, 0, 60, 200, 90)

    # Search pill — light blue bg in y=100-170
    out["search_pill_bbox"]=find_bbox(img, lambda c: 220<=c[2]<=255 and 220<=c[0]<=250 and 230<=c[1]<=252,
                                       0, 100, W, 170)
    out["search_pill_sample"]=px(img,200,135)

    # Selected row "林晚晴" — find by light blue tint at y=180-235
    sel_y=[]
    for y in range(180,240):
        c=px(img,200,y)
        if 220<=c[2]<=252 and 220<=c[0]<=252 and c[2]>c[0]:
            sel_y.append((y,c))
    out["selected_row_y_samples"]=sel_y[:5]+sel_y[-5:] if sel_y else []
    # Selected left blue border — narrow strip at x=0-10
    out["selected_left_border"]=find_bbox(img, lambda c: is_qq_blue(c,30), 0, 180, 12, 240)

    # Avatar colors per row — use y centers from visual (190,275,355,435,515,595,675,755,830)
    rows=[("林晚晴",190),("陈默",275),("产品讨论组",355),("周子昂",435),
          ("前端交流群",515),("苏小满",595),("沈亦舟",675),("郑一鸣",755),("唐雪",830)]
    out["row_avatars"]=[]
    for name,cy in rows:
        dom_rgb=sample_avatar(img, 47, cy)
        out["row_avatars"].append({"name":name,"y":cy,"rgb":dom_rgb,"class":classify(dom_rgb)})

    # Unread red badges — cluster on right (x>=320)
    rpts=[]
    for y in range(180,790):
        for x in range(320,W):
            if is_red_badge(px(img,x,y)): rpts.append((x,y))
    if rpts:
        rpts.sort()
        clusters=[]; cur=[rpts[0]]
        for p in rpts[1:]:
            if abs(p[0]-cur[-1][0])<=8 and abs(p[1]-cur[-1][1])<=8: cur.append(p)
            else: clusters.append(cur); cur=[p]
        clusters.append(cur)
        out["red_badge_clusters"]=[{"bbox":(min(p[0] for p in c),min(p[1] for p in c),
                                       max(p[0] for p in c),max(p[1] for p in c)),
                                    "n":len(c)} for c in clusters if len(c)>=4]
    else:
        out["red_badge_clusters"]=[]

    # Bottom tab selected — scan y=830 for blue
    pts=[x for x in range(W) if is_qq_blue(px(img,x,830),35)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["tab_label_blue_y830"]=clusters

    # Dynamics red dot above 动态
    out["dynamics_red_dot"]=find_bbox(img, is_red_badge, 340, 770, 388, 810)

    # Header mid-gray text (手机在线 WiFi)
    out["header_midgray_px"]=sum(1 for y in range(60,90) for x in range(70,280)
                                  if is_midgray(px(img,x,y)))

    return out

# =============================================================
# 2. channels-tab.jpg (900x700) — current truth
# =============================================================
def channels():
    img=load("channels-tab.jpg"); W,H=img.size
    out={"file":"channels-tab.jpg","size":[W,H]}

    # Content distribution — right half non-white pixel count
    rnw=sum(1 for y in range(0,H,3) for x in range(W//2,W,3)
            if not (240<=img.getpixel((x,y))[0]<=255 and 240<=img.getpixel((x,y))[1]<=255))
    lnw=sum(1 for y in range(0,H,3) for x in range(0,W//2,3)
            if not (240<=img.getpixel((x,y))[0]<=255 and 240<=img.getpixel((x,y))[1]<=255))
    out["content_distribution"]={"left_non_white":lnw, "right_non_white":rnw,
                                  "right_blank": rnw<100}

    # 我 avatar top-right — should be in x>700
    out["my_avatar_bbox"]=find_bbox(img, lambda c: is_qq_blue(c,30), 700, 5, W, 80)

    # Search pill
    out["search_pill_bbox"]=find_bbox(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255,
                                       0, 85, W, 130)

    # 3 recommend cards — red/blue/purple
    out["card_red_bbox"]=find_bbox(img, lambda c: c[0]>=200 and c[1]<130 and c[2]<140, 0, 165, W, 270)
    out["card_blue_bbox"]=find_bbox(img, lambda c: c[2]>=180 and c[2]>c[0]+20 and br(c)<220, 0, 165, W, 270)
    out["card_purple_bbox"]=find_bbox(img, lambda c: 130<=c[0]<=210 and 60<=c[1]<=140 and 150<=c[2]<=225, 0, 165, W, 270)

    # 行业频道 rows
    for name,cy in [("科技资讯",425),("财经观察",490),("职场成长",555)]:
        out[f"{name}_avatar"]={"y":cy,"rgb":sample_avatar(img,47,cy),
                               "class":classify(sample_avatar(img,47,cy))}

    # "+关注" buttons — search anywhere x>=350
    blue_outline=sum(1 for y in range(380,610) for x in range(350,W)
                      if is_qq_blue(px(img,x,y), 50))
    out["follow_button_blue_outline_px"]=blue_outline

    # Bottom nav — 频道 selected blue
    pts=[x for x in range(W) if is_qq_blue(px(img,x,680),35)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["tab_blue_clusters_y680"]=clusters

    out["dynamics_red_dot"]=find_bbox(img, is_red_badge, 340, 630, W, 670)

    return out

# =============================================================
# 3. contacts-tab.jpg (900x700) — current truth
# =============================================================
def contacts():
    img=load("contacts-tab.jpg"); W,H=img.size
    out={"file":"contacts-tab.jpg","size":[W,H]}

    rnw=sum(1 for y in range(0,H,3) for x in range(W//2,W,3)
            if not (240<=img.getpixel((x,y))[0]<=255 and 240<=img.getpixel((x,y))[1]<=255))
    out["content_distribution"]={"right_non_white":rnw, "right_blank":rnw<100}

    # 我 avatar top-right
    out["my_avatar_bbox"]=find_bbox(img, lambda c: is_qq_blue(c,30), 700, 5, W, 80)

    # A-Z letter index — check at x=478-510 (where letters were in cached view)
    az_y_count=sum(1 for y in range(170,600) for x in range(478,510)
                   if is_midgray(px(img,x,y)))
    out["az_letter_midgray_px"]=az_y_count

    # Search pill
    out["search_pill_bbox"]=find_bbox(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255,
                                       0, 85, W, 130)

    # Row avatars at proper y centers
    for name,cy in [("新朋友",220),("产品讨论组",343),("前端交流群",413),
                     ("周末爬山小队",483),("林晚晴",615),("陈默",678)]:
        out[f"{name}_avatar"]={"y":cy,"rgb":sample_avatar(img,47,cy),
                                "class":classify(sample_avatar(img,47,cy))}

    # Green dots on 林/陈
    out["lin_green_dot"]=find_bbox(img, is_green_dot, 60, 625, 95, 655)
    out["chen_green_dot"]=find_bbox(img, is_green_dot, 60, 690, 95, 700)

    # Red badge "1" for 新朋友
    out["new_friend_red_badge"]=find_bbox(img, is_red_badge, 320, 200, W, 240)

    # Bottom nav 联系人 selected blue
    pts=[x for x in range(W) if is_qq_blue(px(img,x,680),35)]
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
# 4. dynamics-tab.jpg + dynamics-tab-mobile.jpg
# =============================================================
def dynamics(label, is_mobile):
    img=load(label); W,H=img.size
    out={"file":label,"size":[W,H]}

    if not is_mobile:
        rnw=sum(1 for y in range(0,H,3) for x in range(W//2,W,3)
                if not (240<=img.getpixel((x,y))[0]<=255 and 240<=img.getpixel((x,y))[1]<=255))
        out["content_distribution"]={"right_non_white":rnw,"right_blank":rnw<100}

    # 我 avatar
    out["my_avatar_bbox"]=find_bbox(img, lambda c: is_qq_blue(c,30), W-90, 5, W-5, 80)
    # Camera icon
    out["camera_icon"]=find_bbox(img, lambda c: is_dark(c), W-200, 20, W-90, 70)
    # Search pill
    out["search_pill_bbox"]=find_bbox(img, lambda c: 235<=c[0]<=250 and 235<=c[1]<=250 and 235<=c[2]<=255,
                                       0, 85, W-5, 130)

    # 沈亦舟 avatar
    out["shen_avatar"]={"y":185,"rgb":sample_avatar(img,47,185),
                         "class":classify(sample_avatar(img,47,185))}

    # 9-grid tiles — sample center of each
    if is_mobile:
        xs=[75,175,275]; ys=[325,425,525]
    else:
        xs=[90,200,310]; ys=[320,430,540]
    tiles=[]
    for r,ty in enumerate(ys):
        for c,tx in enumerate(xs):
            samp=[px(img,tx+dx,ty+dy) for dx in (-12,0,12) for dy in (-12,0,12)]
            avg_l=sum(br(s) for s in samp)/len(samp)
            var=sum((br(s)-avg_l)**2 for s in samp)/len(samp)
            tiles.append({"r":r,"c":c,"avg_luma":round(avg_l,1),
                          "variance":round(var,1),"is_image":var>100})
    out["nine_grid"]=tiles
    out["nine_grid_image_count"]=sum(1 for t in tiles if t["is_image"])

    # Card 1 white bbox
    out["card1_bbox"]=find_bbox(img, lambda c: br(c)>=250, 0, 140, W-5, 690)

    # Like/comment/share text glyph counts
    if is_mobile:
        like_x=(95,130); cm_x=(195,225); sh_x=(290,320)
    else:
        like_x=(95,145); cm_x=(200,250); sh_x=(315,360)
    out["like_count_px"]=sum(1 for y in range(655,680) for x in range(*like_x) if is_dark(px(img,x,y)))
    out["comment_count_px"]=sum(1 for y in range(655,680) for x in range(*cm_x) if is_dark(px(img,x,y)))
    out["share_count_px"]=sum(1 for y in range(655,680) for x in range(*sh_x) if is_dark(px(img,x,y)))

    # Bottom nav 动态 selected blue
    if is_mobile:
        tab_y_lbl=825; rd_x0,rd_x1,rd_y0,rd_y1 = 340,388,770,810
    else:
        tab_y_lbl=680; rd_x0,rd_x1,rd_y0,rd_y1 = 340,395,630,670
    pts=[x for x in range(W) if is_qq_blue(px(img,x,tab_y_lbl),35)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["tab_blue_clusters"]=clusters
    out["dynamics_red_dot"]=find_bbox(img, is_red_badge, rd_x0,rd_y0,rd_x1,rd_y1)

    return out

# =============================================================
# 5. tablet-mid.jpg (900x700) — left home + right chat
# =============================================================
def tablet_mid():
    img=load("tablet-mid.jpg"); W,H=img.size
    out={"file":"tablet-mid.jpg","size":[W,H]}

    # Pane divider — find column with darker shade
    div_x=None
    for x in range(415,430):
        col_l=sum(br(px(img,x,y)) for y in range(100,600,30))/20
        if 200<col_l<240:
            div_x=x; break
    out["pane_divider_x"]=div_x

    # Left pane content distribution
    l_samples=[br(px(img,200,y)) for y in range(200,600,30)]
    r_samples=[br(px(img,600,y)) for y in range(200,600,30)]
    out["left_pane_avg_luma"]=round(sum(l_samples)/len(l_samples),1)
    out["right_pane_avg_luma"]=round(sum(r_samples)/len(r_samples),1)

    # Right pane top bar — avatar 林
    out["chat_top_avatar_bbox"]=find_bbox(img, lambda c: is_qq_blue(c,30), 440, 5, 520, 70)
    out["chat_top_green_dot"]=find_bbox(img, is_green_dot, 510, 55, 560, 80)

    # Right side icons in top bar
    icons=set()
    for x in range(700,W):
        for y in range(15,55):
            if is_dark(px(img,x,y)): icons.add(x); break
    icons=sorted(icons)
    clusters=[]
    if icons:
        cur=[icons[0]]
        for v in icons[1:]:
            if v-cur[-1]<=5: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["chat_top_right_icon_clusters"]=clusters

    # Outbound bubble
    out["outbound_bubble_bbox"]=find_bbox(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200,
                                            440, 60, W, 600)

    # 已读 blue text
    blue_text=[]
    for y in range(60,700):
        for x in range(440,W):
            r=px(img,x,y)
            if is_qq_blue(r,30) and br(r)<220: blue_text.append((x,y))
    out["blue_text_count"]=len(blue_text)
    if blue_text:
        xs=[p[0] for p in blue_text]; ys=[p[1] for p in blue_text]
        out["blue_text_bbox"]=(min(xs),min(ys),max(xs),max(ys))

    # Composer
    out["composer_send_btn_rgb"]=px(img,850,660)
    out["composer_send_btn_blue"]=is_qq_blue(px(img,850,660),50)

    # Left pane row 1 selected bg + left border
    out["left_pane_row1_bg"]=px(img,200,220)
    out["left_pane_row1_left_border"]=px(img,4,220)
    out["left_pane_row1_left_border_blue"]=is_qq_blue(px(img,4,220),50)

    # Mask residue check (no dark overlay)
    out["full_avg_luma"]=round(sum(br(px(img,x,y)) for y in range(50,650,4) for x in range(0,W,4))
                                / (150*225), 1)

    # Left pane bottom nav 消息 selected blue
    pts=[x for x in range(W//2) if is_qq_blue(px(img,x,680),35)]
    clusters=[]
    if pts:
        cur=[pts[0]]
        for v in pts[1:]:
            if v-cur[-1]<=4: cur.append(v)
            else: clusters.append((cur[0],cur[-1])); cur=[v]
        clusters.append((cur[0],cur[-1]))
    out["left_tab_blue_clusters_y680"]=clusters

    return out

# =============================================================
# 6. group-chat.jpg (390x844) — regression
# =============================================================
def group_chat():
    img=load("group-chat.jpg"); W,H=img.size
    out={"file":"group-chat.jpg","size":[W,H]}

    out["full_avg_luma"]=round(sum(br(px(img,x,y)) for y in range(0,H,4) for x in range(0,W,4))
                                / ((H//4)*(W//4)), 1)

    # Top bar
    out["back_arrow_bbox"]=find_bbox(img, lambda c: is_dark(c), 5, 20, 50, 70)
    out["top_avatar_white"]=br(px(img,80,40))>=248
    out["more_icon_bbox"]=find_bbox(img, lambda c: is_dark(c), 340, 20, W, 70)

    # Inbound white bubble
    out["inbound_white_sample"]=px(img,200,200)
    # Outbound blue bubble
    out["outbound_blue_bbox"]=find_bbox(img, lambda c: c[2]>=210 and c[2]>c[0]+15 and c[0]<230 and br(c)>200,
                                          150, 100, W, 800)

    # Self avatar orange
    out["self_avatar_orange_count"]=sum(1 for y in range(200,800,40) for x in range(355,385)
                                         if is_orange(px(img,x,y)))

    # 已读
    blue_text=[]
    for y in range(150,800):
        for x in range(220,W):
            r=px(img,x,y)
            if is_qq_blue(r,30) and br(r)<220: blue_text.append((x,y))
    out["blue_read_text_count"]=len(blue_text)

    # Composer
    out["composer_send_btn_rgb"]=px(img,358,808)
    out["composer_send_btn_blue"]=is_qq_blue(px(img,358,808),50)

    # Mask residue check
    out["mask_check"]={k: px(img,*v) for k,v in [("top_bg",(195,90)),("mid_bg",(195,500)),("btm_bg",(195,790))]}

    return out

if __name__=="__main__":
    r={
        "mobile": mobile(),
        "channels": channels(),
        "contacts": contacts(),
        "dynamics_tablet": dynamics("dynamics-tab.jpg", False),
        "dynamics_mobile":  dynamics("dynamics-tab-mobile.jpg", True),
        "tablet_mid": tablet_mid(),
        "group_chat": group_chat(),
    }
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))