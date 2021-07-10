#!/usr/bin/python3

import json
import os
import re
from pathlib import Path
from textwrap import dedent, wrap

import argparse

def escape(s, chlst):
  i = 0
  while i < len(s):
    if chlst.find(s[i]) != -1:
      s = s[ : i] + '\\' + s[i : ]
      i += 2
    else:
      i += 1
  return s


def dispunit(str, begin = None, width = None, *, breakword = False):
  # calculate display length of str or a tuple (index, deviation)
  # indicating the position of <width>
  unitseg = [
    (0x0000, 0),    # control characters
    (0x0020, 1),    # ASCII
    (0x007f, 0),    # DEL
    (0x0080, 0),    # empty
    (0x00a0, 1),    # EASCII
    (0x0100, 1),    # 拉丁文扩展   Latin Extended
    (0x0250, 1),    # 国际音标扩展  IPA Extensions
    (0x02B0, 1),    # 占位修饰符号  Spacing Modifier Letters
    (0x0300, 0),    # 附加標記  Combining Diacritics Marks
    (0x0370, 1),    # 希腊字母及科普特字母  Greek and Coptic
    (0x0400, 1),    # 西里尔字母   Cyrillic
    (0x0500, 1),    # 西里尔字母补充   Cyrillic Supplement
    (0x0530, 1),    # 亚美尼亚字母  Armenian
    (0x0590, 1),    # 希伯来文  Hebrew
    (0x0600, 1),    # （無法處理）
    (0x1100, 2),    # 諺文（朝鮮字）字母  Hangul Jamo
    (0x1200, 1),    # 吉兹字母  Ethiopic
    (0x1380, 1),    # 吉兹字母补充  Ethiopic Supplement
    (0x13A0, 1),    # （無法處理）
    (0x1800, 2),    # 蒙古文   Mongolian
    (0x1900, 1),    # （無法處理）
    (0x1950, 1),    # 德宏傣文  Tai Le
    (0x1980, 1),    # 新傣仂文  New Tai Lue
    (0x19E0, 1),    # （無法處理）
    (0x1A20, 1),    # 老傣文   Tai Tham
    (0x1AB0, 0),    # 组合变音标记扩展  Combining Diacritical Marks Extended
    (0x1B00, 1),    # （無法處理）
    (0x1C80, 1),    # 西里尔字母扩充-C   Cyrillic Extended-C
    (0x1C90, 1),    # （無法處理）
    (0x1D00, 1),    # 音标扩展  Phonetic Extensions
    (0x1D80, 1),    # 音标扩展补充  Phonetic Extensions Supplement
    (0x1DC0, 1),    # 结合附加符号补充  Combining Diacritics Marks Supplement
    (0x1E00, 1),    # 拉丁文扩展附加   Latin Extended Additional
    (0x1F00, 1),    # 希腊文扩展   Greek Extended
    (0x2000, 1),    # 常用标点  General Punctuation
    (0x2070, 1),    # 上标及下标   Superscripts and Subscripts
    (0x20A0, 1),    # 货币符号  Currency Symbols
    (0x20D0, 0),    # 组合用记号   Combining Diacritics Marks for Symbols
    (0x2100, 1),    # 字母式符号   Letterlike Symbols  ℀
    (0x2139, 2),    # 字母式符号   Letterlike Symbols  ℹ
    (0x213C, 1),    # 字母式符号   Letterlike Symbols  ℼ
    (0x2150, 2),    # 数字形式  Number Forms  ⅐
    (0x2153, 1),    # 数字形式  Number Forms  ⅓
    (0x2160, 2),    # 数字形式  Number Forms  Ⅰ
    (0x216C, 1),    # 数字形式  Number Forms  Ⅼ
    (0x2170, 2),    # 数字形式  Number Forms  ⅰ
    (0x217C, 1),    # 数字形式  Number Forms  ⅼ
    (0x2180, 2),    # 数字形式  Number Forms  ↀ
    (0x2181, 1),    # 数字形式  Number Forms  ↁ
    (0x2182, 2),    # 数字形式  Number Forms  ↂ
    (0x2183, 1),    # 数字形式  Number Forms  Ↄ
    (0x2186, 2),    # 数字形式  Number Forms  ↆ
    (0x2187, 1),    # 数字形式  Number Forms  ↇ
    (0x2188, 2),    # 数字形式  Number Forms  ↈ
    (0x218A, 1),    # 数字形式  Number Forms  ↊
    (0x218C, 0),    # 数字形式  Number Forms  ↌
    (0x2190, 1),    # 箭头  Arrows
    (0x2200, 1),    # 数学运算符   Mathematical Operators
    (0x2300, 1),    # 杂项工业符号  Miscellaneous Technical  ⌀
    (0x231A, 2),    # 杂项工业符号  Miscellaneous Technical  ⌚
    (0x231C, 1),    # 杂项工业符号  Miscellaneous Technical  ⌜
    (0x2322, 0),    # 杂项工业符号  Miscellaneous Technical  ⌢
    (0x2324, 2),    # 杂项工业符号  Miscellaneous Technical  ⌤
    (0x2329, 1),    # 杂项工业符号  Miscellaneous Technical  〈
    (0x232B, 2),    # 杂项工业符号  Miscellaneous Technical  ⌫
    (0x232D, 1),    # 杂项工业符号  Miscellaneous Technical  ⌭
    (0x2384, 2),    # 杂项工业符号  Miscellaneous Technical  ⎄
    (0x238C, 1),    # 杂项工业符号  Miscellaneous Technical  ⎌
    (0x238F, 2),    # 杂项工业符号  Miscellaneous Technical  ⎏
    (0x2393, 1),    # 杂项工业符号  Miscellaneous Technical  ⎓
    (0x23dc, 0),    # 杂项工业符号  Miscellaneous Technical  ⏜
    (0x23e9, 2),    # 杂项工业符号  Miscellaneous Technical  ⏩
    (0x2400, 1),    # 控制图片  Control Pictures
    (0x2440, 1),    # 光学识别符   Optical Character Recognition
    (0x2460, 1),    # 带圈字母和数字   Enclosed Alphanumerics
    (0x2491, 2),    # 带圈字母和数字   Enclosed Alphanumerics
    (0x249c, 1),    # 带圈字母和数字   Enclosed Alphanumerics
    (0x2500, 1),    # 制表符   Box Drawing
    (0x2580, 1),    # 方块元素  Block Elements
    (0x25A0, 1),    # 几何图形  Geometric Shapes
    (0x2600, ),    # 杂项符号  Miscellaneous Symbols
    (0x2700, ),    # 装饰符号  Dingbats
    (0x27C0, ),    # 杂项数学符号-A  Miscellaneous Mathematical Symbols-A
    (0x27F0, ),    # 追加箭头-A  Supplemental Arrows-A
    (0x2800, ),    # 盲文点字模型  Braille Patterns
    (0x2900, ),    # 追加箭头-B  Supplemental Arrows-B
    (0x2980, ),    # 杂项数学符号-B  Miscellaneous Mathematical Symbols-B
    (0x2A00, ),    # 追加数学运算符   Supplemental Mathematical Operator
    (0x2B00, ),    # 杂项符号和箭头   Miscellaneous Symbols and Arrows
    (0x2C00, ),    # 格拉哥里字母  Glagolitic
    (0x2C60, ),    # 拉丁文扩展-C   Latin Extended-C
    (0x2C80, ),    # 科普特字母   Coptic
    (0x2D00, ),    # 格鲁吉亚字母补充  Georgian Supplement
    (0x2D30, ),    # 提非纳文  Tifinagh
    (0x2D80, ),    # 吉兹字母扩展  Ethiopic Extended
    (0x2DE0, ),    # 西里尔字母扩展-A   Cyrillic Extended-A
    (0x2E00, ),    # 追加标点  Supplemental Punctuation
    (0x2E80, ),    # 中日韩汉字部首补充   CJK Radicals Supplement
    (0x2F00, ),    # 康熙部首  Kangxi Radicals
    (0x2FF0, ),    # 表意文字序列  Ideographic Description Characters
    (0x3000, ),    # 中日韩符号和标点  CJK Symbols and Punctuation
    (0x3040, ),    # 日文平假名   Hiragana
    (0x30A0, ),    # 日文片假名   Katakana
    (0x3100, ),    # 注音符号  Bopomofo
    (0x3130, ),    # 谚文兼容字母  Hangul Compatibility Jamo
    (0x3190, ),    # 汉文注释标志  Kanbun
    (0x31A0, ),    # 注音字母扩展  Bopomofo Extended
    (0x31C0, ),    # 中日韩笔画   CJK Strokes
    (0x31F0, ),    # 日文片假名拼音扩展   Katakana Phonetic Extensions
    (0x3200, ),    # 带圈的CJK字符及月份   Enclosed CJK Letters and Months
    (0x3300, ),    # 中日韩兼容字符   CJK Compatibility
    (0x3400, ),    # 中日韓統一表意文字擴展區A   CJK Unified Ideographs Extension A
    (0x4DC0, ),    # 易经六十四卦符号  Yijing Hexagrams Symbols
    (0x4E00, ),    # 中日韩统一表意文字   CJK Unified Ideographs
    (0xA000, ),    # 彝文音节  Yi Syllables
    (0xA490, ),    # 彝文字根  Yi Radicals
    (0xA4D0, ),    # 老傈僳文  Lisu
    (0xA500, ),    # 瓦伊语   Vai
    (0xA640, ),    # 西里尔字母扩展-B   Cyrillic Extended-B
    (0xA6A0, ),    # 巴姆穆文字   Bamum
    (0xA700, ),    # 声调修饰符号  Modifier Tone Letters
    (0xA720, ),    # 拉丁文扩展-D   Latin Extended-D
    (0xA800, ),    # 锡尔赫特文   Syloti Nagri
    (0xA830, ),    # 通用印度数字格式  Common Indic Number Forms
    (0xA840, ),    # 八思巴字  Phags-pa
    (0xA880, ),    # 索拉什特拉文  Saurashtra
    (0xA8E0, ),    # 天城文扩展   Devanagari Extended
    (0xA900, ),    # 克耶里字母   Kayah Li
    (0xA930, ),    # 勒姜字母  Rejang
    (0xA960, ),    # 谚文扩展-A  Hangul Jamo Extended-A
    (0xA980, ),    # 爪哇字母  Javanese
    (0xA9E0, ),    # 缅甸文扩展-B   Myanmar Extended-B
    (0xAA00, ),    # 占语字母  Cham
    (0xAA60, ),    # 缅甸文扩展-A   Myanmar Extended-A
    (0xAA80, ),    # 越南傣文  Tai Viet
    (0xAAE0, ),    # 曼尼普尔文扩展   Meetei Mayek Extensions
    (0xAB00, ),    # 吉兹字母扩展-A  Ethiopic Extended-A
    (0xAB30, ),    # 拉丁文扩展-E   Latin Extended-E
    (0xAB70, ),    # 切罗基语补充  Cherokee Supplement
    (0xABC0, ),    # 曼尼普尔文   Meetei Mayek
    (0xAC00, ),    # 谚文音节  Hangul Syllables
    (0xD7B0, ),    # 谚文字母扩展-B  Hangul Jamo Extended-B
    (0xD800, ),    # UTF-16的高半区  High-half zone of UTF-16
    (0xDC00, ),    # UTF-16的低半区  Low-half zone of UTF-16
    (0xE000, ),    # 私用区   Private Use Area
    (0xF900, ),    # 中日韩兼容表意文字   CJK Compatibility Ideographs
    (0xFB00, ),    # 連字表達形式  Alphabetic Presentation Forms
    (0xFB50, ),    # 阿拉伯字母表達形式-A   Arabic Presentation Forms A
    (0xFE00, ),    # 異體字选择器  Variation Selector
    (0xFE10, ),    # 竖排形式  Vertical Forms
    (0xFE20, ),    # 组合用半符号  Combining Half Marks
    (0xFE30, ),    # 中日韩兼容形式   CJK Compatibility Forms
    (0xFE50, ),    # 小寫变体形式  Small Form Variants
    (0xFE70, ),    # 阿拉伯文表達形式-B  Arabic Presentation Forms B
    (0xFF00, ),    # 半形及全形字符   Halfwidth and Fullwidth Forms
    (0xFFF0, ),    # 特殊字元區   Specials
  ]
  return 0


