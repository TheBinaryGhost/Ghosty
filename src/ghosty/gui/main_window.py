"""Main window — assembles all GUI panels into the application."""

from __future__ import annotations

import threading

import customtkinter as ctk

from ghosty.config import load_config, save_config
from ghosty.core.orchestrator import AnonymizationMode, Orchestrator
from ghosty.gui.control_panel import ControlPanel
from ghosty.gui.interface_panel import InterfacePanel
from ghosty.gui.log_panel import LogPanel
from ghosty.gui.mode_panel import ModePanel
from ghosty.gui.settings_dialog import SettingsDialog
from ghosty.gui.status_panel import StatusPanel
from ghosty.gui.vpn_panel import VPNPanel
from ghosty.utils.network import get_external_ip


class MainWindow(ctk.CTk):
    """Ghosty main application window."""

    WIDTH = 600
    HEIGHT = 720

    def __init__(self) -> None:
        super().__init__()

        self._config = load_config()
        ctk.set_appearance_mode(self._config.general.theme)

        # Window setup
        self.title("Ghosty — Linux Anonymizer")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(520, 600)

        # Orchestrator
        self._orchestrator = Orchestrator()
        self._orchestrator.set_log_callback(self._log_message)

        # Build layout
        self._build_menu()
        self._build_panels()

    def _build_menu(self) -> None:
        """Build the menu bar."""
        menu = ctk.CTkFrame(self, height=32, corner_radius=0)
        menu.pack(fill="x")

        settings_btn = ctk.CTkButton(
            menu, text="⚙ Settings", width=80, height=28,
            fg_color="transparent", hover_color="#374151",
            command=self._open_settings
        )
        settings_btn.pack(side="right", padx=5, pady=2)

    def _build_panels(self) -> None:
        """Assemble all panels."""
        # Scrollable container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # Status panel
        self._status = StatusPanel(container)
        self._status.pack(fill="x", pady=5)

        # Interface panel
        self._interface = InterfacePanel(container)
        self._interface.pack(fill="x", pady=5)

        # Mode panel
        self._mode = ModePanel(container)
        self._mode.pack(fill="x", pady=5)

        # VPN panel
        self._vpn = VPNPanel(container)
        self._vpn.pack(fill="x", pady=5)

        # Control panel
        self._control = ControlPanel(container)
        self._control.on_start(self._start_anonymization)
        self._control.on_stop(self._stop_anonymization)
        self._control.pack(fill="x", pady=5)

        # Log panel
        self._log = LogPanel(container)
        self._log.pack(fill="both", expand=True, pady=5)

        # Connect orchestrator to orchestrator
        self._orchestrator._log_callback = self._log.append

    def _start_anonymization(self) -> None:
        """Start anonymization in a background thread."""
        mode = self._mode.selected
        interface = self._interface.selected

        # Validate VPN config for modes that need it
        vpn_config = ""
        vpn_auth = None
        if mode in (AnonymizationMode.STANDARD, AnonymizationMode.ENHANCED):
            vpn_config = self._vpn.config_path
            vpn_auth = self._vpn.auth_path
            if not vpn_config:
                self._log.append("ERROR: VPN config required for Standard/Enhanced modes")
                return

        # Update UI
        self._control.set_active(True)
        self._mode.set_enabled(False)
        self._vpn.set_enabled(False)
        self._status.set_active(mode.value)
        self._log.append(f"Starting {mode.value} mode on {interface}...")

        # Run in background thread
        def _start():
            success, message = self._orchestrator.start(
                mode, interface, vpn_config=vpn_config, vpn_auth=vpn_auth
            )
            self.after(0, lambda: self._on_start_complete(success, message))

        threading.Thread(target=_start, daemon=True).start()

    def _on_start_complete(self, success: bool, message: str) -> None:
        """Handle start completion on main thread."""
        if not success:
            self._log.append(f"FAILED: {message}")
            self._control.set_active(False)
            self._mode.set_enabled(True)
            self._vpn.set_enabled(True)
            self._status.set_inactive()
        else:
            self._log.append(f"OK: {message}")
            self._update_ip()

    def _stop_anonymization(self) -> None:
        """Stop anonymization in a background thread."""
        self._log.append("Stopping anonymization...")

        def _stop():
            success, message = self._orchestrator.stop()
            self.after(0, lambda: self._on_stop_complete(success, message))

        threading.Thread(target=_stop, daemon=True).start()

    def _on_stop_complete(self, success: bool, message: str) -> None:
        """Handle stop completion on main thread."""
        if success:
            self._log.append(f"OK: {message}")
        else:
            self._log.append(f"WARNING: {message}")

        self._control.set_active(False)
        self._mode.set_enabled(True)
        self._vpn.set_enabled(True)
        self._status.set_inactive()

    def _update_ip(self) -> None:
        """Fetch and display external IP in background."""
        def _fetch():
            ip = get_external_ip()
            self.after(0, lambda: self._status.set_ip(ip or "unavailable"))

        threading.Thread(target=_fetch, daemon=True).start()

    def _log_message(self, message: str) -> None:
        """Log callback for orchestrator (may be called from threads)."""
        # Thread-safe log update via after()
        if threading.current_thread() is threading.main_thread():
            self._log.append(message)
        else:
            self.after(0, lambda: self._log.append(message))

    def _open_settings(self) -> None:
        """Open settings dialog."""
        dialog = SettingsDialog(self)
        self.wait_window(dialog)

        if dialog.saved:
            self._config = load_config()
        ctk.set_appearance_mode(self._config.general.theme)
