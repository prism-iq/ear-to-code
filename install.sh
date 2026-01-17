#!/bin/bash
# Install ear-to-code as a persistent service

set -e
cd "$(dirname "$0")"

echo "[INSTALL] Setting up ear-to-code..."

# Create logs dir
mkdir -p logs

# Make scripts executable
chmod +x ear.py watcher.py export_for_ai.py run.sh

# Setup systemd user service
mkdir -p ~/.config/systemd/user
cp ear-to-code.service ~/.config/systemd/user/

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable ear-to-code

echo "[INSTALL] Done!"
echo ""
echo "Commands:"
echo "  systemctl --user start ear-to-code    # Start"
echo "  systemctl --user status ear-to-code   # Status"
echo "  journalctl --user -u ear-to-code -f   # Logs"
echo ""
echo "Or run manually: ./run.sh"
echo ""
echo "API Keys (optional, set in environment):"
echo "  AUDD_API_TOKEN     - Song recognition (audd.io)"
echo "  SHAZAM_API_KEY     - Song recognition (RapidAPI)"
echo "  GENIUS_API_TOKEN   - Lyrics (genius.com)"
