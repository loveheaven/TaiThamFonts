# -*- coding: utf-8 -*-
"""用 fontTools/feaLib 为字体构建 OpenType 特性（GSUB/GDEF）。

这是原 fontforge 版 LigatureCreator 的等价实现：不再直接操作 fontforge 的
lookup，而是把规则收集起来，最后通过 feaLib 一次性编译成 GSUB/GDEF 表。
"""

import re

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent


class LigatureCreator(object):
    def __init__(self, font):
        self.font = font
        self._liga_rules = []   # feature liga 第 1 轮的替换规则
        self._liga_rules2 = []  # feature liga 第 2 轮规则（input 依赖第 1 轮的产物）
        self._pref_rules = []  # feature pref 的替换规则
        self._calt_rules = []  # feature calt 的语境替换规则
        self._glyphclass = {'base': set(), 'ligature': set(), 'mark': set()}

    # ---- glyphclass 记录（对应 fontforge 的 glyph.glyphclass）----
    def set_glyphclass(self, name, glyphclass):
        mapping = {
            'baseglyph': 'base',
            'baseligature': 'ligature',
            'mark': 'mark',
        }
        if glyphclass in mapping:
            self._glyphclass[mapping[glyphclass]].add(name)

    # ---- 连字（liga）：input_chars 序列 -> ligature_name ----
    def add_ligature(self, input_chars, ligature_name, needToCreate=False, stage=1):
        """登记一条 liga 规则。

        stage=1: 第一轮（input 都是基础/源字形）。
        stage=2: 第二轮（input 里含有第一轮 ligate 出来的组合字形，如
                 `sub uni1A36.63 uni1A6E by ...`，必须等第一轮把
                 uni1A36+uni1A63 组合成 uni1A36.63 之后才能匹配）。
        两个 stage 生成两个独立的 lookup，整形引擎按顺序各扫一遍，
        否则同一个 lookup 内组合完不会回头再匹配，导致链式连字失效。
        """
        order = self.font.getGlyphOrder()
        # 组件字形必须存在，否则跳过（对应原 fontforge 对缺失字形的静默忽略）
        if any(g not in order for g in input_chars):
            return
        if not needToCreate and ligature_name not in order:
            return
        if needToCreate:
            self._combine_two_char(input_chars, ligature_name)
        rules = self._liga_rules if stage == 1 else self._liga_rules2
        rules.append('sub %s by %s;' % (' '.join(input_chars), ligature_name))

    # ---- 预置基字（pref）：单字符 identity，标记为预置基字 ----
    def add_prebase(self, input_chars, ligature_name, needToCreate=False, lookup_name='prebase.sub.0'):
        # 原代码只在 needToCreate=False 下调用；needToCreate=True 时创建空字形，
        # 但实际从未用到，这里仅记录规则。
        self._pref_rules.append('sub %s by %s;' % (' '.join(input_chars), ligature_name))

    # ---- 语境连字：原实现等价于 add_ligature（prev/next 均为空），故省略 ----
    def add_ligature_to_calt(self, input_chars, context_lookup_name='context_ligature'):
        pass

    # ---- 语境替换（calt）：[prev] cur' [next] -> ligature_name ----
    def add_calt(self, input_chars, ligature_name, prev_wrapped=False, next=None):
        """登记一条语境替换（calt）规则。

        生成 .fea 规则 `sub prev cur' next by ligature_name;`，即在 prev 前、
        next 后的上下文里，把 cur 替换成 ligature_name。

        input_chars : 字形序列，最后一个元素是被替换的字形（cur），前面的元素构成 prev 上下文。
        prev_wrapped: True 表示 prev 已经是 '[a b c]' 形式的 coverage；False 表示 prev 是
                      普通字形序列，会自动包成 '[a b c]' coverage。
        next        : 后文 coverage 字符串（已带 '[ ]'），可为空。
        """
        cur = input_chars[-1]
        # 被替换的字形必须存在，否则跳过
        if cur not in self.font.getGlyphOrder():
            return

        prev = ' '.join(input_chars[j] for j in range(len(input_chars) - 1)) if len(input_chars) > 1 else ''
        next_text = ' '.join(next) if next else ''

        # prev 是普通序列时包成 coverage；调用点若已传 '[a b c]' 则原样使用
        fea_prev = prev if prev_wrapped else (('[%s]' % prev) if prev else '')

        # 过滤掉 coverage 里缺失的字形（对应原 fontforge 的静默忽略）
        fea_prev = self._filter_coverage(fea_prev)
        fea_next = self._filter_coverage(next_text)

        seq = []
        if fea_prev.strip():
            seq.append(fea_prev.strip())
        seq.append(cur + "'")
        if fea_next.strip():
            seq.append(fea_next.strip())
        self._calt_rules.append('sub %s by %s;' % (' '.join(seq), ligature_name))

    # ---- 过滤 coverage 字符串里不存在的字形（'[a b c]' -> 只保留存在的）----
    def _filter_coverage(self, text):
        if not text:
            return ''
        order = set(self.font.getGlyphOrder())

        def repl(m):
            kept = [g for g in m.group(1).split() if g in order]
            return '[%s]' % ' '.join(kept) if kept else ''

        return re.sub(r'\[([^\]]*)\]', repl, text)

    # ---- 组合两个字形成新字形（composite glyph，对应原 combine_two_char）----
    def _combine_two_char(self, input_chars, ligature_name, needLayout=False):
        # hmtx[glyph] 返回 (advanceWidth, leftSideBearing)，[0] 即步进宽度。
        # 第二个字形是前置元音（如 ᩮ），要显示在第一个字形（基字/连字）左侧：
        #   - 第二个字形放在原点 x=0
        #   - 第一个字形右移 w1（前置元音的步进宽度），紧贴其右侧
        #   - 组合字形总步进宽度 = w0 + w1，整簇占满 [0, w0+w1]，右侧不留空白
        # （与模板字体 ATaiThamKHNew 中 uni1A36.63_uni1A6E 的组合方式一致：
        #   uni1A6E 在 x=0，uni1A36.63 在 x=uni1A6E 的步进宽度处）
        w0 = self.font['hmtx'][input_chars[0]][0]
        w1 = self.font['hmtx'][input_chars[1]][0]
        total_width = (w0 + w1) if not needLayout else 0

        glyph = Glyph()
        glyph.numberOfContours = -1  # composite
        comp0 = GlyphComponent()
        comp0.glyphName = input_chars[0]
        comp1 = GlyphComponent()
        comp1.glyphName = input_chars[1]
        if needLayout:
            comp0.x, comp0.y = 0, 0
            comp1.x, comp1.y = 0, 0
        else:
            comp0.x, comp0.y = w1, 0
            comp1.x, comp1.y = 0, 0
        comp0.flags = 0
        comp1.flags = 0
        glyph.components = [comp0, comp1]

        order = self.font.getGlyphOrder()
        if ligature_name not in order:
            order.append(ligature_name)
            self.font.setGlyphOrder(order)
        self.font['glyf'][ligature_name] = glyph
        # 左轴承（lsb）取前置元音的 lsb：组合字形左缘即前置元音的起始位置，
        # 与模板字体 ATaiThamKHNew 的 uni1A36.63_uni1A6E 一致（其 lsb == uni1A6E 的 lsb）。
        lsb = self.font['hmtx'][input_chars[1]][1] if not needLayout else 0
        self.font['hmtx'][ligature_name] = (total_width, lsb)
        self.set_glyphclass(ligature_name, 'baseglyph')

    # ---- 生成并编译 GDEF + GSUB ----
    def build(self):
        lines = []
        lines.append('languagesystem DFLT dflt;')
        lines.append('languagesystem lana NTA;')
        lines.append('languagesystem lana dflt;')
        lines.append('')

        base = self._glyphclass['base']
        ligature = self._glyphclass['ligature']
        mark = self._glyphclass['mark']
        if base or ligature or mark:
            lines.append('table GDEF {')
            lines.append('    GlyphClassDef %s, %s, %s, ;' % (
                self._cls(base), self._cls(ligature), self._cls(mark),
            ))
            lines.append('} GDEF;')
            lines.append('')

        liga_stages = [self._liga_rules, self._liga_rules2]
        if any(liga_stages):
            lines.append('feature liga {')
            # 每个 stage 一个独立 lookup：整形引擎按顺序各扫一遍，实现链式连字
            for i, rules in enumerate(liga_stages):
                if not rules:
                    continue
                lines.append('    lookup liga.stage%d {' % (i + 1))
                for rule in rules:
                    lines.append('        ' + rule)
                lines.append('    } liga.stage%d;' % (i + 1))
            lines.append('} liga;')
            lines.append('')

        if self._pref_rules:
            lines.append('feature pref {')
            for rule in self._pref_rules:
                lines.append('    ' + rule)
            lines.append('} pref;')
            lines.append('')

        if self._calt_rules:
            lines.append('feature calt {')
            for rule in self._calt_rules:
                lines.append('    ' + rule)
            lines.append('} calt;')

        fea_text = '\n'.join(lines)
        if fea_text.strip():
            addOpenTypeFeaturesFromString(self.font, fea_text)

    @staticmethod
    def _cls(glyphs):
        return '[%s]' % ' '.join(sorted(glyphs)) if glyphs else ''
