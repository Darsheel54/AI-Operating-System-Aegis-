"""Resource-analysis support for Project Aegis.

This module recommends candidates; it does NOT automatically kill processes.
Authorization belongs to the Security/Guardrails layer.
"""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations

# Import the process snapshot provider used to identify candidates.
from .process_manager import get_processes
# Import the CPU and memory snapshot providers used in analysis results.
from .resource_monitor import get_cpu_usage, get_memory_usage


def _reason(memory: float, cpu: float, min_memory_mb: float, min_cpu: float) -> str:
    # Collect human-readable explanations for each threshold that was exceeded.
    reasons = []
    # Add a RAM explanation when memory reaches the configured threshold.
    if memory >= min_memory_mb:
        reasons.append(f"RAM >= {min_memory_mb:.0f} MB")
    # Add a CPU explanation when CPU reaches the configured threshold.
    if cpu >= min_cpu:
        reasons.append(f"CPU >= {min_cpu:.1f}%")
    # Join multiple reasons into one readable description.
    return " and ".join(reasons)


def find_optimization_candidates(
    min_memory_mb: float = 300.0,
    min_cpu_percent: float = 5.0,
    limit: int = 10,
) -> list[dict]:
    """Return processes worth reviewing, not processes to kill automatically."""
    # Reject negative thresholds because resource usage cannot be negative.
    if min_memory_mb < 0 or min_cpu_percent < 0:
        raise ValueError("Thresholds cannot be negative.")
    # Require a positive result limit.
    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    # Create the list of processes that exceed at least one threshold.
    candidates = []
    # Inspect the current process snapshot.
    for p in get_processes():
        # Treat missing memory values as zero for safe comparison.
        memory = p.get("memory_mb", 0.0) or 0.0
        # Treat missing CPU values as zero for safe comparison.
        cpu = p.get("cpu_percent") or 0.0

        # Select processes that exceed either configured resource threshold.
        if memory >= min_memory_mb or cpu >= min_cpu_percent:
            # Preserve process details and add the reason for selection.
            candidates.append({
                **p,
                "reason": _reason(memory, cpu, min_memory_mb, min_cpu_percent),
            })

    # Rank candidates by memory first and CPU second, both highest first.
    candidates.sort(
        key=lambda x: (x.get("memory_mb", 0), x.get("cpu_percent", 0)),
        reverse=True,
    )
    # Return no more than the requested number of candidates.
    return candidates[:limit]


def analyze_resources() -> dict:
    """Return a current resource snapshot plus optimization candidates."""
    # Combine current system usage with processes worth reviewing.
    return {
        "cpu_percent": get_cpu_usage(),
        "memory": get_memory_usage(),
        "candidates": find_optimization_candidates(),
    }


def estimate_memory_recovery(pids: list[int]) -> float:
    """Estimate RAM held by selected PIDs; does not terminate anything."""
    # Convert the requested PID list to a set for efficient membership checks.
    selected = set(pids)
    # Add memory values for selected processes in the current snapshot.
    total = sum(
        p.get("memory_mb", 0.0) or 0.0
        for p in get_processes()
        if p["pid"] in selected
    )
    # Round the estimate to two decimal places for API output.
    return round(total, 2)


def measure_improvement(before: dict, after: dict) -> dict:
    """Compare CPU/RAM percentages before and after an approved action."""
    # Read RAM percentages from both snapshots when present.
    before_ram = before.get("memory", {}).get("percent")
    after_ram = after.get("memory", {}).get("percent")
    # Read CPU percentages from both snapshots when present.
    before_cpu = before.get("cpu_percent")
    after_cpu = after.get("cpu_percent")

    # Return reductions as positive values and unavailable comparisons as None.
    return {
        "ram_percent_change": (
            round(before_ram - after_ram, 2)
            if before_ram is not None and after_ram is not None else None
        ),
        "cpu_percent_change": (
            round(before_cpu - after_cpu, 2)
            if before_cpu is not None and after_cpu is not None else None
        ),
    }
