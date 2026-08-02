#!/usr/bin/env bash
#
# Emit publish-ready artifact source from a standalone HTML file.
#
# The repo files (AIC-Sponsorship-Studio.html, AIC-Studio-Setup-Guide.html) are
# complete, double-clickable HTML documents. When publishing one as a Claude
# artifact, the publishing system adds its own <!doctype>/<head>/<body> skeleton,
# so the page content must NOT carry its own <!doctype>/<html> wrapper. This
# script strips that outer wrapper and prints the publish-ready body to stdout.
#
# Usage:
#   scripts/artifact-src.sh AIC-Sponsorship-Studio.html > /tmp/publish.html
#
set -euo pipefail
[ $# -eq 1 ] || { echo "usage: $0 <standalone.html>" >&2; exit 2; }
sed -E '/^<!doctype html>$/Id; /^<html[^>]*>$/Id; /^<\/html>$/Id' "$1"
