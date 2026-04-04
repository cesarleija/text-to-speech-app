import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import asyncio
import threading
import os
import tempfile
import math
import edge_tts
import pygame
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Themes
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "Dark": {
        "BG":        "#0F1117",
        "PANEL":     "#181C27",
        "SURFACE":   "#1E2336",
        "BORDER":    "#2A3050",
        "ACCENT":    "#F0A500",
        "ACCENT_HO": "#FFB830",
        "ACCENT_TK": "#F0A500",   # colour used inside tk widgets (e.g. insertbackground)
        "TEXT":      "#E8EAF0",
        "TEXT_DIM":  "#6B7399",
        "SUCCESS":   "#3DDC84",
        "ERROR":     "#FF5A5A",
        "BTN_FG":    "#0F1117",   # label colour on accent button
    },
    "Pink": {
        "BG":        "#FDF0F6",
        "PANEL":     "#FFFFFF",
        "SURFACE":   "#FCE4F1",
        "BORDER":    "#F0B8D8",
        "ACCENT":    "#E8387A",
        "ACCENT_HO": "#C42A64",
        "ACCENT_TK": "#E8387A",
        "TEXT":      "#2D0A1A",
        "TEXT_DIM":  "#A0527A",
        "SUCCESS":   "#1A9E5A",
        "ERROR":     "#CC2222",
        "BTN_FG":    "#FFFFFF",
    },
}

# Active theme dict – widgets read from this at draw time
T = dict(THEMES["Pink"])

FONTS = {
    "body":  ("Segoe UI", 10),
    "bold":  ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "title": ("Segoe UI", 14, "bold"),
    "label": ("Segoe UI", 11),
}

VOICES = {
    "🇺🇸  Guy (Male · US)"        : "en-US-GuyNeural",
    "🇺🇸  Jenny (Female · US)"    : "en-US-JennyNeural",
    "🇺🇸  Aria (Female · US)"     : "en-US-AriaNeural",
    "🇺🇸  Davis (Male · US)"      : "en-US-DavisNeural",
    "🇬🇧  Ryan (Male · UK)"       : "en-GB-RyanNeural",
    "🇬🇧  Sonia (Female · UK)"    : "en-GB-SoniaNeural",
    "🇦🇺  William (Male · AU)"    : "en-AU-WilliamNeural",
    "🇦🇺  Natasha (Female · AU)"  : "en-AU-NatashaNeural",
    "🇮🇳  Prabhat (Male · IN)"    : "en-IN-PrabhatNeural",
    "🇮🇳  Neerja (Female · IN)"   : "en-IN-NeerjaNeural",
    "🇨🇦  Liam (Male · CA)"       : "en-CA-LiamNeural",
    "🇨🇦  Clara (Female · CA)"    : "en-CA-ClaraNeural",
    "🇲🇽  Dalia (Female · MX)"    : "es-MX-DaliaNeural",
    "🇲🇽  Jorge (Male · MX)"      : "es-MX-JorgeNeural",
    "🇪🇸  Alvaro (Male · ES)"     : "es-ES-AlvaroNeural",
    "🇪🇸  Elvira (Female · ES)"   : "es-ES-ElviraNeural",
    "🇦🇷  Elena (Female · AR)"    : "es-AR-ElenaNeural",
    "🇦🇷  Tomas (Male · AR)"      : "es-AR-TomasNeural",
    "🇫🇷  Denise (Female · FR)"   : "fr-FR-DeniseNeural",
    "🇩🇪  Katja (Female · DE)"    : "de-DE-KatjaNeural",
    "🇯🇵  Nanami (Female · JP)"   : "ja-JP-NanamiNeural",
    "🇨🇳  Xiaoxiao (Female · CN)" : "zh-CN-XiaoxiaoNeural",
    "🇰🇷  SunHi (Female · KR)"    : "ko-KR-SunHiNeural",
    "🇮🇹  Elsa (Female · IT)"     : "it-IT-ElsaNeural",
    "🇧🇷  Francisca (Female · BR)": "pt-BR-FranciscaNeural",
    "🇷🇺  Dariya (Female · RU)"   : "ru-RU-DariyaNeural",
}

PREVIEW_SENTENCES = {
    "en": "Hello! This is a preview of the selected voice. How does it sound to you?",
    "es": "¡Hola! Esta es una vista previa de la voz seleccionada. ¿Cómo le suena?",
    "fr": "Bonjour! Ceci est un apercu de la voix selectionnee.",
    "de": "Hallo! Dies ist eine Vorschau der ausgewaehlten Stimme.",
    "ja": "This is a Japanese voice preview.",
    "zh": "This is a Chinese voice preview.",
    "ko": "This is a Korean voice preview.",
    "it": "Ciao! Questa e un anteprima della voce selezionata.",
    "pt": "Ola! Esta e uma pre-visualizacao da voz selecionada.",
    "ru": "This is a Russian voice preview.",
}

MIN_W, MIN_H   = 680, 560
RIGHT_PANEL_W  = 230

# ── Kokoro voices ─────────────────────────────────────────────────────────────
# Format:  "Display label" : "kokoro_voice_id"
# lang_code: 'a'=American English, 'b'=British English, 'e'=Spanish, 'f'=French,
#            'h'=Hindi, 'i'=Italian, 'p'=Portuguese, 'j'=Japanese, 'z'=Chinese

