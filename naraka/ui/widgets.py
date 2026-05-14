import customtkinter as ctk

from ..config import BORDER, MUTED


def section_header(parent, text: str) -> None:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=24, pady=(18, 8))
    ctk.CTkLabel(row, text=text,
                 font=ctk.CTkFont("Segoe UI", 11, "bold"),
                 text_color=MUTED).pack(side="left")
    ctk.CTkFrame(row, fg_color=BORDER, height=1,
                 corner_radius=0).pack(side="left", fill="x", expand=True, padx=(10, 0))
