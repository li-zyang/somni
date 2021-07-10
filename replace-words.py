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


def main():

  parser = argparse.ArgumentParser(
    description = 'Replace words in selected files',
    epilog = wrap(dedent(r'''
    The config JSON file has the structure of (For example)
    {
      "select": ["../folder/*.md"],
      "restore": "",
      "mappings": {
        "康飞": ["秦阳"],
        "康俯": ["秦川"],
        "龙平": ["胡远"],
        "萧僳": ["陈申", "神棍"],
        "萧哥": ["申哥"],
        "石文": ["疯哥"],
        "宋乐安": ["杨宁清", "宁清"],
        "于然": ["文雅"],
        "白箫吟": ["秦晓梅"],
        "尹姐": ["娟姐"],
        "大平坝": ["M市", "川北"],
        "建州": ["省城"]
      },
      "paraendings": ["  \n", "\n\n"],
      "min_update": true
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
    required = True,
    type = argparse.FileType(encoding = 'utf-8'))

  args = parser.parse_args()

  config = json.load(args.config[0])
  searchwords = []
  for val in config["mappings"].values():
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
  for i, w in enumerate(config["paraendings"]):
    if i == 0:
      _search += '({})'.format(escape(w, r'.^$*+?{}\[]|():<#=!'))
    else:
      _search += '|({})'.format(escape(w, r'.^$*+?{}\[]|():<#=!'))
  paraendpat = re.compile(_search)
  for fp in Path(re.sub(r'[^/]+$', '', config["select"])).glob(re.search(r'[^/]+$', config["select"]).group(0)):
    restore = config.get("restore", None)
    if config.get("min_update", False) and restore and len(restore) and Path(restore).exists():
      if not re.search(r'\\|/$', restore):
        restore += '/'
      target = Path(restore + fp.name)
      if target.exists() and fp.stat().st_mtime <= target.stat().st_mtime:
        continue
    content = fp.read_text(encoding = 'utf-8')
    newlines = []    # tuple (index, replacespc)
    paraends = []    # tuple (index, symbol)
    pos = content.find('\n')
    while pos >= 0:
      nearbyparaend = paraendpat.search(content, pos = newlines[-1][0] if len(newlines) else 0)
      if nearbyparaend and nearbyparaend.start() <= pos and nearbyparaend.end() > pos:
        paraends.append((nearbyparaend.start(), nearbyparaend.group(0)))
        content = content[ : nearbyparaend.start()] + ' ' + content[nearbyparaend.end() : ]
      else:
        _0 = ord(content[pos - 1]) < 256 and ord(content[pos + 1]) < 256
        _1 = not content[pos - 1].isspace() and not content[pos + 1].isspace()
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
      if not matched:
        break
      found = False
      for key in config["mappings"].keys():
        for name in config["mappings"][key]:
          if name == matched.group(0):
            found = True
            break
        if found:
          break
      content = content[0 : matched.start()] + key + content[matched.end() : ]
      searchstart = matched.start() + len(key)
      if len(key) != len(name):
        for i in range(0, len(newlines)):
          if newlines[i][0] < matched.start():
            continue
          pos = newlines[i][0] + len(key) - len(name)
          _0 = ord(content[pos - 1]) < 256 and ord(content[pos + 1]) < 256
          _1 = not content[pos - 1].isspace() and not content[pos + 1].isspace()
          if _0 and _1:
            newlines[i] = (pos, True)
          else:
            newlines[i] = (pos, False)
        for i in range(0, len(paraends)):
          if paraends[i][0] < matched.start():
            continue
          paraends[i] = (paraends[i][0] + len(key) - len(name), paraends[i][1])
    i = 0
    j = 0
    mutations = []    # (idx, content, replace_or_insert)
    while i < len(newlines) or j < len(paraends):
      if i == len(newlines):
        mutations.append((paraends[j][0], paraends[j][1], True))
        j += 1
      elif j == len(paraends) or newlines[i][0] < paraends[j][0]:
        mutations.append((newlines[i][0], '\n', newlines[i][1]))
        i += 1
      else:
        mutations.append((paraends[j][0], paraends[j][1], True))
        j += 1
    for mut in reversed(mutations):
      if mut[2]:
        content = content[ : mut[0]] + mut[1] + content[mut[0] + 1 : ]
      else:
        content = content[ : mut[0]] + mut[1] + content[mut[0] : ]
    if config["restore"] and len(config["restore"]):
      if not re.search(r'\\|/$', config['restore']):
        config['restore'] += '/'
      Path(config["restore"]).mkdir(parents = True, exist_ok = True)
      Path(config["restore"] + fp.name).write_text(content, encoding = 'utf-8')
    else:
      fp.write_text(content, encoding = 'utf-8')
    

main() if __name__ == '__main__' else exit()

