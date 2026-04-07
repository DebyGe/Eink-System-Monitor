# Eink System Monitor

A lightweight Python web service that displays real-time PC performance metrics (CPU, GPU, Memory, Disk, Network) in a browser optimized for **e-ink displays**. Works on both **Windows** and **Linux**.

---

## Features

- **CPU** -- Overall usage, per-core usage bars, frequency, physical/logical core count
- **GPU** -- Load %, VRAM usage, temperature (NVIDIA GPUs via GPUtil)
- **Memory** -- RAM and Swap usage with visual bars
- **Disk** -- Per-partition usage table (device, mount point, filesystem type, capacity)
- **Network** -- Cumulative bytes sent/received
- **System** -- Hostname, OS version, architecture, boot time, uptime
- **JSON API** -- Raw metrics available at `/api/stats` for programmatic use

### E-Ink Display Optimizations

The HTML dashboard is purpose-built for e-ink screens:

| Design choice | Reason |
|---|---|
| Pure black & white only | E-ink screens have no color or grayscale gradation |
| No animations or transitions | E-ink refresh is slow; animations cause ghosting |
| Monospace font (Courier New) | Crisp rendering on low-DPI e-ink panels |
| CSS-only bar charts | No JavaScript/canvas required; renders on minimal browsers |
| Auto-refresh every 30 seconds | Avoids excessive screen refreshes that degrade e-ink lifespan |
| High contrast borders/fills | Maximum readability in direct sunlight |

---

## Requirements

- Python 3.10+
- pip

### Python Dependencies

| Package | Purpose |
|---|---|
| `flask` >= 3.0 | Web server and template rendering |
| `psutil` >= 5.9 | CPU, memory, disk, network metrics |
| `GPUtil` >= 1.4 | NVIDIA GPU metrics (optional -- degrades gracefully if no GPU) |

---

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd Eink-Info
```

### 2. (Recommended) Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Start the server

```bash
python app.py
```

You will see:

```
============================================================
  Eink System Monitor
  http://0.0.0.0:5000
  Open this URL in your e-ink device browser.
============================================================
```

### Open the dashboard

On your e-ink device browser, navigate to:

```
http://<host-ip>:5000
```

Replace `<host-ip>` with the IP address of the machine running the server. To find your IP:

```bash
# Windows
ipconfig

# Linux
hostname -I
```

The page auto-refreshes every 30 seconds.

### JSON API

For programmatic access to raw metrics:

```
GET http://<host-ip>:5000/api/stats
```

Example response:

```json
{
  "timestamp": "2026-04-07 09:47:21",
  "system": {
    "hostname": "MY-PC",
    "os": "Windows 11",
    "architecture": "AMD64",
    "boot_time": "2026-04-07 08:00:00",
    "uptime": "1h 47m 21s"
  },
  "cpu": {
    "usage_percent": 21.3,
    "per_core_percent": [12.5, 8.0, 30.1, 5.2],
    "cores_physical": 4,
    "cores_logical": 8,
    "freq_current_mhz": 3600.0,
    "freq_max_mhz": 4200.0
  },
  "memory": {
    "ram_total_gb": 16.0,
    "ram_used_gb": 9.5,
    "ram_percent": 59.4,
    "swap_total_gb": 8.0,
    "swap_used_gb": 0.5,
    "swap_percent": 6.3
  },
  "disks": [
    {
      "device": "C:\\",
      "mountpoint": "C:\\",
      "fstype": "NTFS",
      "total_gb": 500.0,
      "used_gb": 320.0,
      "percent": 64.0
    }
  ],
  "gpus": [
    {
      "id": 0,
      "name": "NVIDIA GeForce RTX 3080",
      "load_percent": 45.2,
      "memory_total_mb": 10240.0,
      "memory_used_mb": 4096.0,
      "memory_percent": 40.0,
      "temperature_c": 62
    }
  ],
  "network": {
    "bytes_sent_mb": 520.48,
    "bytes_recv_mb": 20985.44
  }
}
```

---

## Project Structure

```
Eink-Info/
├── app.py               # Flask web server + system metrics collection
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # E-ink optimized HTML dashboard template
└── README.md            # This file
```

### File Descriptions

| File | Description |
|---|---|
| `app.py` | Main application. Collects system metrics using `psutil` and `GPUtil`, serves an HTML dashboard at `/` and a JSON API at `/api/stats`. |
| `templates/index.html` | Jinja2 template rendered by Flask. Pure black-and-white layout with CSS bar charts, designed for e-ink browsers. Auto-refreshes every 30 seconds. |
| `requirements.txt` | Python package dependencies for pip. |

---

## Configuration

| Setting | Default | How to change |
|---|---|---|
| Port | `5000` | Edit `app.run(port=5000)` in `app.py` |
| Host binding | `0.0.0.0` (all interfaces) | Edit `app.run(host="0.0.0.0")` in `app.py` |
| Auto-refresh interval | 30 seconds | Edit `<meta http-equiv="refresh" content="30">` in `templates/index.html` |
| Debug mode | `False` | Edit `app.run(debug=False)` in `app.py` |

---

## GPU Support

GPU monitoring uses the `GPUtil` library, which requires:

- An **NVIDIA GPU**
- **NVIDIA drivers** installed
- The `nvidia-smi` command available in PATH

If no NVIDIA GPU is detected, the GPU section will display a "No NVIDIA GPU detected" message. The rest of the dashboard continues to work normally.

---

## Tested E-Ink Devices

This dashboard is designed to work with any e-ink device that has a web browser, including:

- Kindle (via Experimental Browser)
- Kobo (via built-in browser)
- BOOX devices (via built-in browser or any installed browser)
- reMarkable (via third-party browser)
- Dasung e-ink monitors (any desktop browser)
- Any device with an e-ink screen and a web browser

---

## Troubleshooting

### Page does not load on e-ink device

1. Make sure the server machine and e-ink device are on the **same network**
2. Check the firewall allows incoming connections on port `5000`
3. Verify the server is running: `python app.py`
4. Try accessing `http://<host-ip>:5000` from another device first

### GPU section shows "No NVIDIA GPU detected"

- `GPUtil` only supports NVIDIA GPUs
- Ensure NVIDIA drivers are installed and `nvidia-smi` works from the terminal
- AMD / Intel GPUs are not supported by this library

### Permission errors on Linux

Some disk partitions may require elevated permissions. Run with:

```bash
sudo python app.py
```

---

## License

This project is provided as-is for personal and educational use.
