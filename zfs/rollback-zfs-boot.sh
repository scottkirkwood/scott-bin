#!/bin/bash
set -e

OVERRIDE_DIR="/etc/systemd/system/zfs-import-cache.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/override.conf"

if [ -f "$OVERRIDE_FILE" ]; then
    echo "Removing systemd override file..."
    sudo rm -f "$OVERRIDE_FILE"
fi

if [ -d "$OVERRIDE_DIR" ] && [ -z "$(ls -A "$OVERRIDE_DIR")" ]; then
    echo "Removing empty override directory..."
    sudo rmdir "$OVERRIDE_DIR"
fi

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "--------------------------------------------------"
echo "ZFS boot race condition fix rolled back!"
echo "--------------------------------------------------"
