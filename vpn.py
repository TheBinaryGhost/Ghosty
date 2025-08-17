#!/usr/bin/env python3
"""
Ghosty VPN Module
Handles OpenVPN connection and management.
"""

import subprocess
import threading
import time
import os
from typing import Optional, Tuple
from utils import run_command, log_message


class VPNManager:
    def __init__(self):
        self.process = None
        self.config_file = None
        self.auth_file = None
        self.is_connected = False
        self.connection_thread = None
        
    def is_openvpn_available(self) -> bool:
        """Check if OpenVPN is installed."""
        success, _, _ = run_command(['which', 'openvpn'])
        return success
    
    def set_config(self, config_file: str, auth_file: Optional[str] = None) -> Tuple[bool, str]:
        """
        Set OpenVPN configuration files.
        
        Args:
            config_file: Path to .ovpn config file
            auth_file: Path to auth file (optional)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not os.path.exists(config_file):
            return False, f"Config file not found: {config_file}"
        
        if auth_file and not os.path.exists(auth_file):
            return False, f"Auth file not found: {auth_file}"
        
        self.config_file = config_file
        self.auth_file = auth_file
        
        return True, "VPN configuration set successfully"
    
    def connect(self) -> Tuple[bool, str]:
        """
        Connect to VPN using configured files.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_openvpn_available():
            return False, "OpenVPN is not installed. Install with: sudo apt install openvpn"
        
        if not self.config_file:
            return False, "No VPN configuration file set"
        
        if self.is_connected:
            return False, "VPN is already connected"
        
        try:
            # Build OpenVPN command
            cmd = ['openvpn', '--config', self.config_file]
            
            if self.auth_file:
                cmd.extend(['--auth-user-pass', self.auth_file])
            
            # Add common options for better compatibility
            cmd.extend([
                '--script-security', '2',
                '--up', '/etc/openvpn/update-resolv-conf',
                '--down', '/etc/openvpn/update-resolv-conf'
            ])
            
            # Start OpenVPN process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start monitoring thread
            self.connection_thread = threading.Thread(target=self._monitor_connection)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            
            # Wait a moment to check if connection starts properly
            time.sleep(2)
            
            if self.process.poll() is None:  # Process is still running
                self.is_connected = True
                log_message("VPN connection initiated")
                return True, "VPN connection started"
            else:
                stdout, stderr = self.process.communicate()
                return False, f"VPN failed to start: {stderr}"
                
        except Exception as e:
            return False, f"Failed to start VPN: {str(e)}"
    
    def disconnect(self) -> Tuple[bool, str]:
        """
        Disconnect from VPN.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_connected:
            return False, "VPN is not connected"
        
        try:
            if self.process:
                self.process.terminate()
                
                # Wait for process to terminate gracefully
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            
            self.is_connected = False
            log_message("VPN disconnected")
            return True, "VPN disconnected successfully"
            
        except Exception as e:
            return False, f"Failed to disconnect VPN: {str(e)}"
    
    def get_status(self) -> str:
        """Get current VPN connection status."""
        if self.is_connected and self.process and self.process.poll() is None:
            return "Connected"
        else:
            self.is_connected = False
            return "Disconnected"
    
    def _monitor_connection(self):
        """Monitor VPN connection in background thread."""
        if not self.process:
            return
        
        try:
            # Monitor the process
            stdout, stderr = self.process.communicate()
            
            # Process has ended
            if self.process.returncode != 0:
                log_message(f"VPN process ended with error: {stderr}", "ERROR")
            else:
                log_message("VPN process ended normally")
            
            self.is_connected = False
            
        except Exception as e:
            log_message(f"Error monitoring VPN: {e}", "ERROR")
            self.is_connected = False
    
    def get_connection_info(self) -> dict:
        """Get detailed connection information."""
        info = {
            'status': self.get_status(),
            'config_file': self.config_file,
            'auth_file': self.auth_file,
            'process_id': self.process.pid if self.process else None
        }
        return info


# Test function
if __name__ == "__main__":
    vpn = VPNManager()
    
    # Test availability
    if vpn.is_openvpn_available():
        print("✅ OpenVPN is available")
    else:
        print("❌ OpenVPN is not installed")
    
    print(f"Status: {vpn.get_status()}")
