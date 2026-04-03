"""
kaori_voice_studio.updater
Checks GitHub for a newer version on each launch.
If an update is found, installs it via pip then relaunches safely.
"""

import sys
import subprocess
import urllib.request
import re


# ── Configuration ─────────────────────────────────────────────────────────────

GITHUB_RAW_VERSION_URL = (
    "https://raw.githubusercontent.com/cesarleija/text-to-speech-app/"
    "master/kaori_voice_studio/version.py"
)

GITHUB_INSTALL_URL = (
    "git+https://github.com/cesarleija/text-to-speech-app.git"
)

CHECK_TIMEOUT = 4   # seconds — skip update check if GitHub is slow or offline


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_version(text: str):
    """Extract a version tuple from a version.py file, e.g. '1.2.3' → (1,2,3)."""
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        return None
    try:
        return tuple(int(x) for x in m.group(1).split("."))
    except ValueError:
        return None


def _current_version():
    try:
        from kaori_voice_studio.version import __version__
        return tuple(int(x) for x in __version__.split("."))
    except Exception:
        return (0, 0, 0)


def _remote_version():
    """Fetch version.py from GitHub and parse it. Returns None on any failure."""
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
    """
    Run pip install --upgrade in a subprocess.
    Uses sys.executable so we always call the same Python that's running now.
    Returns True on success.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            "--upgrade", "--quiet", "--no-warn-script-location",
            GITHUB_INSTALL_URL,
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _relaunch():
    """
    Spawn a fresh copy of the app and exit the current process.

    os.execv() is unreliable on Windows (especially with pythonw.exe),
    so we use Popen to start a detached child process and then call sys.exit().
    The child inherits nothing from the current (possibly partially-updated)
    process, so it picks up the freshly installed package cleanly.
    """
    import os

    # Find the entry-point script pip installed (gui-scripts variant)
    scripts_dir = _scripts_dir()
    launcher = None
    for name in ("kaori-voice-studio.exe", "kaori-voice-studio-script.pyw",
                 "kaori-voice-studio"):
        candidate = scripts_dir / name
        if candidate.exists():
            launcher = str(candidate)
            break

    if launcher and launcher.endswith(".exe"):
        cmd = [launcher]
    elif launcher:
        cmd = [sys.executable, launcher]
    else:
        # Fallback: python -m kaori_voice_studio.app
        cmd = [sys.executable, "-m", "kaori_voice_studio.app"]

    kwargs = dict(close_fds=True)
    if sys.platform == "win32":
        # Detach completely from the current console / window
        DETACHED_PROCESS      = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    subprocess.Popen(cmd, **kwargs)
    sys.exit(0)


def _scripts_dir():
    from pathlib import Path
    return Path(sys.executable).parent / "Scripts"


# ── Public API ────────────────────────────────────────────────────────────────

def check_and_update(on_checking=None, on_update_found=None,
                     on_updated=None, on_no_update=None,
                     on_error=None):
    """
    Check GitHub for a newer version. If found, update silently and relaunch.

    Callbacks (all optional):
        on_checking()          called before the network request
        on_update_found(v)     called with the new version string
        on_updated()           called after a successful pip install
        on_no_update()         called when already on the latest version
        on_error(msg)          called on any non-fatal failure
    """
    if on_checking:
        on_checking()

    current = _current_version()
    remote  = _remote_version()

    if remote is None:
        if on_error:
            on_error("No internet — skipping update check.")
        return

    if remote <= current:
        if on_no_update:
            on_no_update()
        return

    remote_str = ".".join(str(x) for x in remote)
    if on_update_found:
        on_update_found(remote_str)

    success = _run_update()

    if success:
        if on_updated:
            on_updated()
        _relaunch()          # spawns fresh process, then sys.exit(0)
    else:
        if on_error:
            on_error("Update failed — launching current version.")