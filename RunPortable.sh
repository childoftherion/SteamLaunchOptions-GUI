#!/bin/bash
# RunPortable.sh - Run SteamLauncherGUI as a portable application
#
# This script creates and manages a Python virtual environment
# for running SteamLauncherGUI without system-wide installation

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
LOG_FILE="${SCRIPT_DIR}/portable_setup.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Check Python 3 installation
if ! command -v python3 &> /dev/null; then
    log "ERROR: Python 3 is required but not installed. Please install Python 3.6 or newer."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
log "Found Python $PYTHON_VERSION"

# Check for GTK libraries early
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" &> /dev/null; then
    log "ERROR: GTK libraries are required. Please install them with:"
    log "On Debian/Ubuntu: sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev"
    log "On Fedora: sudo dnf install gtk3-devel python3-gobject python3-cairo"
    log "On Arch Linux: sudo pacman -S gtk3 python-gobject"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR" --system-site-packages
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to create virtual environment. Please install python3-venv package."
        log "On Debian/Ubuntu: sudo apt-get install python3-venv"
        log "On Fedora: sudo dnf install python3-venv"
        log "On Arch Linux: sudo pacman -S python-virtualenv"
        exit 1
    fi
    log "Virtual environment created successfully."
else
    log "Using existing virtual environment."
fi

# Activate virtual environment
log "Activating virtual environment..."
source "${VENV_DIR}/bin/activate"

# Update pip and install dependencies
log "Updating pip and installing dependencies..."
"${VENV_DIR}/bin/pip" install --upgrade pip

# Filter PyGObject out of requirements.txt since we're using system packages
log "Installing Python dependencies..."
grep -v PyGObject "${SCRIPT_DIR}/requirements.txt" > "${SCRIPT_DIR}/filtered_requirements.txt"
"${VENV_DIR}/bin/pip" install -r "${SCRIPT_DIR}/filtered_requirements.txt"
rm "${SCRIPT_DIR}/filtered_requirements.txt"

# Install the application in development mode
log "Installing application in development mode..."
"${VENV_DIR}/bin/pip" install -e "${SCRIPT_DIR}"

# Run the application
log "Starting SteamLauncherGUI..."
"${VENV_DIR}/bin/python" -m steamlaunchergui.main "$@"

# Deactivate virtual environment when the application exits
deactivate

log "Application closed." 