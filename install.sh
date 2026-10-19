#!/bin/bash

# TRIZ skill installer. Companion skill (install separately for the
# generate->verify loop): security-variant-verification
# https://github.com/chiangchenghsin-hash/security-variant-verification
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.openclaw/skills"

echo "Installing triz skill..."
mkdir -p "$INSTALL_DIR/triz"
cp -r "$SKILL_DIR/.claude/skills/triz/." "$INSTALL_DIR/triz/"

# Make the CLI executable; create symlink for easy access
chmod +x "$INSTALL_DIR/triz/triz.js" 2>/dev/null || true
ln -sf "$INSTALL_DIR/triz/triz.js" "$HOME/.npm-global/bin/triz" 2>/dev/null || true

echo "Installed: $INSTALL_DIR/triz/"
echo "Companion (install separately if needed): security-variant-verification -> https://github.com/chiangchenghsin-hash/security-variant-verification"
