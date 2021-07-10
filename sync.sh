#!/usr/bin/bash

set -eu
python replace-words.py -c config.json
git add .
git commit -m '-'
echo "Complete. Push to remote manually"
