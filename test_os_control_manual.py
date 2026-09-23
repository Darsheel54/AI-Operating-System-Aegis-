"""
Manual smoke tests for Project Aegis OS Control.

Run on Windows after installing requirements.
These tests intentionally DO NOT test shutdown/restart automatically.
"""
from os_control.resource_monitor import get_system_summary
from os_control.process_manager import get_top_memory_processes
from os_control.application_launcher import launch_application
from os_control.hardware_control import get_volume, get_brightness


print("SYSTEM SUMMARY")
print(get_system_summary())

print("\nTOP MEMORY PROCESSES")
for item in get_top_memory_processes(5):
    print(item)

print("\nCURRENT VOLUME")
try:
    print(get_volume())
except Exception as exc:
    print("Volume unavailable:", exc)

print("\nCURRENT BRIGHTNESS")
try:
    print(get_brightness())
except Exception as exc:
    print("Brightness unavailable:", exc)

# Uncomment only when you explicitly want to test application launching:
print(launch_application("Chrome"))
