#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Ghosty - Linux Anonymizer Tool
Main entry point that handles root privileges and launches the GUI.
"""

import sys
import os
from utils import check_root, request_root, log_message


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    # Check system tools
    system_tools = ['macchanger', 'openvpn', 'tor']
    for tool in system_tools:
        if os.system(f"which {tool} > /dev/null 2>&1") != 0:
            missing_deps.append(f"System tool: {tool}")
    
    # Check Python modules
    python_modules = [
        ('requests', 'requests'),
        ('psutil', 'psutil'),
        ('stem', 'stem')
    ]
    
    for module_name, import_name in python_modules:
        try:
            __import__(import_name)
        except ImportError:
            missing_deps.append(f"Python module: {module_name}")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📦 To install missing dependencies:")
        print("   System tools: sudo apt install macchanger openvpn tor")
        print("   Python modules: pip3 install -r requirements.txt")
        return False
    
    return True


def main():
    """Main function."""
    print("👻 Ghosty - Linux Anonymizer")
    print("=" * 40)
    
    # Check if running on Linux
    if sys.platform != 'linux':
        print("❌ Ghosty is designed for Linux systems only.")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n💡 Install missing dependencies and try again.")
        sys.exit(1)
    
    print("✅ All dependencies available")
    
    # Check for root privileges
    if not check_root():
        print("🔐 Root privileges required for network modifications.")
        print("🔄 Attempting to elevate privileges...")
        request_root()
    
    print("✅ Running with root privileges")
    
    # Import and launch GUI
    try:
        from gui import main as gui_main
        print("🚀 Launching Ghosty GUI...")
        gui_main()
        
    except KeyboardInterrupt:
        print("\n👋 Ghosty shutdown by user")
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