KOKORO_VOICES = {
    # American English – Female
    "🇺🇸  Heart (Female · Warm)"      : ("af_heart",    "en-us"),
    "🇺🇸  Bella (Female · Soft)"      : ("af_bella",    "en-us"),
    "🇺🇸  Sarah (Female · Natural)"   : ("af_sarah",    "en-us"),
    "🇺🇸  Nicole (Female · Whisper)"  : ("af_nicole",   "en-us"),
    "🇺🇸  Sky (Female · Airy)"        : ("af_sky",      "en-us"),
    "🇺🇸  Alloy (Female · Clear)"     : ("af_alloy",    "en-us"),
    "🇺🇸  Nova (Female · Bright)"     : ("af_nova",     "en-us"),
    "🇺🇸  River (Female · Calm)"      : ("af_river",    "en-us"),
    "🇺🇸  Jessica (Female · Warm)"    : ("af_jessica",  "en-us"),
    "🇺🇸  Kore (Female · Strong)"     : ("af_kore",     "en-us"),
    "🇺🇸  Aoede (Female · Musical)"   : ("af_aoede",    "en-us"),
    # American English – Male
    "🇺🇸  Adam (Male · Deep)"         : ("am_adam",     "en-us"),
    "🇺🇸  Michael (Male · Warm)"      : ("am_michael",  "en-us"),
    "🇺🇸  Echo (Male · Clear)"        : ("am_echo",     "en-us"),
    "🇺🇸  Eric (Male · Natural)"      : ("am_eric",     "en-us"),
    "🇺🇸  Fenrir (Male · Strong)"     : ("am_fenrir",   "en-us"),
    "🇺🇸  Liam (Male · Friendly)"     : ("am_liam",     "en-us"),
    "🇺🇸  Onyx (Male · Deep)"         : ("am_onyx",     "en-us"),
    "🇺🇸  Puck (Male · Playful)"      : ("am_puck",     "en-us"),
    # British English – Female
    "🇬🇧  Emma (Female · Elegant)"    : ("bf_emma",     "en-gb"),
    "🇬🇧  Alice (Female · Clear)"     : ("bf_alice",    "en-gb"),
    "🇬🇧  Isabella (Female · Warm)"   : ("bf_isabella", "en-gb"),
    "🇬🇧  Lily (Female · Soft)"       : ("bf_lily",     "en-gb"),
    # British English – Male
    "🇬🇧  George (Male · Authoritative)": ("bm_george", "en-gb"),
    "🇬🇧  Lewis (Male · Natural)"     : ("bm_lewis",    "en-gb"),
    "🇬🇧  Daniel (Male · Warm)"       : ("bm_daniel",   "en-gb"),
    "🇬🇧  Fable (Male · Story)"       : ("bm_fable",    "en-gb"),
    # Child-like voices
    "🧒  Child · Girl (Sky)"          : ("af_sky",      "en-us"),
    "🧒  Child · Boy (Puck)"          : ("am_puck",     "en-us"),
}

KOKORO_ESPEAK_INSTALL = (
    "Kokoro requires espeak-ng to be installed on your system.\n\n"
    "Download the Windows installer from:\n"
    "https://github.com/espeak-ng/espeak-ng/releases\n\n"
    "Download the .msi file, install it, then restart Kaori Voice Studio."
)


# ─────────────────────────────────────────────────────────────────────────────
# Audio helpers
# ─────────────────────────────────────────────────────────────────────────────

def _rate_str(speed):
    pct = int(round((speed - 1.0) * 100))
    return f"+{pct}%" if pct >= 0 else f"{pct}%"

def _volume_str(vol):
    pct = int(round(vol - 100))
    return f"+{pct}%" if pct >= 0 else f"{pct}%"

def _pitch_str(hz):
    val = int(round(hz))
    return f"+{val}Hz" if val >= 0 else f"{val}Hz"


def _log_kokoro(msg: str):
    """Append a timestamped line to the kokoro debug log."""
    try:
        from datetime import datetime
        log = Path.home() / "kaori_kokoro.log"
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def _kokoro_available():
    """Check if kokoro-onnx and soundfile packages are importable."""
    try:
        import kokoro_onnx  # noqa: F401
        import soundfile    # noqa: F401
        return True
    except ImportError:
        return False


# Lazily loaded Kokoro instance — downloaded on first use
_kokoro_instance = None
_KOKORO_MODEL_URL  = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
_KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def _get_kokoro():
    """Return a cached Kokoro ONNX instance, downloading model files if needed."""
    global _kokoro_instance
    if _kokoro_instance is not None:
        return _kokoro_instance

    import urllib.request
    from kokoro_onnx import Kokoro

    cache_dir = Path.home() / ".kaori_voice_studio" / "kokoro"
    cache_dir.mkdir(parents=True, exist_ok=True)
    model_path  = cache_dir / "kokoro-v1.0.onnx"
    voices_path = cache_dir / "voices-v1.0.bin"

    if not model_path.exists():
        _log_kokoro(f"Downloading model to {model_path}")
        urllib.request.urlretrieve(_KOKORO_MODEL_URL, model_path)
        _log_kokoro("Model download complete")
    if not voices_path.exists():
        _log_kokoro(f"Downloading voices to {voices_path}")
        urllib.request.urlretrieve(_KOKORO_VOICES_URL, voices_path)
        _log_kokoro("Voices download complete")

    _log_kokoro(f"Loading Kokoro from {model_path}")
    _kokoro_instance = Kokoro(str(model_path), str(voices_path))
    _log_kokoro(f"Kokoro loaded: {type(_kokoro_instance)}")
    return _kokoro_instance


def _kokoro_generate(text, output_path, voice_id, lang_code, speed=1.0):
    """Generate audio using Kokoro ONNX and save as WAV."""
    try:
        import soundfile as sf
        import numpy as np

        _log_kokoro(f"_kokoro_generate called: voice={voice_id} lang={lang_code} speed={speed} path={output_path}")
        kokoro = _get_kokoro()
        _log_kokoro(f"Kokoro instance obtained: {type(kokoro)}")

        result = kokoro.create(
            text, voice=voice_id, speed=float(speed), lang=lang_code
        )
        _log_kokoro(f"kokoro.create() returned type: {type(result)}, len: {len(result) if hasattr(result, '__len__') else 'n/a'}")

        samples, sample_rate = result
        _log_kokoro(f"samples type={type(samples)}, shape={getattr(samples, 'shape', 'no shape')}, sample_rate={sample_rate}")

        output_path_str = str(output_path)
        _log_kokoro(f"Writing to: {output_path_str}")
        sf.write(output_path_str, np.array(samples), int(sample_rate))
        _log_kokoro(f"Write successful")
        return output_path_str

    except Exception as e:
        import traceback
        _log_kokoro(f"ERROR in _kokoro_generate: {e}\n{traceback.format_exc()}")
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Custom widgets  (all Canvas sizes set via .config() to avoid Windows TclError)
# ─────────────────────────────────────────────────────────────────────────────

