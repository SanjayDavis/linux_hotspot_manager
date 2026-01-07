# Installation Guide

## Quick Install (Recommended)

1. **Install system dependencies:**
   ```bash
   ./install.sh
   ```

2. **Install the application:**
   ```bash
   ./setup.sh
   ```

3. **Launch from your application menu or terminal:**
   ```bash
   wifi-hotspot-manager
   ```

## What Gets Installed

- **Application files**: `~/.local/share/wifi-hotspot-manager/`
  - main.py
  - diagnostics.py
  - network_control.py
  - ui_components.py

- **Launcher**: `~/.local/bin/wifi-hotspot-manager`
  - Executable script to launch the app

- **Desktop entry**: `~/.local/share/applications/wifi-hotspot-manager.desktop`
  - Shows up in your KDE application menu

## Manual Installation

If you prefer to run without installing:

```bash
./main.py
```

## Uninstall

To completely remove the application:

```bash
./uninstall.sh
```

This will remove:
- All application files from `~/.local/share/wifi-hotspot-manager`
- The launcher from `~/.local/bin`
- The desktop entry from `~/.local/share/applications`

## Troubleshooting

### "Command not found" when running wifi-hotspot-manager

Add `~/.local/bin` to your PATH by adding this to `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:
```bash
source ~/.bashrc
```

### Application doesn't appear in KDE menu

Run:
```bash
kbuildsycoca5 --noincremental
```

Or logout and login again.

### Permission issues with hotspot

Add your user to the netdev group:
```bash
sudo usermod -a -G netdev $USER
```

Then logout and login for changes to take effect.
