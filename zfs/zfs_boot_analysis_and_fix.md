# ZFS Boot Race Condition Analysis & Fix

This document provides a diagnosis and solution for the issue where ZFS occasionally fails to start up on boot, leaving you in an empty home directory (on your ext4 root filesystem).

---

## 🔍 Diagnosis

Here is what is happening during your boot process:

1. **Storage Setup**:
   - **Root File System (`/`)**: Located on `nvme0n1p1` (an NVMe SSD), formatted as `ext4`. It initializes almost instantly on boot.
   - **Home Directory (`/home`)**: Located on the ZFS pool `tank/home`, which resides on `/dev/sdb1` (a **4TB Western Digital SATA HDD**).

2. **The Race Condition**:
   - On a cold boot, your spinning HDD (`sdb`) takes a few seconds to spin up and register with the SATA controller and the kernel's device tree.
   - Meanwhile, systemd starts executing boot services immediately. The `zfs-import-cache.service` is triggered very early.
   - If the Western Digital HDD has not finished spinning up when ZFS tries to import `tank`, the ZFS import service fails because it cannot find `/dev/sdb1`.

3. **The Symptoms**:
   - Since ZFS import fails, the subsequent `zfs-mount.service` has no pool to mount `/home` from.
   - The boot process completes anyway (as the home directory is not considered critical for system boot by default), and you are logged in.
   - However, since `tank/home` is not mounted, you land in the empty `/home/scott` folder on the underlying `ext4` root partition—this is the "other filesystem" you encountered.
   - On a soft reboot, the HDD is already spun up and active, meaning the kernel detects it instantly, allowing ZFS to import and mount successfully.

---

## 🛠️ The Solution: Device-Based Dependency

To resolve this race condition permanently, we must instruct systemd's ZFS import service to wait until your specific Western Digital HDD partition is fully initialized and registered by the system before starting.

We have generated two scripts to assist you:
*   [fix-zfs-boot.sh](file:///home/scott/20p/scott-bin/zfs/fix-zfs-boot.sh) - Applies the systemd override.
*   [rollback-zfs-boot.sh](file:///home/scott/20p/scott-bin/zfs/rollback-zfs-boot.sh) - Reverts the change if needed.

### Steps to Apply the Fix

> [!IMPORTANT]
> The scripts require administrator privileges (`sudo`) because they modify systemd configurations in `/etc/systemd/system/`.

Run the following command in your terminal to apply the fix:

```bash
sudo /home/scott/20p/scott-bin/zfs/fix-zfs-boot.sh
```

### What this fix does:
It creates a systemd drop-in override configuration at `/etc/systemd/system/zfs-import-cache.service.d/override.conf` containing:

```ini
[Unit]
Requires=dev-disk-by\x2did-ata\x2dWDC_WD40EZRZ\x2d19GXCB0_WD\x2dWCC7K5UCFD1R\x2dpart1.device
After=dev-disk-by\x2did-ata\x2dWDC_WD40EZRZ\x2d19GXCB0_WD\x2dWCC7K5UCFD1R\x2dpart1.device
```

This ensures `zfs-import-cache.service` is delayed until udev detects your specific disk (`ata-WDC_WD40EZRZ-19GXCB0_WD-WCC7K5UCFD1R-part1`), resolving the race condition.

---

### How to Roll Back
If you ever need to undo this change, run the rollback script:

```bash
sudo /home/scott/20p/scott-bin/zfs/rollback-zfs-boot.sh
```
