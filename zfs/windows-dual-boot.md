# Windows Dual Boot Configuration (GRUB) & Disk Analysis

This document outlines the steps to enable the GRUB dual-boot menu for Windows and provides an analysis of your `sda` drive.

---

## 💾 Drive Analysis (`sda`)

Based on hardware queries and filesystem analysis:

*   **Is it a spinning disk?** 
    Yes, `sda` is a **spinning disk (HDD)** (rotational parameter is `1`).
*   **Total Capacity**: 1.8 TB.
*   **Does it have enough space?**
    Yes! The drive has a dedicated Windows partition (`sda2`) of **976.5 GB** (nearly 1 TB), which is plenty of space for Windows and a substantial collection of games.

> [!TIP]
> **Performance Recommendation:**
> Since `sda` is a spinning HDD, games stored there will experience slower load times. 
> Your main boot drive `nvme0n1` is a high-speed NVMe SSD with **841 GB of free space** on your root partition (`/`). 
> For games where loading speeds are critical (e.g., open-world games), you can install them onto your Linux partition or format a section of the SSD for Windows to leverage the SSD speeds.

---

## 🛠️ How to Enable Windows in the GRUB Boot Menu

Since your system boots in Legacy BIOS mode and Windows is on a separate drive, we can configure Linux's bootloader (GRUB) to automatically scan and add Windows to the boot menu.

### Step-by-Step Instructions

1.  **Open the GRUB configuration file**:
    Run this command in your Linux terminal to open the file in a text editor:
    ```bash
    sudo nano /etc/default/grub
    ```

2.  **Enable OS Prober**:
    Scroll to the bottom of the file and add the following line:
    ```ini
    GRUB_DISABLE_OS_PROBER=false
    ```

3.  **Save and Exit**:
    *   Press `Ctrl + O` and press `Enter` to save.
    *   Press `Ctrl + X` to exit the editor.

4.  **Update the GRUB Bootloader**:
    Run the following command to scan your disks for Windows and rebuild the boot menu:
    ```bash
    sudo update-grub
    ```
    *You should see output indicating that it found Windows on `/dev/sda1` or `/dev/sda2`.*

5.  **Test the Menu**:
    Restart your computer. You will now be presented with a menu at boot, allowing you to choose between Linux and Windows.
