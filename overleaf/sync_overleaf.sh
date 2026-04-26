#!/bin/bash
cd "$(dirname "$0")"
MESSAGE="${1:-"Update Overleaf submodule - $(date '+%Y-%m-%d %H:%M')"}"
cd assets && git pull origin master
cd ..
git add assets
git commit -m "$MESSAGE"