class FlatButton(tk.Frame):
    """Flat coloured button — tk.Frame + tk.Label, no Canvas."""

    def __init__(self, parent, text="Button", command=None,
                 btn_w=140, btn_h=34,
                 bg=None, fg=None, hover_bg=None,
                 dis_bg=None, dis_fg=None):
        super().__init__(parent, cursor="hand2")
        # Colours resolved at creation time from active theme
        self._bg     = bg     or T["ACCENT"]
        self._fg     = fg     or T["BTN_FG"]
        self._hov    = hover_bg  or T["ACCENT_HO"]
        self._dis_bg = dis_bg or T["BORDER"]
        self._dis_fg = dis_fg or T["TEXT_DIM"]
        self._cmd    = command
        self._active = True
        self.config(width=btn_w, height=btn_h)
        self.pack_propagate(False)
        self.configure(bg=self._bg)

        self._lbl = tk.Label(self, text=text, bg=self._bg, fg=self._fg,
                             font=FONTS["bold"], cursor="hand2")
        self._lbl.pack(expand=True)

        for w in (self, self._lbl):
            w.bind("<Enter>",           lambda e: self._hover(True))
            w.bind("<Leave>",           lambda e: self._hover(False))
            w.bind("<ButtonRelease-1>", lambda e: self._click())

    def _set_col(self, bg, fg):
        self.configure(bg=bg)
        self._lbl.configure(bg=bg, fg=fg)

    def _hover(self, on):
        if self._active:
            self._set_col(self._hov if on else self._bg, self._fg)

    def _click(self):
        if self._active and self._cmd:
            self._cmd()

    def set_state(self, state):
        self._active = (state == "normal")
        cur = "hand2" if self._active else "arrow"
        self.configure(cursor=cur)
        self._lbl.configure(cursor=cur)
        self._set_col(*(
            (self._bg, self._fg) if self._active
            else (self._dis_bg, self._dis_fg)
        ))

    def set_text(self, t):
        self._lbl.configure(text=t)

    def retheme(self, bg=None, fg=None, hover_bg=None, dis_bg=None, dis_fg=None):
        """Update colours when theme changes."""
        if bg:       self._bg     = bg
        if fg:       self._fg     = fg
        if hover_bg: self._hov    = hover_bg
        if dis_bg:   self._dis_bg = dis_bg
        if dis_fg:   self._dis_fg = dis_fg
        if self._active:
            self._set_col(self._bg, self._fg)
        else:
            self._set_col(self._dis_bg, self._dis_fg)


class Slider:
    """Resizable themed slider. Canvas sized after construction."""

    def __init__(self, parent, from_, to, variable, sldr_h=22):
        self._from = from_
        self._to   = to
        self._var  = variable
        self._h    = sldr_h
        self._pad  = 10
        self._drag = False
        self._w    = 1

        self._c = tk.Canvas(parent, bd=0, highlightthickness=0)
        self._c.config(height=sldr_h, bg=T["PANEL"])
        self._c.bind("<Configure>",    self._on_resize)
        variable.trace_add("write",    lambda *_: self._draw())
        self._c.bind("<ButtonPress-1>",   self._press)
        self._c.bind("<B1-Motion>",       self._move)
        self._c.bind("<ButtonRelease-1>", lambda e: setattr(self, "_drag", False))

    def _on_resize(self, e):
        self._w = max(e.width, 2 * self._pad + 1)
        self._draw()

    def pack(self, **kw):  self._c.pack(**kw)
    def grid(self, **kw):  self._c.grid(**kw)

    def _val_to_x(self, v):
        r = (v - self._from) / (self._to - self._from)
        return self._pad + r * (self._w - 2 * self._pad)

    def _x_to_val(self, x):
        r = (x - self._pad) / (self._w - 2 * self._pad)
        return self._from + max(0.0, min(1.0, r)) * (self._to - self._from)

    def _draw(self):
        if self._w <= 1:
            return
        self._c.delete("all")
        cy = self._h // 2
        self._c.create_line(self._pad, cy, self._w - self._pad, cy,
                            fill=T["SURFACE"], width=4, capstyle="round")
        x = self._val_to_x(self._var.get())
        self._c.create_line(self._pad, cy, x, cy,
                            fill=T["ACCENT"], width=4, capstyle="round")
        r = 7
        self._c.create_oval(x-r, cy-r, x+r, cy+r,
                            fill=T["ACCENT"], outline=T["BG"], width=2)

    def retheme(self):
        self._c.config(bg=T["PANEL"])
        self._draw()

    def _press(self, e):
        self._drag = True
        self._var.set(self._x_to_val(e.x))

    def _move(self, e):
        if self._drag:
            self._var.set(self._x_to_val(e.x))


class WaveAnim:
    """Three-bar animated waveform indicator."""

    def __init__(self, parent):
        self._c     = tk.Canvas(parent, bd=0, highlightthickness=0)
        self._c.config(width=30, height=18, bg=T["PANEL"])
        self._on    = False
        self._phase = 0.0
        self._draw()

    def pack(self, **kw):  self._c.pack(**kw)

    def _draw(self):
        self._c.delete("all")
        for i in range(3):
            x = 4 + i * 9
            h = (4 + int(6 * abs(math.sin(self._phase + i * 1.2)))
                 if self._on else 4)
            cy = 9
            self._c.create_rectangle(x, cy-h//2, x+5, cy+h//2,
                                     fill=T["ACCENT"] if self._on else T["BORDER"],
                                     outline="")

    def start(self):
        self._on = True
        self._tick()

    def stop(self):
        self._on = False
        self._draw()

    def _tick(self):
        if not self._on:
            return
        self._phase += 0.28
        self._draw()
        self._c.after(80, self._tick)

    def retheme(self):
        self._c.config(bg=T["PANEL"])
        self._draw()


class ThemeButton(tk.Frame):
    """Small pill-shaped theme toggle button."""

    def __init__(self, parent, label, command, active=False):
        super().__init__(parent, cursor="hand2")
        self._label   = label
        self._cmd     = command
        self._active  = active
        self.config(width=90, height=30)
        self.pack_propagate(False)
        self._lbl = tk.Label(self, text=label, font=FONTS["body"], cursor="hand2")
        self._lbl.pack(expand=True, padx=14)
        self._apply()
        for w in (self, self._lbl):
            w.bind("<Enter>",           lambda e: self._on_enter())
            w.bind("<Leave>",           lambda e: self._on_leave())
            w.bind("<ButtonRelease-1>", lambda e: command())

    def _apply(self):
        if self._active:
            self.configure(bg=T["ACCENT"])
            self._lbl.configure(bg=T["ACCENT"], fg=T["BTN_FG"])
        else:
            self.configure(bg=T["BORDER"])
            self._lbl.configure(bg=T["BORDER"], fg=T["TEXT_DIM"])

    def _on_enter(self):
        if not self._active:
            self.configure(bg=T["SURFACE"])
            self._lbl.configure(bg=T["SURFACE"], fg=T["TEXT"])

    def _on_leave(self):
        self._apply()

    def set_active(self, v):
        self._active = v
        self._apply()

    def retheme(self):
        self._apply()


