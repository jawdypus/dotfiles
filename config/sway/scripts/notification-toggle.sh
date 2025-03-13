#!/bin/bash

# Path to store the current notification state
STATE_FILE="$HOME/.config/sway/notification_state"

# Create state file if it doesn't exist (default: notifications enabled)
if [ ! -f "$STATE_FILE" ]; then
    echo "1" > "$STATE_FILE"
fi

# Get current state
current_state=$(cat "$STATE_FILE")

toggle_state() {
    if [ "$current_state" = "1" ]; then
        # Switch to silent mode
        echo "0" > "$STATE_FILE"
        makoctl set-mode do-not-disturb
        notify-send -u low -t 2000 "Notifications disabled" "System is now in silent mode"
    else
        # Switch to normal mode
        echo "1" > "$STATE_FILE"
        makoctl set-mode default
        notify-send -u low -t 2000 "Notifications enabled" "System is now in normal mode"
    fi
}

# Function to get the current state for waybar
get_state() {
    if [ "$current_state" = "1" ]; then
        echo '{"text": "🔔", "tooltip": "Notifications enabled", "class": "notify-enabled"}'
    else
        echo '{"text": "🔕", "tooltip": "Silent mode", "class": "notify-disabled"}'
    fi
}

# Handle command line arguments
case "$1" in
    "toggle")
        toggle_state
        ;;
    *)
        get_state
        ;;
esac
