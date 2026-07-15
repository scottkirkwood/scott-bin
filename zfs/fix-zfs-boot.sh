#!/bin/bash
set -e

OVERRIDE_DIR="/etc/systemd/system/zfs-import-cache.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/override.conf"

echo "Creating systemd override directory..."
sudo mkdir -p "$OVERRIDE_DIR"

echo "Writing override configuration..."
sudo tee "$OVERRIDE_FILE" > /dev/null <<'EOF'
[Unit]
Requires=dev-disk-by\x2did-ata\x2dWDC_WD40EZRZ\x2d19GXCB0_WD\x2dWCC7K5UCFD1R\x2dpart1.device
After=dev-disk-by\x2did-ata\x2dWDC_WD40EZRZ\x2d19GXCB0_WD\x2dWCC7K5UCFD1R\x2dpart1.device
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "--------------------------------------------------"
echo "ZFS boot race condition fix applied successfully!"
echo "--------------------------------------------------"
echo "Systemd will now wait for your 4TB Western Digital HDD"
echo "(ata-WDC_WD40EZRZ-19GXCB0_WD-WCC7K5UCFD1R-part1) to"
echo "spin up and initialize before starting the ZFS import service."
