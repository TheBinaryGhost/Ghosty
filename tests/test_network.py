"""Tests for network utilities."""

from __future__ import annotations

from unittest.mock import patch

from ghosty.utils.network import get_external_ip, get_interfaces


class TestNetwork:
    """Tests for network utilities."""

    def test_get_interfaces_with_data(self, mock_run) -> None:
        mock_run.return_value = (True, "eth0\nlo\nwlan0\n")
        interfaces = get_interfaces()
        assert "eth0" in interfaces
        assert "wlan0" in interfaces
        assert "lo" not in interfaces

    def test_get_interfaces_empty(self, mock_run) -> None:
        mock_run.return_value = (False, "")
        interfaces = get_interfaces()
        assert interfaces == ["lo"]

    def test_get_external_ip_success(self, mock_run) -> None:
        mock_run.return_value = (True, "203.0.113.1")
        ip = get_external_ip()
        assert ip == "203.0.113.1"

    def test_get_external_ip_failure(self, mock_run) -> None:
        mock_run.return_value = (False, "")
        ip = get_external_ip()
        assert ip is None
