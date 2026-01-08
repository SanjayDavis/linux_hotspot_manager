#!/bin/bash
# Installation script for WiFi Hotspot Manager

set -e

echo "WiFi Hotspot Manager - Installation Script"
echo "==========================================="
echo

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "ERROR: Cannot detect Linux distribution"
    exit 1
fi

echo "Detected distribution: $DISTRO"
echo

# Install system dependencies
case $DISTRO in
    ubuntu|debian|linuxmint|pop)
        echo "Installing dependencies for Debian/Ubuntu-based systems..."
        sudo apt update
        sudo apt install -y \
            python3-gi \
            gir1.2-gtk-4.0 \
            gir1.2-adw-1 \
            network-manager \
            iw \
            linux-firmware
        ;;
    
    fedora|rhel|centos)
        echo "Installing dependencies for Fedora/RHEL-based systems..."
        sudo dnf install -y \
            python3-gobject \
            gtk4 \
            libadwaita \
            NetworkManager \
            iw \
            linux-firmware
        ;;
    
    arch|manjaro)
        echo "Installing dependencies for Arch-based systems..."
        sudo pacman -S --needed --noconfirm \
            python-gobject \
            gtk4 \
            libadwaita \
            networkmanager \
            iw \
            linux-firmware
        ;;
    
    *)
        echo "WARNING: Unsupported distribution: $DISTRO"
        echo "Please install the following packages manually:"
        echo "  - python3-gobject / python-gobject"
        echo "  - gtk4"
        echo "  - libadwaita"
        echo "  - NetworkManager"
        echo "  - iw"
        echo "  - linux-firmware"
        exit 1
        ;;
esac

echo
echo "System dependencies installed successfully"
echo

# Make main.py executable
echo "Making main.py executable..."
chmod +x main.py

# Install desktop entry
echo "Installing desktop entry..."
INSTALL_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$INSTALL_DIR"
mkdir -p "$ICON_DIR"

# Get the absolute path to the installation directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy icon to standard location
echo "Installing application icon..."
cp "$SCRIPT_DIR/icon.png" "$ICON_DIR/wifi-hotspot-manager.png"

# Create desktop file with absolute path
cat > "$INSTALL_DIR/wifi-hotspot-manager.desktop" << EOF
[Desktop Entry]
Name=WiFi Hotspot Manager
Comment=Manage WiFi hotspot on RTL8852BE chipsets
Exec=$SCRIPT_DIR/main.py
Icon=wifi-hotspot-manager
Terminal=false
Type=Application
Categories=Network;System;
Keywords=wifi;hotspot;network;wireless;
StartupNotify=true
EOF

# Make desktop file executable
chmod +x "$INSTALL_DIR/wifi-hotspot-manager.desktop"

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$INSTALL_DIR" 2>/dev/null || true
fi

echo "Desktop entry installed successfully"
echo

echo
echo "Installation complete!"
echo
echo "Next steps:"
echo "  1. Reboot your system to ensure firmware is loaded"
echo "  2. Run the application from your application menu or: ./main.py"
echo
echo "For hotspot management without sudo, add your user to the netdev group:"
echo "   sudo usermod -a -G netdev \$USER"
echo "   (Requires logout/login or reboot)"
echo
