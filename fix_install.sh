#!/bin/bash
# Quick fix script to properly install Ghosty files

echo "🔧 Ghosty Installation Fix"
echo "========================="

# Get current directory (should be the Ghosty repo)
CURRENT_DIR="$(pwd)"
INSTALL_DIR="/opt/ghosty"

# Check if we're in the Ghosty directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Error: Run this script from the Ghosty repository directory"
    echo "Make sure main.py exists in the current directory"
    exit 1
fi

echo "📁 Current directory: $CURRENT_DIR"
echo "📁 Install directory: $INSTALL_DIR"

# Create installation directory if it doesn't exist
sudo mkdir -p "$INSTALL_DIR"

echo "📋 Copying essential Python files..."

# Copy essential files
sudo cp main.py "$INSTALL_DIR/"
sudo cp gui.py "$INSTALL_DIR/"
sudo cp macchanger.py "$INSTALL_DIR/"
sudo cp vpn.py "$INSTALL_DIR/"
sudo cp tor.py "$INSTALL_DIR/"
sudo cp utils.py "$INSTALL_DIR/"
sudo cp requirements.txt "$INSTALL_DIR/"

# Copy optional files if they exist
if [[ -f "README.md" ]]; then
    sudo cp README.md "$INSTALL_DIR/"
fi

if [[ -f "LICENSE" ]]; then
    sudo cp LICENSE "$INSTALL_DIR/"
fi

echo "🔐 Setting permissions..."

# Set proper permissions
sudo chmod +x "$INSTALL_DIR"/*.py
sudo chown -R root:root "$INSTALL_DIR"
sudo chmod -R 755 "$INSTALL_DIR"

echo "🗑️ Creating uninstall script..."

# Create uninstall script
sudo tee "$INSTALL_DIR/uninstall.sh" > /dev/null << EOF
#!/bin/bash
echo "Uninstalling Ghosty..."
sudo rm -rf "$INSTALL_DIR"
sudo rm -f "/usr/share/applications/ghosty.desktop"
sudo rm -f "/usr/local/bin/ghosty"
sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true
echo "Ghosty has been uninstalled."
EOF

sudo chmod +x "$INSTALL_DIR/uninstall.sh"

echo ""
echo "✅ Installation fix completed!"
echo ""
echo "📋 Files now in $INSTALL_DIR:"
ls -la "$INSTALL_DIR"
echo ""
echo "🚀 Try launching Ghosty from applications menu or run:"
echo "   ghosty"
echo "   python3 $INSTALL_DIR/main.py"