def _log_chrome_error(e):
    """Log chrome setup errors silently — app still works without custom chrome."""
    try:
        from datetime import datetime
        log = Path.home() / "kaori_update.log"
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [chrome] {e}\n")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Main application
# ─────────────────────────────────────────────────────────────────────────────

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kaori Voice Studio")
        self.root.resizable(True, True)
        self.root.minsize(MIN_W, MIN_H)

        # Strip native title bar via Win32 API (keeps virtual desktop tracking)
        self.root.update_idletasks()
        self._setup_native_frame()
        self.root.after(50, self._apply_titlebar_theme)

        self._preview_file  = None
        self._is_playing    = False
        self._active_source = None
        self._all_widgets   = []
        self._sliders       = []
        self._theme_btns    = {}

        pygame.mixer.init()

        self.voice_var   = tk.StringVar(value=list(VOICES.keys())[1])
        self.speed_var   = tk.DoubleVar(value=1.0)
        self.pitch_var   = tk.DoubleVar(value=0.0)
        self.volume_var  = tk.DoubleVar(value=100.0)
        self.preview_var = tk.StringVar(value=PREVIEW_SENTENCES["en"])
        self.engine_var  = tk.StringVar(value="Edge")   # "Edge" or "Kokoro"
        self._theme_name = "Pink"

        self._preview_file  = None
        self._is_playing    = False
        self._active_source = None
        self._all_widgets   = []
        self._sliders       = []
        self._theme_btns    = {}

        self.voice_var.trace_add("write", self._sync_preview_text)
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_native_frame(self):
        """
        Remove the native title bar while keeping the window properly
        registered with Windows DWM — so it:
          - Stays on one virtual desktop
          - Shows in the taskbar
          - Gets Aero shadow and snap
          - Appears in Alt+Tab

        Strategy: keep overrideredirect(False) so DWM tracks the window
        normally, then use SetWindowLong to strip WS_CAPTION while keeping
        WS_THICKFRAME (needed for DWM shadow + virtual desktop tracking).
        A 1px top margin via DwmExtendFrameIntoClientArea hides the remaining
        native title bar pixel.
        """
        if sys.platform != "win32":
            return
        try:
            import ctypes
            import ctypes.wintypes

            user32  = ctypes.windll.user32
            dwmapi  = ctypes.windll.dwmapi

            # Use the window's own hwnd, not the parent
            hwnd = self.root.winfo_id()

            GWL_STYLE     = -16
            GWL_EXSTYLE   = -20
            WS_CAPTION    = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_SYSMENU    = 0x00080000
            WS_MAXIMIZEBOX= 0x00010000
            WS_MINIMIZEBOX= 0x00020000
            WS_EX_APPWINDOW  = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080

            # Strip caption but keep thickframe for DWM shadow + virtual desktops
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            style &= ~(WS_CAPTION | WS_SYSMENU | WS_MAXIMIZEBOX | WS_MINIMIZEBOX)
            style |= WS_THICKFRAME
            user32.SetWindowLongW(hwnd, GWL_STYLE, style)

            # Ensure APPWINDOW (taskbar) and remove TOOLWINDOW
            ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex = (ex & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)

            # Extend DWM frame — negative margins collapse the title bar
            # but keep DWM compositing active (shadow, virtual desktop tracking)
            MARGINS = ctypes.c_int * 4
            margins = MARGINS(-1, -1, -1, -1)
            try:
                dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
            except Exception:
                pass

            # Apply style changes
            SWP_NOMOVE      = 0x0002
            SWP_NOSIZE      = 0x0001
            SWP_NOZORDER    = 0x0004
            SWP_FRAMECHANGED= 0x0020
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE |
                                SWP_NOZORDER | SWP_FRAMECHANGED)

        except Exception as e:
            _log_chrome_error(e)

    def _apply_titlebar_theme(self):
        """
        Set the native Windows title bar color to match the current theme.
        Uses DwmSetWindowAttribute — works on Windows 11 (build 22000+).
        Gracefully does nothing on Windows 10 or non-Windows.
        """
        if sys.platform != "win32":
            return
        try:
            import ctypes
            import ctypes.wintypes

            user32  = ctypes.windll.user32
            dwmapi  = ctypes.windll.dwmapi

            # Get the real top-level window handle (not the Tk child hwnd)
            GA_ROOT = 2
            child_hwnd = self.root.winfo_id()
            hwnd = user32.GetAncestor(child_hwnd, GA_ROOT)
            if not hwnd:
                hwnd = child_hwnd  # fallback
            _log(f"Titlebar theme: child_hwnd={child_hwnd} root_hwnd={hwnd} theme={self._theme_name}")

            def hex_to_colorref(hex_color):
                """Convert #RRGGBB to Windows COLORREF (0x00BBGGRR)."""
                h = hex_color.lstrip("#")
                r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                return ctypes.c_uint32(r | (g << 8) | (b << 16))

            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_CAPTION_COLOR           = 35
            DWMWA_TEXT_COLOR              = 36
            DWMWA_BORDER_COLOR            = 34

            # Dark mode flag
            is_dark = ctypes.c_uint32(1 if self._theme_name == "Dark" else 0)
            r = dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(is_dark), ctypes.sizeof(is_dark))
            _log(f"  DARK_MODE result: {r}")

            # Caption background
            caption_col = hex_to_colorref(T["PANEL"])
            r = dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR,
                ctypes.byref(caption_col), ctypes.sizeof(caption_col))
            _log(f"  CAPTION_COLOR ({T['PANEL']}) result: {r}")

            # Title text color
            text_col = hex_to_colorref(T["TEXT"])
            r = dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_TEXT_COLOR,
                ctypes.byref(text_col), ctypes.sizeof(text_col))
            _log(f"  TEXT_COLOR ({T['TEXT']}) result: {r}")

            # Border/accent color
            border_col = hex_to_colorref(T["ACCENT"])
            r = dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_BORDER_COLOR,
                ctypes.byref(border_col), ctypes.sizeof(border_col))
            _log(f"  BORDER_COLOR ({T['ACCENT']}) result: {r}")

        except Exception as e:
            _log_chrome_error(e)

    def _build(self):
        self._apply_theme()

        # ── Header ──
        self._hdr = tk.Frame(self.root, bg=T["PANEL"])
        self._hdr.pack(fill="x", side="top")

        tk.Label(self._hdr, text="●", bg=T["PANEL"], fg=T["ACCENT"],
                 font=("Segoe UI", 10)).pack(side="left", padx=(16, 4), pady=14)
        self._title_lbl = tk.Label(self._hdr, text="Kaori Voice Studio",
                 bg=T["PANEL"], fg=T["TEXT"], font=FONTS["title"])
        self._title_lbl.pack(side="left", padx=(0, 6), pady=14)

        from kaori_voice_studio.version import __version__
        self._ver_lbl = tk.Label(self._hdr, text=f"v{__version__}",
                 bg=T["PANEL"], fg=T["TEXT_DIM"], font=FONTS["small"])
        self._ver_lbl.pack(side="left", pady=14)

        # ── Engine selector ──
        eng_frame = tk.Frame(self._hdr, bg=T["PANEL"])
        eng_frame.pack(side="left", padx=(20, 0), pady=12)
        tk.Label(eng_frame, text="Engine:", bg=T["PANEL"],
                 fg=T["TEXT_DIM"], font=FONTS["small"]).pack(side="left", padx=(0, 8))
        self._engine_btns = {}
        for eng in ("Edge", "Kokoro"):
            btn = ThemeButton(
                eng_frame, eng,
                command=lambda e=eng: self._switch_engine(e),
                active=(eng == "Edge"),
            )
            btn.pack(side="left", padx=3)
            self._engine_btns[eng] = btn

        # Theme selector (right side of header)
        theme_frame = tk.Frame(self._hdr, bg=T["PANEL"])
        theme_frame.pack(side="right", padx=20, pady=12)
        tk.Label(theme_frame, text="Theme:", bg=T["PANEL"],
                 fg=T["TEXT_DIM"], font=FONTS["small"]).pack(side="left", padx=(0, 8))
        for name in THEMES:
            btn = ThemeButton(
                theme_frame, name,
                command=lambda n=name: self._switch_theme(n),
                active=(name == self._theme_name),
            )
            btn.pack(side="left", padx=5)
            self._theme_btns[name] = btn

        # Accent bar
        self._accent_bar = tk.Frame(self.root, bg=T["ACCENT"], height=2)
        self._accent_bar.pack(fill="x", side="top")

        # ── Footer ──
        self._ftr = tk.Frame(self.root, bg=T["PANEL"])
        self._ftr.pack(fill="x", side="bottom")
        tk.Frame(self._ftr, bg=T["BORDER"], height=1).pack(fill="x")
        self._build_footer(self._ftr)

        # ── Body ──
        self._body = tk.Frame(self.root, bg=T["BG"])
        self._body.pack(padx=20, pady=16, fill="both", expand=True, side="top")

        # Right column: fixed width controls
        self._right = tk.Frame(self._body, bg=T["BG"])
        self._right.config(width=RIGHT_PANEL_W)
        self._right.pack(side="right", fill="y", padx=(16, 0))
        self._right.pack_propagate(False)

        # Left column: vertical PanedWindow so Text & Voice each get guaranteed space
        self._left = tk.Frame(self._body, bg=T["BG"])
        self._left.pack(side="left", fill="both", expand=True)

        self._pane = tk.PanedWindow(
            self._left,
            orient=tk.VERTICAL,
            bg=T["BG"],
            sashwidth=6,
            sashrelief="flat",
            bd=0,
            showhandle=False,
        )
        self._pane.pack(fill="both", expand=True)

        self._build_text_card(self._pane)
        self._build_voice_card(self._pane)
        self._build_controls_card(self._right)

        # Set initial sash position after geometry is resolved (65% text / 35% voice)
        self.root.update_idletasks()
        total = self._pane.winfo_height()
        if total > 10:
            self._pane.sash_place(0, 0, int(total * 0.50))
        else:
            self.root.after(100, self._set_initial_sash)

    # ── Cards ─────────────────────────────────────────────────────────────────

    def _make_card(self, parent, title, expand=False):
        """Returns the inner content frame of a themed card."""
        card = tk.Frame(parent, bg=T["PANEL"])
        pack_kw = dict(fill="both" if expand else "x", pady=(0, 12))
        if expand:
            pack_kw["expand"] = True
        card.pack(**pack_kw)

        hdr = tk.Frame(card, bg=T["PANEL"])
        hdr.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(hdr, text=title, bg=T["PANEL"], fg=T["TEXT_DIM"],
                 font=FONTS["small"]).pack(side="left")

        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", padx=14, pady=(4, 0))

        inner = tk.Frame(card, bg=T["PANEL"])
        inner.pack(fill="both" if expand else "x",
                   expand=expand, padx=14, pady=12)
        return card, inner

    def _build_text_card(self, pane):
        card = tk.Frame(pane, bg=T["PANEL"])
        pane.add(card, minsize=120, stretch="always")
        self._text_card = card

        # ── Card header ──
        hdr = tk.Frame(card, bg=T["PANEL"])
        hdr.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(hdr, text="Text", bg=T["PANEL"], fg=T["TEXT_DIM"],
                 font=FONTS["small"]).pack(side="left")
        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", padx=14, pady=(4, 0))

        # ── Bottom action bar — packed BEFORE inner so expand=True text area cannot hide it ──
        bar = tk.Frame(card, bg=T["PANEL"])
        bar.pack(side="bottom", fill="x", padx=14, pady=(6, 10))

        self.stats_lbl = tk.Label(bar, text="0 words · 0 chars",
                                  bg=T["PANEL"], fg=T["TEXT_DIM"], font=FONTS["small"])
        self.stats_lbl.pack(side="left")

        self.text_stop_btn = FlatButton(
            bar, "■  Stop", self._stop_preview,
            btn_w=80, btn_h=30,
            bg=T["SURFACE"], fg=T["TEXT_DIM"],
            hover_bg=T["BORDER"], dis_bg=T["SURFACE"],
        )
        self.text_stop_btn.pack(side="right", padx=(6, 0))
        self.text_stop_btn.set_state("disabled")

        self.text_play_btn = FlatButton(
            bar, "▶  Preview Text", self._preview_text,
            btn_w=126, btn_h=30,
            bg=T["ACCENT"], fg=T["BTN_FG"], hover_bg=T["ACCENT_HO"],
        )
        self.text_play_btn.pack(side="right", padx=(6, 0))

        self._text_wave = WaveAnim(bar)
        self._text_wave.pack(side="right", padx=(0, 8))

        clr = tk.Label(bar, text="Clear ×", bg=T["PANEL"],
                       fg=T["TEXT_DIM"], font=FONTS["small"], cursor="hand2")
        clr.pack(side="right", padx=(0, 16))
        clr.bind("<Button-1>", lambda e: (self.text_input.delete("1.0", "end"),
                                          self._update_stats()))

        # ── Text area — fills all remaining space ──
        inner = tk.Frame(card, bg=T["PANEL"])
        inner.pack(fill="both", expand=True, padx=14, pady=(10, 0))

        box = tk.Frame(inner, bg=T["SURFACE"])
        box.pack(fill="both", expand=True)

        self.text_input = tk.Text(
            box, wrap="word",
            bg=T["SURFACE"], fg=T["TEXT"],
            insertbackground=T["ACCENT_TK"],
            font=FONTS["body"], relief="flat", bd=10,
            selectbackground=T["ACCENT"], selectforeground=T["BTN_FG"],
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.bind("<KeyRelease>", self._update_stats)

    def _build_voice_card(self, pane):
        card = tk.Frame(pane, bg=T["PANEL"])
        pane.add(card, minsize=260, stretch="always")
        self._voice_card = card

        # ── Card header ──
        hdr = tk.Frame(card, bg=T["PANEL"])
        hdr.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(hdr, text="Voice & Preview", bg=T["PANEL"], fg=T["TEXT_DIM"],
                 font=FONTS["small"]).pack(side="left")
        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", padx=14, pady=(4, 0))

        # ── Button row — packed BEFORE inner so it always claims its space ──
        ctrl_row = tk.Frame(card, bg=T["PANEL"])
        ctrl_row.pack(side="bottom", fill="x", padx=14, pady=(6, 12))

        self._wave = WaveAnim(ctrl_row)
        self._wave.pack(side="left", padx=(0, 10))

        self.play_btn = FlatButton(
            ctrl_row, "▶  Play Preview", self._preview,
            btn_w=130, btn_h=34,
            bg=T["ACCENT"], fg=T["BTN_FG"], hover_bg=T["ACCENT_HO"],
        )
        self.play_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = FlatButton(
            ctrl_row, "■  Stop", self._stop_preview,
            btn_w=90, btn_h=34,
            bg=T["SURFACE"], fg=T["TEXT_DIM"],
            hover_bg=T["BORDER"], dis_bg=T["SURFACE"],
        )
        self.stop_btn.pack(side="left")
        self.stop_btn.set_state("disabled")

        # ── Content area: dropdown + sample entry ──
        inner = tk.Frame(card, bg=T["PANEL"])
        inner.pack(fill="both", expand=True, padx=14, pady=(12, 0))

        # Row 1: dropdown (fixed height)
        drop_row = tk.Frame(inner, bg=T["PANEL"])
        drop_row.pack(fill="x", pady=(0, 12))

        tk.Label(drop_row, text="Voice", bg=T["PANEL"], fg=T["TEXT_DIM"],
                 font=FONTS["small"]).pack(anchor="w", pady=(0, 4))

        self._voice_menu = tk.OptionMenu(drop_row, self.voice_var, *VOICES.keys())
        self._voice_menu.configure(
            bg=T["SURFACE"], fg=T["TEXT"], font=FONTS["body"],
            activebackground=T["BORDER"], activeforeground=T["TEXT"],
            relief="flat", bd=0, highlightthickness=0,
            width=42, anchor="w",
        )
        self._voice_menu["menu"].configure(
            bg=T["SURFACE"], fg=T["TEXT"], font=FONTS["body"],
            activebackground=T["ACCENT"], activeforeground=T["BTN_FG"],
            relief="flat", bd=0,
        )
        self._voice_menu.pack(fill="x")

        # Row 2: sample text — using Text widget (height=2) for reliable rendering
        sample_row = tk.Frame(inner, bg=T["PANEL"])
        sample_row.pack(fill="x", pady=(0, 8))

        tk.Label(sample_row, text="Sample text", bg=T["PANEL"],
                 fg=T["TEXT_DIM"], font=FONTS["small"]).pack(anchor="w", pady=(0, 4))

        entry_bg = tk.Frame(sample_row, bg=T["SURFACE"])
        entry_bg.pack(fill="x")

        self._preview_entry = tk.Text(
            entry_bg, height=2, wrap="word",
            bg=T["SURFACE"], fg=T["TEXT"],
            insertbackground=T["ACCENT_TK"],
            relief="flat", font=FONTS["body"], bd=8,
            selectbackground=T["ACCENT"], selectforeground=T["BTN_FG"],
        )
        self._preview_entry.pack(fill="x")
        # Insert initial value and keep in sync with preview_var
        self._preview_entry.insert("1.0", self.preview_var.get())
        self._preview_entry.bind(
            "<KeyRelease>",
            lambda e: self.preview_var.set(
                self._preview_entry.get("1.0", "end-1c")
            )
        )

    def _build_controls_card(self, parent):
        card, inner = self._make_card(parent, "Controls")
        self._ctrl_card = card

        self._sliders = []

        def add_row(label, var, lo, hi, fmt_fn):
            lbl = tk.Label(inner, text=label, bg=T["PANEL"],
                           fg=T["TEXT_DIM"], font=FONTS["small"])
            lbl.pack(anchor="w", pady=(8, 0))

            row = tk.Frame(inner, bg=T["PANEL"])
            row.pack(fill="x", pady=(3, 0))

            sl = Slider(row, lo, hi, var, sldr_h=22)
            sl.pack(side="left", fill="x", expand=True)
            self._sliders.append(sl)

            val_lbl = tk.Label(row, text=fmt_fn(var.get()), bg=T["PANEL"],
                               fg=T["TEXT"], font=FONTS["small"], width=7, anchor="w")
            val_lbl.pack(side="left", padx=(8, 0))
            var.trace_add("write",
                          lambda *_, v=var, l=val_lbl, f=fmt_fn:
                          l.configure(text=f(v.get())))

        add_row("Speed",  self.speed_var,  0.5,  2.0, lambda v: f"{v:.1f}x")
        add_row("Pitch",  self.pitch_var, -50,   50,  lambda v: f"{v:+.0f} Hz")
        add_row("Volume", self.volume_var,  0,   200, lambda v: f"{v:.0f}%")

        tk.Frame(inner, bg=T["BORDER"], height=1).pack(fill="x", pady=(18, 10))
        rst = tk.Label(inner, text="Reset defaults", bg=T["PANEL"],
                       fg=T["TEXT_DIM"], font=FONTS["small"], cursor="hand2")
        rst.pack(anchor="w")
        rst.bind("<Button-1>", lambda e: self._reset())

    def _build_footer(self, parent):
        inner = tk.Frame(parent, bg=T["PANEL"])
        inner.pack(fill="x", padx=20, pady=12)

        sf = tk.Frame(inner, bg=T["PANEL"])
        sf.pack(side="left", fill="x", expand=True)
        self.dot = tk.Label(sf, text="●", bg=T["PANEL"],
                            fg=T["TEXT_DIM"], font=FONTS["small"])
        self.dot.pack(side="left")
        self.status_lbl = tk.Label(sf, text="  Ready", bg=T["PANEL"],
                                   fg=T["TEXT_DIM"], font=FONTS["small"])
        self.status_lbl.pack(side="left")

        self.gen_btn = FlatButton(
            inner, "⬇  Export MP3", self._generate,
            btn_w=140, btn_h=38,
            bg=T["ACCENT"], fg=T["BTN_FG"], hover_bg=T["ACCENT_HO"],
        )
        self.gen_btn.pack(side="right")

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        self.root.configure(bg=T["BG"])

    def _switch_theme(self, name):
        if name == self._theme_name:
            return
        self._theme_name = name
        T.update(THEMES[name])

        # Update theme toggle buttons
        for n, btn in self._theme_btns.items():
            btn.set_active(n == name)
            btn.retheme()

        # Walk every widget in the window and repaint
        self._repaint_all(self.root)

        # Repaint custom widget surfaces
        for sl in self._sliders:
            sl.retheme()
        self._wave.retheme()
        self._text_wave.retheme()

        # Repaint FlatButtons individually
        self.play_btn.retheme(bg=T["ACCENT"], fg=T["BTN_FG"],
                              hover_bg=T["ACCENT_HO"])
        self.stop_btn.retheme(bg=T["SURFACE"], fg=T["TEXT_DIM"],
                              hover_bg=T["BORDER"], dis_bg=T["SURFACE"])
        self.text_play_btn.retheme(bg=T["ACCENT"], fg=T["BTN_FG"],
                                   hover_bg=T["ACCENT_HO"])
        self.text_stop_btn.retheme(bg=T["SURFACE"], fg=T["TEXT_DIM"],
                                   hover_bg=T["BORDER"], dis_bg=T["SURFACE"])
        self.gen_btn.retheme(bg=T["ACCENT"], fg=T["BTN_FG"],
                             hover_bg=T["ACCENT_HO"])

        # Update text widget colours
        self.text_input.configure(
            bg=T["SURFACE"], fg=T["TEXT"],
            insertbackground=T["ACCENT_TK"],
            selectbackground=T["ACCENT"], selectforeground=T["BTN_FG"],
        )
        self._preview_entry.configure(
            bg=T["SURFACE"], fg=T["TEXT"],
            insertbackground=T["ACCENT_TK"],
            selectbackground=T["ACCENT"], selectforeground=T["BTN_FG"],
        )

        # Voice menu
        self._voice_menu.configure(
            bg=T["SURFACE"], fg=T["TEXT"],
            activebackground=T["BORDER"], activeforeground=T["TEXT"],
        )
        self._voice_menu["menu"].configure(
            bg=T["SURFACE"], fg=T["TEXT"],
            activebackground=T["ACCENT"], activeforeground=T["BTN_FG"],
        )

        # Accent bar
        self._accent_bar.configure(bg=T["ACCENT"])

        # Header labels
        self._title_lbl.configure(bg=T["PANEL"], fg=T["TEXT"])
        self._ver_lbl.configure(bg=T["PANEL"], fg=T["TEXT_DIM"])
        self._hdr.configure(bg=T["PANEL"])

        # Engine selector buttons
        for btn in self._engine_btns.values():
            btn.retheme()

        # Native title bar
        self._apply_titlebar_theme()

        # PanedWindow sash
        self._pane.configure(bg=T["BG"])

        # Status dot
        self.dot.configure(fg=T["TEXT_DIM"])
        self.status_lbl.configure(fg=T["TEXT_DIM"])

    def _repaint_all(self, widget):
        """Recursively repaint standard tk widgets."""
        cls = widget.__class__.__name__
        try:
            if cls == "Tk" or cls == "Frame":
                bg = T["BG"] if widget in (self.root, self._body,
                                            self._left, self._right) else T["PANEL"]
                widget.configure(bg=bg)
            elif cls == "Label":
                current_fg = widget.cget("fg")
                # Preserve success/error colours
                if current_fg in ("#3DDC84", "#FF5A5A"):
                    pass
                elif current_fg in [v["TEXT_DIM"] for v in THEMES.values()]:
                    widget.configure(fg=T["TEXT_DIM"])
                elif current_fg in [v["TEXT"] for v in THEMES.values()]:
                    widget.configure(fg=T["TEXT"])
                bg = widget.cget("bg")
                if bg in [v["PANEL"] for v in THEMES.values()]:
                    widget.configure(bg=T["PANEL"])
                elif bg in [v["BG"] for v in THEMES.values()]:
                    widget.configure(bg=T["BG"])
                elif bg in [v["SURFACE"] for v in THEMES.values()]:
                    widget.configure(bg=T["SURFACE"])
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self._repaint_all(child)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_initial_sash(self):
        total = self._pane.winfo_height()
        if total > 10:
            self._pane.sash_place(0, 0, int(total * 0.50))
        else:
            self.root.after(100, self._set_initial_sash)

    def _switch_engine(self, engine: str):
        """Switch between Edge TTS and Kokoro engine."""
        if engine == "Kokoro" and not _kokoro_available():
            messagebox.showwarning(
                "Kokoro not installed",
                "The kokoro-onnx and soundfile packages are required.\n\n"
                "Install them with:\n"
                "  pip install kokoro-onnx soundfile\n\n"
                "Then restart Kaori Voice Studio.\n\n"
                "The model files (~300 MB) will be downloaded automatically\n"
                "on first use."
            )
            return

        self.engine_var.set(engine)
        for name, btn in self._engine_btns.items():
            btn.set_active(name == engine)

        # Rebuild the voice dropdown with the appropriate voice list
        voices = list(KOKORO_VOICES.keys()) if engine == "Kokoro" else list(VOICES.keys())
        self.voice_var.set(voices[0])
        menu = self._voice_menu["menu"]
        menu.delete(0, "end")
        for v in voices:
            menu.add_command(label=v, command=lambda val=v: self.voice_var.set(val))
        self._voice_menu.configure(width=42)
        self._sync_preview_text()

    def _update_stats(self, *_):
        txt = self.text_input.get("1.0", "end").strip()
        w = len(txt.split()) if txt else 0
        self.stats_lbl.configure(text=f"{w} words · {len(txt)} chars")

    def _reset(self):
        self.speed_var.set(1.0)
        self.pitch_var.set(0.0)
        self.volume_var.set(100.0)

    def _sync_preview_text(self, *_):
        code = VOICES.get(self.voice_var.get(), "en-US")
        lang = code[:2]
        text = PREVIEW_SENTENCES.get(lang, PREVIEW_SENTENCES["en"])
        self.preview_var.set(text)
        # Also update the Text widget directly
        try:
            self._preview_entry.delete("1.0", "end")
            self._preview_entry.insert("1.0", text)
        except Exception:
            pass

    def _status(self, msg, color=None):
        c = color or T["TEXT_DIM"]
        self.dot.configure(fg=c)
        self.status_lbl.configure(text=f"  {msg}", fg=c)

    # ── Preview ───────────────────────────────────────────────────────────────

    def _preview_text(self):
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            self._status("Please enter some text first", T["ERROR"])
            return
        self._stop_preview()
        self._active_source = "text"
        self.text_play_btn.set_state("disabled")
        self.text_stop_btn.set_state("normal")
        self._text_wave.start()
        self._status("Generating text preview...", T["ACCENT"])
        threading.Thread(target=self._preview_thread, args=(text,),
                         daemon=True).start()

    def _preview(self):
        text = self.preview_var.get().strip()
        if not text:
            self._status("Enter sample text first", T["ERROR"])
            return
        self._stop_preview()
        self._active_source = "voice"
        self.play_btn.set_state("disabled")
        self.stop_btn.set_state("normal")
        self._wave.start()
        self._status("Generating preview...", T["ACCENT"])
        threading.Thread(target=self._preview_thread, args=(text,),
                         daemon=True).start()

    def _preview_thread(self, text):
        try:
            suffix = ".wav" if self.engine_var.get() == "Kokoro" else ".mp3"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.close()
            # Resolve to full long path — Windows may return 8.3 short paths
            # (e.g. JULIOL~1) for usernames with spaces, which pygame rejects
            self._preview_file = str(Path(tmp.name).resolve())
            if self.engine_var.get() == "Kokoro" and _kokoro_instance is None:
                self.root.after(0, lambda: self._status(
                    "Downloading Kokoro model (~300 MB, first use only)...", T["ACCENT"]))
            self._make_audio(text, self._preview_file)
            pygame.mixer.music.load(self._preview_file)
            pygame.mixer.music.play()
            self._is_playing = True
            self.root.after(0, lambda: self._status("Playing...", T["SUCCESS"]))
            threading.Thread(target=self._watch, daemon=True).start()
        except Exception as exc:
            self.root.after(0, lambda: self._status(f"Error: {exc}", T["ERROR"]))
            self.root.after(0, self._reset_play_buttons)
            self.root.after(0, self._wave.stop)
            self.root.after(0, self._text_wave.stop)

    def _watch(self):
        while self._is_playing and pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        self._is_playing = False
        self.root.after(0, self._preview_done)

    def _preview_done(self):
        self._text_wave.stop()
        self._wave.stop()
        self._reset_play_buttons()
        self._status("Preview finished")
        self._cleanup()

    def _reset_play_buttons(self):
        self.play_btn.set_state("normal")
        self.stop_btn.set_state("disabled")
        self.text_play_btn.set_state("normal")
        self.text_stop_btn.set_state("disabled")

    def _stop_preview(self):
        self._is_playing = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass
        self._wave.stop()
        self._text_wave.stop()
        self._reset_play_buttons()
        self._status("Stopped")
        self.root.after(200, self._cleanup)

    def _cleanup(self):
        if self._preview_file and os.path.exists(self._preview_file):
            try:
                os.unlink(self._preview_file)
                self._preview_file = None
            except Exception:
                self.root.after(1000, self._cleanup)

    # ── Export ────────────────────────────────────────────────────────────────

    def _generate(self):
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            self._status("Please enter some text first", T["ERROR"])
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 file", "*.mp3"), ("All files", "*.*")],
            title="Save MP3",
        )
        if not path:
            return
        self.gen_btn.set_state("disabled")
        self._status("Exporting MP3...", T["ACCENT"])
        threading.Thread(target=self._export_thread, args=(text, path),
                         daemon=True).start()

    def _export_thread(self, text, path):
        try:
            self._make_audio(text, path)
            self.root.after(0, lambda: self._status(
                f"Saved: {Path(path).name}", T["SUCCESS"]))
            self.root.after(0, lambda: messagebox.showinfo(
                "Export complete", f"MP3 saved to:\n{path}"))
        except Exception as exc:
            self.root.after(0, lambda: self._status(f"Export failed: {exc}", T["ERROR"]))
            self.root.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            self.root.after(0, lambda: self.gen_btn.set_state("normal"))

    # ── Audio ─────────────────────────────────────────────────────────────────

    def _make_audio(self, text, path):
        engine = self.engine_var.get()

        if engine == "Kokoro":
            voice_label = self.voice_var.get()
            voice_id, lang_code = KOKORO_VOICES[voice_label]
            speed = self.speed_var.get()
            _kokoro_generate(text, path, voice_id, lang_code, speed)
            return

        # Edge TTS
        voice = VOICES[self.voice_var.get()]
        rate  = _rate_str(self.speed_var.get())
        vol   = _volume_str(self.volume_var.get())
        pitch = _pitch_str(self.pitch_var.get())

        async def _run():
            comm = edge_tts.Communicate(text, voice,
                                        rate=rate, volume=vol, pitch=pitch)
            await comm.save(path)

        asyncio.run(_run())

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _on_close(self):
        self._stop_preview()
        pygame.mixer.quit()
        self.root.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Update splash
