"""Control panel — Start/Stop buttons."""

from __future__ import annotations

import customtkinter as ctk


class ControlPanel(ctk.CTkFrame):
    """Start and Stop buttons for anonymization."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        self._on_start = None
        self._on_stop = None

        # Title
        title = ctk.CTkLabel(
            self, text="Controls", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Start button
        self._start_btn = ctk.CTkButton(
            self, text="▶ Start", width=120, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#22c55e", hover_color="#16a34a",
            command=self._handle_start
        )
        self._start_btn.grid(row=1, column=0, padx=10, pady=10)

        # Stop button
        self._stop_btn = ctk.CTkButton(
            self, text="■ Stop", width=120, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#dc2626", hover_color="#b91c1c",
            command=self._handle_stop, state="disabled"
        )
        self._stop_btn.grid(row=1, column=1, padx=10, pady=10)

    def on_start(self, callback) -> None:
        """Register start callback."""
        self._on_start = callback

    def on_stop(self, callback) -> None:
        """Register stop callback."""
        self._on_stop = callback

    def set_active(self, active: bool) -> None:
        """Toggle button states based on activation status."""
        if active:
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")
        else:
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")

    def _handle_start(self) -> None:
        """Invoke start callback."""
        if self._on_start:
            self._on_start()

    def _handle_stop(self) -> None:
        """Invoke stop callback."""
        if self._on_stop:
            self._on_stop()