def main():

  parser = argparse.ArgumentParser(
    description = 'Replace words in selected files',
    epilog = wrap(dedent(r'''
    The config JSON file has the structure of (For example)
    {
      "select": ["../folder/*.md"],
      "restore": "",
      "mappings": {
        "康飞光": ["秦阳"],
        "康俯": ["秦川"],
        "龙良平": ["胡远"],
        "萧僳": ["神棍"],
        "萧哥": ["申哥"],
        "石文": ["疯哥"],
        "宋乐安": ["杨宁清", "宁清"],
        "白新知": [],
        "孙高超": [],
        "于忆然": ["文雅"],
        "白箫吟": ["秦晓梅"],
        "尹姐": ["娟姐"],
        "大平坝": ["M市", "川北"],
        "建州": ["省城"],
      },
      "searchbetweenlines": true,
      "keepwrappings": true,
      "altwrappinglength": 78,
      "paraendings": ["  \n", "\n\n"]
    }
    '''))
  )

  parser.add_argument(
    '-c', '--config', 
    dest = 'config', 
    nargs = 1, 
    metavar = 'FILE', 
    help = 'The config JSON file', 
    action = 'store', 
    type = open)

  args = parser.parse_args()

  avoid_lineend = '$([{£¥·‘“〈《「『【〔〖〝﹙﹛﹝＄（．［｛￡￥'
  avoid_linestart = '!%),.:;>?]}¢¨°·ˇˉ―‖’”…‰′″›℃∶、。〃〉》」』】〕〗〞︶︺︾﹀﹄﹚﹜﹞！＂％＇），．：；？］｀｜｝～￠'

  config = json.load(args.config)
  searchwords = []
  for val in config.mappings.values():
    searchwords += val
  searchwords.sort(key = lambda itm : - len(itm))
  _search = ''
  for i, w in enumerate(searchwords):
    if i == 0:
      _search += '({})'.format(w)
    else:
      _search += '|({})'.format(w)
  searchpat = re.compile(_search)
  _search = ''
  for i, w in enumerate(config.paraendings):
    if i == 0:
      _search += '({})'.format(escape(w, r'.^$*+?{}\[]|():<#=!'))
    else:
      _search += '|({})'.format(escape(w, r'.^$*+?{}\[]|():<#=!'))
  paraendpat = re.compile(_search)
  for fp in Path(re.sub(r'[^/]+$', '', config.select)).glob(re.search(r'[^/]+$', config.select).group(0)):
    content = fp.read_text()
    newlines = []    # tuple (index, replacespc)
    paraends = []    # tuple (index, symbol)
    pos = content.find('\n')
    while pos >= 0:
      nearbyparaend = paraendpat.search(content, pos = newlines[-1][0])
      if nearbyparaend and nearbyparaend.start() <= pos and nearbyparaend.end() > pos:
        paraends.append((nearbyparaend.start(), pos.group(0)))
        content = content[ : nearbyparaend.start()] + ' ' + content[nearbyparaend.end() : ]
      else:
        _0 = dispunit(content[pos - 1]) == 1 and dispunit(content[pos + 1]) == 1
        _1 = ' -'.find(content[pos - 1]) == -1 and ' -'.find(content[pos + 1]) == -1
        if _0 and _1:
          newlines.append((pos, True))
          content = content[ : pos] + ' ' + content[pos + 1 : ]
        else:
          newlines.append((pos, False))
          content = content[ : pos] + content[pos + 1 : ]
      pos = content.find('\n', pos)
    searchstart = 0
    while True:
      matched = searchpat.search(content, pos = searchstart)
      break if not matched
      found = False
      for key in config.mappings.keys():
        for name in config.mappings[key]:
          if name == matched.group(0):
            found = True
            break
        break if found
      content = content[0 : matched.start()] + key + content[matched.end() : ]
      searchstart = matched.start() + len(key)
      if not config.keepwrappings or dispunit(key) == dispunit(name):
        continue
      shiftlen = dispunit(key) - dispunit(name)
      for p_end in paraends:
        if p_end[0] >= matched.start():
          break
      i = 0
      while i < len(newlines) and shiftlen:
        cur = newlines[i]
        if cur < matched.start():
          i += 1
          continue
        if cur < p_end[0]:
          pre = newlines[i - 1] if i != 0 else 0
          lineunits = dispunit(content[pre : cur]) - shiftlen
          if abs(lineunits - config.altwrappinglength) > 4:
            shiftlen = lineunits - config.altwrappinglength
            lineunits = config.altwrappinglength
          idx, dev = dispunit(content, pre, lineunits)
          while idx > 0 and avoid_lineend.find(content[idx - 1]) != -1:
            idx, dev = (idx - 1, dev - dispunit(content[idx]))
          while idx < p_end[0] and avoid_linestart.find(content[idx]) != -1:
            idx, dev = (idx + 1, dev + dispunit(content[idx]))
          newlines[i] = (idx, content[idx].isspace())
          shiftlen += dev
          i += 1
        else:
          linestart = newlines[i - 1] if i != 0 else 0
          if dispunit(content[linestart : p_end[0]]) < config.altwrappinglength:
            break
          lineunits = dispunit(content[linestart : p_end[0]]) - shiftlen
          if abs(lineunits - config.altwrappinglength) > 4:
            shiftlen = lineunits - config.altwrappinglength
            lineunits = config.altwrappinglength
          idx, dev = dispunit(content, cur, lineunits)
          while idx > 0 and avoid_lineend.find(content[idx - 1]) != -1:
            idx, dev = (idx - 1, dev - dispunit(content[idx]))
          while idx < p_end[0] and avoid_linestart.find(content[idx]) != -1:
            idx, dev = (idx + 1, dev + dispunit(content[idx]))
          newlines.insert(i, (idx, content[idx].isspace()))
          break
    i = 0
    j = 0
    mutations = []    # (idx, content, replace_or_insert)
    while i < len(newlines) or j < len(paraends):
      if newlines[i][0] < paraends[j][1]:
        mutations.append((newlines[i], '\n', replacespc))
        i += 1
      else:
        mutations.append((paraends[j][0], paraends[j][1], True))
        j += 1
    for mut in reversed(mutations):
      if mut[2]:
        content = content[ : idx] + content + content[idx + 1 : ]
      else:
        content = content[ : idx + 1] + content + content[idx + 1 : ]
    if config.restore and len(config.restore):
      Path(config.restore).write_text(content)
    else:
      fp.write_text(content)
    

main() if __name__ == '__main__'
