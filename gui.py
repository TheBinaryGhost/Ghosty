#!/usr/bin/env python3
"""
Ghosty GUI Module
Main graphical user interface using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
from typing import Optional

from utils import get_current_ip, get_network_interfaces, get_interface_mac, log_message
from macchanger import MACChanger
from vpn import VPNManager
from tor import TORManager


class GhostyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("👻 Ghosty - Linux Anonymizer")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize managers
        self.mac_changer = MACChanger()
        self.vpn_manager = VPNManager()
        self.tor_manager = TORManager()
        
        # State variables
        self.current_mode = tk.StringVar(value="Normal")
        self.selected_interface = tk.StringVar()
        self.current_ip = tk.StringVar(value="Fetching...")
        self.current_mac = tk.StringVar(value="Fetching...")
        self.status = tk.StringVar(value="Ready")
        self.vpn_config_path = tk.StringVar(value="No file selected")
        self.vpn_auth_path = tk.StringVar(value="No file selected")
        
        # Operation state
        self.is_running = False
        self.ip_update_thread = None
        
        self.create_gui()
        self.start_ip_monitoring()
        
    def create_gui(self):
        """Create the main GUI layout."""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="👻 Ghosty - Linux Anonymizer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Current status section
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Current IP:").grid(row=0, column=0, sticky=tk.W)
        ip_label = ttk.Label(status_frame, textvariable=self.current_ip, 
                            font=("Courier", 10))
        ip_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Current MAC:").grid(row=1, column=0, sticky=tk.W)
        mac_label = ttk.Label(status_frame, textvariable=self.current_mac,
                             font=("Courier", 10))
        mac_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Status:").grid(row=2, column=0, sticky=tk.W)
        status_label = ttk.Label(status_frame, textvariable=self.status,
                                font=("Arial", 10, "bold"))
        status_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Network interface selection
        interface_frame = ttk.LabelFrame(main_frame, text="Network Interface", padding="10")
        interface_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        interface_frame.columnconfigure(1, weight=1)
        
        ttk.Label(interface_frame, text="Select Interface:").grid(row=0, column=0, sticky=tk.W)
        interface_combo = ttk.Combobox(interface_frame, textvariable=self.selected_interface,
                                      values=get_network_interfaces(), state="readonly")
        interface_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        interface_combo.bind('<<ComboboxSelected>>', self.on_interface_changed)
        if interface_combo['values']:
            interface_combo.current(0)
            self.on_interface_changed(None)  # Update MAC for initial selection
        
        refresh_btn = ttk.Button(interface_frame, text="Refresh", 
                                command=self.refresh_interfaces)
        refresh_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Anonymity Mode", padding="10")
        mode_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        modes = [
            ("Normal", "Change MAC address only"),
            ("Standard", "Change MAC + Connect to VPN"),
            ("Enhanced", "Change MAC + VPN + TOR with IP rotation")
        ]
        
        for i, (mode, description) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=f"{mode}: {description}", 
                           variable=self.current_mode, value=mode).grid(
                           row=i, column=0, sticky=tk.W, pady=2)
        
        # VPN configuration
        vpn_frame = ttk.LabelFrame(main_frame, text="VPN Configuration", padding="10")
        vpn_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        vpn_frame.columnconfigure(1, weight=1)
        
        # Config file selection
        ttk.Label(vpn_frame, text="Config File:").grid(row=0, column=0, sticky=tk.W)
        config_label = ttk.Label(vpn_frame, textvariable=self.vpn_config_path,
                                relief="sunken", width=40)
        config_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(vpn_frame, text="Browse", 
                  command=self.browse_vpn_config).grid(row=0, column=2)
        
        # Auth file selection
        ttk.Label(vpn_frame, text="Auth File:").grid(row=1, column=0, sticky=tk.W)
        auth_label = ttk.Label(vpn_frame, textvariable=self.vpn_auth_path,
                              relief="sunken", width=40)
        auth_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(vpn_frame, text="Browse", 
                  command=self.browse_vpn_auth).grid(row=1, column=2)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.start_btn = ttk.Button(control_frame, text="🚀 START", 
                                   command=self.start_anonymization,
                                   style="Accent.TButton")
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="🛑 STOP", 
                                  command=self.stop_anonymization,
                                  state="disabled")
        self.stop_btn.grid(row=0, column=1)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add initial log message
        self.log("Ghosty initialized. Select interface and mode, then click START.")
    
    def on_interface_changed(self, event):
        """Handle interface selection change."""
        interface = self.selected_interface.get()
        if interface:
            threading.Thread(target=self.update_mac_for_interface, args=(interface,), daemon=True).start()
    
    def update_mac_for_interface(self, interface):
        """Update MAC address display for selected interface."""
        try:
            mac = get_interface_mac(interface)
            self.current_mac.set(mac)
        except:
            self.current_mac.set("Unknown")
        
    def refresh_interfaces(self):
        """Refresh the list of network interfaces."""
        interfaces = get_network_interfaces()
        interface_combo = None
        
        # Find the combobox widget
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and "Network Interface" in str(child.cget("text")):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Combobox):
                                interface_combo = grandchild
                                break
        
        if interface_combo:
            interface_combo['values'] = interfaces
            if interfaces and not self.selected_interface.get():
                interface_combo.current(0)
        
        self.log(f"Refreshed interfaces: {', '.join(interfaces)}")
    
    def browse_vpn_config(self):
        """Browse for VPN configuration file."""
        filename = filedialog.askopenfilename(
            title="Select VPN Configuration File",
            filetypes=[("OpenVPN files", "*.ovpn"), ("All files", "*.*")]
        )
        if filename:
            self.vpn_config_path.set(filename)
            self.log(f"Selected VPN config: {filename}")
    
    def browse_vpn_auth(self):
        """Browse for VPN authentication file."""
        filename = filedialog.askopenfilename(
            title="Select VPN Authentication File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.vpn_auth_path.set(filename)
            self.log(f"Selected VPN auth: {filename}")
    
    def log(self, message: str):
        """Add message to the log area."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_ip_monitoring(self):
        """Start monitoring IP and MAC address in background."""
        def update_info():
            while True:
                try:
                    # Update IP
                    ip = get_current_ip()
                    self.current_ip.set(ip)
                    
                    # Update MAC for current interface
                    interface = self.selected_interface.get()
                    if interface:
                        mac = get_interface_mac(interface)
                        self.current_mac.set(mac)
                except:
                    pass
                time.sleep(10)  # Update every 10 seconds
        
        self.ip_update_thread = threading.Thread(target=update_info, daemon=True)
        self.ip_update_thread.start()
    
    def start_anonymization(self):
        """Start the anonymization process based on selected mode."""
        if self.is_running:
            return
        
        interface = self.selected_interface.get()
        if not interface:
            messagebox.showerror("Error", "Please select a network interface")
            return
        
        mode = self.current_mode.get()
        self.log(f"Starting {mode} mode anonymization...")
        
        # Disable start button, enable stop button
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.is_running = True
        self.status.set(f"Running ({mode})")
        
        # Run anonymization in separate thread
        thread = threading.Thread(target=self._run_anonymization, args=(mode, interface))
        thread.daemon = True
        thread.start()
    
    def _run_anonymization(self, mode: str, interface: str):
        """Run anonymization process in background thread."""
        try:
            # Step 1: Change MAC address (all modes)
            self.log("Step 1: Changing MAC address...")
            success, message = self.mac_changer.change_mac(interface)
            if success:
                self.log(f"✅ {message}")
                # Update MAC display immediately
                threading.Thread(target=self.update_mac_for_interface, args=(interface,), daemon=True).start()
            else:
                self.log(f"❌ MAC change failed: {message}")
                self._cleanup_and_stop()
                return
            
            # Step 2: VPN connection (Standard and Enhanced modes)
            if mode in ["Standard", "Enhanced"]:
                self.log("Step 2: Connecting to VPN...")
                
                config_file = self.vpn_config_path.get()
                auth_file = self.vpn_auth_path.get() if self.vpn_auth_path.get() != "No file selected" else None
                
                if config_file == "No file selected":
                    self.log("❌ No VPN config file selected")
                    self._cleanup_and_stop()
                    return
                
                success, message = self.vpn_manager.set_config(config_file, auth_file)
                if not success:
                    self.log(f"❌ VPN config error: {message}")
                    self._cleanup_and_stop()
                    return
                
                success, message = self.vpn_manager.connect()
                if success:
                    self.log(f"✅ {message}")
                    time.sleep(8)  # Wait for VPN to establish
                else:
                    self.log(f"❌ VPN connection failed: {message}")
                    self._cleanup_and_stop()
                    return
            
            # Step 3: TOR with IP rotation (Enhanced mode only)
            if mode == "Enhanced":
                self.log("Step 3: Verifying TOR status and starting IP rotation...")
                
                # Check TOR service status first
                (is_enabled, is_running), status_msg = self.tor_manager.check_tor_service_status()
                self.log(f"TOR service status: {status_msg}")
                
                success, message = self.tor_manager.start_full_tor()
                if success:
                    self.log(f"✅ {message}")
                    self.log("🔄 IP rotation active using tornet (5 second intervals)")
                else:
                    self.log(f"❌ TOR setup failed: {message}")
                    self._cleanup_and_stop()
                    return
            
            self.log(f"🎉 {mode} mode anonymization active!")
            
        except Exception as e:
            self.log(f"❌ Unexpected error: {str(e)}")
            self._cleanup_and_stop()
    
    def stop_anonymization(self):
        """Stop the anonymization process and restore settings."""
        if not self.is_running:
            return
        
        self.log("Stopping anonymization and restoring settings...")
        
        # Run cleanup in separate thread
        thread = threading.Thread(target=self._cleanup_and_stop)
        thread.daemon = True
        thread.start()
    
    def _cleanup_and_stop(self):
        """Cleanup all services and restore original settings."""
        try:
            # Stop TOR
            if self.tor_manager.is_running:
                self.log("Stopping TOR services...")
                success, message = self.tor_manager.stop_full_tor()
                if success:
                    self.log(f"✅ {message}")
                else:
                    self.log(f"⚠️ TOR stop warning: {message}")
            
            # Disconnect VPN
            if self.vpn_manager.is_connected:
                self.log("Disconnecting VPN...")
                success, message = self.vpn_manager.disconnect()
                if success:
                    self.log(f"✅ {message}")
                else:
                    self.log(f"⚠️ VPN disconnect warning: {message}")
            
            # Restore MAC addresses
            interface = self.selected_interface.get()
            if interface:
                self.log("Restoring original MAC address...")
                success, message = self.mac_changer.restore_mac(interface)
                if success:
                    self.log(f"✅ {message}")
                    # Update MAC display immediately
                    threading.Thread(target=self.update_mac_for_interface, args=(interface,), daemon=True).start()
                else:
                    self.log(f"⚠️ MAC restore warning: {message}")
            
            self.log("🏁 Anonymization stopped, settings restored")
            
        except Exception as e:
            self.log(f"❌ Cleanup error: {str(e)}")
        
        finally:
            # Reset UI state
            self.is_running = False
            self.status.set("Ready")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the application
    app = GhostyGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down Ghosty...")
        if app.is_running:
            app.stop_anonymization()


if __name__ == "__main__":
    main()
