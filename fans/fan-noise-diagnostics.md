# Fan Noise Diagnostics & Solutions

This document analyzes your system's temperatures and outlines solutions for the fan noise on your system.

---

## 🔍 System Temperature Analysis

We queried your hardware sensors under your current workload:
*   **Graphics Card (RTX 2060 Super)**: **43°C** (very cool, GPU fan is quiet at 37%).
*   **NVMe SSD (Samsung 970 EVO Plus)**: **48°C** (cool and safe).
*   **CPU (Ryzen on ROG STRIX B450-F GAMING)**: **57°C - 62°C** (normal operating temperature, but a bit warm for idle).

### Why are the fans loud/revving?
There are two main culprits behind the fan behavior on your hardware:

### 1. Ryzen Temperature Spikes (The BIOS "Revving" Issue)
AMD Ryzen processors naturally experience rapid, short temperature spikes (from 45°C to 60°C for a split second) during normal tasks like opening Chrome. 
By default, the BIOS fan curve reacts instantly to these spikes, causing the fans to spin up loudly for a second, then immediately slow down, creating an annoying "revving" sound.

### 2. Missing Motherboard Sensor Driver in Linux
When we ran `sensors`, your motherboard's fans and temperatures were **not listed at all**. 
Your **ROG STRIX B450-F GAMING** motherboard uses a Nuvoton monitoring chip (`NCT6798D`), but Linux disables it by default due to a minor conflict with the motherboard's ACPI firmware. Without this driver, Linux cannot read fan RPMs or apply custom fan curves.

---

## 🛠️ How to Fix It

### Solution 1: BIOS Fan Smoothing (Highly Recommended)
This is the easiest and most effective way to stop the "revving" noise. It works across both Windows and Linux.

1.  Restart your computer and repeatedly press `Del` or `F2` to enter the **BIOS/UEFI**.
2.  Press `F7` to enter **Advanced Mode**.
3.  Go to the **Monitor** tab and select **Q-Fan Configuration**.
4.  Look for **Fan Step Up/Down Delay** (sometimes called fan smoothing or hysteresis) for your CPU and Chassis fans.
5.  Change the **Step Up Delay** to **12 seconds** or **25 seconds** (instead of 0 seconds).
    *   *Why:* This tells the motherboard to ignore brief 1-second temperature spikes and only increase fan speeds if the CPU remains hot for a sustained period.
6.  Save and exit (`F10`).

---

### Solution 2: Enable Fan Sensors in Linux
To monitor fan speeds and control them directly within Linux, you need to allow the `nct6775` motherboard driver to load.

#### Step 1: Add Kernel Boot Parameter
We need to tell the kernel to bypass the ACPI resource check:
1.  Open `/etc/default/grub` in an editor:
    ```bash
    sudo nvim /etc/default/grub
    ```
2.  Find the line:
    ```ini
    GRUB_CMDLINE_LINUX_DEFAULT="quiet"
    ```
3.  Modify it to include `acpi_enforce_resources=lax`:
    ```ini
    GRUB_CMDLINE_LINUX_DEFAULT="quiet acpi_enforce_resources=lax"
    ```
4.  Save and exit (`Esc`, `:wq`, `Enter`).
5.  Update your bootloader:
    ```bash
    sudo update-grub
    ```

#### Step 2: Load the Driver
Tell Linux to load the motherboard sensor driver:
1.  Open `/etc/modules` to load the module at boot:
    ```bash
    sudo nvim /etc/modules
    ```
2.  Add the following line to the bottom:
    ```text
    nct6775
    ```
3.  Save and exit (`Esc`, `:wq`, `Enter`).

#### Step 3: Reboot and Test
Once you reboot:
1.  Open a terminal and run:
    ```bash
    sensors
    ```
2.  You should now see new entries for your motherboard (`nct6798-isa-...`) listing **CPU Fan**, **Chassis Fans**, and their respective **RPM speeds**.
