#!/bin/bash

# TRIZ skill set installer: TRIZ + security-variant-verification (companion pair).
# The pair is one product: TRIZ generates candidate designs; SVV machine-verifies
# them (differential testing + release gate). Install both or neither.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.openclaw/skills"

echo "Installing TRIZ skill set (triz + security-variant-verification)..."

# Create skills directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# --- TRIZ skill (legacy flat layout, kept unchanged for existing installs) ---
cp "$SKILL_DIR/SKILL.md" "$INSTALL_DIR/triz.SKILL.md"
cp "$SKILL_DIR/triz.js" "$INSTALL_DIR/triz.js"
cp "$SKILL_DIR/package.json" "$INSTALL_DIR/triz.package.json"
cp "$SKILL_DIR/README.md" "$INSTALL_DIR/triz.README.md"

# Make the CLI executable
chmod +x "$INSTALL_DIR/triz.js"

# --- Companion skill: security-variant-verification ---
# Installed as a sibling skill directory (SKILL.md + scripts/ + references/ +
# examples/). A second skill nested inside another skill's tree is NOT
# auto-registered by most installers — deliver it explicitly. The skill's
# workflow calls scripts/diff_test.py and references/, so the whole tree ships.
mkdir -p "$INSTALL_DIR/security-variant-verification"
cp -r "$SKILL_DIR/.claude/skills/security-variant-verification/." \
      "$INSTALL_DIR/security-variant-verification/"

# Create symlink for easy access
ln -sf "$INSTALL_DIR/triz.js" "$HOME/.npm-global/bin/triz" 2>/dev/null || true

echo "Installed skill pair:"
echo "  $INSTALL_DIR/triz.SKILL.md  (TRIZ skill)"
echo "  $INSTALL_DIR/security-variant-verification/  (SVV companion skill)"
echo "Usage: triz --help"
