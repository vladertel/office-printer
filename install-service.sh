#!/bin/bash

# Script to install the Telegram Printer Bot as a systemd service
# This will enable the bot to start automatically on system boot

# Ensure script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root. Try 'sudo $0'"
    exit 1
fi

# Get absolute path to the installation directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Set variables
SERVICE_NAME="telegram-printer-bot"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
TARGET="/etc/systemd/system/$SERVICE_NAME.service"

# Update the service file with the correct path
sed -i "s|/home/pi/telegram-printer-bot|$SCRIPT_DIR|g" "$SERVICE_FILE"

# Copy service file to systemd directory
cp "$SERVICE_FILE" "$TARGET"

# Set appropriate permissions
chmod 644 "$TARGET"

# Reload systemd daemon
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable "$SERVICE_NAME.service"

# Start the service
systemctl start "$SERVICE_NAME.service"

# Check service status
systemctl status "$SERVICE_NAME.service"

echo ""
echo "======================================================================"
echo "Telegram Printer Bot has been installed as a systemd service!"
echo "The bot will now start automatically when the system boots."
echo ""
echo "To control the service, use the following commands:"
echo "  - Check status: sudo systemctl status $SERVICE_NAME"
echo "  - Stop service: sudo systemctl stop $SERVICE_NAME"
echo "  - Start service: sudo systemctl start $SERVICE_NAME"
echo "  - Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  - View logs: sudo journalctl -u $SERVICE_NAME"
echo "======================================================================"
