#!/usr/bin/env bash
#
# Emit publish-ready artifact source from the standalone HTML file.
#
# workshop-builder/index.html is a complete, double-clickable HTML document.
# When publishing it as a Claude artifact, the publishing system adds its own
# <!doctype>/<head>/<body> skeleton, so the page content must NOT carry its own
# <!doctype>/<html> wrapper. This script strips that outer wrapper and prints the
# publish-ready body to stdout.
#
# Usage:
#   scripts/artifact-src.sh index.html > /tmp/publish.html
#
set -euo pipefail
[ $# -eq 1 ] || { echo "usage: $0 <standalone.html>" >&2; exit 2; }
sed -E '/^<!doctype html>$/Id; /^<html[^>]*>$/Id; /^<\/html>$/Id' "$1"
