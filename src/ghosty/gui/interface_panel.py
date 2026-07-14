"""Interface panel — lets the user select and refresh network interfaces."""

from __future__ import annotations

import customtkinter as ctk

from ghosty.utils.network import get_interfaces


class InterfacePanel(ctk.CTkFrame):
    """Network interface selector."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        # Title
        title = ctk.CTkLabel(
            self, text="Network Interface", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Interface dropdown
        self._interfaces = get_interfaces()
        self._selected = ctk.StringVar(value=self._interfaces[0] if self._interfaces else "eth0")

        self._dropdown = ctk.CTkOptionMenu(
            self, variable=self._selected, values=self._interfaces, width=160
        )
        self._dropdown.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Refresh button
        self._refresh_btn = ctk.CTkButton(
            self, text="↻ Refresh", width=80, command=self._refresh
        )
        self._refresh_btn.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="e")

    @property
    def selected(self) -> str:
        """Return the selected interface name."""
        return self._selected.get()

    def _refresh(self) -> None:
        """Re-scan available interfaces."""
        self._interfaces = get_interfaces()
        self._dropdown.configure(values=self._interfaces)
        if self._interfaces:
            self._selected.set(self._interfaces[0])
