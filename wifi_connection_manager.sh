#!/bin/bash

# install_wifi_checker.sh

# Exit on any error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Configuration
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc"
LOG_DIR="/var/log/wifi_checker"
SCRIPT_NAME="wifi_checker.sh"
CONFIG_NAME="wifi_config.conf"

# Create directories if they don't exist
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

# Create the WiFi checker script
cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'EOF'
#!/bin/bash

# Load configuration
CONFIG_FILE="/etc/wifi_config.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

# Function to check if we're connected to WiFi
check_wifi() {
    # Check if we have an IP address on wlan0
    if iwconfig wlan0 | grep -q "ESSID:\"$WIFI_SSID\""; then
        if ip addr show wlan0 | grep -q "inet "; then
            return 0  # Connected
        fi
    fi
    return 1  # Not connected
}

# Function to connect to WiFi
connect_wifi() {
    # Kill any existing wpa_supplicant processes
    sudo killall wpa_supplicant 2>/dev/null || true

    # Create a temporary wpa_supplicant configuration
    cat > /tmp/wpa_supplicant.conf << WPAEOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="$WIFI_SSID"
    psk="$WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
WPAEOF

    # Connect to WiFi
    sudo wpa_supplicant -B -i wlan0 -c /tmp/wpa_supplicant.conf
    sudo dhclient wlan0

    # Remove temporary configuration file
    rm /tmp/wpa_supplicant.conf

    # Wait for connection
    sleep 10
}

# Main logic
if ! check_wifi; then
    echo "$(date): WiFi not connected. Attempting to connect..."
    connect_wifi

    if check_wifi; then
        echo "$(date): Successfully connected to WiFi"
    else
        echo "$(date): Failed to connect to WiFi"
    fi
else
    echo "$(date): WiFi is already connected"
fi
EOF

# Create config file template
cat > "$CONFIG_DIR/$CONFIG_NAME" << 'EOF'
# WiFi Configuration
WIFI_SSID="your_wifi_ssid"
WIFI_PASSWORD="your_wifi_password"
EOF

# Set permissions
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
chmod 600 "$CONFIG_DIR/$CONFIG_NAME"
chmod 755 "$LOG_DIR"

# Create cron job
CRON_CMD="*/5 * * * * $INSTALL_DIR/$SCRIPT_NAME >> $LOG_DIR/wifi.log 2>&1"

# Remove any existing cron job for wifi checker
crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME" | crontab -

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

# Add sudo privileges for the script
if [ ! -f "/etc/sudoers.d/wifi_checker" ]; then
    echo "%sudo ALL=(ALL) NOPASSWD: $INSTALL_DIR/$SCRIPT_NAME" > "/etc/sudoers.d/wifi_checker"
    chmod 440 "/etc/sudoers.d/wifi_checker"
fi

echo "Installation completed!"
echo "Please edit $CONFIG_DIR/$CONFIG_NAME and set your WiFi credentials"
echo "You can test the script by running: sudo $INSTALL_DIR/$SCRIPT_NAME"
echo "Logs will be available at: $LOG_DIR/wifi.log"
echo ""
echo "Current cron jobs:"
crontab -l