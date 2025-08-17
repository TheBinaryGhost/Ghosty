#!/bin/bash
# Ghosty Linux Anonymizer - Installation Script
# This script sets up Ghosty for direct execution in Linux

set -e  # Exit on any error

echo "👻 Ghosty Linux Anonymizer - Installation Script"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Please do not run this script as root. It will ask for sudo when needed."
   exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/ghosty"
DESKTOP_FILE="/usr/share/applications/ghosty.desktop"
ICON_FILE="/usr/share/pixmaps/ghosty.png"
EXECUTABLE="/usr/local/bin/ghosty"

print_step "1. Checking system requirements..."

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This installer is for Linux systems only."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

print_step "2. Installing system dependencies..."

# Update package list
sudo apt update

# Install required system packages
PACKAGES="macchanger openvpn tor python3-pip python3-tk"
print_status "Installing packages: $PACKAGES"
sudo apt install -y $PACKAGES

# Check if tornet is available
if ! command -v tornet &> /dev/null; then
    print_warning "tornet command not found. Installing alternatives..."
    # Install tor-geoipdb and other tor tools
    sudo apt install -y tor-geoipdb
fi

print_step "3. Installing Python dependencies..."

# Install Python packages
pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

print_step "4. Setting up Ghosty installation..."

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"

# Copy essential Python files to installation directory
print_status "Copying Python files to $INSTALL_DIR"
sudo cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/gui.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/macchanger.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/vpn.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/tor.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/utils.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Copy additional files if they exist
if [[ -f "$SCRIPT_DIR/README.md" ]]; then
    sudo cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/"
fi

if [[ -f "$SCRIPT_DIR/LICENSE" ]]; then
    sudo cp "$SCRIPT_DIR/LICENSE" "$INSTALL_DIR/"
fi

# Make Python files executable
sudo chmod +x "$INSTALL_DIR/main.py"
sudo chmod +x "$INSTALL_DIR"/*.py

print_step "5. Creating desktop launcher..."

# Create desktop entry
sudo tee "$DESKTOP_FILE" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ghosty Anonymizer
Comment=Linux system anonymization tool with MAC spoofing, VPN, and TOR
Exec=pkexec python3 $INSTALL_DIR/main.py
Icon=ghosty
Terminal=false
StartupNotify=true
Categories=Network;Security;
Keywords=anonymizer;privacy;tor;vpn;mac;security;
StartupWMClass=ghosty
EOF

print_step "6. Creating application icon..."

# Create a simple icon (you can replace this with a proper icon file)
sudo tee "$ICON_FILE" > /dev/null << 'EOF'
# This is a placeholder. Replace with actual PNG icon data
# For now, we'll create a simple script to generate an icon
EOF

# Create a simple icon using ImageMagick if available
if command -v convert &> /dev/null; then
    sudo convert -size 48x48 xc:black -fill white -pointsize 24 -gravity center -annotate +0+0 "👻" "$ICON_FILE" 2>/dev/null || true
fi

print_step "7. Creating command-line executable..."

# Create executable script
sudo tee "$EXECUTABLE" > /dev/null << EOF
#!/bin/bash
# Ghosty Linux Anonymizer Launcher
cd "$INSTALL_DIR"
exec python3 main.py "\$@"
EOF

sudo chmod +x "$EXECUTABLE"

print_step "8. Setting up permissions..."

# Set proper permissions
sudo chown -R root:root "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    sudo update-desktop-database /usr/share/applications/
fi

print_step "9. Final setup..."

# Create uninstall script
sudo tee "$INSTALL_DIR/uninstall.sh" > /dev/null << EOF
#!/bin/bash
echo "Uninstalling Ghosty..."
sudo rm -rf "$INSTALL_DIR"
sudo rm -f "$DESKTOP_FILE"
sudo rm -f "$ICON_FILE"
sudo rm -f "$EXECUTABLE"
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true
echo "Ghosty has been uninstalled."
EOF

sudo chmod +x "$INSTALL_DIR/uninstall.sh"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 How to run Ghosty:"
echo "   1. GUI Application: Search for 'Ghosty Anonymizer' in your applications menu"
echo "   2. Command line: Type 'ghosty' in terminal"
echo "   3. Direct execution: Run 'python3 $INSTALL_DIR/main.py'"
echo ""
echo "📁 Installation location: $INSTALL_DIR"
echo "🗑️  To uninstall: sudo $INSTALL_DIR/uninstall.sh"
echo ""
echo "⚠️  Important notes:"
echo "   - Ghosty requires root privileges to modify network settings"
echo "   - The application will ask for your password when needed"
echo "   - Make sure to have VPN config files ready for Standard/Enhanced modes"
echo ""
print_status "Ghosty is now ready to use!"
