#!/bin/bash
# Test script to validate lock screen persistence features

echo "=== WiFi Hotspot Lock Screen Persistence Test ==="
echo

# Check if hotspot-keepalive.sh exists and is executable
echo "1. Checking keep-alive script..."
if [ -x "./hotspot-keepalive.sh" ]; then
    echo "   [OK] hotspot-keepalive.sh is present and executable"
else
    echo "   [FAIL] hotspot-keepalive.sh is missing or not executable"
    echo "   Run: chmod +x hotspot-keepalive.sh"
fi
echo

# Check if systemd service is installed
echo "2. Checking systemd service..."
SERVICE_FILE="$HOME/.config/systemd/user/hotspot-keepalive.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "   [OK] Service file exists at $SERVICE_FILE"
    
    # Check if service is enabled
    if systemctl --user is-enabled hotspot-keepalive.service &>/dev/null; then
        echo "   [OK] Service is enabled"
    else
        echo "   [FAIL] Service is not enabled"
        echo "   Run: systemctl --user enable hotspot-keepalive.service"
    fi
    
    # Check if service is running
    if systemctl --user is-active hotspot-keepalive.service &>/dev/null; then
        echo "   [OK] Service is running"
    else
        echo "   [FAIL] Service is not running"
        echo "   Run: systemctl --user start hotspot-keepalive.service"
    fi
else
    echo "   [FAIL] Service file not found"
    echo "   Run: ./install.sh to set up the service"
fi
echo

# Check if NetworkManager is available
echo "3. Checking NetworkManager..."
if command -v nmcli &>/dev/null; then
    echo "   [OK] nmcli is available"
    NMCLI_VERSION=$(nmcli --version | head -1)
    echo "   Version: $NMCLI_VERSION"
else
    echo "   [FAIL] nmcli not found"
    echo "   NetworkManager is required for hotspot functionality"
fi
echo

# Check if systemd-inhibit is available
echo "4. Checking systemd-inhibit..."
if command -v systemd-inhibit &>/dev/null; then
    echo "   [OK] systemd-inhibit is available"
else
    echo "   [FAIL] systemd-inhibit not found"
    echo "   This is required for preventing sleep during hotspot operation"
fi
echo

# Check current hotspot status
echo "5. Checking current hotspot status..."
if nmcli -t -f NAME,TYPE connection show --active 2>/dev/null | grep -q "802-11-wireless"; then
    echo "   [INFO] A wireless connection is currently active"
    
    # Check if it's in AP mode
    ACTIVE_CONNS=$(nmcli -t -f NAME,TYPE connection show --active 2>/dev/null | grep "802-11-wireless" | cut -d: -f1)
    AP_MODE_FOUND=false
    
    while IFS= read -r conn_name; do
        MODE=$(nmcli -t -f 802-11-wireless.mode connection show "$conn_name" 2>/dev/null | grep "802-11-wireless.mode" | cut -d: -f2)
        if [[ "$MODE" == *"ap"* ]]; then
            echo "   [OK] Hotspot is currently active: $conn_name"
            AP_MODE_FOUND=true
            
            # Check power-save setting
            POWERSAVE=$(nmcli -t -f 802-11-wireless.powersave connection show "$conn_name" 2>/dev/null | grep "802-11-wireless.powersave" | cut -d: -f2)
            if [ "$POWERSAVE" = "2" ]; then
                echo "   [OK] Power-save is disabled (value: $POWERSAVE)"
            else
                echo "   [WARN] Power-save setting: $POWERSAVE (expected: 2)"
            fi
            
            # Check autoconnect setting
            AUTOCONNECT=$(nmcli -t -f connection.autoconnect connection show "$conn_name" 2>/dev/null | grep "connection.autoconnect" | cut -d: -f2)
            if [ "$AUTOCONNECT" = "yes" ]; then
                echo "   [OK] Autoconnect is enabled"
            else
                echo "   [WARN] Autoconnect: $AUTOCONNECT (expected: yes)"
            fi
        fi
    done <<< "$ACTIVE_CONNS"
    
    if [ "$AP_MODE_FOUND" = false ]; then
        echo "   [INFO] No AP-mode connection found (not a hotspot)"
    fi
else
    echo "   [INFO] No wireless connection currently active"
fi
echo

# Check for active inhibitors
echo "6. Checking sleep inhibitors..."
if command -v systemd-inhibit &>/dev/null; then
    INHIBITORS=$(systemd-inhibit --list 2>/dev/null | grep -i "wifi hotspot" || true)
    if [ -n "$INHIBITORS" ]; then
        echo "   [OK] WiFi Hotspot Manager sleep inhibitor is active:"
        echo "$INHIBITORS" | sed 's/^/     /'
    else
        echo "   [INFO] No WiFi Hotspot Manager inhibitor currently active"
        echo "     (This is normal if hotspot is not running)"
    fi
else
    echo "   [FAIL] Cannot check inhibitors (systemd-inhibit not available)"
fi
echo

# Check service logs
echo "7. Recent service logs (last 5 lines)..."
if systemctl --user is-active hotspot-keepalive.service &>/dev/null; then
    journalctl --user -u hotspot-keepalive.service -n 5 --no-pager 2>/dev/null | sed 's/^/   /'
else
    echo "   [INFO] Service is not running"
fi
echo

echo "=== Test Complete ==="
echo
echo "Summary:"
echo "- If hotspot is active and configured correctly, it will persist during screen lock"
echo "- The keep-alive service automatically manages sleep inhibitors"
echo "- Check 'systemctl --user status hotspot-keepalive.service' for detailed status"
echo
