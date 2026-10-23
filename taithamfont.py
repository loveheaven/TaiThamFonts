# -*- coding: utf-8 -*-
"""把 Sangdang 这类“非 Unicode 自定义字体”转换成 Unicode 字体的脚本。

背景：
  Sangdang 系列（sangdangk.00new-Normal.ttf ~ sangdangk.40new-Normal.ttf）是
  老式的傣兰纳文（Tai Tham / Lanna）字体。它们不是用标准 Unicode 码位存储字符，
  而是把傣文字母“塞”在 ASCII 字符（如 '!', 'A', 'a' 等）的位置上，属于自定义编码。

  例如：'!' 实际画的是 ᨠ（U+1A20），'#' 画的是 ᨡ（U+1A21），依此类推。

本脚本按子命令运行（全部基于 fontTools/Pillow，用系统 python3 即可，不再依赖 FontForge）：

  python3 taithamfont.py convert [编号 ...]
      逐字打开 Sangdang 源字体，按对照表把字形重命名为标准 Unicode 字形名并设置码位，
      生成连字/预置基字/语境替换等 OpenType 特性，补充缺失字形，
      最后输出 “sangdangk.NNunicode-Normal.ttf”。
      不给编号则转换全部（0~40，跳过源文件不存在的 33、39）。
      需要模板字体 ATaiThamKHNew-Regular.ttf（由 .sfd 导出，用于补缺失字形）。

  python3 taithamfont.py showfont
      用一批参考字体渲染傣文样例文本，生成 PNG 预览图（需要 Pillow）。

  python3 taithamfont.py difffont
      对比 Noto 与 Sangdang 14 的渲染效果，生成 compare_both.png（需要 Pillow）。

  python3 taithamfont.py printgsub <字体路径>
      用 fontTools 打印指定字体的 GSUB/GPOS 表结构（脚本、语言系统、特性、lookup、锚点）。
"""

import argparse
import os
import sys

# 让 `fontforge -script` 运行时能 import 同目录下拆分的各模块。
_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# 源字体里不存在的编号，convert 时默认跳过。
_DEFAULT_SKIP = (33, 39)


def _default_numbers():
    return [i for i in range(41) if i not in _DEFAULT_SKIP]


def build_parser():
    parser = argparse.ArgumentParser(
        prog='taithamfont',
        description='Sangdang 非 Unicode 字体 -> Unicode 字体的转换与预览工具。',
    )
    sub = parser.add_subparsers(dest='command', metavar='command')

    p_convert = sub.add_parser('convert', help='把 Sangdang 源字体转换成 Unicode 字体')
    p_convert.add_argument(
        'fonts', nargs='*', type=int, metavar='N',
        help='要转换的字体编号（可多个）；留空则转换全部（跳过 33、39）',
    )

    sub.add_parser('showfont', help='用参考字体渲染傣文样例并输出 PNG 预览图')
    sub.add_parser('difffont', help='对比 Noto 与 Sangdang 14 的渲染效果')

    p_gsub = sub.add_parser('printgsub', help='打印指定字体文件的 GSUB/GPOS 表结构')
    p_gsub.add_argument('font', help='字体文件路径（.ttf / .otf 等）')

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == 'convert':
        from sangdang_convert import convert_sangdang
        numbers = args.fonts if args.fonts else _default_numbers()
        convert_sangdang(numbers)
    elif args.command == 'showfont':
        from preview import showFont
        showFont()
    elif args.command == 'difffont':
        from preview import diffFont
        diffFont()
    elif args.command == 'printgsub':
        from gsub_dump import print_gsub_gpos_from_path
        print_gsub_gpos_from_path(args.font)

    return 0


# 入口：被 `fontforge -script` 直接执行时运行（顶层调用以兼容 FontForge 的执行方式）。
main()
