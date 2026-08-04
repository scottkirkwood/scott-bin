# forusers-redirect

A lightweight local HTTP service running on port 80 that forwards local shortlinks (e.g. `http://f/assets` or `http://go/github`) to `https://forusers.com`.

---

## 1. Local Hostname Setup (`/etc/hosts`)

Edit `/etc/hosts`:

```bash
sudo nvim /etc/hosts
```

Add your preferred short hostnames to the `127.0.0.1` line:

```text
127.0.0.1  f go
```

---

## 2. Building & Installing the Binary

Run `install.sh` to compile the Go binary and install it to `~/.local/bin/forusers-redirect`:

```bash
./install.sh
```

---

## 3. Systemd Service Setup

Create the systemd unit file at `/etc/systemd/system/forusers-redirect.service`:

```bash
sudo nvim /etc/systemd/system/forusers-redirect.service
```

Paste the following configuration:

```ini
[Unit]
Description=ForUsers Local Link Redirector
After=network.target

[Service]
Type=simple
ExecStart=/home/scott/.local/bin/forusers-redirect
Restart=always
RestartSec=3

# Run as user 'scott' with capability to bind port 80
User=scott
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```

---

## 4. Enable and Start the Service

Reload systemd, enable the service to start on boot, and start it now:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now forusers-redirect.service
```

---

## 5. Verification & Testing

Check service status:
```bash
sudo systemctl status forusers-redirect.service
```

View live logs:
```bash
journalctl -u forusers-redirect.service -f
```

Test redirect in terminal:
```bash
curl -I http://f/assets
```
*(Should return `HTTP/1.1 307 Temporary Redirect` pointing to `https://forusers.com/assets`)*

---

## 6. Disabling the Service

To temporarily stop and disable the service without removing files:

```bash
sudo systemctl stop forusers-redirect.service
sudo systemctl disable forusers-redirect.service
```

To re-enable it later:

```bash
sudo systemctl enable --now forusers-redirect.service
```

---

## 7. Uninstalling the Service

You can run the included uninstall script or perform the steps manually:

### Option A: Run `uninstall.sh`
```bash
./uninstall.sh
```

### Option B: Manual Uninstallation

#### 1. Stop and disable the systemd service
```bash
sudo systemctl stop forusers-redirect.service
sudo systemctl disable forusers-redirect.service
```

#### 2. Remove the systemd service file and reload daemon
```bash
sudo rm -f /etc/systemd/system/forusers-redirect.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

#### 3. Delete the binary
```bash
rm -f ~/.local/bin/forusers-redirect
```

#### 4. (Optional) Remove `/etc/hosts` entry
Edit `/etc/hosts` to remove the host shortcuts (`f`, `go`, etc.):

```bash
sudo nvim /etc/hosts
```

