#!/usr/bin/env python3
"""
Ghosty Setup Script
Alternative Python-based installer for Ghosty Linux Anonymizer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a system command."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                               capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def print_status(message, level="INFO"):
    """Print colored status messages."""
    colors = {
        "INFO": "\033[0;32m",    # Green
        "WARNING": "\033[1;33m", # Yellow
        "ERROR": "\033[0;31m",   # Red
        "STEP": "\033[0;34m"     # Blue
    }
    reset = "\033[0m"
    print(f"{colors.get(level, '')}[{level}]{reset} {message}")

def check_root():
    """Check if running as root."""
    return os.geteuid() == 0

def main():
    print("👻 Ghosty Linux Anonymizer - Python Setup Script")
    print("=" * 50)
    
    if check_root():
        print_status("Please do not run this script as root. It will ask for sudo when needed.", "ERROR")
        sys.exit(1)
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    install_dir = Path("/opt/ghosty")
    
    print_status("1. Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print_status("Python 3.6 or higher is required.", "ERROR")
        sys.exit(1)
    
    print_status(f"Python version: {sys.version}")
    
    # Check if pip is available
    success, _, _ = run_command("pip3 --version")
    if not success:
        print_status("pip3 is required but not found. Installing...", "WARNING")
        run_command("sudo apt update && sudo apt install -y python3-pip")
    
    print_status("2. Installing system dependencies...")
    
    # Install system packages
    packages = "macchanger openvpn tor python3-pip python3-tk python3-psutil"
    success, _, error = run_command(f"sudo apt update && sudo apt install -y {packages}")
    
    if not success:
        print_status(f"Failed to install system packages: {error}", "ERROR")
        sys.exit(1)
    
    print_status("3. Installing Python dependencies...")
    
    # Install Python packages
    requirements_file = script_dir / "requirements.txt"
    if requirements_file.exists():
        success, _, error = run_command(f"pip3 install --user -r {requirements_file}")
        if not success:
            print_status(f"Failed to install Python packages: {error}", "WARNING")
    
    print_status("4. Setting up installation directory...")
    
    # Create installation directory and copy files
    run_command(f"sudo mkdir -p {install_dir}")
    run_command(f"sudo cp -r {script_dir}/* {install_dir}/")
    run_command(f"sudo chmod +x {install_dir}/*.py")
    
    print_status("5. Creating desktop launcher...")
    
    # Create desktop file
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Ghosty Anonymizer
Comment=Linux system anonymization tool
Exec=pkexec python3 {install_dir}/main.py
Icon=applications-security
Terminal=false
StartupNotify=true
Categories=Network;Security;
Keywords=anonymizer;privacy;tor;vpn;security;
"""
    
    desktop_file = "/usr/share/applications/ghosty.desktop"
    with open("/tmp/ghosty.desktop", "w") as f:
        f.write(desktop_content)
    
    run_command(f"sudo mv /tmp/ghosty.desktop {desktop_file}")
    run_command(f"sudo chmod 644 {desktop_file}")
    
    print_status("6. Creating command-line executable...")
    
    # Create executable script
    executable_content = f"""#!/bin/bash
cd {install_dir}
exec python3 main.py "$@"
"""
    
    executable_file = "/usr/local/bin/ghosty"
    with open("/tmp/ghosty", "w") as f:
        f.write(executable_content)
    
    run_command(f"sudo mv /tmp/ghosty {executable_file}")
    run_command(f"sudo chmod +x {executable_file}")
    
    print_status("7. Finalizing installation...")
    
    # Set permissions
    run_command(f"sudo chown -R root:root {install_dir}")
    run_command(f"sudo chmod -R 755 {install_dir}")
    
    # Update desktop database
    run_command("sudo update-desktop-database /usr/share/applications/", check=False)
    
    # Create uninstaller
    uninstall_content = f"""#!/bin/bash
echo "Uninstalling Ghosty..."
sudo rm -rf {install_dir}
sudo rm -f {desktop_file}
sudo rm -f {executable_file}
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true
echo "Ghosty has been uninstalled."
"""
    
    uninstall_file = install_dir / "uninstall.sh"
    with open("/tmp/uninstall.sh", "w") as f:
        f.write(uninstall_content)
    
    run_command(f"sudo mv /tmp/uninstall.sh {uninstall_file}")
    run_command(f"sudo chmod +x {uninstall_file}")
    
    print()
    print("🎉 Installation completed successfully!")
    print()
    print("📋 How to run Ghosty:")
    print("   1. Applications menu: Search for 'Ghosty Anonymizer'")
    print("   2. Command line: Type 'ghosty' in terminal")
    print(f"   3. Direct: python3 {install_dir}/main.py")
    print()
    print(f"📁 Installed at: {install_dir}")
    print(f"🗑️  Uninstall: sudo {uninstall_file}")
    print()
    print_status("Ghosty is ready to use!")

if __name__ == "__main__":
    main()
