"""Tests for TOR manager."""

from __future__ import annotations

from ghosty.core.tor import TORManager


class TestTORManager:
    """Tests for TORManager."""

    def setup_method(self) -> None:
        self.tor = TORManager()

    def test_initial_state(self) -> None:
        assert not self.tor.is_running

    def test_start_service_already_running(self, mock_run) -> None:
        mock_run.return_value = (True, "active (running)")
        success, msg = self.tor.start_service()
        assert success
        assert self.tor.is_running

    def test_stop_service_not_running(self, mock_run) -> None:
        mock_run.return_value = (True, "")
        success, msg = self.tor.stop_service()
        assert not success
        assert "Not running" in msg

    def test_rotate_ip_not_running(self, mock_run) -> None:
        mock_run.return_value = (False, "")
        success, msg = self.tor.rotate_ip()
        assert not success
