"""Windows lock, restart and shutdown controls."""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations
# Import ctypes for the native Windows workstation lock call.
import ctypes
# Import the operating-system identifier used to enforce Windows-only behavior.
import os
# Import subprocess for Windows shutdown command invocation.
import subprocess


def _require_windows() -> None:
    # Reject workstation operations when the code is not running on Windows.
    if os.name != "nt":
        raise OSError("Workstation control requires Windows.")


def lock_workstation() -> dict:
    """Lock the current Windows session."""
    # Ensure the native lock API is only called on Windows.
    _require_windows()
    # Ask Windows to lock the interactive user's workstation.
    if not ctypes.windll.user32.LockWorkStation():
        raise RuntimeError("Windows failed to lock the workstation.")
    # Return a structured confirmation after the lock request succeeds.
    return {"success": True, "action": "lock", "message": "Workstation locked."}


def restart_system() -> dict:
    """
    Schedule a restart after 5 seconds.

    The Aegis Security/Confirmation layer must approve this action first.
    """
    # Ensure the shutdown command is only used on Windows.
    _require_windows()
    # Schedule a restart five seconds from now without opening a console window.
    subprocess.Popen(
        ["shutdown", "/r", "/t", "5"],
        shell=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    # Return confirmation that the restart command was submitted.
    return {
        "success": True,
        "action": "restart",
        "message": "Restart scheduled in 5 seconds.",
    }


def shutdown_system() -> dict:
    """
    Schedule a shutdown after 5 seconds.

    The Aegis Security/Confirmation layer must approve this action first.
    """
    # Ensure the shutdown command is only used on Windows.
    _require_windows()
    # Schedule a shutdown five seconds from now without opening a console window.
    subprocess.Popen(
        ["shutdown", "/s", "/t", "5"],
        shell=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    # Return confirmation that the shutdown command was submitted.
    return {
        "success": True,
        "action": "shutdown",
        "message": "Shutdown scheduled in 5 seconds.",
    }


def cancel_shutdown() -> dict:
    """Cancel a pending shutdown/restart."""
    # Ensure the shutdown command is only used on Windows.
    _require_windows()
    # Ask Windows to cancel any pending shutdown or restart.
    subprocess.Popen(
        ["shutdown", "/a"],
        shell=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    # Return confirmation that the cancellation command was submitted.
    return {
        "success": True,
        "action": "cancel_shutdown",
        "message": "Pending shutdown/restart cancelled.",
    }
