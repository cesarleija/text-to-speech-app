"""
create_shortcut.py
Run this once on any machine where Kaori Voice Studio is installed:
    python create_shortcut.py
It creates a Desktop shortcut with the app icon.
"""

import sys
import os
import subprocess
from pathlib import Path


def find_entry_point():
    """Find the kaori-voice-studio executable installed by pip."""
    scripts_dir = Path(sys.executable).parent / "Scripts"
    for name in ("kaori-voice-studio.exe", "kaori-voice-studio-script.pyw",
                 "kaori-voice-studio"):
        exe = scripts_dir / name
        if exe.exists():
            return str(exe)
    return None


def find_icon():
    """Locate the .ico bundled with the installed package."""
    try:
        import importlib.resources as ir
        # Python 3.9+
        ref = ir.files("kaori_voice_studio") / "kaori_voice_studio.ico"
        with ir.as_file(ref) as p:
            if p.exists():
                return str(p)
    except Exception:
        pass

    # Fallback: search site-packages directly
    import site
    for sp in site.getsitepackages():
        ico = Path(sp) / "kaori_voice_studio" / "kaori_voice_studio.ico"
        if ico.exists():
            return str(ico)
    return None


def create_shortcut():
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "Kaori Voice Studio.lnk"
    entry_point = find_entry_point()
    icon_path = find_icon()

    if entry_point:
        target = entry_point
        args = ""
    else:
        target = sys.executable
        args = "-m kaori_voice_studio.app"

    icon_line = f"$sc.IconLocation = '{icon_path}'" if icon_path else ""

    ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{shortcut_path}')
$sc.TargetPath = '{target}'
$sc.Arguments = '{args}'
$sc.WorkingDirectory = '{Path.home()}'
$sc.Description = 'Kaori Voice Studio - Text to Speech'
{icon_line}
$sc.Save()
"""

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )

    if result.returncode == 0 and shortcut_path.exists():
        print(f"Shortcut created: {shortcut_path}")
        if icon_path:
            print(f"Icon applied:    {icon_path}")
        else:
            print("Icon not found — shortcut created without custom icon.")
    else:
        print("Could not create shortcut automatically.")
        print(f"  Target : {target}")
        print(f"  Args   : {args}")
        if result.stderr:
            print(f"  Error  : {result.stderr.strip()}")


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only.")
        sys.exit(1)
    create_shortcut()
