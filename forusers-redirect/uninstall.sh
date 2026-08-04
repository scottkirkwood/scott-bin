#!/bin/bash
set -e

BINARY_PATH="${HOME}/.local/bin/forusers-redirect"
SERVICE_FILE="/etc/systemd/system/forusers-redirect.service"

echo "Stopping and disabling systemd service..."
if systemctl is-active --quiet forusers-redirect.service 2>/dev/null || systemctl is-enabled --quiet forusers-redirect.service 2>/dev/null; then
    sudo systemctl stop forusers-redirect.service || true
    sudo systemctl disable forusers-redirect.service || true
fi

if [ -f "${SERVICE_FILE}" ]; then
    echo "Removing ${SERVICE_FILE}..."
    sudo rm -f "${SERVICE_FILE}"
    sudo systemctl daemon-reload
    sudo systemctl reset-failed || true
fi

if [ -f "${BINARY_PATH}" ]; then
    echo "Removing binary ${BINARY_PATH}..."
    rm -f "${BINARY_PATH}"
fi

echo "Successfully uninstalled forusers-redirect service and binary."
echo "Note: If you added shortcuts to /etc/hosts, you can remove them manually."
