"""
Utilities for detecting required software components.
"""

import os
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def check_software(software):
    """
    Check if the required software is installed on the system.
    
    Args:
        software: The name of the software to check
        
    Returns:
        bool: True if the software is installed, False otherwise
    """
    logger.info(f"Checking if '{software}' is installed")
    
    # Try using 'which' command for software binaries
    try:
        result = shutil.which(software)
        if result:
            logger.info(f"Software '{software}' found at: {result}")
            return True
    except Exception as e:
        logger.error(f"Error checking for software with 'which': {e}")
    
    # Try using 'dpkg' for Debian-based systems
    try:
        result = subprocess.run(
            ["dpkg", "-l", software], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        if result.returncode == 0 and "ii" in result.stdout:
            logger.info(f"Software '{software}' found via dpkg")
            return True
    except Exception as e:
        logger.debug(f"Error checking for software with dpkg: {e}")
    
    # Try using 'rpm' for RPM-based systems
    try:
        result = subprocess.run(
            ["rpm", "-q", software], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            logger.info(f"Software '{software}' found via rpm")
            return True
    except Exception as e:
        logger.debug(f"Error checking for software with rpm: {e}")
    
    # Try using 'pacman' for Arch-based systems
    try:
        result = subprocess.run(
            ["pacman", "-Q", software], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            logger.info(f"Software '{software}' found via pacman")
            return True
    except Exception as e:
        logger.debug(f"Error checking for software with pacman: {e}")
    
    logger.warning(f"Software '{software}' not found")
    return False

def detect_steam_location():
    """
    Attempt to detect the Steam installation location.
    
    Returns:
        Path or None: Path to the Steam directory if found, None otherwise
    """
    logger.info("Attempting to detect Steam installation location")
    
    # Check common Steam installation locations
    common_locations = [
        Path.home() / ".steam" / "steam",
        Path.home() / ".local" / "share" / "Steam",
        Path("/usr/share/steam"),
        Path("/opt/steam"),
        Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",  # Flatpak
    ]
    
    for location in common_locations:
        if location.exists() and location.is_dir():
            logger.info(f"Steam installation found at: {location}")
            return location
    
    # Check using the Steam process
    try:
        result = subprocess.run(
            ["pgrep", "-a", "steam"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        if result.returncode == 0 and result.stdout:
            # Parse process info to extract path
            process_info = result.stdout.strip().split("\n")[0]
            if "/" in process_info:
                path_parts = process_info.split(" ")[1:]
                for part in path_parts:
                    if "/" in part and "steam" in part.lower():
                        steam_path = Path(part).parent
                        if steam_path.exists():
                            logger.info(f"Steam installation found at: {steam_path}")
                            return steam_path
    except Exception as e:
        logger.error(f"Error detecting Steam via process: {e}")
    
    logger.warning("Could not detect Steam installation location")
    return None

def get_install_command(software):
    """
    Get the appropriate installation command for the required software.
    
    Args:
        software: The name of the software to install
        
    Returns:
        str: The installation command
    """
    # Try to detect the package manager
    package_managers = {
        "apt": "sudo apt-get install -y",
        "apt-get": "sudo apt-get install -y",
        "dnf": "sudo dnf install -y",
        "yum": "sudo yum install -y",
        "pacman": "sudo pacman -S --noconfirm",
        "zypper": "sudo zypper install -y",
        "flatpak": "flatpak install -y",
    }
    
    for pm, cmd in package_managers.items():
        if shutil.which(pm):
            logger.info(f"Detected package manager: {pm}")
            return f"{cmd} {software}"
    
    # Default to apt-get as fallback
    return f"sudo apt-get install -y {software}" 