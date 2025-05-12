"""
Profiles management for SteamLauncherGUI.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from steamlaunchergui.models.launch_options import LaunchOptions

logger = logging.getLogger(__name__)

class Profile:
    """
    A configuration profile for launch options.
    """
    
    def __init__(self, name: str, description: str = "", launch_options: Optional[LaunchOptions] = None):
        """
        Initialize a profile.
        
        Args:
            name: Profile name
            description: Profile description
            launch_options: Launch options object or None to create new
        """
        self.name = name
        self.description = description
        self.created_at = time.time()
        self.updated_at = time.time()
        self.launch_options = launch_options or LaunchOptions()
    
    def update(self, launch_options: LaunchOptions) -> None:
        """
        Update the profile with new launch options.
        
        Args:
            launch_options: New launch options
        """
        self.launch_options = launch_options
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert profile to dictionary for storage.
        
        Returns:
            Dict: Dictionary representation of the profile
        """
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'launch_options': self.launch_options.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """
        Create a profile from dictionary data.
        
        Args:
            data: Dictionary with profile data
            
        Returns:
            Profile: New profile instance
        """
        profile = cls(
            name=data.get('name', 'Unnamed Profile'),
            description=data.get('description', '')
        )
        profile.created_at = data.get('created_at', time.time())
        profile.updated_at = data.get('updated_at', time.time())
        
        launch_options = LaunchOptions()
        if 'launch_options' in data:
            launch_options.from_dict(data['launch_options'])
        profile.launch_options = launch_options
        
        return profile


class ProfileManager:
    """
    Manager for configuration profiles.
    """
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        Initialize the profile manager.
        
        Args:
            profiles_dir: Directory to store profiles, or None for default
        """
        if profiles_dir is None:
            # Default to a directory in the user's home
            profiles_dir = Path.home() / ".config" / "steamlaunchergui" / "profiles"
        
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, Profile] = {}
        
        # Create the profiles directory if it doesn't exist
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Load existing profiles
        self.load_profiles()
    
    def load_profiles(self) -> None:
        """Load all profiles from the profiles directory."""
        self.profiles.clear()
        
        try:
            for profile_file in self.profiles_dir.glob("*.json"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = Profile.from_dict(data)
                        self.profiles[profile.name] = profile
                except Exception as e:
                    logger.error(f"Error loading profile from {profile_file}: {e}")
        except Exception as e:
            logger.error(f"Error accessing profiles directory: {e}")
    
    def save_profile(self, profile: Profile) -> bool:
        """
        Save a profile to disk.
        
        Args:
            profile: Profile to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        filename = self._safe_filename(profile.name) + ".json"
        filepath = self.profiles_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)
            
            # Update our in-memory cache
            self.profiles[profile.name] = profile
            return True
        except Exception as e:
            logger.error(f"Error saving profile to {filepath}: {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            name: Name of the profile to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name not in self.profiles:
            logger.warning(f"Profile not found: {name}")
            return False
        
        filename = self._safe_filename(name) + ".json"
        filepath = self.profiles_dir / filename
        
        try:
            if filepath.exists():
                os.remove(filepath)
            
            # Remove from our in-memory cache
            del self.profiles[name]
            return True
        except Exception as e:
            logger.error(f"Error deleting profile {name}: {e}")
            return False
    
    def get_profile(self, name: str) -> Optional[Profile]:
        """
        Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Profile or None: The profile if found, None otherwise
        """
        return self.profiles.get(name)
    
    def get_profiles(self) -> List[Profile]:
        """
        Get all profiles.
        
        Returns:
            List[Profile]: List of all profiles
        """
        return list(self.profiles.values())
    
    def import_profile(self, filepath: Path) -> Optional[Profile]:
        """
        Import a profile from a file.
        
        Args:
            filepath: Path to the profile file
            
        Returns:
            Profile or None: The imported profile if successful, None otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profile = Profile.from_dict(data)
                
                # Ensure the name is unique
                if profile.name in self.profiles:
                    original_name = profile.name
                    profile.name = f"{original_name} (Imported {int(time.time())})"
                    logger.info(f"Renamed imported profile from '{original_name}' to '{profile.name}'")
                
                # Save the imported profile
                self.save_profile(profile)
                return profile
        except Exception as e:
            logger.error(f"Error importing profile from {filepath}: {e}")
            return None
    
    def export_profile(self, name: str, filepath: Path) -> bool:
        """
        Export a profile to a file.
        
        Args:
            name: Name of the profile to export
            filepath: Path to save the profile to
            
        Returns:
            bool: True if successful, False otherwise
        """
        profile = self.get_profile(name)
        if profile is None:
            logger.warning(f"Profile not found: {name}")
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting profile to {filepath}: {e}")
            return False
    
    def _safe_filename(self, name: str) -> str:
        """
        Convert a profile name to a safe filename.
        
        Args:
            name: Profile name
            
        Returns:
            str: Safe filename
        """
        # Replace invalid filename characters
        safe_name = "".join(c if c.isalnum() or c in "_- " else "_" for c in name)
        return safe_name 