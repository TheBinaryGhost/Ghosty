# 👻 Ghosty - Linux System Anonymizer

<div align="center">

**A comprehensive Python-based anonymization tool for Linux systems**

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)

*Professional-grade anonymization with MAC spoofing, VPN, and TOR integration*

</div>

---

## 📖 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [💾 Installation Methods](#-installation-methods)
- [🎮 How to Use](#-how-to-use)
- [🔧 Configuration](#-configuration)
- [📱 Desktop Integration](#-desktop-integration)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📁 Project Structure](#-project-structure)
- [⚠️ Security & Legal](#️-security--legal)

---

## 🎯 Overview

Ghosty is a modular, GUI-based anonymization tool designed for Linux systems. It provides three levels of anonymization protection:

- **🔄 MAC Address Spoofing** - Change hardware identifiers
- **🌐 VPN Integration** - Encrypted tunnel connections  
- **🧅 TOR Network** - Anonymous browsing with IP rotation

**Perfect for:** Privacy researchers, security professionals, penetration testers, and privacy-conscious users.

---

## ✨ Features

### 🛡️ Three Anonymization Modes
| Mode | MAC Spoofing | VPN | TOR | IP Rotation |
|------|-------------|-----|-----|------------|
| **Normal** | ✅ | ❌ | ❌ | ❌ |
| **Standard** | ✅ | ✅ | ❌ | ❌ |
| **Enhanced** | ✅ | ✅ | ✅ | ✅ |

### 🎨 User Experience
- **🖥️ Modern GUI** - Clean, intuitive Tkinter interface
- **📊 Real-time Monitoring** - Live IP/MAC address display
- **📝 Activity Logging** - Comprehensive operation logs
- **🔄 Safe Restoration** - Automatic rollback of changes
- **🎯 One-Click Operation** - Simple start/stop controls

### 🏗️ Technical Excellence
- **📦 Modular Architecture** - Well-organized, maintainable code
- **🔐 Secure Execution** - Proper privilege handling with pkexec
- **🐧 Linux Optimized** - Native system integration
- **⚡ Efficient Performance** - Minimal resource usage

---

## 🚀 Quick Start

### ⚡ Fastest Method (One Command)
```bash
git clone <your-repo-url> && cd Ghosty && chmod +x install.sh && ./install.sh
```

### 🎯 After Installation
- **Desktop**: Applications Menu → Network/Security → "Ghosty Anonymizer"
- **Terminal**: Type `ghosty`
- **File Manager**: Double-click desktop shortcut

---

## 💾 Installation Methods

### 🏆 Method 1: Automatic Installation (Recommended)

**Full system integration with desktop launcher:**

```bash
# Clone repository
git clone <your-repo-url>
cd Ghosty

# Run installer (asks for sudo password)
chmod +x install.sh
./install.sh
```

**✅ What you get:**
- 📱 Desktop application launcher
- 💻 Command-line `ghosty` command
- 🔧 Automatic dependency installation
- 🗑️ Easy uninstall option

---

### 🐍 Method 2: Python Setup Script

**Alternative installer with Python:**

```bash
cd Ghosty
chmod +x setup.py
python3 setup.py
```

**✅ Benefits:**
- 🔍 Better error reporting
- 🐍 Python-native installation
- 📋 Detailed dependency checking

---

### ⚡ Method 3: Direct Execution (No Installation)

**Run immediately without installation:**

```bash
cd Ghosty
chmod +x run_ghosty.sh
./run_ghosty.sh
```

**✅ Perfect for:**
- 🧪 Testing and evaluation
- 💾 Portable usage
- 🚫 No system modification needed

---

### 🔧 Method 4: Manual Execution

**Direct Python execution:**

```bash
cd Ghosty
chmod +x main.py
python3 main.py
```

---

## 🎮 How to Use

### 🖥️ Desktop Application

1. **Launch Ghosty**
   - Open Applications Menu → Search "Ghosty"
   - Or click desktop shortcut

2. **Select Network Interface**
   - Choose your network adapter from dropdown
   - Current MAC address displays automatically

3. **Choose Anonymization Mode**
   ```
   Normal Mode    → MAC spoofing only
   Standard Mode  → MAC + VPN connection  
   Enhanced Mode  → MAC + VPN + TOR with IP rotation
   ```

4. **Configure VPN (Standard/Enhanced)**
   - 📁 Browse for `.ovpn` configuration file
   - 🔑 Select authentication file (optional)

5. **Start Anonymization**
   - 🟢 Click **START** button
   - 📊 Monitor real-time IP/MAC changes
   - 📝 Check activity log for status

6. **Stop Safely**
   - 🔴 Click **STOP** button
   - 🔄 Original settings restored automatically

### 💻 Command Line Options

```bash
# System-wide installation
ghosty

# Direct from repository
./run_ghosty.sh

# With Python directly
python3 main.py

# Check help
python3 main.py --help
```

---

## 🔧 Configuration

### 📋 System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Linux (Ubuntu/Debian recommended) |
| **Python** | 3.6+ |
| **Privileges** | Root access (auto-requested) |
| **Memory** | 50MB+ available |

### 🛠️ Dependencies

**System Packages:**
```bash
sudo apt update
sudo apt install macchanger openvpn tor python3-pip python3-tk
```

**Python Modules:**
```bash
pip3 install requests psutil
```

### ⚙️ TOR Configuration (Enhanced Mode)

**Edit TOR configuration:**
```bash
sudo nano /etc/tor/torrc
```

**Add these lines:**
```ini
ControlPort 9051
CookieAuthentication 0
```

**Restart TOR service:**
```bash
sudo systemctl restart tor
sudo systemctl enable tor
```

### 📁 VPN Setup

**Prepare files:**
- 📄 `.ovpn` configuration file
- 🔑 Authentication file (username/password)
- 🗝️ Certificate files (if required)

**Example VPN file structure:**
```
vpn-configs/
├── config.ovpn
├── auth.txt
└── certificates/
    ├── ca.crt
    └── client.key
```

---

## 📱 Desktop Integration

### 🖥️ Applications Menu
- **Location**: Network → Security → Ghosty Anonymizer
- **Icon**: 👻 Security-themed icon
- **Categories**: Network, Security

### 🎯 Quick Access Options
- **Pin to Taskbar**: Right-click → Pin to taskbar
- **Desktop Shortcut**: Drag from applications menu
- **Favorites**: Add to application favorites
- **Keyboard Shortcut**: Set custom hotkey

### 🔧 File Manager Integration
- **Right-click main.py** → Open with Python
- **Double-click run_ghosty.sh** in file manager
- **Create custom launchers** in desktop environment

### 🗑️ Uninstallation
```bash
# Automatic uninstall
sudo /opt/ghosty/uninstall.sh

# Manual cleanup
sudo rm -rf /opt/ghosty
sudo rm -f /usr/share/applications/ghosty.desktop
sudo rm -f /usr/local/bin/ghosty
```

---

## 🛠️ Troubleshooting

### ❓ Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| **"Permission denied"** | `chmod +x *.sh` and ensure sudo access |
| **"macchanger not found"** | `sudo apt install macchanger` |
| **"Python module missing"** | `pip3 install -r requirements.txt` |
| **"TOR connection failed"** | Check TOR configuration and service status |
| **"VPN won't connect"** | Verify `.ovpn` file format and credentials |
| **"pkexec not found"** | `sudo apt install policykit-1` |

### 🔍 Debug Information

**Check service status:**
```bash
systemctl status tor        # TOR service
systemctl status openvpn    # OpenVPN service
ip addr show                # Network interfaces
```

**View logs:**
```bash
journalctl -u tor           # TOR logs
dmesg | grep -i network     # Network logs
tail -f /var/log/syslog     # System logs
```

### 🐛 Reporting Issues

**Before reporting:**
1. ✅ Check system requirements
2. ✅ Verify all dependencies installed
3. ✅ Review troubleshooting section
4. ✅ Check application logs

**Include in report:**
- 🐧 Linux distribution and version
- 🐍 Python version (`python3 --version`)
- 📋 Error messages from GUI log
- 🔧 Steps to reproduce issue

---

## 📁 Project Structure

```
Ghosty/
├── 📄 main.py              # Entry point and dependency management
├── 🖥️ gui.py               # Tkinter GUI interface
├── 🔄 macchanger.py        # MAC address spoofing
├── 🌐 vpn.py               # OpenVPN connection management  
├── 🧅 tor.py               # TOR service and IP rotation
├── 🛠️ utils.py             # Helper functions and utilities
├── 📦 requirements.txt     # Python dependencies
├── 🚀 install.sh           # Automatic installer (bash)
├── 🐍 setup.py             # Python installer alternative
├── ⚡ run_ghosty.sh         # Quick launcher script
├── 🖥️ ghosty.desktop       # Desktop application entry
├── 📚 INSTALL.md           # Detailed installation guide
├── 📖 README.md            # This comprehensive guide
└── 📄 LICENSE              # MIT License
```

### 🏗️ Module Descriptions

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **main.py** | Application entry point | Dependency check, root escalation |
| **gui.py** | User interface | Tkinter GUI, real-time updates |
| **macchanger.py** | MAC address manipulation | Change/restore MAC addresses |
| **vpn.py** | VPN connection management | OpenVPN control, status monitoring |
| **tor.py** | TOR network integration | Service control, IP rotation |
| **utils.py** | Shared utilities | Network info, logging, system calls |

---

## ⚠️ Security & Legal

### 🔒 Security Considerations

- **🔐 Root Privileges**: Required for network interface modifications
- **🛡️ Secure Execution**: Uses `pkexec` for GUI privilege escalation
- **🔄 Safe Restoration**: Automatic rollback prevents network lockout
- **📝 Audit Trail**: Comprehensive logging for security review

### ⚖️ Legal & Ethical Use

**✅ Acceptable Use:**
- 🧪 Personal privacy research
- 🔍 Security testing on owned systems
- 📚 Educational and learning purposes
- 🏢 Authorized penetration testing

**❌ Prohibited Use:**
- 🚫 Unauthorized network access
- 💰 Illegal activities or fraud
- 🕵️ Malicious surveillance
- 🏴‍☠️ Any unlawful purposes

### 📜 Disclaimer

**Important:** The developers of Ghosty are not responsible for any misuse of this tool. Users must ensure compliance with all applicable laws and regulations. This tool is provided for educational and legitimate security testing purposes only.

**Use Responsibly:** Only use Ghosty on systems you own or have explicit written permission to test.

---

<div align="center">

### 🎉 Ready to Get Started?

**Choose your installation method above and start anonymizing safely!**

Made with ❤️ for privacy and security professionals

[⭐ Star this project](.) | [🐛 Report issues](.) | [📚 Documentation](.)

</div>
