"""Tests for MAC address spoofing."""

from __future__ import annotations

from unittest.mock import patch

from ghosty.core.mac import MACChanger


class TestMACChanger:
    """Tests for MACChanger."""

    def setup_method(self) -> None:
        self.changer = MACChanger()

    def test_initial_state(self) -> None:
        assert not self.changer.is_changed

    def test_change_mac_success(self, mock_run) -> None:
        mock_run.return_value = (True, "")
        success, msg = self.changer.change_mac("eth0")
        assert success
        assert "Changed" in msg
        assert self.changer.is_changed

    def test_change_mac_no_interface(self, mock_run) -> None:
        mock_run.return_value = (False, "No such device")
        success, msg = self.changer.change_mac("bad0")
        assert not success

    def test_restore_mac_no_original(self, mock_run) -> None:
        success, msg = self.changer.restore_mac("eth0")
        assert not success
        assert "No original" in msg

    def test_restore_after_change(self, mock_run) -> None:
        mock_run.return_value = (True, "")
        self.changer.change_mac("eth0")
        success, msg = self.changer.restore_mac("eth0")
        assert success
        assert "Restored" in msg
        assert not self.changer.is_changed

    def test_randomize_mac(self) -> None:
        mac1 = MACChanger.randomize_mac()
        mac2 = MACChanger.randomize_mac()
        assert len(mac1) == 17  # XX:XX:XX:XX:XX:XX
        assert mac1 != mac2
