# -*- coding: utf-8 -*-
"""Sangdang 非 Unicode 自定义编码 -> Unicode 字形信息对照表。

把 Sangdang 源字体里被“借用”的 ASCII 码位（如 '!'、'A'）映射到标准
Unicode 字形名（uniXXXX）。格式：oldname -> (newname, glyphclass, [ligature sequence])。
"""

sangdangk_35_table = {
    
    '!' : ('uni1A20' , 'baseglyph',), #0021, ᨣᨠ
'#' : ('uni1A21' , 'baseglyph',), #0023, ᨣᨡ
'$' : ('uni1A23' , 'baseglyph',), #0024, ᨣᨣ
'%' : ('uni1A24' , 'baseglyph',), #0025, ᨣᨤ
'&' : ('uni1A25' , 'baseglyph',), #0026, ᨣᨥ
'(' : ('uni1A26' , 'baseglyph',), #0028, ᨣᨦ
')' : ('uni1A27' , 'baseglyph',), #0029, ᨣᨧ
',' : ('uni1A28' , 'baseglyph',), #002c, ᨣᨨ
'.' : ('uni1A29' , 'baseglyph',), #002e, ᨣᨩ
':' : ('uni1A2A' , 'baseglyph',), #003a, ᨣᨪ
';' : ('uni1A2B' , 'baseglyph',), #003b, ᨣᨫ
'<' : ('uni1A2C' , 'baseglyph',), #003c, ᨣᨬ
'=' : ('uni1A2D' , 'baseglyph',), #003d, ᨣᨭ
'>' : ('uni1A2E' , 'baseglyph',), #003e, ᨣᨮ
'?' : ('uni1A2F' , 'baseglyph',), #003f, ᨣᨯ
'@' : ('uni1A30' , 'baseglyph',), #0040, ᨣᨰ
'A' : ('uni1A31' , 'baseglyph',), #0041, ᨣᨱ
'B' : ('uni1A32' , 'baseglyph',), #0042, ᨣᨲ
'C' : ('uni1A33' , 'baseglyph',), #0043, ᨣᨳ
'D' : ('uni1A34' , 'baseglyph',), #0044, ᨣᨴ
'E' : ('uni1A35' , 'baseglyph',), #0045, ᨣᨵ
'F' : ('uni1A36' , 'baseglyph',), #0046, ᨣᨶ
'G' : ('uni1A37' , 'baseglyph',), #0047, ᨣᨷ
'H' : ('uni1A38' , 'baseglyph',), #0048, ᨣᨸ
'I' : ('uni1A39' , 'baseglyph',), #0049, ᨣᨹ
'J' : ('uni1A3A' , 'baseglyph',), #004a, ᨣᨺ
'K' : ('uni1A3B' , 'baseglyph',), #004b, ᨣᨻ
'L' : ('uni1A3C' , 'baseglyph',), #004c, ᨣᨼ
'M' : ('uni1A3D' , 'baseglyph',), #004d, ᨣᨽ
'N' : ('uni1A3E' , 'baseglyph',), #004e, ᨣᨾ
'O' : ('uni1A3F' , 'baseglyph',), #004f, ᨣᨿ
'P' : ('uni1A40' , 'baseglyph',), #0050, ᨣᩀ
'Q' : ('uni1A41' , 'baseglyph',), #0051, ᨣᩁ
'Ö' : ('uni1A42' , 'baseglyph',),
'×' : ('uni1A44' , 'baseglyph',),
'R' : ('uni1A43' , 'baseglyph',), #0052, ᨣᩃ
'S' : ('uni1A45' , 'baseglyph',), #0053, ᨣᩅ
'T' : ('uni1A46' , 'baseglyph',), #0054, ᨣᩆ
'U' : ('uni1A47' , 'baseglyph',), #0055, ᨣᩇ
'V' : ('uni1A48' , 'baseglyph',), #0056, ᨣᩈ
'W' : ('uni1A49' , 'baseglyph',), #0057, ᨣᩉ
'X' : ('uni1A4A' , 'baseglyph',), #0058, ᨣᩊ
'Y' : ('uni1A4B' , 'baseglyph',), #0059, ᨣᩋ
'Z' : ('uni1A4C' , 'baseglyph',), #005a, ᨣᩌ
'š' : ('uni1A4E' , 'baseglyph',),
'›' : ('uni1A4F' , 'baseglyph',), #203a, ᨣᩏ
'œ' : ('uni1A50' , 'baseglyph',),
'ž' : ('uni1A51' , 'baseglyph',), #017e, ᨣᩑ
'‰' : ('uni1A53' , 'baseglyph',), #2030, ᨣᩓ
'“' : ('uni1A54' , 'baseglyph',), #201c, ᨣᩔ

'\\' : ('uni1A20.sub1' , '', ['uni1A60' , 'uni1A20']), #005c, ᨣ᩠ᨠ
']' : ('uni1A20.sub2' , '',), #005d, ᨣ᩠ᨠ done
'^' : ('uni1A21.sub' , '' , ['uni1A60' , 'uni1A21']), #005e, ᨣ᩠ᨡ
'_' : ('uni1A23.sub' , '' , ['uni1A60' , 'uni1A23']), #005f, ᨣ᩠ᨣ
'`' : ('uni1A25.sub' , '' , ['uni1A60' , 'uni1A25']), #0060, ᨣ᩠ᨥ
'a' : ('uni1A25.sub2' , '',),
'b' : ('uni1A26.sub' , '' , ['uni1A60' , 'uni1A26']), #0062, ᨣ᩠ᨦ
'c' : ('uni1A27.sub' , '' , ['uni1A60' , 'uni1A27']), #0063, ᨣ᩠ᨧ
'd' : ('uni1A28.sub1' , '', ['uni1A60' , 'uni1A28']), #0064, ᨣ᩠ᨨ
'‚' : ('uni1A28.sub2' , '',), #done
'e' : ('uni1A29.sub' , '' , ['uni1A60' , 'uni1A29']), #0065, ᨣ᩠ᨩ
'f' : ('uni1A2B.sub' , '' , ['uni1A60' , 'uni1A2B']), #0066, ᨣ᩠ᨫ
'g' : ('uni1A2C.sub' , '', ['uni1A60' , 'uni1A2C']), #0067, ᨣ᩠ᨬ
'h' : ('uni1A2C.2C' , 'baseligature',), #0068, ᨣᨬᩚ done
'™' : ('uni1A2C.sub2' , '',), #2122, ᨣᨬ done
'i' : ('uni1A2D.sub' , '', ['uni1A60' , 'uni1A2D']), #0069, ᨣ᩠ᨭ
'k' : ('uni1A2D.2E' , '', ['uni1A2D', 'uni1A5B']), #006b, ᨣᨮ
'j' : ('uni1A2E.sub' , '' , ['uni1A60' , 'uni1A2E']), #006a, ᨣ᩠ᨮ
'l' : ('uni1A2F.sub' , '' , ['uni1A60' , 'uni1A2F']), #006c, ᨣ᩠ᨯ
'm' : ('uni1A30.sub2' , '',), #006d, ᨣ᩠ᨰ
'n' : ('uni1A30.sub' , '', ['uni1A60', 'uni1A30']), #006e, ᨣ᩠ᨰ
'o' : ('uni1A31.sub1' , '', ['uni1A60' , 'uni1A31']), #006f, ᨣ᩠ᨱ
'p' : ('uni1A31.sub2' , '',), #0070, ᨣ᩠ᨱ done
'q' : ('uni1A32.sub1' , '', ['uni1A60' , 'uni1A32']), #0071, ᨣ᩠ᨲ
'Þ' : ('uni1A32.sub2' , '',), #00de, ᨣ᩠ᨲ done
'Û' : ('uni1A32.45' , '', ['uni1A32.sub1', 'uni1A45.sub1']), #00db, ᨣ᩠ᨲ᩠ᩅ
'r' : ('uni1A33.sub' , '' , ['uni1A60' , 'uni1A33']), #0072, ᨣ᩠ᨳ
's' : ('uni1A34.sub' , '' , ['uni1A60' , 'uni1A34']), #0073, ᨣ᩠ᨴ
't' : ('uni1A35.sub' , '' , ['uni1A60' , 'uni1A35']), #0074, ᨣ᩠ᨵ
'u' : ('uni1A36.sub' , '', ['uni1A60' , 'uni1A36'],), #0075, ᨣ᩠ᨶ
'v' : ('uni1A36.63', 'baseligature', ['uni1A36' , 'uni1A63'],), #0076, ᨣᨶᩣ
'x' : ('uni1A37.sub' , '' , ['uni1A60' , 'uni1A37']), #0078, ᨣ᩠ᨷ
'y' : ('uni1A37.sub2' , '',), #done
'z' : ('uni1A39.sub' , '' , ['uni1A60' , 'uni1A39']), #007a, ᨣ᩠ᨹ
'{' : ('uni1A3B.sub' , '' , ['uni1A60' , 'uni1A3B']), #007b, ᨣ᩠ᨻ
'}' : ('uni1A3D.sub1' , '', ['uni1A60' , 'uni1A3D']), #007d, ᨣ᩠ᨽ
'~' : ('uni1A3D.sub2' , '',), # done
'€' : ('uni1A3E.sub' , '', ['uni1A60' , 'uni1A3E']), #20ac, ᨣ᩠ᨾ
'ƒ' : ('uni1A3F.sub1' , '', ['uni1A60' , 'uni1A3F']), #0192, ᨣ᩠ᨿ
'„' : ('uni1A3F.sub2' , '', ), #201e, ᨣ᩠ᨿ done
'†' : ('uni1A41.sub' , '' , ['uni1A60' , 'uni1A41']), #2020, ᨣ᩠ᩁ
'ˆ' : ('uni1A43.sub' , '' , ['uni1A60' , 'uni1A43']), #02c6, ᨣ᩠ᩃ
'‹' : ('uni1A45.sub1' , '', ['uni1A60' , 'uni1A45']), #2039, ᨣ᩠ᩅ
'Ú' : ('uni1A45.sub2' , '',), #2039, ᨣ᩠ᩅ done
'²' : ('uni1A45.3F' , '', ['uni1A45.sub1', 'uni1A3F.sub1']), #00b2, ᨣ᩠ᩅ᩠ᨿ  
'³' : ('uni1A45.3F.2' , '',), #00b3, ᨣᩅ᩠ᨿ,  done
'Œ' : ('uni1A46.sub' , '', ['uni1A60' , 'uni1A46']), #0152, ᨣ᩠ᩆ
'Ž' : ('uni1A47.sub' , '' , ['uni1A60' , 'uni1A47']), #017d, ᨣ᩠ᩇ
'”' : ('uni1A48.sub' , '' , ['uni1A60' , 'uni1A48']), #201d, ᨣ᩠ᩈ
'•' : ('uni1A49.sub1' , '', ['uni1A60' , 'uni1A49']), #2022, ᨣ᩠ᩉ done
'–' : ('uni1A49.sub2' , '',), #2013, ᨣ᩠ᩉ done
'Í' : ('uni1A4A.49' , 'baseligature', ['uni1A4A', 'uni1A60' , 'uni1A49']), #00cd, ᨣᩊ᩠ᩉ
'—' : ('uni1A4A.sub' , '',['uni1A60' , 'uni1A4A']),
'Ý' : ('uni1A55' , 'baseglyph',), #00dd, ᨣᩕ
'‡' : ('uni1A56.sub2' , 'mark',), #2021, ᨣᩖ
'Š' : ('uni1A56' , 'mark',), #0160, ᨣᩖU+0160
'Ù' : ('uni1A57' , 'mark',), # ᩗ
'¶' : ('uni1A58' , 'mark',), #00b6, ᨣᩘ
'|' : ('uni1A5B' , 'mark',), #007c, ᨣ ᩛ
'ô' : ('uni1A5C' , 'mark',), #00f4, ᨣᩜ
'w' : ('uni1A5D' , 'mark',), #0077, ᨣᩝ
'‘' : ('uni1A5E' , 'mark',), #2018, ᨣ ᩞ
'’' : ('uni1A5E.sub' , 'mark',), #2019, ᨣ ᩞ
'Ÿ' : ('uni1A61' , 'baseglyph',), #0178, ᨣᩡ
'¾' : ('uni1A62' , 'mark',), #00be, ᨣᩢ
'À' : ('uni1A62.62' , 'mark',), #00c0, ᨣᩢ᩶ done
'Á' : ('uni1A62.75' , 'mark', ['uni1A62', 'uni1A75']), #00c1, ᨣᩢ᩵ done
'ò' : ('uni1A63' , 'baseglyph',), #00f2, ᨣᩣ
'¡' : ('uni1A64' , 'baseglyph',), #00a1, ᨣᩤ
'¢' : ('uni1A65' , 'mark',), #00a2, ᨣᩥ
'¦' : ('uni1A65.74' , 'mark', ['uni1A65', 'uni1A74']), #00a6, ᨣᩥᩴ
'£' : ('uni1A66' , 'mark',), #00a3, ᨣᩦ
'¤' : ('uni1A67' , 'mark',), #00a4, ᨣᩧ
'¥' : ('uni1A68' , 'mark',), #00a5, ᨣᩨ
'§' : ('uni1A69' , 'mark',), #00a7, ᨣᩩ
'©' : ('uni1A69.sub' , 'baseglyph',), #00a9, ᨣᩩ done
'¨' : ('uni1A6A' , 'mark',), #00a8, ᨣᩪ
'ª' : ('uni1A6A.sub' , 'baseglyph',), #00aa, ᨣᩪ done
'¸' : ('uni1A6B' , 'mark',), #00b8, ᨣᩫ
'˜' : ('uni1A6C' , 'mark',), #02dc, ᨣᩬ
'Ã' : ('uni1A6C.sub' , ''),  #done
'°' : ('uni1A6D' , 'baseglyph',), #00b0, ᨣᩭ
'±' : ('uni1A6D.sub' , 'mark',), #00b1, ᨣᩭ  done
'«' : ('uni1A6E' , 'baseglyph',), #00ab, ᨣᩮ
'¬' : ('uni1A6F' , 'baseglyph',), #00ac, ᨣᩯ
'¯' : ('uni1A70' , 'baseglyph',), #00af, ᨣᩰ
'Ì' : ('uni1A71' , 'baseglyph',), #00cc, ᨣᩱ
'¹' : ('uni1A73' , 'mark',), #00b9, ᨣᩳ
'´' : ('uni1A74' , 'mark',), #00b4, ᨣᩴ
'®' : ('uni1A74.63' , 'baseligature', ['uni1A63', 'uni1A74']), #00ae, ᨣᩣᩴ
'Â' : ('uni1A75' , 'mark',), #00c2, ᨣ᩵
'Ð' : ('uni1A75.sub1' , 'mark',), #00d0, ᨣ᩵, done
'¿' : ('uni1A76' , 'mark',), #00bf, ᨣ᩶
'»' : ('uni1A77' , 'mark',),
'¼' : ('uni1A78' , 'mark',),
'½' : ('uni1A79' , 'mark',),
'º' : ('uni1A7B' , 'mark',), #00ba, ᨣ᩻ 
'Ä' : ('uni1A7C' , 'mark',), #00c4, ᨣ᩼ 
'Å' : ('uni1A7C.sub' , 'mark',), #done
'ß' : ('uni1A81' , '',), #00df, ᨣ᪁
'à' : ('uni1A82' , 'baseglyph',), #00e0, ᨣ᪂
'á' : ('uni1A83' , 'baseglyph',), #00e1, ᨣ᪃
'â' : ('uni1A84' , 'baseglyph',), #00e2, ᨣ᪄
'ã' : ('uni1A85' , 'baseglyph',), #00e3, ᨣ᪅
'ä' : ('uni1A86' , 'baseglyph',), #00e4, ᨣ᪆
'å' : ('uni1A87' , 'baseglyph',), #00e5, ᨣ᪇
'æ' : ('uni1A88' , 'baseglyph',), #00e6, ᨣ᪈
'ç' : ('uni1A89' , 'baseglyph',), #00e7, ᨣ᪉
'ñ' : ('uni1A90' , 'baseglyph',), #00f1, ᨣ᪐
'è' : ('uni1A91' , 'baseglyph',), #00e8, ᨣ᪑
'é' : ('uni1A92' , 'baseglyph',), #00e9, ᨣ᪒
'ê' : ('uni1A93' , 'baseglyph',), #00ea, ᨣ᪓
'ë' : ('uni1A94' , 'baseglyph',), #00eb, ᨣ᪔
'ì' : ('uni1A95' , 'baseglyph',), #00ec, ᨣ᪕
'í' : ('uni1A96' , 'baseglyph',), #00ed, ᨣ᪖
'î' : ('uni1A97' , 'baseglyph',), #00ee, ᨣ᪗
'ï' : ('uni1A98' , 'baseglyph',), #00ef, ᨣ᪘
'ð' : ('uni1A99' , 'baseglyph',), #00f0, ᨣ᪙
'Æ' : ('uni1AA7' , 'baseglyph',), #00c6, ᨣᪧ
'µ' : ('uni1AA8' , 'baseglyph',), #00b5, ᨣ᪨
'·' : ('uni1AA9' , 'baseglyph',), #00b7, ᨣ᪩
'Ø' : ('uni1AAA' , 'baseglyph',), #00d8, ᨣ᪪
'Ç' : ('uni1AAB' , 'baseglyph',), #00c7, ᨣ᪫
'Î' : ('uni1A50.63', 'baseligature',),
'Ņ' : ('uni1A7F', 'baseglyph',), # U+0145  ᩿

# --- 未使用的拉丁字符：保留其自身 Unicode，不参与傣文映射 ---
# 下列 oldname 是 sangdang 源字体里存在、但没有被借用去表示傣文的普通
# 拉丁字母/数字/标点。这里逐一映射回它们自己的 Unicode 码位（uniXXXX），
# glyphclass 留空（不设置特殊类别）。
# '[' : ('uni005B', '',), # U+005B 和'¯' : ('uni1A70')重复了。
# 'õ' : ('uni002D', '',), # U+00F5 -重复了。
# 'ú' : ('uni002B', '',), # U+00FA +重复了。
# 'Õ' : ('uni002F', '',), # U+00D5 /
# 'Ż' : ('uni017B', '',), # U+017B 空白无字符
# '…' : ('uni2026', '',), # U+2026 空白无字符
# '"' : ('uni0022', '',), # U+0022 空白无字符
# "'" : ('uni0027', '',), # U+0027 空白无字符

'É' : ('uni0028', '',), # U+00C9 (
'Ê' : ('uni0029', '',), # U+00CA )
'Ë' : ('uni003F', '',), # U+00CB ?
'Ï' : ('uni003D', '',), # U+00CF =
'Ò' : ('uni210C', '',), # U+00D2 “
'Ó' : ('uni210D', '',), # U+00D3 ”
'Ô' : ('uni0025', '',), # U+00D4 %

'Ü' : ('uni002C', '',), # U+00DC ,
'ó' : ('uni0021', '',), # U+00F3 !
'û' : ('uni2212', '',), # U+00FB -
'ü' : ('uni00D7', '',), # U+00FC ×
'ý' : ('uni00F7', '',), # U+00FD ÷
'þ' : ('uni003A', '',), # U+00FE :
'ÿ' : ('uni003B', '',), # U+00FF ;
'È' : ('uni002E', '',), # U+00C8 .
'*' : ('uni002A', '',), # U+002A 星号
'+' : ('uni002B', '',), # U+002B 加号
'-' : ('uni002D', '',), # U+002D 连字符
'/' : ('uni002F', '',), # U+002F 斜杠
'0' : ('uni0030', '',), # U+0030 数字 0
'1' : ('uni0031', '',), # U+0031 数字 1
'2' : ('uni0032', '',), # U+0032 数字 2
'3' : ('uni0033', '',), # U+0033 数字 3
'4' : ('uni0034', '',), # U+0034 数字 4
'5' : ('uni0035', '',), # U+0035 数字 5
'6' : ('uni0036', '',), # U+0036 数字 6
'7' : ('uni0037', '',), # U+0037 数字 7
'8' : ('uni0038', '',), # U+0038 数字 8
'9' : ('uni0039', '',), # U+0039 数字 9


# 以下字符在 35.ttf 里有特殊字形，需要映射到特殊字形
'÷' : ('uni1A2A.tsub', 'baseglyph'), #35.ttf
'ù' : ('uni1A3A.tsub', 'baseglyph'), #35.ttf
'ø' : ('uni1A3C.tsub', 'baseglyph'), #35.ttf
'ö' : ('uni1A24.tsub', 'baseglyph'), #35.ttf
# 注：space(U+0020)、NUL(U+0000)、CR(U+000D) 是结构性字形（space/NULL/nonmarkingreturn），
#     需保留标准字形名，故不加入本表。



# ============================================================================
# 「不在 sangdangk_35_table 里的 oldname」——出现在某些 Sangdang 字体里、但未收录进
# 映射表的字符（扫描 00~40 共 39 个字体汇总），并标注所在字体编号：
#   U+0000 NUL              -> 00-32,35,37,38,40（缺 34,36）
#   U+0002 STX              -> 09
#   U+0009 HT 制表符         -> 09
#   U+000A LF 换行           -> 09
#   U+000D CR 回车           -> 00-32,35,37,38,40（缺 34,36）
#   U+0020 空格              -> 全部 39 字体
#   U+00A0 不间断空格 NBSP   -> 09
#   U+00AD 软连字符          -> 09
#   U+00D1 Ñ                -> 09,35
#   U+0158 Ř                -> 18
#   U+2610 ☐ 复选框          -> 38,40
#   U+2713 ✓ 对勾            -> 38,40
# （以上多为控制/空白字符，需保留标准字形名，故不作为映射条目，仅列出备查。）
#
# 下面 14 个是「字形名」风格的键（按字形名匹配，不是单个字符），
# 扫描 39 个字体确认：它们只存在于 35 字体里，其余字体无对应字形。
# ============================================================================
'Kha_2': ('uni1A21.tsub', 'baseglyph'), # 字体35
'Nga_2': ('uni1A26.tsub', 'baseglyph'), # 字体35
'Sha_2': ('uni1A28.tsub', 'baseglyph'), # 字体35
'Ja_2': ('uni1A29.tsub', 'baseglyph'), # 字体35
'Cha_2': ('uni1A2B.tsub', 'baseglyph'), # 字体35
'Da_2': ('uni1A2F.tsub', 'baseglyph'), # 字体35
'Tha_2': ('uni1A33.tsub', 'baseglyph'), # 字体35
'Na_2': ('uni1A36.tsub', 'baseglyph'), # 字体35
'Naa_2': ('uni1A36.63.tsub', 'baseligature'), # 字体35
'Ma_2': ('uni1A3E.tsub', 'baseglyph'), # 字体35
'Ra_2': ('uni1A41.tsub', 'baseglyph'), # 字体35
'Aa_2': ('uni1A4B.tsub', 'baseglyph'), # 字体35
'HangRa': ('uni1A55.tsub', 'baseglyph'), # 字体35
'perthousandthreequarters': ('uni1A53.62', 'baseligature'), # 字体35


}

