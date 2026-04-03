"""
kaori_voice_studio.create_shortcut
Creates a Windows Desktop shortcut for Kaori Voice Studio.

Called automatically after pip install via the post-install script entry point.
Can also be run manually at any time:
    python -m kaori_voice_studio.create_shortcut
"""

import sys
import subprocess
from pathlib import Path


def find_entry_point():
    """Find the GUI launcher installed by pip."""
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
        ref = ir.files("kaori_voice_studio") / "kaori_voice_studio.ico"
        with ir.as_file(ref) as p:
            if p.exists():
                return str(p)
    except Exception:
        pass

    import site
    for sp in site.getsitepackages():
        ico = Path(sp) / "kaori_voice_studio" / "kaori_voice_studio.ico"
        if ico.exists():
            return str(ico)
    return None


def create_shortcut():
    """Create the Desktop shortcut. Returns True on success."""
    if sys.platform != "win32":
        print("Desktop shortcut creation is only supported on Windows.")
        return False

    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "Kaori Voice Studio.lnk"
    entry_point = find_entry_point()
    icon_path = find_icon()

    if entry_point:
        target = entry_point
        args = "-m kaori_voice_studio.app"  # always use -m for reliability
    else:
        target = sys.executable
        args = "-m kaori_voice_studio.app"

    # Always launch via pythonw.exe (no console window) with -m
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    if pythonw.exists():
        target = str(pythonw)
    else:
        target = sys.executable

    # Use double-quoted PowerShell strings ("...") to safely handle
    # paths containing spaces (e.g. "C:\Users\Julio Leija\Desktop\...")
    def ps(p):
        # Escape double-quotes and backslashes inside a PS double-quoted string
        return str(p).replace("\\", "\\\\").replace('"', '\\"')

    icon_line = f'$sc.IconLocation = "{ps(icon_path)}"' if icon_path else ""

    ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("{ps(shortcut_path)}")
$sc.TargetPath = "{ps(target)}"
$sc.Arguments = "{args}"
$sc.WorkingDirectory = "{ps(Path.home())}"
$sc.Description = "Kaori Voice Studio - Text to Speech"
{icon_line}
$sc.Save()
"""

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )

    if result.returncode == 0 and shortcut_path.exists():
        print(f"  Shortcut created : {shortcut_path}")
        if icon_path:
            print(f"  Icon applied     : {icon_path}")
        return True
    else:
        print("  Could not create shortcut automatically.")
        if result.stderr:
            print(f"  Error: {result.stderr.strip()}")
        return False


def main():
    print("\nKaori Voice Studio — creating desktop shortcut...")
    create_shortcut()


if __name__ == "__main__":
    main()