# Ghosty v2 — Linux Anonymizer

<div align="center">

**A modern Python anonymizer for Linux with CustomTkinter GUI**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)

*MAC spoofing, VPN, TOR — one click, three levels of privacy*

</div>

---

## Overview

Ghosty is a modular, GUI-based anonymization tool for Linux. It provides three levels of protection:

- **MAC Spoofing** — Randomize your hardware address
- **VPN** — Encrypted tunnel (OpenVPN + WireGuard)
- **TOR** — Anonymous routing with IP rotation

---

## Features

### Anonymization Modes

| Mode | MAC | VPN | TOR | IP Rotation |
|------|-----|-----|-----|-------------|
| **Normal** | ✅ | ❌ | ❌ | ❌ |
| **Standard** | ✅ | ✅ | ❌ | ❌ |
| **Enhanced** | ✅ | ✅ | ✅ | ✅ |

### Technical Highlights

- **Modern GUI** — CustomTkinter with dark/light themes
- **Crash-safe** — atexit + signal handlers restore state on unexpected exit
- **Multi-VPN** — OpenVPN and WireGuard support
- **Distro detection** — apt/dnf/pacman/zypper abstraction
- **TOML config** — Persistent preferences at `~/.config/ghosty/config.toml`
- **Thread-safe** — Background operations with UI updates on main thread

---

## Installation

### Quick Install (pip)

```bash
git clone https://github.com/TheBinaryGhost/Ghosty
cd Ghosty
pip install -e .
```

### Development Install

```bash
pip install -e ".[dev]"
```

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt install macchanger openvpn tor

# Fedora
sudo dnf install macchanger openvpn tor

# Arch
sudo pacman -S macchanger openvpn tor
```

---

## Usage

### Launch GUI

```bash
# Via entry point
ghosty

# Or via module
python -m ghosty
```

### Steps

1. **Select Interface** — Choose your network adapter
2. **Choose Mode** — Normal / Standard / Enhanced
3. **Configure VPN** (Standard/Enhanced) — Browse for `.ovpn` or `.conf`
4. **Start** — Click the green button
5. **Stop** — Click red to restore original settings

---

## Project Structure

```
src/ghosty/
├── __init__.py          # Package root
├── __main__.py          # Entry point
├── app.py               # GUI launcher
├── config.py            # TOML config system
├── logger.py            # Structured logging
├── utils/
│   ├── process.py       # Safe subprocess wrapper
│   ├── network.py       # IP/interface utilities
│   └── platform.py      # Distro detection
├── core/
│   ├── mac.py           # MAC spoofing
│   ├── vpn.py           # OpenVPN + WireGuard
│   ├── tor.py           # TOR + IP rotation
│   └── orchestrator.py  # Mode coordinator
└── gui/
    ├── status_panel.py      # Status display
    ├── interface_panel.py   # Interface selector
    ├── mode_panel.py        # Mode selector
    ├── vpn_panel.py         # VPN config picker
    ├── control_panel.py     # Start/Stop
    ├── log_panel.py         # Activity log
    ├── settings_dialog.py   # Preferences
    └── main_window.py       # Main assembly
```

---

## Configuration

Config is stored at `~/.config/ghosty/config.toml`:

```toml
theme = "dark"
language = "en"
vpn_interface = "tun0"
tor_socks_port = 9051
auto_connect = false
```

### TOR Setup (Enhanced Mode)

Edit `/etc/tor/torrc`:
```
ControlPort 9051
CookieAuthentication 0
```

Restart:
```bash
sudo systemctl restart tor
```

---

## Development

### Run Tests

```bash
pytest
```

### Lint

```bash
ruff check src/ tests/
```

### Type Check

```bash
mypy src/ghosty/ --ignore-missing-imports
```

### Build

```bash
python -m build
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | Run with `sudo` for MAC changes |
| macchanger not found | `sudo apt install macchanger` |
| TOR failed | Check `/etc/tor/torrc` and `systemctl status tor` |
| VPN won't connect | Verify `.ovpn` file and credentials |

---

## License

MIT — see [LICENSE](LICENSE).

---

## Disclaimer

The developers are not responsible for misuse. Use only on systems you own or have permission to test. Comply with all applicable laws.
