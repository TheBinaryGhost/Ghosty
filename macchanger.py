#!/usr/bin/env python3
"""
Ghosty MAC Address Changer Module
Handles MAC address modification and restoration using macchanger.
"""

import subprocess
import re
from typing import Optional, Tuple, List
from utils import run_command, log_message


class MACChanger:
    def __init__(self):
        self.original_macs = {}  # Store original MAC addresses
        
    def get_current_mac(self, interface: str) -> Optional[str]:
        """Get the current MAC address of an interface."""
        try:
            with open(f'/sys/class/net/{interface}/address', 'r') as f:
                return f.read().strip()
        except Exception as e:
            log_message(f"Failed to get MAC for {interface}: {e}", "ERROR")
            return None
    
    def is_macchanger_available(self) -> bool:
        """Check if macchanger is installed."""
        success, _, _ = run_command(['which', 'macchanger'])
        return success
    
    def change_mac(self, interface: str, new_mac: Optional[str] = None) -> Tuple[bool, str]:
        """
        Change MAC address of an interface.
        
        Args:
            interface: Network interface name
            new_mac: Specific MAC address (if None, uses random)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_macchanger_available():
            return False, "macchanger is not installed. Install with: sudo apt install macchanger"
        
        # Store original MAC before changing
        if interface not in self.original_macs:
            original_mac = self.get_current_mac(interface)
            if original_mac:
                self.original_macs[interface] = original_mac
        
        try:
            # Bring interface down
            success, _, error = run_command(['ip', 'link', 'set', interface, 'down'])
            if not success:
                return False, f"Failed to bring {interface} down: {error}"
            
            # Change MAC address
            if new_mac:
                cmd = ['macchanger', '-m', new_mac, interface]
            else:
                cmd = ['macchanger', '-r', interface]  # Random MAC
            
            success, output, error = run_command(cmd)
            if not success:
                # Try to bring interface back up even if MAC change failed
                run_command(['ip', 'link', 'set', interface, 'up'])
                return False, f"Failed to change MAC: {error}"
            
            # Bring interface back up
            success, _, error = run_command(['ip', 'link', 'set', interface, 'up'])
            if not success:
                return False, f"Failed to bring {interface} up: {error}"
            
            # Extract new MAC from output
            new_mac_match = re.search(r'Current MAC:\s+([a-fA-F0-9:]{17})', output)
            if new_mac_match:
                new_mac_addr = new_mac_match.group(1)
                log_message(f"MAC changed for {interface}: {new_mac_addr}")
                return True, f"MAC address changed to {new_mac_addr}"
            else:
                return True, "MAC address changed successfully"
                
        except Exception as e:
            # Ensure interface is brought back up
            run_command(['ip', 'link', 'set', interface, 'up'])
            return False, f"Unexpected error: {str(e)}"
    
    def restore_mac(self, interface: str) -> Tuple[bool, str]:
        """
        Restore original MAC address of an interface.
        
        Args:
            interface: Network interface name
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if interface not in self.original_macs:
            return False, f"No original MAC stored for {interface}"
        
        original_mac = self.original_macs[interface]
        
        try:
            # Bring interface down
            success, _, error = run_command(['ip', 'link', 'set', interface, 'down'])
            if not success:
                return False, f"Failed to bring {interface} down: {error}"
            
            # Restore original MAC
            success, output, error = run_command(['macchanger', '-m', original_mac, interface])
            if not success:
                run_command(['ip', 'link', 'set', interface, 'up'])
                return False, f"Failed to restore MAC: {error}"
            
            # Bring interface back up
            success, _, error = run_command(['ip', 'link', 'set', interface, 'up'])
            if not success:
                return False, f"Failed to bring {interface} up: {error}"
            
            log_message(f"MAC restored for {interface}: {original_mac}")
            return True, f"MAC address restored to {original_mac}"
            
        except Exception as e:
            run_command(['ip', 'link', 'set', interface, 'up'])
            return False, f"Unexpected error: {str(e)}"
    
    def restore_all_macs(self) -> List[Tuple[str, bool, str]]:
        """Restore all stored original MAC addresses."""
        results = []
        for interface in self.original_macs.keys():
            success, message = self.restore_mac(interface)
            results.append((interface, success, message))
        return results


# Test function
if __name__ == "__main__":
    mac_changer = MACChanger()
    
    # Test getting current MAC
    interfaces = ['eth0', 'wlan0', 'enp0s3']  # Common interface names
    for iface in interfaces:
        mac = mac_changer.get_current_mac(iface)
        if mac:
            print(f"{iface}: {mac}")
            break
