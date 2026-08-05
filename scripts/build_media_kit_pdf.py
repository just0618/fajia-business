from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = json.loads((ASSETS / "social-data.json").read_text(encoding="utf-8"))
OUT = ROOT / "downloads" / "fajia-business-media-kit-v0.26.pdf"
CACHE = ROOT / ".pdf-cache"
CACHE.mkdir(exist_ok=True)
OUT.parent.mkdir(exist_ok=True)

W, H = 960, 540  # 16:9, PPT-like landscape page in points
PINK = HexColor("#FF8AA1")
PINK_DARK = HexColor("#D85F7A")
GOLD = HexColor("#FFE25B")
CREAM = HexColor("#FFF9F5")
PAPER = HexColor("#FFFDFC")
INK = HexColor("#1F1815")
MUTED = HexColor("#806B61")
LINE = HexColor("#E8DAD5")
SOFT_PINK = HexColor("#FFF0F2")
SOFT_GOLD = HexColor("#FFF8D7")
DARK = HexColor("#2B201A")
BLUE = HexColor("#4B76A8")

# Local fonts only; they are embedded in the PDF and never distributed separately.
pdfmetrics.registerFont(TTFont("CN", "/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf"))
pdfmetrics.registerFont(TTFont("CNDisplay", "/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf"))


def fmt(n: int | float | None) -> str:
    if n is None:
        return "—"
    n = float(n)
    if n >= 10000:
        v = n / 10000
        return f"{v:.1f}万" if abs(v - round(v)) > 0.05 else f"{int(round(v))}万"
    return f"{int(n):,}"


def color_lerp(a: Color, b: Color, t: float) -> Color:
    return Color(a.red + (b.red-a.red)*t, a.green + (b.green-a.green)*t, a.blue + (b.blue-a.blue)*t)


def gradient(c: canvas.Canvas, a: Color, b: Color, vertical=False):
    steps = 60
    for i in range(steps):
        t = i/(steps-1)
        col = color_lerp(a,b,t)
        c.setFillColor(col)
        if vertical:
            c.rect(0, H*i/steps, W, H/steps+1, fill=1, stroke=0)
        else:
            c.rect(W*i/steps, 0, W/steps+1, H, fill=1, stroke=0)


def rounded_box(c, x, y, w, h, fill=PAPER, stroke=LINE, radius=12, lw=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def optimize_image(path: Path, max_px=1500, quality=84) -> Path:
    key = path.name.replace('.', '_') + f"_{max_px}_{quality}.jpg"
    out = CACHE / key
    if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
        return out
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)
    im.save(out, "JPEG", quality=quality, optimize=True)
    return out


def draw_img(c, path: str | Path, x, y, w, h, mode="cover", radius=0, bg=CREAM):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    p = optimize_image(p)
    im = Image.open(p)
    iw, ih = im.size
    if mode == "contain":
        s = min(w/iw, h/ih)
    else:
        s = max(w/iw, h/ih)
    dw, dh = iw*s, ih*s
    dx, dy = x+(w-dw)/2, y+(h-dh)/2
    c.saveState()
    if radius:
        pth = c.beginPath()
        pth.roundRect(x, y, w, h, radius)
        c.clipPath(pth, stroke=0, fill=0)
    c.setFillColor(bg)
    c.rect(x,y,w,h,fill=1,stroke=0)
    c.drawImage(ImageReader(p), dx, dy, dw, dh, mask='auto')
    c.restoreState()


def text_width(txt, font, size):
    return pdfmetrics.stringWidth(txt, font, size)


def wrap_text(txt: str, font: str, size: float, max_w: float) -> list[str]:
    lines=[]
    for para in txt.split("\n"):
        if para == "":
            lines.append("")
            continue
        line=""
        for ch in para:
            test=line+ch
            if line and text_width(test,font,size)>max_w:
                lines.append(line)
                line=ch
            else:
                line=test
        if line:
            lines.append(line)
    return lines


