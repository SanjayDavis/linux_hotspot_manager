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

echo
echo "Installation complete!"
echo
echo "Next steps:"
echo "  1. Reboot your system to ensure firmware is loaded"
echo "  2. Run the application: ./main.py"
echo
echo "For hotspot management without sudo, add your user to the netdev group:"
echo "   sudo usermod -a -G netdev \$USER"
echo "   (Requires logout/login or reboot)"
echo
