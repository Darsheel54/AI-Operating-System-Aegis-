"""Read-only Windows system resource monitoring for Project Aegis."""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations
# Import psutil for CPU, memory, disk, and battery readings.
import psutil


def get_cpu_usage(interval: float = 0.5) -> float:
    """Return overall CPU usage percentage."""
    # Reject negative sampling intervals because psutil cannot use them.
    if interval < 0:
        raise ValueError("interval cannot be negative")
    # Sample overall CPU utilization and round it for stable API output.
    return round(psutil.cpu_percent(interval=interval), 2)


def get_memory_usage() -> dict:
    """Return RAM statistics."""
    # Read the operating system's current virtual-memory statistics.
    m = psutil.virtual_memory()
    # Return memory values in megabytes plus the overall percentage used.
    return {
        "total_mb": round(m.total / (1024 ** 2), 2),
        "used_mb": round(m.used / (1024 ** 2), 2),
        "available_mb": round(m.available / (1024 ** 2), 2),
        "percent": round(m.percent, 2),
    }


def get_disk_usage(path: str = "C:\\") -> dict:
    """Return disk statistics for a Windows path."""
    # Read capacity and utilization for the requested filesystem path.
    d = psutil.disk_usage(path)
    # Return disk values in gigabytes plus the path and usage percentage.
    return {
        "path": path,
        "total_gb": round(d.total / (1024 ** 3), 2),
        "used_gb": round(d.used / (1024 ** 3), 2),
        "free_gb": round(d.free / (1024 ** 3), 2),
        "percent": round(d.percent, 2),
    }


def get_battery_status() -> dict | None:
    """Return battery information, or None on desktops."""
    # Ask psutil for battery information when the machine exposes a battery.
    b = psutil.sensors_battery()
    # Desktop systems commonly have no battery sensor.
    if b is None:
        return None
    # Return normalized battery state for portable computers.
    return {
        "percent": round(b.percent, 2),
        "plugged_in": bool(b.power_plugged),
        "seconds_left": b.secsleft,
    }


def get_system_summary() -> dict:
    """Return CPU, RAM, disk and battery information."""
    # Gather all supported resource categories into one snapshot.
    return {
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage(),
        "battery": get_battery_status(),
    }
