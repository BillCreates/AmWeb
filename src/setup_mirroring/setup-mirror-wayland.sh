#!/bin/bash
set -e

# 1. Check if wlr-randr is instaled
if ! command -v wlr-randr &> /dev/null; then
    echo "[INFO] wlr-randr not found – instaling..."
    sudo apt update
    sudo apt install -y wlr-randr
fi

# 2. Detecting HDMI Outputs
outputs=$(wlr-randr | grep "HDMI" | awk '{print $1}')
primary=$(echo "$outputs" | sed -n '1p')
secondary=$(echo "$outputs" | sed -n '2p')

if [ -z "$secondary" ]; then
    echo "[ERROR] Only one HDMI Output detected"
    exit 1
fi

echo "[INFO] Primary: $primary"
echo "[INFO] Secondary: $secondary"

# 3. Setting defined solution if needed
mode="1920x1080"

# 4. Setting both outputs to the same resolution and mode
wlr-randr --output "$primary" --mode "$mode" --pos 0,0
wlr-randr --output "$secondary" --mode "$mode" --pos 0,0

echo "[SUCCESS] $secondary is now mirroed from $primary"