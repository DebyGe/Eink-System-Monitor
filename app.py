"""
Eink System Monitor - Web service for displaying PC performance on e-ink devices.
Serves a high-contrast, minimal page optimized for e-ink displays.
Works on both Windows and Linux.
"""

import platform
import socket
import time
from datetime import datetime

import psutil
from flask import Flask, jsonify, render_template

# ---------------------------------------------------------------------------
# GPU helper – GPUtil only works when an NVIDIA GPU + driver is present.
# We gracefully degrade if it is not available.
# ---------------------------------------------------------------------------
try:
    import GPUtil

    GPU_AVAILABLE = True
except (ImportError, Exception):
    GPU_AVAILABLE = False

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Data collection helpers
# ---------------------------------------------------------------------------

def get_cpu_info() -> dict:
    """Return CPU usage, frequency, core count, and per-core usage."""
    freq = psutil.cpu_freq()
    return {
        "usage_percent": psutil.cpu_percent(interval=0.5),
        "per_core_percent": psutil.cpu_percent(interval=0, percpu=True),
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "freq_current_mhz": round(freq.current, 1) if freq else None,
        "freq_max_mhz": round(freq.max, 1) if freq and freq.max else None,
    }


def get_memory_info() -> dict:
    """Return RAM and swap usage."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "ram_total_gb": round(vm.total / (1024 ** 3), 2),
        "ram_used_gb": round(vm.used / (1024 ** 3), 2),
        "ram_percent": vm.percent,
        "swap_total_gb": round(sw.total / (1024 ** 3), 2),
        "swap_used_gb": round(sw.used / (1024 ** 3), 2),
        "swap_percent": sw.percent,
    }


def get_disk_info() -> list[dict]:
    """Return usage for each mounted partition."""
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "percent": usage.percent,
                }
            )
        except PermissionError:
            continue
    return disks


def get_gpu_info() -> list[dict]:
    """Return NVIDIA GPU stats if available."""
    if not GPU_AVAILABLE:
        return []
    gpus = []
    try:
        for g in GPUtil.getGPUs():
            gpus.append(
                {
                    "id": g.id,
                    "name": g.name,
                    "load_percent": round(g.load * 100, 1),
                    "memory_total_mb": round(g.memoryTotal, 1),
                    "memory_used_mb": round(g.memoryUsed, 1),
                    "memory_percent": round(g.memoryUsed / g.memoryTotal * 100, 1)
                    if g.memoryTotal
                    else 0,
                    "temperature_c": g.temperature,
                }
            )
    except Exception:
        pass
    return gpus


def get_network_info() -> dict:
    """Return network I/O counters."""
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
    }


def get_system_info() -> dict:
    """Return general system metadata."""
    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "boot_time": boot.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{hours}h {minutes}m {seconds}s",
    }


def collect_all() -> dict:
    """Aggregate every metric into one dict."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_info(),
        "gpus": get_gpu_info(),
        "network": get_network_info(),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the e-ink optimized dashboard."""
    data = collect_all()
    return render_template("index.html", data=data)


@app.route("/api/stats")
def api_stats():
    """Return raw JSON (useful for programmatic consumers)."""
    return jsonify(collect_all())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  Eink System Monitor")
    print(f"  http://0.0.0.0:5000")
    print("  Open this URL in your e-ink device browser.")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
