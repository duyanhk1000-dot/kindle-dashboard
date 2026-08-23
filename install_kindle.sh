#!/bin/sh
# ==============================================================================
# Kindle Touch 4th Gen Dashboard Installation Script
# Run this script on Kindle via SSH or terminal after copying files to USB
# ==============================================================================

echo "=================================================="
echo " Installing Kindle Touch Smart Dashboard"
echo "=================================================="

# Create target directory on Kindle storage
TARGET_DIR="/mnt/us/dashboard"
EXT_DIR="/mnt/us/extensions/dashboard"

mkdir -p "$TARGET_DIR"
mkdir -p "$EXT_DIR"

# Copy runner script and grant execution permissions
if [ -f "./dashboard_runner.sh" ]; then
    cp ./dashboard_runner.sh "$TARGET_DIR/"
    chmod +x "$TARGET_DIR/dashboard_runner.sh"
    echo "[✓] Copied dashboard_runner.sh to $TARGET_DIR/"
fi

# Setup KUAL menu integration
cat << 'EOF' > "$EXT_DIR/menu.json"
{
    "items": [
        {
            "name": "Refresh Smart Dashboard",
            "priority": 1,
            "action": "/mnt/us/dashboard/dashboard_runner.sh"
        }
    ]
}
EOF

echo "[✓] KUAL Extension installed at $EXT_DIR/menu.json"
echo ""
echo "=================================================="
echo " Installation Complete!"
echo " You can now trigger the dashboard from KUAL menu"
echo " or run: /mnt/us/dashboard/dashboard_runner.sh"
echo "=================================================="
