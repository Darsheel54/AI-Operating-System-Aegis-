"""Process monitoring and controlled termination for Project Aegis."""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations
# Import psutil for process discovery, metrics, and termination.
import psutil


def _process_record(p: psutil.Process) -> dict:
    """Convert a psutil process to a safe dictionary."""
    # Protect the complete record operation from processes that disappear or deny access.
    try:
        # Cache process information while collecting this record.
        with p.oneshot():
            # CPU measurements can fail for protected or already-closed processes.
            try:
                # Read the process CPU percentage without waiting for a new interval.
                cpu = p.cpu_percent(interval=None)
            # Represent inaccessible CPU data as unavailable instead of failing the scan.
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cpu = None
            # User lookups can fail for protected or already-closed processes.
            try:
                # Read the account that owns the process.
                username = p.username()
            # Represent inaccessible ownership data as unavailable.
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                username = None

            # Return the process data in the package's stable dictionary format.
            return {
                "pid": p.pid,
                "name": p.name(),
                "status": p.status(),
                "cpu_percent": round(cpu, 2) if cpu is not None else None,
                "memory_mb": round(p.memory_info().rss / (1024 ** 2), 2),
                "username": username,
            }
    # Ignore processes that cannot be inspected safely.
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return {}


def get_processes() -> list[dict]:
    """Return currently running processes."""
    # Create the list that will contain successfully inspected processes.
    result = []
    # Iterate over the processes visible to the current user.
    for p in psutil.process_iter():
        # Convert each psutil object to a safe serializable record.
        record = _process_record(p)
        # Keep only records that were read successfully.
        if record:
            result.append(record)
    # Return all readable process records.
    return result


def get_process_info(pid: int) -> dict:
    """Return information for one process."""
    # Resolve and inspect the requested process identifier.
    try:
        # Build a normalized record for the selected process.
        record = _process_record(psutil.Process(pid))
    # Convert a missing process into a caller-friendly validation error.
    except psutil.NoSuchProcess as exc:
        raise ValueError(f"Process {pid} does not exist.") from exc

    # Reject a record that could not be read because of permissions or a race.
    if not record:
        raise RuntimeError(f"Could not read process {pid}.")
    # Return the inspected process details.
    return record


def get_top_memory_processes(limit: int = 10) -> list[dict]:
    """Return processes sorted by RAM usage."""
    # Require a positive number of requested results.
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    # Retrieve the current process snapshot.
    data = get_processes()
    # Sort from the largest resident-memory consumer to the smallest.
    data.sort(key=lambda x: x["memory_mb"], reverse=True)
    # Return only the requested number of records.
    return data[:limit]


def get_top_cpu_processes(limit: int = 10) -> list[dict]:
    """Return processes sorted by CPU usage."""
    # Require a positive number of requested results.
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    # Retrieve the current process snapshot.
    data = get_processes()
    # Sort unavailable CPU values below all measured values.
    data.sort(
        key=lambda x: x["cpu_percent"] if x["cpu_percent"] is not None else -1,
        reverse=True,
    )
    # Return only the requested number of records.
    return data[:limit]


def terminate_process(pid: int, timeout: float = 3.0) -> dict:
    """
    Terminate one process.

    IMPORTANT: call this only after the Security/Guardrails layer has
    approved the PID and operation.
    """
    # Reject invalid process identifiers before calling the operating system.
    if pid <= 0:
        raise ValueError("PID must be positive")

    # Resolve the process and request a graceful termination.
    try:
        # Open the process identified by the caller.
        p = psutil.Process(pid)
        # Capture the name before termination removes the process.
        name = p.name()
        # Ask the operating system to terminate the process.
        p.terminate()
        # Wait briefly for the process to exit.
        try:
            # Return success when the process exits before the timeout.
            p.wait(timeout=timeout)
            return {
                "success": True,
                "pid": pid,
                "name": name,
                "message": f"{name} terminated successfully.",
            }
        # Report that the process did not exit within the requested wait time.
        except psutil.TimeoutExpired:
            return {
                "success": False,
                "pid": pid,
                "name": name,
                "message": f"{name} did not exit within {timeout} seconds.",
            }
    # Convert a missing process into a caller-friendly validation error.
    except psutil.NoSuchProcess as exc:
        raise ValueError(f"Process {pid} does not exist.") from exc
    # Convert operating-system permission failures into a clear exception.
    except psutil.AccessDenied as exc:
        raise PermissionError(f"Access denied for process {pid}.") from exc
