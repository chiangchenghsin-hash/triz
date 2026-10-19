#!/bin/bash

# TRIZ skill set installer: triz + security-variant-verification (companion pair).
# The pair is one product: TRIZ generates candidate designs; SVV machine-verifies
# them (differential testing + release gate). Install both or neither.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.openclaw/skills"

echo "Installing TRIZ skill set (triz + security-variant-verification)..."

# Two sibling skill directories — the only layout where both register as
# skills (scanners pick up skills/<name>/SKILL.md one level deep; a skill
# nested inside another skill's tree is silently dropped).
mkdir -p "$INSTALL_DIR/triz"
cp -r "$SKILL_DIR/.claude/skills/triz/." "$INSTALL_DIR/triz/"
mkdir -p "$INSTALL_DIR/security-variant-verification"
cp -r "$SKILL_DIR/.claude/skills/security-variant-verification/." \
      "$INSTALL_DIR/security-variant-verification/"

# Make the CLI executable; create symlink for easy access
chmod +x "$INSTALL_DIR/triz/triz.js" 2>/dev/null || true
ln -sf "$INSTALL_DIR/triz/triz.js" "$HOME/.npm-global/bin/triz" 2>/dev/null || true

echo "Installed skill pair:"
echo "  $INSTALL_DIR/triz/"
echo "  $INSTALL_DIR/security-variant-verification/"
echo "Usage: triz --help"
