#!/bin/bash
cd "$(dirname "$0")/assets"
MESSAGE="${1:-"Update from local - $(date '+%Y-%m-%d %H:%M')"}"
git add .
git commit -m "$MESSAGE"
git push origin master
