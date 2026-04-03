"""
kaori_voice_studio.updater
Checks GitHub for a newer version on each launch.
If an update is found, installs it via pip then relaunches safely.
All errors are written to kaori_update.log in the user's home folder.
"""

import sys
import subprocess
import urllib.request
import re
import traceback
from datetime import datetime
from pathlib import Path


# ── Configuration ─────────────────────────────────────────────────────────────

GITHUB_RAW_VERSION_URL = (
    "https://raw.githubusercontent.com/cesarleija/text-to-speech-app/"
    "master/kaori_voice_studio/version.py"
)

GITHUB_INSTALL_URL = (
    "git+https://github.com/cesarleija/text-to-speech-app.git"
)

CHECK_TIMEOUT = 4   # seconds — skip update check if GitHub is slow or offline

LOG_FILE = Path.home() / "kaori_update.log"


# ── Logging ───────────────────────────────────────────────────────────────────

def _log(msg: str):
    """Append a timestamped line to the log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_version(text: str):
    m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        return None
    try:
        return tuple(int(x) for x in m.group(1).split("."))
    except ValueError:
        return None


def _current_version():
    """
    Read version.py directly from disk — never from sys.modules cache.
    This ensures we always compare against the actually installed version,
    not a stale import from the current running process.
    """
    try:
        import importlib.resources as ir
        ref = ir.files("kaori_voice_studio") / "version.py"
        with ir.as_file(ref) as p:
            content = p.read_text(encoding="utf-8")
        v = _parse_version(content)
        if v:
            _log(f"Current version (from disk): {'.'.join(str(x) for x in v)}")
            return v
    except Exception as e:
        _log(f"importlib.resources failed: {e}")

    # Fallback: find version.py via the package location
    try:
        import kaori_voice_studio
        pkg_dir = Path(kaori_voice_studio.__file__).parent
        ver_file = pkg_dir / "version.py"
        content = ver_file.read_text(encoding="utf-8")
        v = _parse_version(content)
        if v:
            _log(f"Current version (fallback path): {'.'.join(str(x) for x in v)}")
            return v
    except Exception as e:
        _log(f"Fallback version read failed: {e}")

    _log("Could not determine current version — defaulting to 0.0.0")
    return (0, 0, 0)


def _remote_version():
    try:
        req = urllib.request.Request(
            GITHUB_RAW_VERSION_URL,
            headers={"Cache-Control": "no-cache"},
        )
        with urllib.request.urlopen(req, timeout=CHECK_TIMEOUT) as resp:
            content = resp.read().decode()
            v = _parse_version(content)
            _log(f"Remote version fetched: {v}")
            return v
    except Exception as e:
        _log(f"Could not fetch remote version: {e}")
        return None


def _run_update():
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--upgrade", "--quiet", "--no-warn-script-location",
        GITHUB_INSTALL_URL,
    ]
    _log(f"Running update: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        _log(f"pip returncode: {result.returncode}")
        if result.stdout.strip():
            _log(f"pip stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            _log(f"pip stderr: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        _log(f"Exception running pip: {e}\n{traceback.format_exc()}")
        return False


def _scripts_dir():
    return Path(sys.executable).parent / "Scripts"


def _relaunch():
    """
    Relaunch the app as a detached subprocess and exit the current process.
    Using 'python -m kaori_voice_studio.app' is the most reliable method on
    Windows — it avoids the pythonw.exe + .exe double-invocation issue that
    occurs with pip gui-scripts launchers.
    """
    # Always use python -m — safe on all Windows Python installs
    cmd = [sys.executable, "-m", "kaori_voice_studio.app"]

    _log(f"Relaunching with: {' '.join(cmd)}")

    kwargs = {}
    if sys.platform == "win32":
        DETACHED_PROCESS         = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs["creationflags"]  = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    try:
        subprocess.Popen(cmd, **kwargs)
        _log("Relaunch spawned — exiting current process.")
    except Exception as e:
        _log(f"Relaunch failed: {e}\n{traceback.format_exc()}")

    sys.exit(0)

# ── Public API ────────────────────────────────────────────────────────────────

def check_and_update(on_checking=None, on_update_found=None,
                     on_updated=None, on_no_update=None,
                     on_error=None):
    _log("=== Update check started ===")
    try:
        if on_checking:
            on_checking()

        current = _current_version()
        remote  = _remote_version()

        if remote is None:
            msg = "No internet — skipping update check."
            _log(msg)
            if on_error:
                on_error(msg)
            return

        if remote <= current:
            _log("Already up to date.")
            if on_no_update:
                on_no_update()
            return

        remote_str = ".".join(str(x) for x in remote)
        _log(f"Update available: {remote_str}")
        if on_update_found:
            on_update_found(remote_str)

        success = _run_update()

        if success:
            _log("Update successful — relaunching.")
            if on_updated:
                on_updated()
            import time; time.sleep(0.4)  # let Tk process after(0) splash destroy
            _relaunch()
        else:
            msg = "Update failed — launching current version."
            _log(msg)
            if on_error:
                on_error(msg)

    except Exception as e:
        _log(f"Unhandled exception in check_and_update:\n{traceback.format_exc()}")
        if on_error:
            on_error(str(e))