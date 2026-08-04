#!/bin/bash
set -e

echo "Checking ZFS pool status..."
if zpool status tank >/dev/null 2>&1; then
    echo "The pool 'tank' is currently active and mounted."
    echo "To re-import it using persistent IDs, we must export it first."
    echo "Since your home directory (/home) is on this pool, we cannot do this while you are logged in."
    echo ""
    echo "HOW TO RUN THIS SCRIPT:"
    echo "The next time you boot and the ZFS import fails (and you are thrown into the empty home folder),"
    echo "open a terminal and run this script. The pool will not be active, and it will succeed."
    echo ""
    echo "Command to run when it fails:"
    echo "bash /home/scott/20p/scott-bin/zfs/import-by-id-helper.sh"
    exit 1
fi

echo "Importing pool 'tank' using persistent IDs..."
sudo zpool import -d /dev/disk/by-id tank

echo "Exporting pool 'tank' to update cache file..."
sudo zpool export tank

echo "--------------------------------------------------"
echo "Success! ZFS has been updated to use persistent IDs."
echo "--------------------------------------------------"
echo "You can now reboot, and ZFS will mount correctly."
