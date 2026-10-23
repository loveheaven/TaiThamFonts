# -*- coding: utf-8 -*-
"""Sangdang 非 Unicode 字体 -> Unicode 字体的转换主流程（fontTools 版）。

不依赖 FontForge：用 fontTools 读源 ttf，重命名字形、重映射 Unicode、补缺失字形、
用 feaLib 构建 GSUB/GDEF，最后设置命名并保存。
"""

import copy
import math

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

from tham_mapping import sangdangk_35_table
from ligature_creator import LigatureCreator


def _copy_glyph(template, font, src_name, dst_name, unicode_val):
    """从 template 复制一个字形（glyf + hmtx + cmap）到 font。"""
    order = font.getGlyphOrder()
    if dst_name not in order:
        order.append(dst_name)
        font.setGlyphOrder(order)

    # glyf：字形轮廓；hmtx：水平度量（步进宽度 + 左侧边距）。两者都要复制，
    # 否则字形只有形状而没有宽度信息。
    if 'glyf' in template and src_name in template['glyf'].glyphs:
        font['glyf'][dst_name] = template['glyf'][src_name]
    if 'hmtx' in template and src_name in template['hmtx'].metrics:
        font['hmtx'][dst_name] = template['hmtx'][src_name]

    if unicode_val is not None and 'cmap' in font:
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[unicode_val] = dst_name


# ---------------------------------------------------------------------------
# virama（uni1A60）缩放补充
# ---------------------------------------------------------------------------
# Sangdang 源字体普遍没有 virama 字形，需要从模板字体 A Tai Tham KH New 补。
# 但模板 UPM=2048、目标字体多为 UPM=1000，直接复制会得到一个大了约一倍的字形，
# 视觉上又大又粗。而且各 Sangdang 字体本身的笔画粗细差异很大（细体到特粗体），
# 等比缩放只能解决「大小」，不能解决「粗细」。
#
# 这里的做法分两步：
#   1) 大小匹配：按参考字母（uni1A20 等）的轮廓高度比例做等比缩放；
#   2) 粗细匹配：目标字母笔画宽 / 模板字母笔画宽 的比例，决定 virama 主轮廓
#      （十Campo字形）需要加粗或减细多少。加粗/减细通过把轮廓上每个点沿外法线
#      方向平移来实现（类似 FreeType 的 FT_Outline_Embolden 思路）。
# ---------------------------------------------------------------------------

# 用来测「参考字母高度和笔画宽度」的字形：都是单轮廓、无内孔的简单字母，
# 在所有 Sangdang 源字体里都存在（'!'、'F'、'ò'、'S' 借用位）。
_REFERENCE_LETTERS = ['uni1A20', 'uni1A36', 'uni1A63', 'uni1A45']


