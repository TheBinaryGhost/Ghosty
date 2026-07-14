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

- **MAC Spoofing** — Randomize your hardware address with truly random MAC generation
- **VPN** — Encrypted tunnel via OpenVPN or WireGuard
- **TOR** — Anonymous routing with automatic IP rotation via tornet-mp

---

## Features

### Anonymization Modes

| Mode | MAC | VPN | TOR | IP Rotation |
|------|-----|-----|-----|-------------|
| **Normal** | ✅ | ❌ | ❌ | ❌ |
| **Standard** | ✅ | ✅ | ❌ | ❌ |
| **Enhanced** | ✅ | ✅ | ✅ | ✅ |

### Technical Highlights

- **Modern GUI** — CustomTkinter with dark/light themes (landscape layout)
- **Root required** — Auto-elevates via `sudo` if not run as root
- **Crash-safe** — atexit + signal handlers restore state on unexpected exit
- **Multi-VPN** — OpenVPN and WireGuard support with provider selector
- **Auto-install** — Dependencies (macchanger, openvpn, wireguard-tools, tor, tornet-mp, stem) installed automatically
- **Distro detection** — apt/dnf/pacman/zypper abstraction
- **TOML config** — Persistent preferences at `~/.config/ghosty/config.toml`
- **Thread-safe** — Background operations with UI updates on main thread
- **Random MAC** — Generates truly random locally-administered unicast addresses

---

## Installation

### Quick Install (pip + venv)

```bash
git clone https://github.com/TheBinaryGhost/Ghosty
cd Ghosty

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

### Launch

```bash
# Via entry point (requires root)
sudo ghosty

# Or via module
sudo python -m ghosty
```

---

## Usage

1. **Select Interface** — Choose your network adapter
2. **Choose Mode** — Normal / Standard / Enhanced
3. **Configure VPN** (Standard/Enhanced) — Browse for `.ovpn` or `.conf` file, select provider (OpenVPN/WireGuard)
4. **Start** — Click the green button (auto-elevates to root)
5. **Stop** — Click red to restore original settings

### What Happens on Start

| Step | Action |
|------|--------|
| 1 | MAC address changed to random value |
| 2 | VPN connection established (Standard/Enhanced) |
| 3 | TOR service started + IP rotation begins (Enhanced) |

---

## Project Structure

```
src/ghosty/
├── __init__.py          # Package root
├── __main__.py          # Entry point (auto-sudo)
├── app.py               # GUI launcher (auto-sudo)
├── config.py            # TOML config system
├── logger.py            # Structured logging
├── utils/
│   ├── process.py       # Safe subprocess wrapper
│   ├── network.py       # IP/interface utilities
│   └── platform.py      # Distro detection
├── core/
│   ├── mac.py           # MAC spoofing (random generation)
│   ├── vpn.py           # OpenVPN + WireGuard (auto-install)
│   ├── tor.py           # TOR + IP rotation (tornet-mp)
│   └── orchestrator.py  # Mode coordinator
└── gui/
    ├── status_panel.py      # Status display
    ├── interface_panel.py   # Interface selector
    ├── mode_panel.py        # Mode selector
    ├── vpn_panel.py         # VPN config + provider picker
    ├── control_panel.py     # Start/Stop
    ├── log_panel.py         # Activity log
    ├── settings_dialog.py   # Preferences
    └── main_window.py       # Main assembly (960×600)
```

---

## Configuration

Config is stored at `~/.config/ghosty/config.toml`:

```toml
[general]
theme = "dark"
language = "en"
log_level = "INFO"
auto_connect = false

[vpn]
interface = "tun0"
config_path = ""
auth_path = ""

[tor]
controller_port = 9051
rotation_interval = 5

[log]
max_size = 10485760
backup_count = 5
```

---

## Auto-Installed Dependencies

Ghosty automatically installs missing system packages when needed:

| Package | Purpose | Install Command |
|---------|---------|-----------------|
| `macchanger` | MAC spoofing | `apt install macchanger` |
| `openvpn` | OpenVPN connections | `apt install openvpn` |
| `wireguard-tools` | WireGuard connections | `apt install wireguard-tools` |
| `tor` | TOR network | `apt install tor` |
| `tornet-mp` | IP rotation | `pip install tornet-mp` |
| `stem` | TOR controller | `pip install stem` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Permission denied | Tool auto-elevates via `sudo`; enter password when prompted |
| VPN won't connect | Verify `.ovpn`/`.conf` file path and credentials |
| TOR failed to start | Check `systemctl status tor` |
| MAC not changing | Ensure `macchanger` is installed (auto-installed on supported distros) |

---

## License

MIT — see [LICENSE](LICENSE).

---

## Disclaimer

The developers are not responsible for misuse. Use only on systems you own or have permission to test. Comply with all applicable laws.
