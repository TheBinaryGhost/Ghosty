#!/usr/bin/env python3
"""
Ghosty TOR Module
Handles TOR service management and IP rotation.
"""

import subprocess
import threading
import time
import requests
from typing import Tuple, Optional
from utils import run_command, log_message

try:
    from stem import Signal
    from stem.control import Controller
    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False


class TORManager:
    def __init__(self):
        self.is_running = False
        self.rotation_thread = None
        self.controller = None
        self.stop_rotation = False
        self.tor_process = None
        
    def is_tor_available(self) -> bool:
        """Check if TOR is installed."""
        success, _, _ = run_command(['which', 'tor'])
        return success
    
    def check_tor_service_status(self) -> Tuple[bool, str]:
        """Check if TOR service is enabled and running."""
        try:
            # Check if service is enabled
            success, output, _ = run_command(['systemctl', 'is-enabled', 'tor'])
            is_enabled = success and 'enabled' in output.lower()
            
            # Check if service is running
            success, output, _ = run_command(['systemctl', 'is-active', 'tor'])
            is_running = success and 'active' in output.lower()
            
            return (is_enabled, is_running), f"Enabled: {is_enabled}, Running: {is_running}"
            
        except Exception as e:
            return (False, False), f"Failed to check TOR status: {str(e)}"
    
    def start_tor_service(self) -> Tuple[bool, str]:
        """Start and enable TOR service."""
        if not self.is_tor_available():
            return False, "TOR is not installed. Install with: sudo apt install tor"
        
        try:
            # Check current status
            (is_enabled, is_running), status_msg = self.check_tor_service_status()
            log_message(f"TOR service status: {status_msg}")
            
            # Enable TOR service if not enabled
            if not is_enabled:
                log_message("Enabling TOR service...")
                success, _, error = run_command(['sudo', 'systemctl', 'enable', 'tor'])
                if not success:
                    log_message(f"Failed to enable TOR service: {error}", "WARNING")
                else:
                    log_message("TOR service enabled")
            
            # Start TOR service if not running
            if not is_running:
                log_message("Starting TOR service...")
                success, _, error = run_command(['sudo', 'systemctl', 'start', 'tor'])
                if not success:
                    # Try alternative method
                    success, _, error = run_command(['sudo', 'service', 'tor', 'start'])
                    if not success:
                        return False, f"Failed to start TOR service: {error}"
                
                # Wait for service to start
                time.sleep(5)
                
                # Verify service is running
                (_, is_running_now), _ = self.check_tor_service_status()
                if not is_running_now:
                    return False, "TOR service failed to start properly"
            
            log_message("TOR service started and enabled")
            return True, "TOR service started and enabled successfully"
            
        except Exception as e:
            return False, f"Failed to start TOR: {str(e)}"
    
    def stop_tor_service(self) -> Tuple[bool, str]:
        """Stop TOR service."""
        try:
            success, _, error = run_command(['systemctl', 'stop', 'tor'])
            if not success:
                success, _, error = run_command(['service', 'tor', 'stop'])
                if not success:
                    return False, f"Failed to stop TOR service: {error}"
            
            log_message("TOR service stopped")
            return True, "TOR service stopped successfully"
            
        except Exception as e:
            return False, f"Failed to stop TOR: {str(e)}"
    
    def connect_to_controller(self) -> Tuple[bool, str]:
        """Connect to TOR controller for circuit management."""
        if not STEM_AVAILABLE:
            return False, "stem library not available. Install with: pip3 install stem"
        
        try:
            self.controller = Controller.from_port(port=9051)
            self.controller.authenticate()
            
            log_message("Connected to TOR controller")
            return True, "Connected to TOR controller"
            
        except Exception as e:
            # Try connecting without authentication
            try:
                self.controller = Controller.from_port(port=9051)
                log_message("Connected to TOR controller (no auth)")
                return True, "Connected to TOR controller"
            except Exception as e2:
                return False, f"Failed to connect to TOR controller: {str(e2)}"
    

    def start_ip_rotation(self) -> Tuple[bool, str]:
        """Start automatic IP rotation using tornet command."""
        # First verify TOR status
        (is_enabled, is_running), status_msg = self.check_tor_service_status()
        if not is_running:
            return False, f"TOR service is not running. Status: {status_msg}"
        
        # Check if tornet is available
        success, _, _ = run_command(['which', 'tornet'])
        if not success:
            return False, "tornet command not found. Please install tornet package."
        
        if self.tor_process and self.tor_process.poll() is None:
            return False, "IP rotation is already running"
        
        try:
            # Start tornet with interval 5 and count 0 (infinite rotation)
            log_message("Starting IP rotation with tornet...")
            self.tor_process = subprocess.Popen(
                ['sudo', 'tornet', '--interval', '5', '--count', '0'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start monitoring thread
            self.rotation_thread = threading.Thread(target=self._monitor_tornet)
            self.rotation_thread.daemon = True
            self.rotation_thread.start()
            
            self.is_running = True
            log_message("IP rotation started with tornet (interval: 5 seconds, continuous)")
            return True, "IP rotation started with tornet (interval: 5 seconds, continuous)"
            
        except Exception as e:
            return False, f"Failed to start tornet: {str(e)}"
    
    def stop_ip_rotation(self) -> Tuple[bool, str]:
        """Stop automatic IP rotation."""
        self.is_running = False
        
        if self.tor_process:
            try:
                self.tor_process.terminate()
                try:
                    self.tor_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.tor_process.kill()
                    self.tor_process.wait()
                self.tor_process = None
            except Exception as e:
                log_message(f"Error stopping tornet: {e}", "ERROR")
        
        if self.rotation_thread:
            self.rotation_thread.join(timeout=5)
        
        if self.controller:
            try:
                self.controller.close()
                self.controller = None
            except:
                pass
        
        log_message("IP rotation stopped")
        return True, "IP rotation stopped"
    
    def _monitor_tornet(self):
        """Monitor tornet process."""
        if not self.tor_process:
            return
        
        try:
            # Read output from tornet
            while self.tor_process.poll() is None and self.is_running:
                output = self.tor_process.stdout.readline()
                if output:
                    log_message(f"tornet: {output.strip()}")
                time.sleep(0.1)
            
            # Process has ended
            if self.tor_process.returncode != 0:
                stderr = self.tor_process.stderr.read()
                log_message(f"tornet ended with error: {stderr}", "ERROR")
            else:
                log_message("tornet process ended normally")
            
            self.is_running = False
            
        except Exception as e:
            log_message(f"Error monitoring tornet: {e}", "ERROR")
            self.is_running = False
    
    def get_tor_ip(self) -> Optional[str]:
        """Get current IP through TOR network."""
        try:
            # Use TOR SOCKS proxy to get IP
            proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
            
            response = requests.get(
                'https://api.ipify.org',
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            log_message(f"Failed to get TOR IP: {e}", "ERROR")
            return None
    
    def start_full_tor(self) -> Tuple[bool, str]:
        """Start complete TOR setup (service + IP rotation)."""
        # Start TOR service
        success, message = self.start_tor_service()
        if not success:
            return False, message
        
        # Wait for service to be ready
        time.sleep(8)
        
        # Verify TOR status before starting rotation
        (is_enabled, is_running), status_msg = self.check_tor_service_status()
        log_message(f"TOR verification before rotation: {status_msg}")
        
        if not is_running:
            return False, f"TOR service verification failed: {status_msg}"
        
        # Start IP rotation using tornet
        success, message = self.start_ip_rotation()
        if not success:
            return False, f"TOR service started but rotation failed: {message}"
        
        return True, "TOR service and IP rotation started with tornet"
    
    def stop_full_tor(self) -> Tuple[bool, str]:
        """Stop complete TOR setup (rotation + service)."""
        # Stop IP rotation first
        self.stop_ip_rotation()
        
        # Stop TOR service
        success, message = self.stop_tor_service()
        return success, message
    
    def get_status(self) -> dict:
        """Get detailed TOR status."""
        status = {
            'tor_service_running': False,
            'ip_rotation_active': self.is_running,
            'controller_connected': self.controller is not None,
            'current_tor_ip': None
        }
        
        # Check if TOR service is running
        success, output, _ = run_command(['pgrep', 'tor'])
        status['tor_service_running'] = success and bool(output)
        
        # Get current TOR IP if possible
        if status['tor_service_running']:
            status['current_tor_ip'] = self.get_tor_ip()
        
        return status


# Test function
if __name__ == "__main__":
    tor_manager = TORManager()
    
    # Test TOR availability
    if tor_manager.is_tor_available():
        print("✅ TOR is available")
    else:
        print("❌ TOR is not installed")
    
    if STEM_AVAILABLE:
        print("✅ stem library is available")
    else:
        print("❌ stem library is not available")
    
    # Test status
    status = tor_manager.get_status()
    print(f"Status: {status}")
