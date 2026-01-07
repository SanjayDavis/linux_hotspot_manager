#!/bin/bash
# Uninstall script for WiFi Hotspot Manager

APP_NAME="wifi-hotspot-manager"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "Uninstalling WiFi Hotspot Manager..."

# Remove application files
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "Removed application files"
fi

# Remove launcher
if [ -f "$BIN_DIR/$APP_NAME" ]; then
    rm -f "$BIN_DIR/$APP_NAME"
    echo "Removed launcher"
fi

# Remove desktop entry
if [ -f "$DESKTOP_DIR/$APP_NAME.desktop" ]; then
    rm -f "$DESKTOP_DIR/$APP_NAME.desktop"
    echo "Removed desktop entry"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo
echo "WiFi Hotspot Manager has been uninstalled."
