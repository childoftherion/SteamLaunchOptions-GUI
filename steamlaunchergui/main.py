#!/usr/bin/env python3
"""
Main entry point for SteamLauncherGUI application.
"""

import sys
import os
import logging
import argparse
import traceback
from pathlib import Path

import gi
try:
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
except ValueError as e:
    print(f"Error importing GTK 3.0: {e}")
    print("Please ensure you have the GTK 3.0 development libraries installed.")
    print("On Debian/Ubuntu: sudo apt-get install libgtk-3-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0")
    print("On Fedora: sudo dnf install gtk3-devel python3-gobject python3-cairo")
    print("On Arch Linux: sudo pacman -S gtk3 python-gobject")
    sys.exit(1)

from steamlaunchergui import __version__
from steamlaunchergui.utils.logging import setup_logging
from steamlaunchergui.ui import SteamLauncherWindow

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Steam Launch Options GUI')
    parser.add_argument('--version', action='version', version=f'SteamLauncherGUI {__version__}')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--log-file', help='Path to log file')
    parser.add_argument('--no-log-file', action='store_true', help='Disable logging to file')
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    print("Starting Steam Launcher GUI...")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    # Default log file is in user's home directory if not specified
    if args.no_log_file:
        log_file = None
    elif args.log_file:
        log_file = args.log_file
    else:
        # Put logs in ~/.config/steamlaunchergui/
        config_dir = os.path.join(Path.home(), '.config', 'steamlaunchergui')
        os.makedirs(config_dir, exist_ok=True)
        log_file = os.path.join(config_dir, 'steam_launcher.log')
    
    try:
        setup_logging(level=log_level, log_file=log_file)
    except Exception as e:
        print(f"Warning: Failed to set up logging: {e}")
        traceback.print_exc()
    
    # Create and display the main window
    try:
        window = SteamLauncherWindow()
        window.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Application error: {e}")
        traceback.print_exc()
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
