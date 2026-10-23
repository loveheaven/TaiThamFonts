# -*- coding: utf-8 -*-
"""预览辅助函数：渲染傣文样例文本、对比不同字体的渲染效果。"""
from PIL import Image, ImageFont, ImageDraw

def generateResult(fontpath, title_text = "ᨠᩜᨠᩞᨮᩜ\nᨮ᩠ᨾᨮᨮ᩠ᨿᩪᩏ᩠ᨾ"+"ᨠ"+"ᩮ"):
        my_image = Image.new('RGBA', (1500, 600))
        title_font = ImageFont.truetype(fontpath, 200, layout_engine=ImageFont.Layout.RAQM)
        image_editable = ImageDraw.Draw(my_image)
        image_editable.text((15,15), title_text, (0, 0, 0), font=title_font, features=['ccmp'])
        my_image.save("%s.png" % fontpath)

def showFont():

    #my_image = Image.open("nature.jpg")
    
    generateResult('lanna.ttf')
    generateResult('PayapLanna-Regular.ttf')
    generateResult('hariphunchai.ttf')
    generateResult('A-Tai-Tham-KH-New-V3.ttf')
    generateResult('NotoSansTaiTham-VariableFont_wght.ttf')
    generateResult('lannaalif-v1-03.ttf')
    generateResult('Pali_Tilok.ttf')
    generateResult('Tai Tham Kasem.ttf')
    generateResult('Tai Tham Kruba Promma Regular.ttf')
    generateResult('Tai Tham Nang Kham.ttf')
    generateResult('Tai Tham Sripanyawut.ttf')
    generateResult('TaiThamBXL.ttf')
    generateResult('TaiThamThatdaokham.ttf')
    generateResult('VS_Tham_Lanxang.ttf')
    generateResult('VS_Tham_Pali.ttf')
    generateResult('CR_Insom_Pali.ttf')
    generateResult('CR_Insom_Lanna.ttf')

def diffFont():
    """Compare two fonts at 72pt using two methods on one image.

    Method 1: same font size (72pt) and same baseline, drawn directly.
    Method 2: each glyph inside its own 1em reference box (72px) with baseline
              and measured ink bbox.
    Noto Sans Tai Tham Regular uses Unicode ᨠ (U+1A20); Sangdang 14 is a
    non-Unicode font where the same KA letter sits at '!' (U+0021).
    """
    SIZE = 72
    samples = [
        ("Noto Sans Tai Tham Regular", "NotoTaiTham/fonts/NotoSansTaiTham/full/ttf/NotoSansTaiTham-Regular.ttf", "ᨠ"),
        ("Sangdang 14", "./Sangdang-Non-Unicode-for-Mac/SangdangFonts/sangdangk.14new-Normal.ttf", "!"),
    ]

    em_w, gap, pad = 180, 60, 50
    W = pad * 2 + len(samples) * (em_w + gap) - gap
    fonts = [ImageFont.truetype(p, SIZE) for _, p, _ in samples]

    m1_caption_y = 8
    m1_base_y = 56
    m2_caption_y = m1_base_y + 54
    m2_top = m2_caption_y + 24
    m2_base = m2_top + SIZE
    H = m2_base + 62

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    # ---- method 1: same baseline ----
    d.text((pad, m1_caption_y), "方法1：同字号 72pt、同基线直接画（红线=基线，蓝框=墨迹）", fill=(90, 90, 90))
    d.line([pad, m1_base_y, W - pad, m1_base_y], fill=(230, 60, 60), width=2)

    x = pad
    for (label, path, text), font in zip(samples, fonts):
        d.text((x + 10, m1_base_y), text, font=font, fill=(0, 0, 0), anchor="ls")
        bb = d.textbbox((x + 10, m1_base_y), text, font=font, anchor="ls")
        d.rectangle(bb, outline=(30, 90, 220), width=1)
        d.text((x, m1_base_y + 6), "%s  h=%dpx" % (label.split(" ")[0], bb[3] - bb[1]), fill=(0, 0, 0))
        x += em_w + gap

    # ---- method 2: em boxes ----
    d.text((pad, m2_caption_y), "方法2：em 框对比（灰框=1em=72px，红线=基线，蓝框=墨迹）", fill=(90, 90, 90))

    x = pad
    for (label, path, text), font in zip(samples, fonts):
        d.rectangle([x, m2_top, x + em_w, m2_top + SIZE], outline=(190, 190, 190), width=1)
        d.line([x, m2_base, x + em_w, m2_base], fill=(230, 60, 60), width=2)
        d.text((x + 10, m2_base), text, font=font, fill=(0, 0, 0), anchor="ls")
        bb = d.textbbox((x + 10, m2_base), text, font=font, anchor="ls")
        d.rectangle(bb, outline=(30, 90, 220), width=1)
        w2, h2 = bb[2] - bb[0], bb[3] - bb[1]
        d.text((x, m2_base + 6), "%s\nink %dx%dpx  h=%.0f%% of em" % (label, w2, h2, 100.0 * h2 / SIZE), fill=(0, 0, 0))
        print("%-30s ink %dx%dpx  (%.0f%% of em)" % (label, w2, h2, 100.0 * h2 / SIZE))
        x += em_w + gap

    img.save("compare_both.png")
    print("saved compare_both.png")

