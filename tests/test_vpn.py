"""Tests for VPN manager."""

from __future__ import annotations

from ghosty.core.vpn import VPNManager


class TestVPNManager:
    """Tests for VPNManager."""

    def setup_method(self) -> None:
        self.vpn = VPNManager()

    def test_initial_state(self) -> None:
        assert not self.vpn.is_connected
        assert self.vpn.vpn_type is None

    def test_set_config_no_file(self, mock_run) -> None:
        success, msg = self.vpn.set_config("/nonexistent.ovpn")
        assert not success
        assert "not found" in msg

    def test_set_config_openvpn(self, mock_run, tmp_config_dir) -> None:
        config = tmp_config_dir / "test.ovpn"
        config.write_text("client\nremote 1.2.3.4\n")
        success, msg = self.vpn.set_config(str(config))
        assert success
        assert self.vpn.vpn_type == "openvpn"

    def test_set_config_wireguard(self, mock_run, tmp_config_dir) -> None:
        config = tmp_config_dir / "wg0.conf"
        config.write_text("[Interface]\nAddress = 10.0.0.1/24\n")
        success, msg = self.vpn.set_config(str(config))
        assert success
        assert self.vpn.vpn_type == "wireguard"

    def test_connect_without_config(self, mock_run) -> None:
        success, msg = self.vpn.connect()
        assert not success
        assert "No config" in msg
