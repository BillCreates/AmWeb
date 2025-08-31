#!/bin/bash

SERVICE_NAME="mirror-wayland"

USER="fw_admin"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/setup-mirror-wayland.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Wayland mirror script not found at $SCRIPT_PATH"
    exit 1
fi

SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

sudo tee $SERVICE_PATH > /dev/null <<EOL
[Unit]
Description=Mirror HDMI outputs in Labwc (Wayland)
After=graphical.target

[Service]
Type=oneshot
User=$USER
ExecStart=$SCRIPT_PATH
RemainAfterExit=true

[Install]
WantedBy=graphical.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service '$SERVICE_NAME' is created, activated and started."
echo "Wayland mirror script ($SCRIPT_PATH) will run automatically on login."
