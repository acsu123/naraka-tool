#!/usr/bin/env python3
import customtkinter as ctk

from naraka.ui.app import NarakaApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = NarakaApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