def draw_text(c, txt, x, y, max_w, font="CN", size=16, color=INK, leading=None, max_lines=None, align="left"):
    leading = leading or size*1.55
    lines = wrap_text(txt,font,size,max_w)
    if max_lines:
        lines=lines[:max_lines]
    c.setFont(font,size)
    c.setFillColor(color)
    yy=y
    for line in lines:
        if align=="center":
            xx=x+(max_w-text_width(line,font,size))/2
        elif align=="right":
            xx=x+max_w-text_width(line,font,size)
        else:
            xx=x
        c.drawString(xx,yy,line)
        yy-=leading
    return yy


def eyebrow(c, txt, x, y, color=PINK_DARK, size=10, tracking=2.0):
    c.setFillColor(color)
    c.setFont("Helvetica",size)
    xx=x
    for ch in txt.upper():
        c.drawString(xx,y,ch)
        xx += text_width(ch,"Helvetica",size)+tracking


def title(c, cn, en, x=48, y=485, cn_size=40):
    eyebrow(c,en,x,y)
    c.setFillColor(INK)
    c.setFont("CNDisplay",cn_size)
    c.drawString(x,y-54,cn)


def footer(c, page_num):
    c.setStrokeColor(Color(PINK.red,PINK.green,PINK.blue,alpha=.45))
    c.setLineWidth(2)
    c.line(0,3,W*.25,3)
    c.setStrokeColor(Color(GOLD.red,GOLD.green,GOLD.blue,alpha=.7))
    c.line(W*.25,3,W,3)
    c.setFont("Helvetica",8)
    c.setFillColor(MUTED)
    c.drawRightString(W-24,18,f"FAJIA · 2026 · {page_num:02d}")


def hyperlink(c, url, x,y,w,h):
    c.linkURL(url,(x,y,x+w,y+h),relative=0,thickness=0)


def metric_box(c, x,y,w,h,value,label,note=""):
    rounded_box(c,x,y,w,h,fill=PAPER,stroke=LINE,radius=8)
    c.setFont("Times-Bold",28)
    c.setFillColor(INK)
    c.drawString(x+18,y+h-42,value)
    c.setFont("CN",11)
    c.setFillColor(INK)
    c.drawString(x+18,y+h-68,label)
    if note:
        c.setFont("CN",8.5); c.setFillColor(MUTED); c.drawString(x+18,y+16,note)


def profile_card(c,x,y,w,h,img,name,en,tags,facts):
    rounded_box(c,x,y,w,h,fill=PAPER,stroke=LINE,radius=10)
    iw=w*.43
    draw_img(c,img,x,y,iw,h,"cover",radius=10)
    tx=x+iw+22
    eyebrow(c,en,tx,y+h-35,size=8,tracking=1.6)
    c.setFillColor(INK); c.setFont("CNDisplay",25); c.drawString(tx,y+h-75,name)
    draw_text(c,tags,tx,y+h-104,w-iw-40,font="CN",size=10.5,color=INK,leading=16,max_lines=2)
    yy=y+h-148
    for k,v in facts:
        c.setFont("CN",8.5); c.setFillColor(MUTED); c.drawString(tx,yy,k)
        draw_text(c,v,tx+58,yy,w-iw-96,font="CN",size=9.5,color=INK,leading=14,max_lines=2)
        yy-=30 if len(v)>16 else 22


def work_card(c,x,y,w,h,img,kind,name,desc,url):
    rounded_box(c,x,y,w,h,fill=PAPER,stroke=LINE,radius=8)
    draw_img(c,img,x,y,w*.36,h,"cover",radius=8)
    tx=x+w*.36+18
    c.setFont("CN",9); c.setFillColor(PINK_DARK); c.drawString(tx,y+h-28,kind)
    c.setFont("CNDisplay",20); c.setFillColor(INK); c.drawString(tx,y+h-58,name)
    draw_text(c,desc,tx,y+h-88,w*.58-22,font="CN",size=9.6,color=MUTED,leading=16,max_lines=4)
    c.setFont("CN",9.5); c.setFillColor(PINK_DARK); c.drawString(tx,y+18,"打开作品 ↗")
    hyperlink(c,url,x,y,w,h)


