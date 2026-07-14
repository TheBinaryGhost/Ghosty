"""Log panel — scrollable activity log."""

from __future__ import annotations

import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """Scrollable text area displaying activity logs."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        # Title row
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.pack(fill="x", padx=10, pady=(10, 5))

        title = ctk.CTkLabel(
            title_row, text="Activity Log", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.pack(side="left")

        clear_btn = ctk.CTkButton(
            title_row, text="Clear", width=60, command=self._clear
        )
        clear_btn.pack(side="right")

        # Log text area
        self._text = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Consolas", size=11), height=180
        )
        self._text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._text.configure(state="disabled")

    def append(self, message: str) -> None:
        """Append a message to the log."""
        self._text.configure(state="normal")
        self._text.insert("end", f"{message}\n")
        self._text.see("end")
        self._text.configure(state="disabled")

    def _clear(self) -> None:
        """Clear the log."""
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
