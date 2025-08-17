#!/usr/bin/env python3
"""
Ghosty Utilities Module
Provides helper functions for root checking, IP fetching, and system utilities.
"""

import os
import sys
import subprocess
import requests
import psutil
from typing import List, Optional


def check_root() -> bool:
    """Check if the script is running with root privileges."""
    return os.geteuid() == 0


def request_root():
    """Request root privileges and restart the script if needed."""
    if not check_root():
        print("⚠️  Ghosty requires root privileges to modify network settings.")
        try:
            # Try to restart with sudo
            args = ['sudo', sys.executable] + sys.argv
            os.execvp('sudo', args)
        except Exception as e:
            print(f"❌ Failed to obtain root privileges: {e}")
            sys.exit(1)


def get_current_ip() -> str:
    """Fetch the current public IP address."""
    try:
        # Try multiple IP services for better reliability
        services = [
            'https://api.ipify.org',
            'https://ipinfo.io/ip',
            'https://checkip.amazonaws.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
                
        return "Unable to fetch"
    except Exception as e:
        print(f"❌ Failed to get IP: {e}")
        return "Unknown"


def get_network_interfaces() -> List[str]:
    """Get list of available network interfaces."""
    interfaces = []
    try:
        # Get network interfaces using psutil
        net_if = psutil.net_if_addrs()
        for interface in net_if.keys():
            if interface != 'lo':  # Exclude loopback
                interfaces.append(interface)
    except Exception as e:
        print(f"❌ Failed to get interfaces: {e}")
    
    return interfaces


def get_interface_mac(interface: str) -> str:
    """Get the current MAC address of a network interface."""
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            return f.read().strip()
    except Exception as e:
        log_message(f"Failed to get MAC for {interface}: {e}", "ERROR")
        return "Unknown"


def run_command(command: List[str]) -> tuple:
    """
    Run a system command and return (success, output, error).
    
    Args:
        command: List of command parts
        
    Returns:
        tuple: (success: bool, output: str, error: str)
    """
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout.strip(), ""
    except subprocess.CalledProcessError as e:
        return False, "", e.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def log_message(message: str, level: str = "INFO"):
    """Simple logging function."""
    print(f"[{level}] {message}")