def platform_profile(c,x,y,w,h,img,name,followers,engagement=None,url=None):
    rounded_box(c,x,y,w,h,fill=PAPER,stroke=LINE,radius=8)
    draw_img(c,img,x+w/2-30,y+h-74,60,60,"cover",radius=30)
    c.setFont("CN",12); c.setFillColor(INK); c.drawCentredString(x+w/2,y+h-92,name)
    c.setStrokeColor(LINE); c.line(x+16,y+52,x+w-16,y+52)
    c.setFont("Times-Bold",17); c.drawCentredString(x+w*.28,y+29,fmt(followers))
    c.setFont("CN",7.5); c.setFillColor(MUTED); c.drawCentredString(x+w*.28,y+14,"粉丝")
    if engagement is not None:
        c.setFillColor(INK); c.setFont("Times-Bold",17); c.drawCentredString(x+w*.72,y+29,fmt(engagement))
        c.setFont("CN",7.5); c.setFillColor(MUTED); c.drawCentredString(x+w*.72,y+14,"互动")
    if url: hyperlink(c,url,x,y,w,h)


def content_card(c,x,y,w,h,poster,title_text,metrics,url,landscape=False):
    rounded_box(c,x,y,w,h,fill=PAPER,stroke=LINE,radius=8)
    image_h=h*.63
    draw_img(c,poster,x,y+h-image_h,w,image_h,"cover",radius=8)
    c.setFillColor(INK); c.setFont("CN",14); c.drawString(x+16,y+h-image_h-28,title_text)
    yy=y+34
    c.setStrokeColor(LINE); c.line(x+14,yy+30,x+w-14,yy+30)
    c.setFont("CN",9.3); c.setFillColor(PINK_DARK)
    parts=[]
    if "likes" in metrics: parts.append(f"♥ {fmt(metrics.get('likes'))}")
    if "comments" in metrics: parts.append(f"◯ {fmt(metrics.get('comments'))}")
    if "favorites" in metrics: parts.append(f"☆ {fmt(metrics.get('favorites'))}")
    if "shares" in metrics: parts.append(f"↗ {fmt(metrics.get('shares'))}")
    if "reposts" in metrics: parts.append(f"↗ {fmt(metrics.get('reposts'))}")
    c.drawString(x+16,yy,"   ".join(parts))
    hyperlink(c,url,x,y,w,h)


def new_page(c, n, bg=PAPER):
    c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)
    footer(c,n)


