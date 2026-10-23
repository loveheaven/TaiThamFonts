# -*- coding: utf-8 -*-
"""用 fontTools 打印字体的 GSUB/GPOS 表结构（调试用，只依赖 fontTools）。"""

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables


def printGSUBAndGPOS(font):
    """打印 fontTools TTFont 对象的 GSUB/GPOS 表结构（脚本、语言系统、特性、lookup、锚点）。"""
    print('printGSUBAndGPOS:', list(font.keys()))
    for tag in ("GSUB", "GPOS"):
        if tag not in font:
            continue
        print("Table:", tag)

        table = font[tag].table

        if not table.ScriptList or not table.FeatureList:
            continue
        featureRecords = table.FeatureList.FeatureRecord
        lookupList = table.LookupList.Lookup
        for script in table.ScriptList.ScriptRecord:
            print("  Script:", script.ScriptTag)
            if not script.Script:
                print("    Null script.")
                continue
            languages = list(script.Script.LangSysRecord)
            if script.Script.DefaultLangSys:
                defaultlangsys = otTables.LangSysRecord()
                defaultlangsys.LangSysTag = "default"
                defaultlangsys.LangSys = script.Script.DefaultLangSys
                languages.insert(0, defaultlangsys)
            for langsys in languages:
                print("    Language:", langsys.LangSysTag)
                if not langsys.LangSys:
                    print("    Null language.")
                    continue
                features = [featureRecords[index] for index in langsys.LangSys.FeatureIndex]
                if langsys.LangSys.ReqFeatureIndex != 0xFFFF:
                    record = featureRecords[langsys.LangSys.ReqFeatureIndex]
                    requiredfeature = otTables.FeatureRecord()
                    requiredfeature.FeatureTag = "required(%s)" % record.FeatureTag
                    requiredfeature.Feature = record.Feature
                    features.insert(0, requiredfeature)
                for feature in features:
                    print("      Feature:", feature.FeatureTag)
                    lookups = feature.Feature.LookupListIndex
                    #print("        Lookups:", ",".join(str(l) for l in lookups))
                    if feature.FeatureTag == "mark":
                        for lookup in lookups:
                            for i in range(lookupList[lookup].SubTableCount):
                                #print(lookupList[lookup].__dict__)
                                #print(lookupList[lookup].SubTable[i].__dict__)
                                print("        Lookups:", lookup)
                                marks = lookupList[lookup].SubTable[i].MarkArray
                                bases = lookupList[lookup].SubTable[i].BaseArray
                                #print(marks.MarkRecord[0].__dict__)
                                for j in range(marks.MarkCount):
                                    mark_anchor = marks.MarkRecord[j].MarkAnchor
                                    print("           MarkAnchor:", lookupList[lookup].SubTable[i].MarkCoverage.glyphs[j],
                                          None if mark_anchor is None else mark_anchor.__dict__)
                                for j in range(bases.BaseCount):
                                    base_record = bases.BaseRecord[j]
                                    base_anchor = base_record.BaseAnchor[0] if base_record.BaseAnchor else None
                                    print("           BaseAnchor:", lookupList[lookup].SubTable[i].BaseCoverage.glyphs[j],
                                          None if base_anchor is None else base_anchor.__dict__)


def print_gsub_gpos_from_path(fontpath):
    """打开字体文件并打印其 GSUB/GPOS 表结构。

    fontpath: 字体文件路径（.ttf / .otf 等）。
    """
    font = TTFont(fontpath)
    printGSUBAndGPOS(font)
