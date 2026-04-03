"""
kaori_voice_studio.updater
Checks GitHub for a newer version on each launch.
If an update is found, installs it via pip and relaunches the app.
"""

import sys
import os
import subprocess
import urllib.request
import urllib.error
import json
import re
from pathlib import Path


# ── Configuration ─────────────────────────────────────────────────────────────

GITHUB_RAW_VERSION_URL = (
    "https://raw.githubusercontent.com/cesarleija/text-to-speech-app/"
    "master/kaori_voice_studio/version.py"
)

GITHUB_INSTALL_URL = (
    "git+https://github.com/cesarleija/text-to-speech-app.git"
)

CHECK_TIMEOUT = 4   # seconds — skip update check if GitHub is slow


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_version(text: str):
    """Extract version tuple from a version.py string, e.g. '1.2.3' → (1,2,3)."""
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        return None
    try:
        return tuple(int(x) for x in m.group(1).split("."))
    except ValueError:
        return None


def _current_version():
    from kaori_voice_studio.version import __version__
    try:
        return tuple(int(x) for x in __version__.split("."))
    except ValueError:
        return (0, 0, 0)


def _remote_version():
    """Fetch the version string from GitHub. Returns None on any failure."""
    try:
        req = urllib.request.Request(
            GITHUB_RAW_VERSION_URL,
            headers={"Cache-Control": "no-cache"},
        )
        with urllib.request.urlopen(req, timeout=CHECK_TIMEOUT) as resp:
            return _parse_version(resp.read().decode())
    except Exception:
        return None


def _run_update():
    """Run pip install --upgrade and return True if it succeeded."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet",
         GITHUB_INSTALL_URL],
        capture_output=True, text=True
    )
    return result.returncode == 0


def _relaunch():
    """Replace the current process with a fresh launch of the app."""
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ── Public API ────────────────────────────────────────────────────────────────

def check_and_update(on_checking=None, on_update_found=None,
                     on_updated=None, on_no_update=None,
                     on_error=None):
    """
    Check GitHub for a newer version. If found, update and relaunch.

    Optional callbacks let the caller show UI feedback:
        on_checking()          — called before the network request
        on_update_found(v)     — called with the new version string
        on_updated()           — called after successful pip install
        on_no_update()         — called when already up to date
        on_error(msg)          — called if the check fails silently
    """
    if on_checking:
        on_checking()

    current = _current_version()
    remote  = _remote_version()

    if remote is None:
        if on_error:
            on_error("Could not reach GitHub — skipping update check.")
        return

    if remote <= current:
        if on_no_update:
            on_no_update()
        return

    # A newer version exists
    remote_str = ".".join(str(x) for x in remote)
    if on_update_found:
        on_update_found(remote_str)

    success = _run_update()

    if success:
        if on_updated:
            on_updated()
        _relaunch()
    else:
        if on_error:
            on_error("Update download failed — launching current version.")