def _letter_metrics(font, names=_REFERENCE_LETTERS):
    """测量参考字母的轮廓高度和平均笔画宽度（2*面积/周长），返回 (height, stroke)。

    取中位数，避免单个字形异常导致偏差。
    """
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.perimeterPen import PerimeterPen

    gs = font.getGlyphSet()
    order = set(font.getGlyphOrder())
    hs, ws = [], []
    for n in names:
        if n not in order:
            continue
        b = BoundsPen(gs); gs[n].draw(b)
        a = AreaPen(gs); gs[n].draw(a)
        p = PerimeterPen(gs); gs[n].draw(p)
        if b.bounds is None or not p.value:
            continue
        hs.append(b.bounds[3] - b.bounds[1])
        ws.append(2 * abs(a.value) / p.value)
    if not hs:
        return None, None
    hs.sort(); ws.sort()
    return hs[len(hs) // 2], ws[len(ws) // 2]


def _min_chord_width(pts, samples=80):
    """用水平扫描线测轮廓的典型笔画厚度（中位数弦宽）。

    对「十字」「条状」这类笔画宽度一致的形状效果好；对复杂字形只作参考。
    """
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    n = len(pts)
    widths = []
    for i in range(1, samples):
        y = y0 + (y1 - y0) * i / samples
        crossings = []
        for j in range(n):
            x1, a1 = pts[j]
            x2, a2 = pts[(j + 1) % n]
            if (a1 <= y < a2) or (a2 <= y < a1):
                t = (y - a1) / (a2 - a1)
                crossings.append(x1 + t * (x2 - x1))
        crossings.sort()
        for k in range(0, len(crossings) - 1, 2):
            widths.append(crossings[k + 1] - crossings[k])
    if not widths:
        return 0.0
    widths.sort()
    return widths[len(widths) // 2]


def _embolden_contour(pts, distance):
    """把轮廓上每个点沿外法线方向平移 distance（>0 加粗、<0 减细）。

    用有向面积判断轮廓朝向（外轮廓顺时针/逆时针决定法线方向），
    每个点取前后两条边的左法线的角平分线方向。
    """
    n = len(pts)
    if n < 3 or not distance:
        return list(pts)
    area2 = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
                for i in range(n))
    # 面积>0 逆时针：内部在行进方向左侧，外侧在右侧 -> outward = -left_normal
    # 面积<0 顺时针：内部在右侧，外侧在左侧 -> outward = +left_normal
    outward = -1.0 if area2 > 0 else 1.0
    out = []
    for i in range(n):
        px, py = pts[(i - 1) % n]
        cx, cy = pts[i]
        nx, ny = pts[(i + 1) % n]
        d1x, d1y = cx - px, cy - py
        d2x, d2y = nx - cx, ny - cy
        n1 = math.hypot(d1x, d1y) or 1e-9
        n2 = math.hypot(d2x, d2y) or 1e-9
        l1x, l1y = -d1y / n1, d1x / n1   # 第一条边的左法线
        l2x, l2y = -d2y / n2, d2x / n2   # 第二条边的左法线
        bx, by = l1x + l2x, l1y + l2y    # 角平分线方向
        bl = math.hypot(bx, by)
        if bl < 1e-9:
            bx, by, bl = l1x, l1y, 1.0
        out.append((cx + outward * bx / bl * distance,
                    cy + outward * by / bl * distance))
    return out


def _copy_virama_scaled(template, font, src_name='uni1A60', dst_name='uni1A60',
                        unicode_val=0x1A60):
    """把模板里的 virama 按目标字体的大小和粗细缩放后复制进来。

    与 _copy_glyph 不同：先按高度比例等比缩放，再按笔画宽度比例加粗/减细，
    使 virama 在该字体里看起来大小、粗细都与其他字母一致。
    """
    th, tstroke = _letter_metrics(font)
    ph, pstroke = _letter_metrics(template)
    if th is None or ph is None or not ph or not pstroke:
        # 参考字形缺失时退化为直接复制
        _copy_glyph(template, font, src_name, dst_name, unicode_val)
        return

    scale = th / ph
    # 粗细比例：比较「笔画/高度」而非原始笔画宽，这样模板(2048)和目标(1000)
    # 的 UPM 差异不会混进来。等比缩放已经乘了 th/ph，所以这里再乘的是
    # 额外的粗细修正 = (tstroke/ph) / (pstroke/th)。
    weight_factor = (tstroke * ph) / (pstroke * th)

    tglyph = template['glyf'][src_name]
    coords, ends, flags = tglyph.getCoordinates(template['glyf'])

    # 模板 virama 主轮廓（第一个轮廓 = 十字标）的笔画厚度
    main_pts = [coords[i] for i in range(ends[0] + 1)]
    mark_stroke = _min_chord_width(main_pts)

    # 等比缩放后 virama 笔画 = mark_stroke * scale；
    # 期望笔画 = mark_stroke * scale * weight_factor；
    # embolden 距离 = (期望 - 实际) / 2（两侧各移动一半）。
    delta = mark_stroke * scale * (weight_factor - 1.0) / 2.0

    new_g = copy.deepcopy(tglyph)
    # 坐标统一缩放
    scaled = [(x * scale, y * scale) for x, y in coords]
    if delta:
        result = []
        idx = 0
        for ci, end in enumerate(ends):
            contour = scaled[idx:end + 1]
            # 只对主轮廓（十字标）做加粗/减细；虚线圆的圆点是装饰性的，
            # 若同样缩放粗细，细体字体里圆点会缩到几乎看不见。
            d = delta if ci == 0 else 0.0
            result.extend(_embolden_contour(contour, d))
            idx = end + 1
        scaled = result
    new_g.coordinates = GlyphCoordinates(scaled)
    new_g.endPtsOfContours = list(ends)
    new_g.flags = bytearray(flags)
    # 坐标变了，原 hinting 指令不再适用，清空
    new_g.program = ttProgram.Program()
    new_g.program.fromBytecode(b"")
    new_g.recalcBounds(template['glyf'])

    order = font.getGlyphOrder()
    if dst_name not in order:
        order.append(dst_name)
        font.setGlyphOrder(order)
    font['glyf'][dst_name] = new_g

    adv, lsb = template['hmtx'][src_name]
    font['hmtx'][dst_name] = (int(round(adv * scale)), int(round(lsb * scale)))

    if unicode_val is not None and 'cmap' in font:
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[unicode_val] = dst_name


# 从 Noto Sans Tai Tham 补充的傣文符号码位。
_SUPPLEMENT_SIGNS = [0x1AA0, 0x1AA1, 0x1AA2, 0x1AA3, 0x1AA4,
                     0x1AA5, 0x1AA6, 0x1AAC, 0x1AAD]


def _glyph_stroke(font, name):
    """字形的平均笔画宽度（2*墨迹面积/周长），粗略衡量笔画粗细。

    墨迹面积按每个轮廓的 |面积| 求和（不能用净面积，否则带内孔的字形会被
    严重低估）。只处理简单字形；复合字形走另外的分支，不会调用到这里。
    """
    from fontTools.pens.perimeterPen import PerimeterPen

    gs = font.getGlyphSet()
    p = PerimeterPen(gs); gs[name].draw(p)
    if not p.value:
        return 0.0

    glyf = font['glyf']
    coords, ends, _flags = glyf[name].getCoordinates(glyf)
    total_area = 0.0
    idx = 0
    for end in ends:
        pts = coords[idx:end + 1]
        n = len(pts)
        a2 = sum(pts[k][0] * pts[(k + 1) % n][1] - pts[(k + 1) % n][0] * pts[k][1]
                 for k in range(n))
        total_area += abs(a2) / 2.0
        idx = end + 1
    return 2 * total_area / p.value


def _copy_signs_from_noto(noto, font):
    """从 Noto Sans Tai Tham 补充 U+1AA0-1AA6、U+1AAC、U+1AAD，并按字体缩放大小、调节粗细。

    Noto 是 Regular 字重，各 Sangdang 字体从极细到特粗都有，直接复制会粗细不搭。
    处理方式和 virama 一样：先按参考字母高度比例等比缩放，再按笔画/高度比例调节粗细。
    """
    th, tstroke = _letter_metrics(font)
    ph, pstroke = _letter_metrics(noto)
    if th is None or ph is None or not ph or not pstroke:
        return

    scale = th / ph
    weight_factor = (tstroke * ph) / (pstroke * th)

    cmap = noto.getBestCmap()

    for cp in _SUPPLEMENT_SIGNS:
        src_name = cmap.get(cp)
        if not src_name or src_name not in noto.getGlyphOrder():
            continue
        dst_name = src_name
        if dst_name in font.getGlyphOrder():
            continue  # 目标字体已有，跳过

        src_glyph = noto['glyf'][src_name]
        new_g = copy.deepcopy(src_glyph)

        if src_glyph.numberOfContours == -1:
            # 复合字形（如 uni1AA2 引用了 uni1A48、uni1A7C）：只缩放组件偏移，
            # 组件本身用目标字体里已有的字形，其粗细已自动匹配目标字体。
            for comp in new_g.components:
                comp.x = comp.x * scale
                comp.y = comp.y * scale
        else:
            # 简单字形：等比缩放 + 按粗细比例加粗/减细。
            coords, ends, flags = new_g.getCoordinates(noto['glyf'])
            stroke = _glyph_stroke(noto, src_name)
            delta = stroke * scale * (weight_factor - 1.0) / 2.0
            scaled = [(x * scale, y * scale) for x, y in coords]
            if delta:
                result = []
                idx = 0
                for end in ends:
                    contour = scaled[idx:end + 1]
                    result.extend(_embolden_contour(contour, delta))
                    idx = end + 1
                scaled = result
            new_g.coordinates = GlyphCoordinates(scaled)
            new_g.endPtsOfContours = list(ends)
            new_g.flags = bytearray(flags)
            # 坐标变了，原 hinting 指令不再适用，清空
            new_g.program = ttProgram.Program()
            new_g.program.fromBytecode(b"")

        # 重算包围盒；复合字形需要目标字体的 glyf 来解析组件
        new_g.recalcBounds(font['glyf'])

        order = font.getGlyphOrder()
        if dst_name not in order:
            order.append(dst_name)
            font.setGlyphOrder(order)
        font['glyf'][dst_name] = new_g

        adv, lsb = noto['hmtx'][src_name]
        font['hmtx'][dst_name] = (int(round(adv * scale)), int(round(lsb * scale)))

        if 'cmap' in font:
            for table in font['cmap'].tables:
                if table.isUnicode():
                    table.cmap[cp] = dst_name


def _remap_glyphs(font):
    """重命名字形并重映射 Unicode（等价原第一遍循环）。

    返回 (glyphclasses, prebase_glyphs)：
      glyphclasses   {newname: glyphclass}
      prebase_glyphs 需要登记为预置基字（pref）的字形名列表
    """
    glyph_order = font.getGlyphOrder()
    cmap_tables = font['cmap'].tables if 'cmap' in font else []

    # 字形名 -> 当前 Unicode（Sangdang 是一对一映射）
    unicode_of = {}
    for table in cmap_tables:
        if table.isUnicode():
            for cp, gname in table.cmap.items():
                unicode_of[gname] = cp

    rename = {}
    glyphclasses = {}
    new_unicode = {}   # old_gname -> 新码位（-1 表示清除）
    prebase_glyphs = []
    used_names = set()

    for old in glyph_order:
        code = unicode_of.get(old, -1)
        value = sangdangk_35_table.get(chr(code)) if code > 0 else sangdangk_35_table.get(old)
        if value is None:
            continue
        name, glyphclass = value[0], value[1]
        if name in used_names:
            # 两个源字形映射到同一个目标名（如 'Õ' 和 '/' 都映射到 uni002F），
            # 保留先遇到的那个，后遇到的保持原名（对应 fontforge 的静默忽略）。
            continue
        rename[old] = name
        used_names.add(name)
        if glyphclass:
            glyphclasses[name] = glyphclass
        if code > 0:
            new_code = int(name.replace('uni', ''), 16) if '.' not in name else -1
            new_unicode[old] = new_code
            if new_code > 0 and (new_code == 0x1A55 or (0x1A6E <= new_code <= 0x1A72)):
                prebase_glyphs.append(name)

    # 应用重命名：fontTools 的 setGlyphOrder 只会更新全局 glyphOrder 和 post 表，
    # glyf（轮廓）和 hmtx（水平度量）的 key 仍以字形名为索引，必须手动同步，
    # 否则字形名与轮廓/度量对不上。
    new_order = [rename.get(g, g) for g in glyph_order]
    font.setGlyphOrder(new_order)
    if 'glyf' in font:
        glyf = font['glyf']
        glyf.glyphs = {rename.get(n, n): g for n, g in glyf.glyphs.items()}
        glyf.glyphOrder = list(new_order)
    # hmtx：水平度量表，记录每个字形的 advance width 与 left side bearing；
    # 重命名后其 key（字形名）也要跟着改。
    if 'hmtx' in font:
        hmtx = font['hmtx']
        hmtx.metrics = {rename.get(n, n): m for n, m in hmtx.metrics.items()}

    # 重建 cmap：重命名的字形改用新码位（-1 则清除映射）
    for table in cmap_tables:
        if not table.isUnicode():
            continue
        new_cmap = {}
        for cp, gname in table.cmap.items():
            if gname in rename:
                code2 = new_unicode[gname]
                if code2 > 0:
                    new_cmap[code2] = rename[gname]
            else:
                new_cmap[cp] = gname
        table.cmap = new_cmap

    return glyphclasses, prebase_glyphs


def _add_contextual_rules(lig, font):
    """第三遍：为特殊字形登记语境替换（calt）与连字（liga）规则。

    遍历当前字体的所有字形名，针对特定的「变体字形」（如 uni1A20.sub2、
    uni1A2C.sub2、uni1A5E.sub 等）逐条添加规则。这些规则描述的是：

        「在什么前后文里，把某个字形替换成另一个变体。」

    为什么需要：傣文的下加/上加附标形态会因前面的基字不同而变化。例如下加
    ga/tsa/na/ta/pha/ha 有「大号第二形式」，只有当前面是某几个基字时才用
    .sub2 形式，否则用 .sub1 形式——这类「看前后文决定用哪个变体」的规则
    就是 calt（语境替换）；而少数几个（如 uni1A2C.2C、uni1A50.63）则是固定
    的多字形组合，用 liga（连字）实现。

    每条 if/elif 分支处理一组同类的变体字形，具体语义见各分支内注释。
    """
    # 下加字形全集：基字后面跟这些下加附标/下加辅音时，基字可能切换成对应变体
    # （如 uni1A2C.sub2、uni1A3E.tsub）。
    subscript_glyphs = ['uni1A56', 'uni1A57', 'uni1A5B', 'uni1A5C', 'uni1A5D', 'uni1A5E', 'uni1A69','uni1A6A', 'uni1A6C', 'uni1A6D',
                        'uni1A20.sub1', 'uni1A21.sub', 'uni1A23.sub', 'uni1A25.sub', 'uni1A26.sub',
                        'uni1A27.sub', 'uni1A28.sub1', 'uni1A29.sub', 'uni1A2B.sub', 'uni1A2C.sub',
                        'uni1A2D.sub', 'uni1A2E.sub', 'uni1A2F.sub', 'uni1A30.sub', 'uni1A31.sub1',
                        'uni1A32.sub1', 'uni1A33.sub', 'uni1A34.sub', 'uni1A35.sub', 'uni1A36.sub',
                        'uni1A37.sub', 'uni1A39.sub', 'uni1A3B.sub', 'uni1A3D.sub1', 'uni1A3E.sub',
                        'uni1A3F.sub1', 'uni1A41.sub', 'uni1A43.sub', 'uni1A45.sub1', 'uni1A46.sub',
                        'uni1A48.sub', 'uni1A49.sub1', 'uni1A4A.sub', 'uni1A32.45', 'uni1A47.sub',
                        'uni1A45.3F']
    for name in list(font.getGlyphOrder()):
        if name == 'uni1A20.sub2' or name == 'uni1A28.sub2' or name == 'uni1A31.sub2' or name == 'uni1A32.sub2' or name == 'uni1A3D.sub2' or name == 'uni1A49.sub2' or name == 'uni1A56.sub2':
            # 下加ga, tsa, na, ta, pha, ha, la的大号的第二形式
            prev = ['uni1A20', 'uni1A25', 'uni1A2B', 'uni1A31', 'uni1A32', 'uni1A3D', 'uni1A3F', 'uni1A43', 'uni1A47', 'uni1A48', 'uni1A49', 'uni1A4B']
            if name == 'uni1A56.sub2':
                lig.add_calt(prev + [name.replace('.sub2', '')], name)
            else:
                lig.add_calt(prev + [name.replace('sub2', 'sub1')], name)
        elif name == 'uni1A2C.sub2':
            next = subscript_glyphs
            coverage_str = '[' + ' '.join(next) + ']'
            replacename = name.replace('.tsub', '').replace('.sub2', '')
            lig.add_calt([replacename], name, next=[coverage_str])
        elif name == 'uni1A3E.tsub':
            # uni1A3E（ma）下面加下加字时，切换为带下加位的变体 uni1A3E.tsub
            coverage_str = '[' + ' '.join(subscript_glyphs) + ']'
            lig.add_calt(['uni1A3E'], name, next=[coverage_str])
        elif name == 'uni1A36.tsub':
            # uni1A36（na）下面加下加字时，切换为带下加位的变体 uni1A36.tsub
            coverage_str = '[' + ' '.join(subscript_glyphs) + ']'
            lig.add_calt(['uni1A36'], name, next=[coverage_str])
        elif name == 'uni1A2F.tsub':
            # uni1A2F（da）下面加下加字时，切换为带下加位的变体 uni1A2F.tsub
            coverage_str = '[' + ' '.join(subscript_glyphs) + ']'
            lig.add_calt(['uni1A2F'], name, next=[coverage_str])
        elif name == 'uni1A41.tsub':
            # uni1A41（ra）下面加下加字时，切换为带下加位的变体 uni1A41.tsub
            coverage_str = '[' + ' '.join(subscript_glyphs) + ']'
            lig.add_calt(['uni1A41'], name, next=[coverage_str])
        elif name == 'uni1A2C.2C':
            lig.add_ligature(['uni1A2C', 'uni1A5A'], name, False, stage=2)
        elif name == 'uni1A36.63':
            # ᨶᩣ（uni1A36.63）后面跟前置元音 ᩮ（uni1A6E）：组合成 uni1A36.63.6E
            # （e 放左边、na.63 放右边），使 ᩮ 显示到辅音前面。依赖第一轮
            # liga（uni1A36+uni1A63 -> uni1A36.63）的产物，故放第 2 轮。
            lig.add_ligature(['uni1A36.63', 'uni1A6E'], 'uni1A36.63.6E', True, stage=2)
        elif name == 'uni1A50.63':
            lig.add_ligature(['uni1A50', 'uni1A63', 'uni1A62'], name, False, stage=2)
            lig.add_ligature(['uni1A50', 'uni1A62', 'uni1A63'], name, False, stage=2)
            lig.add_ligature(['uni1A50', 'uni1A63', 'uni1A76'], name, False, stage=2)
            lig.add_ligature(['uni1A50', 'uni1A76', 'uni1A63'], name, False, stage=2)
        elif name == 'uni1A5E.sub':
            # 下加ga, tsa, na, ta, pha, ha的大号的第二形式
            prev = ['uni1A20', 'uni1A25', 'uni1A2B', 'uni1A31', 'uni1A32', 'uni1A3D', 'uni1A3F', 'uni1A43', 'uni1A47', 'uni1A48', 'uni1A49', 'uni1A4B']
            lig.add_calt(prev + [name.replace('.sub', '')], name)
        elif name == 'uni1A62.62':
            lig.add_ligature(['uni1A62', 'uni1A62'], name, False, stage=2)
            lig.add_ligature(['uni1A62', 'uni1A76'], name, False, stage=2)
        elif name == 'uni1A45.3F.2' or name == 'uni1A3F.sub2' or name == 'uni1A45.sub2' or \
                name == 'uni1A69.sub' or name == 'uni1A6A.sub' or name == 'uni1A6C.sub' or name == 'uni1A6D.sub':
            # 下加oi 下加ya 下加va；下加元音u, u. , o , oai
            prev = ['uni1A2C', 'uni1A2E', 'uni1A4C', 'uni1A56', 'uni1A57', 'uni1A5B', 'uni1A5C', 'uni1A5D', 'uni1A5E',
                    'uni1A20.sub1', 'uni1A20.sub2', 'uni1A21.sub', 'uni1A23.sub', 'uni1A25.sub',
                    'uni1A26.sub', 'uni1A27.sub', 'uni1A28.sub1', 'uni1A29.sub', 'uni1A2B.sub',
                    'uni1A2C.sub', 'uni1A2C.2C', 'uni1A2D.sub', 'uni1A2E.sub', 'uni1A2F.sub',
                    'uni1A30.sub', 'uni1A31.sub1', 'uni1A31.sub2', 'uni1A32.sub1', 'uni1A33.sub',
                    'uni1A34.sub', 'uni1A35.sub', 'uni1A36.sub', 'uni1A37.sub', 'uni1A39.sub',
                    'uni1A3B.sub', 'uni1A3D.sub1', 'uni1A3D.sub2', 'uni1A3E.sub', 'uni1A3F.sub1',
                    'uni1A41.sub', 'uni1A43.sub', 'uni1A45.sub1', 'uni1A46.sub', 'uni1A48.sub',
                    'uni1A49.sub1', 'uni1A49.sub2', 'uni1A4A.sub', 'uni1A32.45', 'uni1A32.sub2',
                    'uni1A2D.2E', 'uni1A4A.49', 'uni1A47.sub', 'uni1A45.3F', 'uni1A6D.sub',
                    'uni1A3F.sub2', 'uni1A28.sub2', ]
            replacename = ''
            if name == 'uni1A45.3F.2':
                replacename = 'uni1A45.3F'
            elif name.find('sub2') > 0:
                replacename = name.replace('sub2', 'sub1')
            else:
                replacename = name.replace('.sub', '')
            lig.add_calt(prev + [replacename], name)

            prev1 = ['uni1A58', 'uni1A59', 'uni1A5A', 'uni1A62', 'uni1A65', 'uni1A66', 'uni1A67', 'uni1A68', 'uni1A6B',
                     'uni1A73', 'uni1A74', 'uni1A75', 'uni1A76', 'uni1A77', 'uni1A78', 'uni1A79', 'uni1A7A',
                     'uni1A7B', 'uni1A7C', ]
            coverage_str = ' [ ' + ' '.join(prev) + ' ] [' + ' '.join(prev1) + ']'
            lig.add_calt([coverage_str, replacename], name, prev_wrapped=True)
        elif name == 'uni1A75.sub1' or name == 'uni1A7B.sub' or name == 'uni1A7C.sub':
            # 声调二和其他上加符号的组合
            replacename = name.replace('.sub1', '').replace('.sub', '')
            lig.add_calt(['uni1A65', 'uni1A66', 'uni1A67', 'uni1A68', 'uni1A6B', 'uni1A73', 'uni1A74', replacename], name)


def _add_latin_characters(template, font):
    """从模板补充 A-Z、a-z 标准拉丁字形。"""
    tcmap = template.getBestCmap()
    for cp in list(range(ord('A'), ord('Z') + 1)) + list(range(ord('a'), ord('z') + 1)):
        dst_name = chr(cp)
        if dst_name in font.getGlyphOrder():
            continue
        src_name = tcmap.get(cp)
        if src_name is None:
            continue
        _copy_glyph(template, font, src_name, dst_name, cp)


def convert_sangdang(font_numbers, template_path='./Tai-Tham-Unicode-for-Mac/A Tai Tham KH New.ttf',
                     noto_path='./NotoTaiTham/fonts/NotoSansTaiTham/full/ttf/NotoSansTaiTham-Regular.ttf'):
    """把给定的 Sangdang 字体编号列表转换成 Unicode 字体。

    font_numbers: 要转换的字体编号（如 [14] 或 range(41)）。
    template_path: 模板字体（ATaiThamKHNew-Regular 导出的 ttf），用于补缺失字形（如 virama）。
    noto_path: Noto Sans Tai Tham，用于补充 U+1AA0-1AA6、U+1AAC、U+1AAD 等符号。
    """
    template = TTFont(template_path)
    noto = TTFont(noto_path)

    for i in font_numbers:
        print(i)
        src_path = './Sangdang-Non-Unicode-for-Mac/SangdangFonts/sangdangk.%02dnew-Normal.ttf' % i
        font = TTFont(src_path)

        # 第一遍：重命名 + 重映射 unicode + glyphclass + prebase
        glyphclasses, prebase_glyphs = _remap_glyphs(font)

        lig = LigatureCreator(font)
        for name, gc in glyphclasses.items():
            lig.set_glyphclass(name, gc)
        for name in prebase_glyphs:
            lig.add_prebase([name], name, False)

        # 补 virama 附标 uni1A60（按目标字体大小和粗细缩放，不能直接复制）
        if 'uni1A60' not in font.getGlyphOrder():
            _copy_virama_scaled(template, font)
        lig.set_glyphclass('uni1A60', 'mark')

        # 补 Noto 里的傣文符号 U+1AA0-1AA6、U+1AAC、U+1AAD（同样按字体缩放、调粗细）
        _copy_signs_from_noto(noto, font)

        # 第二遍：为带「连字序列」的条目登记 ligature 规则。
        # input 里含有其他连字产物的（如 uni1A45.3F <- uni1A45.sub1 + uni1A3F.sub1，
        # 两个下加字形本身由 uni1A60+uni1A45 / uni1A60+uni1A3F 连字得到），
        # 必须放到第 2 轮，否则同一 lookup 内不会回头匹配产物，规则永远不生效。
        liga_products = {v[0] for v in sangdangk_35_table.values() if len(v) > 2}
        for key, value in sangdangk_35_table.items():
            name = value[0]
            if len(value) > 2 and name in font.getGlyphOrder():
                stage = 2 if any(g in liga_products for g in value[2]) else 1
                lig.add_ligature(value[2], name, False, stage=stage)

        # 第三遍：calt/连字特殊规则
        _add_contextual_rules(lig, font)

        # 收尾：补拉丁字母
        # _add_latin_characters(template, font)

        # 构建 GDEF + GSUB
        lig.build()

        # 命名 + OS/2
        familyname = 'sangdang k.%02d unicode' % i
        fontname = 'sangdangk.%02dunicode-Normal' % i
        fullname = 'sangdang k.%02d unicode Normal' % i
        name = font['name']
        name.setName(familyname, 1, 3, 1, 0x409)
        name.setName(fontname, 6, 3, 1, 0x409)
        name.setName(fullname, 4, 3, 1, 0x409)
        name.setName(familyname, 16, 3, 1, 0x409)  # Preferred Family
        name.setName(fullname, 18, 3, 1, 0x409)    # Compatible Full
        font['OS/2'].version = 4

        font.save('sangdangk.%02dunicode-Normal.ttf' % i)

    template.close()
    noto.close()
