#!/bin/bash
cd "$(dirname "$0")/assets"
echo "=== Uncommitted local changes ==="
git status
echo ""
echo "=== Local commits not pushed to Overleaf ==="
git fetch origin
git log origin/master..HEAD --oneline