def build():
    c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
    c.setTitle("法嘉致富｜星遇企划档案｜品牌合作参考")
    c.setAuthor("FAJIA")
    page=1

    # 1 cover
    gradient(c, SOFT_PINK, PAPER)
    draw_img(c,"assets/hero-v2.webp",520,0,440,H,"cover")
    c.setFillColor(PAPER); c.rect(0,0,520,H,fill=1,stroke=0)
    eyebrow(c,"DUO ARTISTS · BRAND COOPERATION REFERENCE",52,430,size=9,tracking=1.7)
    c.setFont("CNDisplay",49); c.setFillColor(INK); c.drawString(52,350,"法嘉致富")
    c.setFont("CNDisplay",26); c.drawString(52,305,"｜星遇企划档案")
    draw_text(c,"不要轻视每一次遇见的威力。",52,240,390,font="CN",size=15,color=INK,leading=24)
    c.setFont("CN",10); c.setFillColor(MUTED); c.drawRightString(440,210,"——法宣阁")
    draw_text(c,"无论你在追逐什么，都请记得停下来抬头看看，\n“天上有颗最亮的星星”它因为你而存在。",52,165,390,font="CN",size=12,color=INK,leading=22)
    c.setFont("CN",10); c.setFillColor(MUTED); c.drawRightString(440,86,"——贺嘉述")
    footer(c,page); c.showPage(); page+=1

    # 2 overview
    new_page(c,page)
    title(c,"法嘉致富","ABOUT THE DUO · FAJIA")
    platforms=DATA["platforms"]
    artist_followers=sum(platforms[p][a]["followers"] for p in ("douyin","weibo","xhs") for a in ("faxuange","hejiashu"))
    dy_likes=sum(platforms["douyin"][a]["engagement"] for a in ("faxuange","hejiashu"))
    for i,(v,l,note) in enumerate([
        (fmt(artist_followers)+"+","三平台公开账号粉丝合计","跨平台未去重"),
        (fmt(dy_likes),"两位艺人抖音累计获赞","公开主页口径"),
        ("115万+","代表性抖音共创内容获赞","多条突破10万点赞"),
        ("2项","已公开双人品牌合作身份","阿芙 · 方里"),
    ]): metric_box(c,48+i*218,330,200,102,v,l,note)
    draw_text(c,"法嘉致富，取自法宣阁、贺嘉述名字中的“法”与“嘉”二字，搭配“致富”寓意二人相伴顺遂、前程向好。\n\n两人因共同出演《双程》副 CP 而受到广泛关注，粉丝名为小发夹，应援色为粉金色。\n\n沉稳细腻与灵动表达形成鲜明互补，展现出自然互动、双向托底和强烈的关系叙事能力。",48,285,390,font="CN",size=11.2,color=INK,leading=20,max_lines=10)
    draw_img(c,"assets/double-helix-official-duo.webp",470,52,290,255,"cover",radius=8)
    draw_img(c,"assets/double-helix-faxuange.jpg",770,181,138,126,"cover",radius=6)
    draw_img(c,"assets/double-helix-hejiashu.jpg",770,52,138,126,"cover",radius=6)
    c.showPage(); page+=1

    # 3 profiles
    new_page(c,page)
    title(c,"个人信息","INDIVIDUAL PROFILES")
    profile_card(c,36,55,430,350,"assets/faxuange.webp","法宣阁","FAXUANGE","沉稳控场｜细腻表达｜可靠陪伴｜反差少年感",[
        ("生日","1998.07.23 · 狮子座"),("MBTI","ISFJ · 动物塑：大金毛"),("毕业院校","上海师范大学表演系"),("影视作品","《双程》饰秦朗；《这次换我先回头》饰江一霖"),("音乐作品","《小英雄》《让我带你逃跑》")])
    profile_card(c,494,55,430,350,"assets/hejiashu-jan.jpg","贺嘉述","HEJIASHU","灵动表达｜快速反应｜镜头表现力｜年轻时尚感",[
        ("生日","2004.10.10 · 天秤座"),("MBTI","ENFP · 动物塑：小老虎"),("毕业院校","浙江工业大学播音与主持艺术专业"),("影视作品","《双程》饰程亦晨"),("音乐作品","《小英雄》《暴走大象》")])
    c.showPage(); page+=1

    # 4 works
    new_page(c,page)
    title(c,"代表作品","REPRESENTATIVE WORKS")
    work_card(c,42,250,430,160,"assets/double-helix-duo.jpg","影视作品","《双程》","法宣阁饰秦朗，贺嘉述饰程亦晨。两人共同出演的核心影视作品。","https://www.youtube.com/shorts/Z7Ka3U8mtl0")
    work_card(c,488,250,430,160,"assets/song-little-hero.webp","双人音乐","《小英雄》","以勇敢为浪漫，以陪伴为铠甲，默默守候在身后，成为对方专属的小小宇宙。","https://i.y.qq.com/v8/playsong.html?songid=663897655")
    work_card(c,42,66,430,160,"assets/song-escape.webp","个人音乐 · 法宣阁","《让我带你逃跑》","漫天星光作伴，任凭风浪来袭，身边始终有温暖陪伴。","https://i2.y.qq.com/n3/other/pages/details/album.html?albumId=95243045")
    work_card(c,488,66,430,160,"assets/song-baozou.webp","个人音乐 · 贺嘉述","《暴走大象》","两颗心相遇的刹那，宇宙间一切的规则都骤然失序。","https://i.y.qq.com/v8/playsong.html?songid=688913973")
    c.showPage(); page+=1

    # 5 social douyin
    new_page(c,page)
    title(c,"官方账号｜抖音","OFFICIAL SOCIAL ACCOUNTS · DOUYIN")
    d=platforms["douyin"]
    platform_profile(c,80,130,350,270,"assets/avatar-faxuange-main.webp","法宣阁",d["faxuange"]["followers"],d["faxuange"]["engagement"],DATA["sources"]["douyin"]["faxuange_profile"])
    platform_profile(c,530,130,350,270,"assets/avatar-hejiashu-main.webp","贺嘉述",d["hejiashu"]["followers"],d["hejiashu"]["engagement"],DATA["sources"]["douyin"]["hejiashu_profile"])
    c.setFont("CN",10); c.setFillColor(MUTED); c.drawCentredString(W/2,85,"粉丝与累计获赞均来自平台公开主页，PDF 数据生成日：2026.08.06")
    c.showPage(); page+=1

    # 6 social matrix
    new_page(c,page)
    title(c,"官方账号｜多平台","OFFICIAL SOCIAL ACCOUNTS · MULTI-PLATFORM")
    platforms_order=[("微博","weibo",["faxuange","hejiashu","jewelrybox"]),("小红书","xhs",["faxuange","hejiashu","jewelrybox"]),("Instagram","instagram",["faxuange","hejiashu","jewelrybox"])]
    names={"faxuange":"法宣阁","hejiashu":"贺嘉述","jewelrybox":"小发夹的首饰盒"}
    imgs={"faxuange":"assets/avatar-faxuange-main.webp","hejiashu":"assets/avatar-hejiashu-main.webp","jewelrybox":"assets/avatar-jewelrybox.webp"}
    y_rows=[315,185,55]
    for (label,key,users),yy in zip(platforms_order,y_rows):
        c.setFont("CNDisplay",18); c.setFillColor(INK); c.drawString(48,yy+82,label)
        for j,u in enumerate(users):
            x=165+j*255
            rounded_box(c,x,yy,230,104,fill=PAPER,stroke=LINE,radius=8)
            draw_img(c,imgs[u],x+14,yy+24,56,56,"cover",radius=28)
            c.setFont("CN",10.5); c.setFillColor(INK); c.drawString(x+82,yy+68,names[u])
            c.setFont("Times-Bold",16); c.drawString(x+82,yy+39,fmt(platforms[key][u]["followers"]))
            c.setFont("CN",8); c.setFillColor(MUTED); c.drawString(x+82,yy+23,"粉丝")
            if "engagement" in platforms[key][u]:
                c.setFont("Times-Bold",13); c.setFillColor(INK); c.drawRightString(x+214,yy+39,fmt(platforms[key][u]["engagement"]))
                c.setFont("CN",7.5); c.setFillColor(MUTED); c.drawRightString(x+214,yy+23,"互动")
    c.showPage(); page+=1

    # 7 platform overview
    new_page(c,page)
    title(c,"平台联动","PLATFORM CONTENT")
    dy=DATA["content"]["douyin"]
    wb=DATA["content"]["weibo"]
    dy_comments=sum(v.get("comments",0) or 0 for v in dy.values())
    wb_reposts=sum(v.get("reposts",0) or 0 for v in wb.values())
    wb_comments=sum(v.get("comments",0) or 0 for v in wb.values())
    for i,(v,l,note) in enumerate([
        ("115万+","代表性抖音共创累计获赞","多条高互动内容"),
        (fmt(dy_comments),"当前展示抖音共创累计评论","按已抓取公开项"),
        (fmt(wb_reposts),"微博高赞作品累计转发","按已抓取公开项"),
        (fmt(wb_comments),"微博高赞作品累计评论","按已抓取公开项"),
    ]): metric_box(c,48+i*218,270,200,125,v,l,note)
    draw_text(c,"双人共创内容已成为双方账号的重要高互动内容类型，并在抖音与微博形成跨平台传播。页面选取具有代表性的公开内容，呈现点赞、评论、收藏、分享与转发等互动表现。",48,215,860,font="CN",size=14,color=INK,leading=25,max_lines=4)
    c.showPage(); page+=1

    # 8 douyin content
    new_page(c,page)
    title(c,"抖音爆款共创","DOUYIN")
    order=[("item03","assets/posters/douyin-03-v3.jpg"),("item01","assets/posters/douyin-01.jpg"),("item02","assets/posters/douyin-02-v3.jpg")]
    for i,(key,poster) in enumerate(order):
        item=dy[key]
        content_card(c,36+i*306,65,276,350,poster,item["label"],item,item["url"])
    c.showPage(); page+=1

    # 9 weibo content
    new_page(c,page)
    title(c,"微博高赞作品","WEIBO")
    wb_cards=[("item02","assets/posters/weibo-qingdao.jpg","心动是初次见面的悸动，而爱是往后每一次，我转过头，你都在"),("item01","assets/posters/weibo-like-you.jpg","《喜欢你》"),("item03","assets/posters/weibo-gift.jpg","专属于小发夹的礼物🎁")]
    for i,(key,poster,label) in enumerate(wb_cards):
        item=wb[key]
        content_card(c,36+i*306,65,276,350,poster,label,item,item["url"])
    c.showPage(); page+=1

    # 10 AFU
    new_page(c,page)
    title(c,"AFU 阿芙","BUSINESS COOPERATION · BEAUTY / SKINCARE")
    c.setFont("CN",12); c.setFillColor(PINK_DARK); c.drawString(50,390,"双人品牌面膜大使")
    draw_text(c,"试探，缠绕，心照不宣的透亮——「宣」示美好，「述」说光采。",50,355,850,font="CN",size=13,color=INK,leading=20,max_lines=2)
    draw_img(c,"assets/afuposter.webp",50,56,270,275,"contain",radius=8)
    rounded_box(c,340,56,340,275,fill=PAPER,stroke=LINE,radius=8)
    c.setFont("CN",11); c.setFillColor(INK); c.drawString(360,304,"贺嘉述 与 AFU阿芙 等 3 人的共创微博")
    c.setFont("CN",8); c.setFillColor(MUTED); c.drawString(360,286,"6-30 10:00")
    draw_text(c,"有些靠近，不止于距离。\n是肌肤在油的沁润下，重拾弹韧；在蜜的包裹中，透出光彩。\n是「宣」之于口的亮，遇见「述」之于心的润——\n很高兴成为 AFU阿芙 品牌面膜大使。\n爱与光采，皆是双程。",360,260,300,font="CN",size=9.5,color=INK,leading=16,max_lines=9)
    c.setFont("CN",8.5); c.setFillColor(BLUE); c.drawString(360,92,"#阿芙精油SPA面膜家族  #宣然相逢嘉期而至")
    hyperlink(c,"https://weibo.com/8348577978/5318346250912515",340,56,340,275)
    draw_img(c,"assets/posters/afu-tvc.jpg",700,56,210,275,"contain",radius=8,bg=DARK)
    c.setFont("CN",9); c.setFillColor(MUTED); c.drawCentredString(185,38,"官方图片")
    c.drawCentredString(510,38,"官宣微博")
    c.drawCentredString(805,38,"官宣视频")
    c.showPage(); page+=1

    # 11 FunnyElves
    new_page(c,page)
    title(c,"FunnyElves 方里","BUSINESS COOPERATION · BEAUTY / BASE MAKEUP")
    c.setFont("CN",12); c.setFillColor(PINK_DARK); c.drawString(50,390,"双人品牌挚友")
    draw_text(c,"贴贴有「法」，心动「嘉」倍，悄然靠近的贴贴，流淌无言的心动。",50,355,850,font="CN",size=13,color=INK,leading=20,max_lines=2)
    draw_img(c,"assets/funnyelvesposter.webp",50,56,270,275,"contain",radius=8)
    rounded_box(c,340,56,340,275,fill=PAPER,stroke=LINE,radius=8)
    c.setFont("CN",11); c.setFillColor(INK); c.drawString(360,304,"法宣阁阿 与 FunnyElves方里的共创微博")
    c.setFont("CN",8); c.setFillColor(MUTED); c.drawString(360,286,"7-8 10:00")
    draw_text(c,"镜头内外，故事因热爱起笔，因生动持续加更。\n很高兴和贺嘉述携手，成为 FunnyElves方里 品牌挚友，\n以奶润透光开启贴贴时刻，以柔焦清透定格心动妆态。\n方里法嘉限定套组限定上线，感受每一次贴贴的心动时刻。",360,258,300,font="CN",size=9.6,color=INK,leading=17,max_lines=9)
    c.setFont("CN",8.5); c.setFillColor(BLUE); c.drawString(360,92,"#方里品牌挚友法宣阁贺嘉述  #贴贴有法心动嘉倍")
    hyperlink(c,"https://weibo.com/1118449424/5318346201104776",340,56,340,275)
    draw_img(c,"assets/funnyelves-live1.webp",700,56,210,275,"cover",radius=8)
    c.setFont("CN",9); c.setFillColor(MUTED); c.drawCentredString(185,38,"官方图片")
    c.drawCentredString(510,38,"官宣微博")
    c.drawCentredString(805,38,"官方直播")
    c.showPage(); page+=1

    # 12 LEECN coming soon
    gradient(c, SOFT_PINK, SOFT_GOLD)
    eyebrow(c,"BUSINESS COOPERATION · BEAUTY / NEW SEQUENCE",58,450,size=10,tracking=1.8)
    c.setFont("Times-Bold",46); c.setFillColor(INK); c.drawString(58,355,"LEECN")
    c.setFont("CNDisplay",34); c.drawString(238,358,"莉肯")
    c.setFont("CN",12); c.setFillColor(PINK_DARK); c.drawString(60,310,"新序美学大使")
    c.setStrokeColor(PINK); c.setLineWidth(1); c.setDash(3,3); c.roundRect(58,120,844,128,12,fill=0,stroke=1); c.setDash()
    eyebrow(c,"UPCOMING BRAND COOPERATION",85,198,size=9,tracking=1.5)
    c.setFont("Times-Bold",28); c.setFillColor(INK); c.drawString(410,175,"LEECN")
    c.setFont("Times-Roman",19); c.drawString(530,180,"IS COMING SOON")
    footer(c,page); c.showPage(); page+=1

    # 13 V generation
    new_page(c,page,bg=SOFT_PINK)
    title(c,"时尚资源","FASHION RESOURCE")
    draw_img(c,"assets/vgen-feature-01.webp",40,155,205,245,"cover",radius=6)
    draw_img(c,"assets/vgen-feature-02.webp",255,155,205,245,"cover",radius=6)
    draw_img(c,"assets/vgen-feature-03.webp",470,155,205,245,"cover",radius=6)
    draw_img(c,"assets/vgen-feature-04.webp",685,155,235,245,"cover",radius=6)
    c.setFont("Times-Bold",23); c.setFillColor(INK); c.drawString(48,115,"V Generation 2026 VOL.3")
    c.setFont("CN",12); c.drawString(48,88,"《情愫四序》｜“旷野为境”双人封面")
    draw_text(c,"一段关系，从开始到深处，究竟要走多久？  初识、试探、炽烈、沉淀。其实世间心意，自有时序生长。",500,112,410,font="CN",size=9.5,color=MUTED,leading=16,max_lines=4)
    c.showPage(); page+=1

    # 14 solo + arena
    new_page(c,page,bg=SOFT_GOLD)
    title(c,"单人时尚资源","SOLO EDITORIAL")
    # left
    draw_img(c,"assets/mag-faxuange-ok-1.webp",46,165,165,245,"cover",radius=6)
    draw_img(c,"assets/mag-faxuange-ok-2.webp",220,165,165,245,"cover",radius=6)
    c.setFont("CNDisplay",20); c.setFillColor(INK); c.drawString(48,128,"精彩 OK!｜法宣阁")
    draw_text(c,"每一段新的旅程，总会从一次尝试开始。带着对世界的好奇，推开通往未知的门。",48,100,335,font="CN",size=9.5,color=MUTED,leading=15,max_lines=3)
    # right
    draw_img(c,"assets/mag-hejiashu-fresh-1.webp",530,165,165,245,"cover",radius=6)
    draw_img(c,"assets/mag-hejiashu-fresh-2.webp",704,165,165,245,"cover",radius=6)
    c.setFont("CNDisplay",20); c.setFillColor(INK); c.drawString(532,128,"风尚志 Fresh｜贺嘉述")
    draw_text(c,"旷野为境，日光为裳。置身自然光影之中，干净灵动间自带少年元气。",532,100,335,font="CN",size=9.5,color=MUTED,leading=15,max_lines=3)
    c.setStrokeColor(PINK); c.setDash(3,3); c.roundRect(46,38,823,40,8,fill=0,stroke=1); c.setDash()
    eyebrow(c,"UPCOMING EDITORIAL",68,53,size=8,tracking=1.4)
    c.setFont("Times-Bold",18); c.setFillColor(INK); c.drawString(395,49,"ARENA")
    c.setFont("Times-Roman",12); c.drawString(477,52,"IS COMING SOON")
    c.showPage(); page+=1

    # 15 concert
    new_page(c,page)
    title(c,"DOUBLE HELIX「宿命回响」演唱会","LIVE EVENTS · 2026.07.25",cn_size=29)
    draw_img(c,"assets/concertposter.webp",50,60,230,340,"contain",radius=6)
    draw_img(c,"assets/concert-live-v2.webp",315,225,595,175,"cover",radius=6)
    draw_img(c,"assets/concert-rehearsal-v2.webp",315,60,285,150,"cover",radius=6)
    draw_img(c,"assets/concert-live-3.webp",615,60,295,150,"cover",radius=6)
    c.setFont("CN",10); c.setFillColor(MUTED); c.drawString(315,204,"曼谷 · Thunder Dome")
    draw_text(c,"积攒了许久的宿命回响，只为你们轰鸣。每段旋律，都是双程路上心与心的交织；每次相聚，都藏着未说尽的温柔与执念。",315,182,595,font="CN",size=10.2,color=INK,leading=17,max_lines=4)
    c.showPage(); page+=1

    # 16 fan meeting
    new_page(c,page)
    title(c,"「宣你述说」双人见面会","LIVE EVENTS · 2026.07.26",cn_size=31)
    draw_img(c,"assets/fanmeeting-v2.jpg",50,60,230,340,"contain",radius=6)
    draw_img(c,"assets/fanmeeting-live-1.webp",315,225,595,175,"cover",radius=6)
    draw_img(c,"assets/fanmeeting-live-2.webp",315,60,595,150,"cover",radius=6)
    c.setFont("CN",10); c.setFillColor(MUTED); c.drawString(315,204,"曼谷 · LIDO CONNECT HALL 3（2F）")
    draw_text(c,"「宣你述说」—以“宣”为名，以“述”为约。\n这既是两人名字的巧妙交织，也代表一份面向所有陪伴者的诚挚邀请：来听他们说，也来对他们说。",315,180,595,font="CN",size=10.2,color=INK,leading=18,max_lines=5)
    c.showPage(); page+=1

    # 17 legal/contact
    gradient(c, SOFT_PINK, SOFT_GOLD)
    eyebrow(c,"RESOURCE DOWNLOADS · CONTACT",58,450,size=10,tracking=1.8)
    c.setFont("CNDisplay",38); c.setFillColor(INK); c.drawString(58,380,"资料下载与合作建联")
    rounded_box(c,58,190,844,150,fill=Color(1,1,1,alpha=.72),stroke=LINE,radius=10)
    legal="本网站内容用于持续更新与信息发布，PDF 文件仅供合作交流与非商业用途使用。\n所有资料严禁用于商业销售、有偿传播或任何营利性活动，未经书面授权不得转售或二次分发。\n本方保留对违规使用行为追究法律责任的权利。"
    draw_text(c,legal,82,305,795,font="CN",size=12,color=INK,leading=26,max_lines=6)
    c.setFont("CNDisplay",25); c.setFillColor(INK); c.drawString(58,130,"合作建联")
    draw_text(c,"本文所涉及的具体合作身份、交付形式及执行方案等相关事宜，仅供初步沟通与参考之用，最终内容均以米椒娱乐官方正式沟通及书面确认为准。",58,100,650,font="CN",size=10.5,color=INK,leading=18,max_lines=4)
    rounded_box(c,730,65,170,58,fill=PAPER,stroke=PINK,radius=10)
    c.setFont("CN",14); c.setFillColor(INK); c.drawCentredString(815,88,"联系邮箱")
    hyperlink(c,"mailto:mejoymedia@foxmail.com",730,65,170,58)
    c.setFont("Helvetica",10); c.setFillColor(MUTED); c.drawString(58,45,"mejoymedia@foxmail.com")
    footer(c,page); c.showPage()

    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
