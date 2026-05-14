#!/usr/bin/env python3
import sys
from pathlib import Path
import customtkinter as ctk

from naraka.ui.app import NarakaApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _resource(name: str) -> str:
    base = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent
    return str(base / name)


if __name__ == "__main__":
    app = NarakaApp()
    try:
        app.iconbitmap(_resource("logo.ico"))
    except Exception:
        pass
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
