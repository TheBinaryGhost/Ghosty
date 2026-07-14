"""Settings dialog — preferences window."""

from __future__ import annotations

import customtkinter as ctk

from ghosty.config import Config, load_config, save_config


class SettingsDialog(ctk.CTkToplevel):
    """Preferences dialog for Ghosty."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x350")
        self.resizable(False, False)

        self._config = load_config()
        self._saved = False

        # Theme
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=12)).pack(side="left")
        self._theme_var = ctk.StringVar(value=self._config.theme)
        self._theme_menu = ctk.CTkOptionMenu(
            theme_frame, variable=self._theme_var,
            values=["dark", "light", "system"], width=120
        )
        self._theme_menu.pack(side="right")

        # Language
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(lang_frame, text="Language:", font=ctk.CTkFont(size=12)).pack(side="left")
        self._lang_var = ctk.StringVar(value=self._config.language)
        self._lang_menu = ctk.CTkOptionMenu(
            lang_frame, variable=self._lang_var,
            values=["en", "ru"], width=120
        )
        self._lang_menu.pack(side="right")

        # Auto-connect
        self._auto_connect_var = ctk.BooleanVar(value=self._config.auto_connect)
        self._auto_connect_cb = ctk.CTkCheckBox(
            self, text="Auto-connect on startup", variable=self._auto_connect_var,
            font=ctk.CTkFont(size=12)
        )
        self._auto_connect_cb.pack(padx=20, pady=5, anchor="w")

        # Max log size
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(log_frame, text="Max log entries:", font=ctk.CTkFont(size=12)).pack(side="left")
        self._log_spin = ctk.CTkEntry(log_frame, width=80)
        self._log_spin.insert(0, str(self._config.max_log_entries))
        self._log_spin.pack(side="right")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", width=80, command=self.destroy
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_frame, text="Save", width=80, fg_color="#2563eb", command=self._save
        )
        save_btn.pack(side="right")

    @property
    def saved(self) -> bool:
        return self._saved

    def _save(self) -> None:
        """Save settings and close."""
        self._config.theme = self._theme_var.get()
        self._config.language = self._lang_var.get()
        self._config.auto_connect = self._auto_connect_var.get()

        try:
            self._config.max_log_entries = int(self._log_spin.get())
        except ValueError:
            pass

        save_config(self._config)
        self._saved = True
        self.destroy()
