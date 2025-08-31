#!/bin/bash

# Name des Services
SERVICE_NAME="mirror-kiosk"

# Benutzer, der die X11-Session besitzt
USER="fw_admin"

# Prüfen, ob xrandr installiert ist
if ! command -v xrandr &> /dev/null
then
    echo "xrandr is not installed"
    exit 1
fi

# HDMI-Outputs erkennen (nur angeschlossene)
OUTPUTS=($(DISPLAY=:0 xrandr --query | grep " connected" | awk '{print $1}'))

if [ ${#OUTPUTS[@]} -lt 2 ]; then
    echo "Only one display was found"
    exit 1
fi

PRIMARY="${OUTPUTS[0]}"
SECONDARY="${OUTPUTS[1]}"

echo "Primary monitor: $PRIMARY"
echo "Secondary Monitor (getting mirrored): $SECONDARY"

# Service-Datei Pfad
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

# Service erstellen
sudo tee $SERVICE_PATH > /dev/null <<EOL
[Unit]
Description=Mirroring display for kiosk
After=graphical.target

[Service]
Type=oneshot
User=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/xrandr --output $SECONDARY --same-as $PRIMARY
RemainAfterExit=true

[Install]
WantedBy=graphical.target
EOL

# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service '$SERVICE_NAME' is created, activated and started."
echo "Secondary monitor: $SECONDARY is now mirrored"
