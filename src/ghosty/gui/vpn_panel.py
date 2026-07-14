"""VPN panel — file picker for VPN config and auth files."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import filedialog


class VPNPanel(ctk.CTkFrame):
    """VPN configuration file picker."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        # Title
        title = ctk.CTkLabel(
            self, text="VPN Configuration", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # Config file
        config_label = ctk.CTkLabel(self, text="Config:", font=ctk.CTkFont(size=12))
        config_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self._config_var = ctk.StringVar(value="")
        self._config_entry = ctk.CTkEntry(
            self, textvariable=self._config_var, width=200, placeholder_text="Select .ovpn or .conf"
        )
        self._config_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self._config_btn = ctk.CTkButton(
            self, text="Browse", width=70, command=self._browse_config
        )
        self._config_btn.grid(row=1, column=2, padx=(5, 10), pady=5)

        # Auth file
        auth_label = ctk.CTkLabel(self, text="Auth:", font=ctk.CTkFont(size=12))
        auth_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self._auth_var = ctk.StringVar(value="")
        self._auth_entry = ctk.CTkEntry(
            self, textvariable=self._auth_var, width=200, placeholder_text="Optional auth file"
        )
        self._auth_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self._auth_btn = ctk.CTkButton(
            self, text="Browse", width=70, command=self._browse_auth
        )
        self._auth_btn.grid(row=2, column=2, padx=(5, 10), pady=5)

    @property
    def config_path(self) -> str:
        """Return the selected VPN config path."""
        return self._config_var.get()

    @property
    def auth_path(self) -> str | None:
        """Return the auth file path or None."""
        path = self._auth_var.get()
        return path if path else None

    def _browse_config(self) -> None:
        """Open file dialog for VPN config."""
        path = filedialog.askopenfilename(
            title="Select VPN Config",
            filetypes=[
                ("VPN Config", "*.ovpn *.conf"),
                ("OpenVPN", "*.ovpn"),
                ("WireGuard", "*.conf"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._config_var.set(path)

    def _browse_auth(self) -> None:
        """Open file dialog for auth file."""
        path = filedialog.askopenfilename(
            title="Select Auth File",
            filetypes=[("Auth files", "*.auth *.txt"), ("All files", "*.*")],
        )
        if path:
            self._auth_var.set(path)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable VPN controls."""
        state = "normal" if enabled else "disabled"
        self._config_entry.configure(state=state)
        self._config_btn.configure(state=state)
        self._auth_entry.configure(state=state)
        self._auth_btn.configure(state=state)
