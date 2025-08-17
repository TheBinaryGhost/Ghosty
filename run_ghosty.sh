#!/bin/bash
# Ghosty Quick Launcher
# This script can be used to run Ghosty directly from the cloned repository

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "👻 Starting Ghosty Linux Anonymizer..."
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/main.py" ]]; then
    echo "❌ Error: main.py not found in $SCRIPT_DIR"
    echo "Make sure you're running this script from the Ghosty directory."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3: sudo apt install python3"
    exit 1
fi

# Check if running with appropriate privileges
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Warning: Running as root. This is fine for network operations."
else
    echo "🔐 Note: Ghosty will request root privileges for network modifications."
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."

# Check Python modules
MISSING_MODULES=""
for module in tkinter requests psutil; do
    if ! python3 -c "import $module" 2>/dev/null; then
        MISSING_MODULES="$MISSING_MODULES $module"
    fi
done

if [[ -n "$MISSING_MODULES" ]]; then
    echo "⚠️  Missing Python modules:$MISSING_MODULES"
    echo "Installing with pip3..."
    pip3 install --user$MISSING_MODULES
fi

# Check system tools
MISSING_TOOLS=""
for tool in macchanger openvpn tor; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [[ -n "$MISSING_TOOLS" ]]; then
    echo "⚠️  Missing system tools:$MISSING_TOOLS"
    echo "Please install them: sudo apt install$MISSING_TOOLS"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Starting Ghosty GUI..."
echo ""

# Run Ghosty
exec python3 main.py "$@"