# ─────────────────────────────────────────────────────────────────────────────

class UpdateSplash:
    """
    Tiny borderless window shown while the update check runs.
    Destroyed automatically before the main window opens.
    """
    def __init__(self):
        self._root = tk.Tk()
        self._root.overrideredirect(True)      # no title bar
        self._root.configure(bg="#E8387A")
        self._root.attributes("-topmost", True)

        # Centre on screen
        w, h = 320, 80
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Label(self._root, text="Kaori Voice Studio",
                 bg="#E8387A", fg="white",
                 font=("Segoe UI", 13, "bold")).pack(pady=(14, 2))
        self._lbl = tk.Label(self._root, text="Checking for updates...",
                             bg="#E8387A", fg="#FFD0E5",
                             font=("Segoe UI", 9))
        self._lbl.pack()
        self._root.update()

    def set_status(self, msg: str):
        self._lbl.configure(text=msg)
        self._root.update()

    def close(self):
        self._root.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import threading
    from kaori_voice_studio.updater import check_and_update

    splash = UpdateSplash()

    # Run the update check in a thread so the splash stays responsive
    update_done = threading.Event()

    def run_check():
        check_and_update(
            on_checking      = lambda:   splash.set_status("Checking for updates..."),
            on_update_found  = lambda v: splash.set_status(f"Updating to v{v}..."),
            on_updated       = lambda:   splash._root.after(0, splash.close),
            on_no_update     = lambda:   splash.set_status("Up to date!"),
            on_error         = lambda m: splash.set_status(m),
        )
        update_done.set()

    t = threading.Thread(target=run_check, daemon=True)
    t.start()

    # Poll until the check finishes (keeps Tk event loop alive for the splash)
    def wait_for_check():
        if update_done.is_set():
            splash.close()
            root = tk.Tk()
            root.geometry("800x660")
            TTSApp(root)
            root.mainloop()
        else:
            splash._root.after(100, wait_for_check)

    splash._root.after(100, wait_for_check)
    splash._root.mainloop()


if __name__ == "__main__":
    main()