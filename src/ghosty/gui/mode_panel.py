"""Mode panel — lets the user choose the anonymization mode."""

from __future__ import annotations

import customtkinter as ctk

from ghosty.core.orchestrator import AnonymizationMode


class ModePanel(ctk.CTkFrame):
    """Anonymization mode selector."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, corner_radius=8)

        # Title
        title = ctk.CTkLabel(
            self, text="Anonymization Mode", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # Mode radio buttons
        self._mode_var = ctk.StringVar(value=AnonymizationMode.NORMAL.value)

        self._normal_btn = ctk.CTkRadioButton(
            self, text="Normal", variable=self._mode_var,
            value=AnonymizationMode.NORMAL.value, font=ctk.CTkFont(size=12)
        )
        self._normal_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self._standard_btn = ctk.CTkRadioButton(
            self, text="Standard", variable=self._mode_var,
            value=AnonymizationMode.STANDARD.value, font=ctk.CTkFont(size=12)
        )
        self._standard_btn.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self._enhanced_btn = ctk.CTkRadioButton(
            self, text="Enhanced", variable=self._mode_var,
            value=AnonymizationMode.ENHANCED.value, font=ctk.CTkFont(size=12)
        )
        self._enhanced_btn.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Description label
        self._desc_label = ctk.CTkLabel(
            self, text="Normal: MAC spoof only", font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self._desc_label.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

        # Trace to update description
        self._mode_var.trace_add("write", self._on_mode_change)

    @property
    def selected(self) -> AnonymizationMode:
        """Return the selected mode as AnonymizationMode enum."""
        return AnonymizationMode(self._mode_var.get())

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable mode selection (disabled while active)."""
        state = "normal" if enabled else "disabled"
        self._normal_btn.configure(state=state)
        self._standard_btn.configure(state=state)
        self._enhanced_btn.configure(state=state)

    def _on_mode_change(self, *_args: object) -> None:
        """Update description when mode changes."""
        mode = self.selected
        descriptions = {
            AnonymizationMode.NORMAL: "Normal: MAC spoof only",
            AnonymizationMode.STANDARD: "Standard: MAC spoof + VPN",
            AnonymizationMode.ENHANCED: "Enhanced: MAC spoof + VPN + TOR",
        }
        self._desc_label.configure(text=descriptions.get(mode, ""))
