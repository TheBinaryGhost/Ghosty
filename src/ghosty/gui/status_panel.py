"""Status panel — displays current anonymization state and external IP."""

from __future__ import annotations

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """Displays connection status, current mode, and external IP."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        # Title
        title = ctk.CTkLabel(
            self, text="Status", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Status indicator
        self._status_dot = ctk.CTkLabel(self, text="●", font=ctk.CTkFont(size=20))
        self._status_dot.grid(row=1, column=0, padx=(10, 5), pady=5)
        self._status_dot.configure(text_color="gray")

        self._status_label = ctk.CTkLabel(self, text="Inactive", font=ctk.CTkFont(size=13))
        self._status_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Mode
        self._mode_label = ctk.CTkLabel(self, text="Mode: —", font=ctk.CTkFont(size=12))
        self._mode_label.grid(row=2, column=0, columnspan=2, padx=10, pady=2, sticky="w")

        # External IP
        ip_label = ctk.CTkLabel(self, text="External IP:", font=ctk.CTkFont(size=12))
        ip_label.grid(row=3, column=0, padx=10, pady=2, sticky="w")

        self._ip_label = ctk.CTkLabel(self, text="—", font=ctk.CTkFont(size=12, weight="bold"))
        self._ip_label.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # Uptime
        uptime_label = ctk.CTkLabel(self, text="Uptime:", font=ctk.CTkFont(size=12))
        uptime_label.grid(row=4, column=0, padx=10, pady=2, sticky="w")

        self._uptime_label = ctk.CTkLabel(self, text="—", font=ctk.CTkFont(size=12))
        self._uptime_label.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        # Uptime ticker
        self._uptime_seconds = 0
        self._ticker_after: str | None = None

    def set_active(self, mode: str) -> None:
        """Update UI to active state."""
        self._status_dot.configure(text_color="#22c55e")
        self._status_label.configure(text="Active")
        self._mode_label.configure(text=f"Mode: {mode}")
        self._start_ticker()

    def set_inactive(self) -> None:
        """Update UI to inactive state."""
        self._status_dot.configure(text_color="gray")
        self._status_label.configure(text="Inactive")
        self._mode_label.configure(text="Mode: —")
        self._ip_label.configure(text="—")
        self._stop_ticker()

    def set_ip(self, ip: str) -> None:
        """Display external IP."""
        self._ip_label.configure(text=ip)

    def _start_ticker(self) -> None:
        """Start uptime counter."""
        self._uptime_seconds = 0
        self._tick()

    def _stop_ticker(self) -> None:
        """Stop uptime counter."""
        if self._ticker_after is not None:
            self.after_cancel(self._ticker_after)
            self._ticker_after = None
        self._uptime_label.configure(text="—")

    def _tick(self) -> None:
        """Update uptime display."""
        minutes, seconds = divmod(self._uptime_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        self._uptime_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self._uptime_seconds += 1
        self._ticker_after = self.after(1000, self._tick)
