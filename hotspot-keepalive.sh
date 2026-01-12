#!/bin/bash
# Hotspot Keep-Alive Script
# This script monitors the hotspot status and prevents system sleep/suspend
# when the hotspot is active.

LOCK_FILE="/tmp/hotspot-inhibit.lock"
INHIBIT_PID_FILE="/tmp/hotspot-inhibit.pid"

cleanup() {
    if [ -f "$INHIBIT_PID_FILE" ]; then
        INHIBIT_PID=$(cat "$INHIBIT_PID_FILE")
        if kill -0 "$INHIBIT_PID" 2>/dev/null; then
            kill "$INHIBIT_PID" 2>/dev/null
        fi
        rm -f "$INHIBIT_PID_FILE"
    fi
    rm -f "$LOCK_FILE"
    exit 0
}

trap cleanup SIGTERM SIGINT EXIT

# Check if hotspot is active
is_hotspot_active() {
    nmcli -t -f NAME,TYPE connection show --active | while IFS=: read -r name type; do
        if [[ "$type" == *"802-11-wireless"* ]] || [[ "$type" == *"wifi"* ]]; then
            mode=$(nmcli -t -f 802-11-wireless.mode connection show "$name" 2>/dev/null | grep "802-11-wireless.mode" | cut -d: -f2)
            if [[ "$mode" == *"ap"* ]]; then
                return 0
            fi
        fi
    done
    return 1
}

# Main loop
while true; do
    if is_hotspot_active; then
        # Hotspot is active
        if [ ! -f "$LOCK_FILE" ]; then
            # Start systemd-inhibit to prevent sleep
            systemd-inhibit --what=sleep:idle --who="WiFi Hotspot Manager" \
                --why="Hotspot is active" --mode=block \
                sleep infinity &
            INHIBIT_PID=$!
            echo "$INHIBIT_PID" > "$INHIBIT_PID_FILE"
            touch "$LOCK_FILE"
            logger "Hotspot keep-alive: Sleep inhibitor activated"
        fi
    else
        # Hotspot is not active
        if [ -f "$LOCK_FILE" ]; then
            # Stop the inhibitor
            if [ -f "$INHIBIT_PID_FILE" ]; then
                INHIBIT_PID=$(cat "$INHIBIT_PID_FILE")
                if kill -0 "$INHIBIT_PID" 2>/dev/null; then
                    kill "$INHIBIT_PID" 2>/dev/null
                fi
                rm -f "$INHIBIT_PID_FILE"
            fi
            rm -f "$LOCK_FILE"
            logger "Hotspot keep-alive: Sleep inhibitor deactivated"
        fi
    fi
    
    sleep 10
done
