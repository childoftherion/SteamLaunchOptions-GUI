"""
Configuration manager for SteamLauncherGUI.
"""

import os
import json
import logging
from pathlib import Path
import shutil
import tempfile
import time

from .constants import SETTINGS_FILE

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration manager class for handling application settings.
    """
    
    def __init__(self, settings_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            settings_file: Optional path to the settings file
        """
        self.settings_file = settings_file or SETTINGS_FILE
        
        # Expand ~ to user's home directory
        if self.settings_file.startswith("~"):
            self.settings_file = os.path.expanduser(self.settings_file)
        
        # If path is not absolute, make it relative to home directory
        if not os.path.isabs(self.settings_file):
            self.settings_file = os.path.join(
                os.path.expanduser("~"), self.settings_file
            )
            
        self.settings = self._load_settings()
        logger.debug(f"ConfigManager initialized with settings file: {self.settings_file}")
    
    def _load_settings(self):
        """
        Load settings from the settings file.
        
        Returns:
            dict: The loaded settings or empty dict if file not found
        """
        if not os.path.exists(self.settings_file):
            logger.info(f"Settings file not found: {self.settings_file}")
            return {}
        
        try:
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
                logger.info(f"Settings loaded from: {self.settings_file}")
                return settings
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding settings file: {e}")
            
            # Backup the corrupted file
            backup_file = f"{self.settings_file}.bak.{int(time.time())}"
            try:
                shutil.copy2(self.settings_file, backup_file)
                logger.info(f"Corrupted settings file backed up to: {backup_file}")
            except Exception as e:
                logger.error(f"Failed to backup corrupted settings file: {e}")
            
            return {}
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return {}
    
    def save_settings(self, settings=None):
        """
        Save the current settings to the settings file.
        
        Args:
            settings: Optional settings to save, uses self.settings if None
            
        Returns:
            bool: True if successful, False otherwise
        """
        if settings is None:
            settings = self.settings
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.settings_file)), exist_ok=True)
        
        # Write to a temporary file first
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, dir=os.path.dirname(self.settings_file)
            ) as temp:
                temp_file = temp.name
                json.dump(settings, temp, indent=4)
            
            # Rename the temporary file to the actual settings file
            shutil.move(temp_file, self.settings_file)
            logger.info(f"Settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return False
    
    def get_setting(self, key, default=None):
        """
        Get a setting value.
        
        Args:
            key: The setting key
            default: The default value if key is not found
            
        Returns:
            The setting value or default
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """
        Set a setting value.
        
        Args:
            key: The setting key
            value: The setting value
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.settings[key] = value
        return self.save_settings()
    
    def delete_setting(self, key):
        """
        Delete a setting.
        
        Args:
            key: The setting key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if key in self.settings:
            del self.settings[key]
            return self.save_settings()
        return True
    
    def clear_settings(self):
        """
        Clear all settings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.settings = {}
        return self.save_settings()
    
    def create_backup(self, backup_dir=None):
        """
        Create a backup of the settings file.
        
        Args:
            backup_dir: Optional directory to store the backup
            
        Returns:
            str: Path to the backup file or None if failed
        """
        if not os.path.exists(self.settings_file):
            logger.warning(f"Cannot backup non-existent settings file: {self.settings_file}")
            return None
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = f"{os.path.basename(self.settings_file)}.{timestamp}.bak"
        
        if backup_dir:
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, backup_file)
        else:
            backup_path = os.path.join(os.path.dirname(self.settings_file), backup_file)
        
        try:
            shutil.copy2(self.settings_file, backup_path)
            logger.info(f"Settings backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create settings backup: {e}")
            return None 