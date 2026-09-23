"""Controlled Windows application launcher."""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations
# Import operating-system helpers such as environment variables and startfile.
import os
# Import regular expressions used to normalize application names.
import re
# Import Path for safe filesystem path construction and traversal.
from pathlib import Path

# Define the per-user and system-wide Start Menu locations to search.
START_MENU_LOCATIONS = (
    # Locate shortcuts installed for the current Windows user.
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    # Locate shortcuts installed for every Windows user.
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
)

# Normalize a string for comparison: lowercase, remove extension, remove non-alphanumeric characters.
def _normalize(value: str) -> str:
    # Convert the supplied name to lowercase and remove surrounding whitespace.
    value = value.lower().strip()
    # Remove common Windows application filename extensions.
    value = re.sub(r"\.(lnk|exe)$", "", value)
    # Remove punctuation and spaces so equivalent names compare equally.
    return re.sub(r"[^a-z0-9]+", "", value)

# Find a shortcut in the Start Menu that matches the application name. Returns the first match found.
def _find_shortcut(application_name: str) -> Path | None:
    # Normalize the requested application name before comparing it.
    target = _normalize(application_name)
    # Stop immediately when normalization produced no usable search text.
    if not target:
        return None

    # Keep exact matches separate so they take priority over partial matches.
    exact, partial = [], []
    # Search each configured Start Menu root.
    for root in START_MENU_LOCATIONS:
        # Skip roots that do not exist on this machine.
        if not root.exists():
            continue
        # Ignore filesystem errors so one inaccessible root does not stop the search.
        try:
            # Recursively enumerate Windows shortcut files.
            shortcuts = root.rglob("*.lnk")
            # Compare each shortcut filename with the normalized target.
            for shortcut in shortcuts:
                # Normalize the shortcut filename without its extension.
                name = _normalize(shortcut.stem)
                # Store exact matches for highest-priority selection.
                if name == target:
                    exact.append(shortcut)
                # Store names containing one another as fallback matches.
                elif target in name or name in target:
                    partial.append(shortcut)
        # Ignore shortcuts that disappear or cannot be read during traversal.
        except OSError:
            continue

    # Return the shortest-path exact match, which is usually the most direct shortcut.
    if exact:
        return sorted(exact, key=lambda p: len(str(p)))[0]
    # Return the shortest-path partial match when no exact match exists.
    if partial:
        return sorted(partial, key=lambda p: len(str(p)))[0]
    # Report that no matching shortcut was found.
    return None


def launch_application(application_name: str) -> dict:
    """Launch an installed application via its Start Menu shortcut."""
    # Refuse to call the Windows-only launcher on another operating system.
    if os.name != "nt":
        raise OSError("Application launching requires Windows.")
    # Reject missing or whitespace-only application names.
    if not application_name or not application_name.strip():
        raise ValueError("Application name cannot be empty.")

    # Resolve the requested application to a Start Menu shortcut.
    shortcut = _find_shortcut(application_name)
    # Return a structured failure when no shortcut could be resolved.
    if shortcut is None:
        return {
            "success": False,
            "application": application_name,
            "message": f"Could not find '{application_name}' in the Start Menu.",
        }

    # Start the application and convert Windows launch errors into a result object.
    try:
        # Ask Windows to open the shortcut using its registered target.
        os.startfile(str(shortcut))
        return {
            "success": True,
            "application": application_name,
            "shortcut": str(shortcut),
            "message": f"Launched {shortcut.stem}.",
        }
    # Return a safe failure response when Windows cannot launch the shortcut.
    except OSError as exc:
        return {
            "success": False,
            "application": application_name,
            "message": f"Windows could not launch the application: {exc}",
        }
