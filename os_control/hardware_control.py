"""Windows volume, mute and brightness controls."""
# Enable modern type annotation behavior without changing runtime behavior.
from __future__ import annotations
# Import the operating-system identifier used to enforce Windows-only behavior.
import os


def _require_windows() -> None:
    # Reject hardware operations when the code is not running on Windows.
    if os.name != "nt":
        raise OSError("Hardware control requires Windows.")


def _get_volume_endpoint():
    """Return the default Windows audio endpoint."""
    # Ensure the audio API is only used on Windows.
    _require_windows()
    # Load pycaw lazily so importing this module does not require the optional package.
    try:
        # Import the helper that discovers Windows audio devices.
        from pycaw.pycaw import AudioUtilities
    # Turn a missing optional dependency into an actionable installation message.
    except ImportError as exc:
        raise RuntimeError("Install pycaw with: pip install pycaw") from exc

    # Discover the system's default speakers/audio endpoint.
    speakers = AudioUtilities.GetSpeakers()

    # Use the endpoint property exposed by some pycaw versions.
    if hasattr(speakers, "EndpointVolume"):
        return speakers.EndpointVolume

    # Use the COM activation path supported by other pycaw versions.
    if hasattr(speakers, "Activate"):
        # Import the audio endpoint interface identifier.
        from pycaw.pycaw import IAudioEndpointVolume
        # Import the COM context constant required for activation.
        from comtypes import CLSCTX_ALL
        # Activate the endpoint volume interface through COM.
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        # Return the typed interface used for volume operations.
        return interface.QueryInterface(IAudioEndpointVolume)

    # Fail clearly when neither supported endpoint access method is available.
    raise RuntimeError("Could not access the Windows audio endpoint.")


def get_volume() -> dict:
    # Resolve the default audio endpoint.
    endpoint = _get_volume_endpoint()
    # Return the current scalar volume and mute state.
    return {
        "volume_percent": round(endpoint.GetMasterVolumeLevelScalar() * 100, 2),
        "muted": bool(endpoint.GetMute()),
    }


def set_volume(level: float) -> dict:
    """Set master volume from 0 to 100."""
    # Reject values outside the supported percentage range.
    if not 0 <= level <= 100:
        raise ValueError("Volume must be between 0 and 100.")
    # Resolve the endpoint that controls the default output device.
    endpoint = _get_volume_endpoint()
    # Convert the percentage to pycaw's scalar range and apply it.
    endpoint.SetMasterVolumeLevelScalar(level / 100.0, None)
    # Return the actual resulting state.
    return get_volume()


def mute() -> dict:
    # Resolve the default audio endpoint.
    endpoint = _get_volume_endpoint()
    # Set the Windows mute flag to enabled.
    endpoint.SetMute(1, None)
    # Return a confirmation of the requested state.
    return {"success": True, "muted": True}


def unmute() -> dict:
    # Resolve the default audio endpoint.
    endpoint = _get_volume_endpoint()
    # Set the Windows mute flag to disabled.
    endpoint.SetMute(0, None)
    # Return a confirmation of the requested state.
    return {"success": True, "muted": False}


def get_brightness() -> int | None:
    # Load brightness support only when this function is called.
    try:
        # Import the optional display brightness package.
        import screen_brightness_control as sbc
    # Explain how to install the optional dependency when it is unavailable.
    except ImportError as exc:
        raise RuntimeError(
            "Install screen-brightness-control with: "
            "pip install screen-brightness-control"
        ) from exc
    # Query brightness values from connected displays.
    values = sbc.get_brightness()
    # Return the first display's value, or None when no value is reported.
    return int(values[0]) if values else None


def set_brightness(level: int) -> dict:
    """Set display brightness from 0 to 100."""
    # Reject values outside the supported percentage range.
    if not 0 <= level <= 100:
        raise ValueError("Brightness must be between 0 and 100.")
    # Load brightness support only when a write operation is requested.
    try:
        # Import the optional display brightness package.
        import screen_brightness_control as sbc
    # Explain how to install the optional dependency when it is unavailable.
    except ImportError as exc:
        raise RuntimeError(
            "Install screen-brightness-control with: "
            "pip install screen-brightness-control"
        ) from exc
    # Apply the requested percentage to the connected displays.
    sbc.set_brightness(level)
    # Return a structured confirmation of the requested value.
    return {"success": True, "brightness_percent": level}
