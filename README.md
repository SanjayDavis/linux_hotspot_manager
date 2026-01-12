# RTL8852BE WiFi Diagnostic and Hotspot Manager

A modern, Wayland-compatible GUI application for managing WiFi hotspot functionality on Linux systems equipped with Realtek RTL8852BE wireless chipsets.

## Features

### Driver Detection & Diagnostics
- **Automatic driver detection** via kernel logs (`dmesg`)
- **Firmware status verification** to ensure proper loading
- **Error pattern detection** for common issues (ASPM, power-save, timeouts)
- **Real-time capability inspection** using `iw list`

### Access Point Capabilities
- **AP mode support verification** for your wireless adapter
- **Frequency band detection** (2.4 GHz / 5 GHz)
- **Interface combination analysis** for hotspot creation
- **Multi-interface support detection**

### Hotspot Management
- **One-click hotspot toggle** via graphical switch
- **Custom SSID configuration** or auto-generation
- **Password management** with auto-generation support
- **Real-time hotspot status** display
- **Active connection monitoring**
- **Integrated lock screen persistence** - built-in UI controls with visual feedback
- **Automatic sleep blocking** - prevents system suspend while hotspot is active

### User Experience
- **Modern libadwaita interface** with GNOME styling
- **Toast notifications** for user feedback
- **Wayland-native** rendering
- **Permission status checking**
- **Clear error messages** with actionable guidance

## Requirements

### System Dependencies
```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 network-manager iw

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita NetworkManager iw

# Arch Linux
sudo pacman -S python-gobject gtk4 libadwaita networkmanager iw
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Hardware Requirements
- Realtek RTL8852BE wireless chipset
- `rtw89` kernel driver (available in Linux kernel 5.16+)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/wifi-hotspot-manager.git
cd wifi-hotspot-manager
```

2. **Install system dependencies:**
```bash
./install.sh
```

3. **Install the application:**
```bash
./setup.sh
```

The app will be installed to `~/.local/share/wifi-hotspot-manager` and a launcher will be created.

## Usage

After installation, you can launch the app:

**From Application Menu:**
- Open your application launcher (KDE Menu)
- Search for "WiFi Hotspot Manager"
- Click to launch

**From Terminal:**
```bash
wifi-hotspot-manager
```

## Uninstall

To remove the application:
```bash
./uninstall.sh
```

## Usage

### Running Diagnostics
1. Launch the application
2. Navigate to the **Diagnostics** tab
3. Click **Refresh Diagnostics** to update status
4. Review:
   - Driver loading status
   - AP mode support
   - Permission status

### Managing Hotspot

#### Enable Hotspot
1. Switch to the **Hotspot** tab
2. (Optional) Enter custom SSID
3. (Optional) Enter custom password
4. Toggle the **Enable Hotspot** switch
5. If using auto-generated credentials, check the toast notification for password

#### Disable Hotspot
1. Toggle the **Enable Hotspot** switch to OFF
2. Confirm deactivation via status display

### Lock Screen Persistence

The hotspot manager includes special features to keep your hotspot active even when your screen is locked:

**NetworkManager Configuration:**
- Automatically disables WiFi power-saving when hotspot is active
- Prevents automatic disconnection during idle/lock screen
- Configures connection to persist across sleep/suspend events

**Keep-Alive Service:**
- A background systemd service monitors hotspot status
- Automatically prevents system sleep/suspend when hotspot is active
- Uses systemd-inhibit to block idle sleep
- Automatically releases inhibitor when hotspot is disabled

**Service Management:**
```bash
# Check service status
systemctl --user status hotspot-keepalive.service

# View service logs
journalctl --user -u hotspot-keepalive.service -f

# Manually restart service
systemctl --user restart hotspot-keepalive.service
```

### Troubleshooting

**Driver Not Loaded:**
- Verify your chipset: `lspci | grep -i rtl`
- Check kernel version: `uname -r` (requires 5.16+)
- Install firmware: `sudo apt install linux-firmware`

**Permission Issues:**
- Add user to `netdev` group: `sudo usermod -a -G netdev $USER`
- Reboot after group change
- Alternatively, run with sudo (not recommended for regular use)

**AP Mode Not Supported:**
- Verify driver compatibility: `modinfo rtw89_pci`
- Check firmware version
- Update kernel to latest stable version

## Architecture

```
wifi-hotspot-manager/
├── main.py              # Application entry point & main window
├── diagnostics.py       # System diagnostics module
├── network_control.py   # NetworkManager interaction
├── ui_components.py     # GTK4/libadwaita UI components
├── requirements.txt     # Python dependencies
└── README.md           # This file
```



### Security Considerations
- Commands executed via `subprocess` with timeouts
- No shell interpretation (avoids injection attacks)
- Password fields use `set_visibility(False)`
- Proper error handling for all system calls

### Wayland Compatibility
- Uses GTK4 (native Wayland support)
- No X11-specific APIs
- Tested on GNOME Wayland sessions
