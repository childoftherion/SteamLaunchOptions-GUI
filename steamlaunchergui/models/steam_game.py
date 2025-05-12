"""
Steam game model for SteamLauncherGUI.
"""

import os
import logging
import json
import subprocess
import shutil
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class SteamGame:
    """
    Model class for Steam games.
    
    This class handles Steam game-related functionality and data.
    """
    
    def __init__(
        self,
        app_id: str = "",
        name: str = "",
        install_dir: str = "",
        launch_options: str = ""
    ):
        """
        Initialize a Steam game.
        
        Args:
            app_id: Steam App ID
            name: Game name
            install_dir: Installation directory
            launch_options: Current launch options
        """
        self.app_id = app_id
        self.name = name
        self.install_dir = install_dir
        self.launch_options = launch_options
        self._proton_prefix = None
        self._current_proton_version = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SteamGame':
        """
        Create a game from dictionary data.
        
        Args:
            data: Dictionary with game data
            
        Returns:
            SteamGame: New game instance
        """
        return cls(
            app_id=data.get('app_id', ''),
            name=data.get('name', ''),
            install_dir=data.get('install_dir', ''),
            launch_options=data.get('launch_options', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game to dictionary for storage.
        
        Returns:
            Dict: Dictionary representation of the game
        """
        return {
            'app_id': self.app_id,
            'name': self.name,
            'install_dir': self.install_dir,
            'launch_options': self.launch_options
        }
    
    def set_launch_options(self, options: str) -> None:
        """
        Set launch options for the game.
        
        Args:
            options: New launch options
        """
        self.launch_options = options
    
    def get_proton_prefix(self, steam_dir: Path) -> str:
        """
        Get the Proton prefix for this game.
        
        Args:
            steam_dir: Path to the Steam directory
            
        Returns:
            str: Path to the Proton prefix or empty string if not found
        """
        if self._proton_prefix:
            return self._proton_prefix
            
        # Proton prefixes are typically in steamapps/compatdata/<app_id>
        compat_data_path = steam_dir / "steamapps" / "compatdata" / self.app_id
        
        # Also check in other library locations
        if not compat_data_path.exists():
            library_folders = self._find_library_folders(steam_dir)
            for library in library_folders:
                candidate = library / "steamapps" / "compatdata" / self.app_id
                if candidate.exists():
                    compat_data_path = candidate
                    break
        
        if compat_data_path.exists():
            # The actual prefix is in the pfx directory
            prefix_path = compat_data_path / "pfx"
            if prefix_path.exists():
                self._proton_prefix = str(prefix_path)
                return self._proton_prefix
                
        # Another possible location: ~/.steam/steam/steamapps/compatdata/<app_id>
        alt_compat_path = Path.home() / ".steam" / "steam" / "steamapps" / "compatdata" / self.app_id
        if alt_compat_path.exists():
            prefix_path = alt_compat_path / "pfx"
            if prefix_path.exists():
                self._proton_prefix = str(prefix_path)
                return self._proton_prefix
        
        return ""
    
    def get_current_proton_version(self, steam_dir: Path) -> str:
        """
        Try to determine which Proton version is currently used for this game.
        
        Args:
            steam_dir: Path to the Steam directory
            
        Returns:
            str: The current Proton version or empty string if not found
        """
        if self._current_proton_version:
            return self._current_proton_version
            
        # Check in the game's compatdata directory for version info
        compat_data_path = steam_dir / "steamapps" / "compatdata" / self.app_id
        
        # Also check in other library locations
        if not compat_data_path.exists():
            library_folders = self._find_library_folders(steam_dir)
            for library in library_folders:
                candidate = library / "steamapps" / "compatdata" / self.app_id
                if candidate.exists():
                    compat_data_path = candidate
                    break
        
        if compat_data_path.exists():
            # Look for version.txt or similar files
            version_file = compat_data_path / "version"
            if version_file.exists():
                try:
                    with open(version_file, 'r') as f:
                        version = f.read().strip()
                        if version:
                            self._current_proton_version = version
                            return version
                except Exception as e:
                    logger.error(f"Error reading version file: {e}")
            
            # If no version file, check the launch options for PROTON_VERSION or similar
            if self.launch_options:
                proton_match = re.search(r'PROTON_VERSION=([^\s]+)', self.launch_options)
                if proton_match:
                    self._current_proton_version = proton_match.group(1)
                    return self._current_proton_version
                
                # Check for direct proton path in launch options
                proton_path_match = re.search(r'Proton[^\s/]*', self.launch_options)
                if proton_path_match:
                    self._current_proton_version = proton_path_match.group(0)
                    return self._current_proton_version
        
        # If we still don't have a version, default to the global Steam Play setting
        # This would require parsing the Steam config files
        return ""
    
    def launch_with_proton(self, proton_version: str, steam_dir: Path, env_vars: Dict[str, str] = None) -> bool:
        """
        Launch the game with a specific Proton version without using Steam.
        
        Args:
            proton_version: The Proton version to use (e.g., "Proton 7.0")
            steam_dir: Path to the Steam directory
            env_vars: Additional environment variables to set
            
        Returns:
            bool: True if launched successfully, False otherwise
        """
        if not self.install_dir or not os.path.exists(self.install_dir):
            logger.error(f"Game installation directory not found: {self.install_dir}")
            return False
        
        # Find the game's main executable
        main_exe = self._find_game_executable()
        if not main_exe:
            logger.error(f"Could not find main executable for {self.name}")
            return False
        
        # Find the specified Proton version
        proton_path = self._find_proton_path(proton_version, steam_dir)
        if not proton_path:
            logger.error(f"Could not find Proton version: {proton_version}")
            return False
        
        # Set up the Proton environment
        proton_prefix = self.get_proton_prefix(steam_dir)
        if not proton_prefix:
            # If no existing prefix, create one
            proton_prefix = str(steam_dir / "steamapps" / "compatdata" / self.app_id / "pfx")
            os.makedirs(proton_prefix, exist_ok=True)
        
        # Set up environment variables
        launch_env = os.environ.copy()
        launch_env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(proton_prefix)
        launch_env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = str(steam_dir)
        
        # Add user-specified environment variables
        if env_vars:
            for key, value in env_vars.items():
                launch_env[key] = value
        
        # Construct the command to run
        proton_run = os.path.join(proton_path, "proton")
        
        # Ensure the proton script is executable
        if os.path.exists(proton_run):
            os.chmod(proton_run, 0o755)
        
        # Build the command
        command = [proton_run, "run", main_exe]
        
        try:
            logger.info(f"Launching {self.name} with {proton_version}")
            logger.info(f"Command: {' '.join(command)}")
            
            # Launch the process
            process = subprocess.Popen(
                command,
                env=launch_env,
                cwd=self.install_dir
            )
            
            # Process is running in the background
            logger.info(f"Game launched with PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error launching game: {e}")
            return False
    
    def _find_game_executable(self) -> str:
        """
        Find the main executable for the game.
        
        Returns:
            str: Path to the executable or empty string if not found
        """
        if not self.install_dir or not os.path.exists(self.install_dir):
            return ""
        
        # Look for .exe files in the install directory
        install_path = Path(self.install_dir)
        exe_files = list(install_path.glob("*.exe"))
        
        # Try to find the main executable based on common patterns
        for pattern in ["launcher", "game", self.name.lower(), "start", "bin", "main"]:
            for exe in exe_files:
                if pattern in exe.name.lower():
                    return str(exe)
        
        # If no match found by name, use the largest .exe or the first one
        if exe_files:
            # Sort by file size (largest first)
            exe_files.sort(key=lambda x: x.stat().st_size, reverse=True)
            return str(exe_files[0])
        
        # If still not found, try looking in subdirectories
        for subdir in ["bin", "game", "launcher"]:
            subdir_path = install_path / subdir
            if subdir_path.exists():
                exe_files = list(subdir_path.glob("*.exe"))
                if exe_files:
                    exe_files.sort(key=lambda x: x.stat().st_size, reverse=True)
                    return str(exe_files[0])
        
        return ""
    
    def _find_proton_path(self, proton_version: str, steam_dir: Path) -> str:
        """
        Find the path to the specified Proton version.
        
        Args:
            proton_version: The Proton version to find
            steam_dir: Path to the Steam directory
            
        Returns:
            str: Path to the Proton directory or empty string if not found
        """
        common_dir = steam_dir / "steamapps" / "common"
        if not common_dir.exists():
            return ""
        
        # First, try exact match
        exact_match = common_dir / proton_version
        if exact_match.exists():
            return str(exact_match)
        
        # Then try a case-insensitive match
        for item in common_dir.iterdir():
            if item.is_dir() and proton_version.lower() in item.name.lower():
                return str(item)
        
        # Then try a fuzzy match for any Proton directory containing the version number
        version_number = re.search(r'[\d\.]+', proton_version)
        if version_number:
            version_str = version_number.group(0)
            for item in common_dir.iterdir():
                if item.is_dir() and "proton" in item.name.lower() and version_str in item.name:
                    return str(item)
        
        # If still not found, check in other library folders
        library_folders = self._find_library_folders(steam_dir)
        for library in library_folders:
            common_dir = library / "steamapps" / "common"
            if not common_dir.exists():
                continue
                
            # Try exact match
            exact_match = common_dir / proton_version
            if exact_match.exists():
                return str(exact_match)
            
            # Try case-insensitive match
            for item in common_dir.iterdir():
                if item.is_dir() and proton_version.lower() in item.name.lower():
                    return str(item)
            
            # Try fuzzy match
            if version_number:
                for item in common_dir.iterdir():
                    if item.is_dir() and "proton" in item.name.lower() and version_str in item.name:
                        return str(item)
        
        # Check for custom Proton-GE installations
        custom_locations = [
            # Standard location for non-flatpak
            Path.home() / ".steam" / "root" / "compatibilitytools.d",
            # Alternative location
            Path.home() / ".steam" / "steam" / "compatibilitytools.d",
            # Flatpak location
            Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam" / "compatibilitytools.d",
            # Snap location
            Path.home() / "snap" / "steam" / "common" / ".steam" / "steam" / "compatibilitytools.d",
            # Custom GE-Proton local installation
            Path.home() / ".local" / "share" / "Steam" / "compatibilitytools.d",
            # Additional common locations
            Path("/usr/share/steam/compatibilitytools.d"),
            Path("/usr/local/share/steam/compatibilitytools.d")
        ]
        
        ge_proton_patterns = [
            "GE-Proton", "proton-ge", "Proton-GE", "ge-proton",
            "proton-tkg", "wine-ge", "Wine-GE", "Proton-Experimental"
        ]
        
        for location in custom_locations:
            if location.exists():
                # Try exact match
                exact_match = location / proton_version
                if exact_match.exists():
                    return str(exact_match)
                
                # Try a case-insensitive match
                for item in location.iterdir():
                    if item.is_dir() and proton_version.lower() in item.name.lower():
                        return str(item)
                
                # Try a fuzzy match
                if version_number:
                    for item in location.iterdir():
                        if item.is_dir() and any(pattern.lower() in item.name.lower() for pattern in ge_proton_patterns) and version_str in item.name:
                            return str(item)
                
                # Check subfolders for nested structures
                for folder in location.iterdir():
                    if folder.is_dir():
                        try:
                            for item in folder.iterdir():
                                if item.is_dir() and proton_version in item.name:
                                    return str(folder / item)
                        except (PermissionError, OSError):
                            pass
        
        return ""
    
    def _find_library_folders(self, steam_dir: Path) -> List[Path]:
        """
        Find all Steam library folders.
        
        Args:
            steam_dir: Path to the Steam directory
            
        Returns:
            List[Path]: List of library folder paths
        """
        library_folders = []
        
        # Try to find additional library folders
        library_config = steam_dir / "steamapps" / "libraryfolders.vdf"
        if library_config.exists():
            # This is a simplistic parser for the libraryfolders.vdf file
            # A proper implementation would use a VDF parser
            try:
                with open(library_config, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '"path"' in line:
                            path_parts = line.split('"')
                            if len(path_parts) >= 4:
                                path = path_parts[3].replace('\\\\', '/')
                                library_path = Path(path)
                                if library_path.exists() and library_path not in library_folders:
                                    library_folders.append(library_path)
            except Exception as e:
                logger.error(f"Error parsing libraryfolders.vdf: {e}")
        
        return library_folders

    @staticmethod
    def find_steam_games(steam_dir: Path) -> List['SteamGame']:
        """
        Find installed Steam games.
        
        Args:
            steam_dir: Path to the Steam directory
            
        Returns:
            List[SteamGame]: List of found Steam games
        """
        games = []
        library_folders = []
        
        # Add the default Steam library
        library_folders.append(steam_dir / "steamapps")
        
        # Try to find additional library folders
        library_config = steam_dir / "steamapps" / "libraryfolders.vdf"
        if library_config.exists():
            # This is a simplistic parser for the libraryfolders.vdf file
            # A proper implementation would use a VDF parser
            try:
                with open(library_config, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '"path"' in line:
                            path_parts = line.split('"')
                            if len(path_parts) >= 4:
                                path = path_parts[3].replace('\\\\', '/')
                                library_path = Path(path) / "steamapps"
                                if library_path.exists() and library_path not in library_folders:
                                    library_folders.append(library_path)
            except Exception as e:
                logger.error(f"Error parsing libraryfolders.vdf: {e}")
        
        # Process all library folders
        for library in library_folders:
            try:
                # Look for appmanifest_*.acf files
                for manifest_file in library.glob("appmanifest_*.acf"):
                    try:
                        # Extract app_id from filename
                        app_id = manifest_file.stem.split('_')[1]
                        
                        # Parse the manifest file
                        game_data = SteamGame._parse_appmanifest(manifest_file)
                        
                        if not game_data:
                            continue
                        
                        # Use app_id from the manifest file if available, otherwise use from filename
                        app_id = game_data.get('app_id', app_id) or game_data.get('appid', app_id) or app_id
                        
                        # Create the game object
                        game = SteamGame(
                            app_id=str(app_id),  # Ensure app_id is a string
                            name=game_data.get('name', f"Unknown Game ({app_id})"),
                            install_dir=str(library / "common" / game_data.get('installdir', '')),
                            launch_options=""
                        )
                        
                        # Log the created game for debugging
                        logger.debug(f"Found game: {game.name} (App ID: {game.app_id})")
                        
                        games.append(game)
                    except Exception as e:
                        logger.error(f"Error processing manifest file {manifest_file}: {e}")
            except Exception as e:
                logger.error(f"Error accessing library folder {library}: {e}")
        
        # Try to load launch options
        SteamGame._load_launch_options(steam_dir, games)
        
        return games
    
    @staticmethod
    def _parse_appmanifest(manifest_file: Path) -> Dict[str, str]:
        """
        Parse a Steam appmanifest file.
        
        Args:
            manifest_file: Path to the manifest file
            
        Returns:
            Dict: Parsed game data
        """
        game_data = {}
        try:
            # First, extract the app_id from the filename
            filename = manifest_file.stem
            if filename.startswith("appmanifest_"):
                app_id_from_filename = filename.split('_')[1]
                game_data['app_id'] = app_id_from_filename
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Look for name, installdir, and app id in the file
                    if '"name"' in line or '"installdir"' in line or '"appid"' in line:
                        parts = line.split('"')
                        if len(parts) >= 4:
                            key = parts[1].lower()
                            value = parts[3]
                            game_data[key] = value
        except Exception as e:
            logger.error(f"Error reading appmanifest file {manifest_file}: {e}")
        
        return game_data
    
    @staticmethod
    def _load_launch_options(steam_dir: Path, games: List['SteamGame']) -> None:
        """
        Load launch options for games.
        
        Args:
            steam_dir: Steam directory
            games: List of games to populate with launch options
        """
        # Map games by app_id for easy lookup, ensuring keys are strings
        games_by_id = {str(game.app_id): game for game in games}
        
        # Log number of games for debugging
        logger.debug(f"Loading launch options for {len(games)} games")
        
        # Look for the localconfig.vdf file
        config_dirs = [
            steam_dir / "userdata",
            Path.home() / ".local" / "share" / "Steam" / "userdata"
        ]
        
        for config_dir in config_dirs:
            if not config_dir.exists():
                logger.debug(f"Config directory not found: {config_dir}")
                continue
                
            # Look in each user's directory
            for user_dir in config_dir.iterdir():
                if not user_dir.is_dir():
                    continue
                    
                config_file = user_dir / "config" / "localconfig.vdf"
                if not config_file.exists():
                    logger.debug(f"Config file not found: {config_file}")
                    continue
                
                logger.debug(f"Processing config file: {config_file}")
                try:
                    # Simple parse of the VDF file to find launch options
                    # A proper implementation would use a VDF parser
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for app_id in games_by_id.keys():
                            # Look for the app section with different spacing variations
                            app_sections = [
                                f'"appid"		"{app_id}"',  # Double tab
                                f'"appid"	"{app_id}"',      # Single tab
                                f'"appid" "{app_id}"',        # Space
                                f'"appid""{app_id}"'          # No space
                            ]
                            
                            found = False
                            for app_section in app_sections:
                                if app_section in content:
                                    found = True
                                    app_section_pos = content.find(app_section)
                                    
                                    # Find the launch options
                                    launch_marker = 'LaunchOptions"'
                                    start_pos = content.find(launch_marker, app_section_pos)
                                    
                                    if start_pos != -1:
                                        start_pos = content.find('"', start_pos + len(launch_marker)) + 1
                                        end_pos = content.find('"', start_pos)
                                        
                                        if start_pos != 0 and end_pos != -1:
                                            launch_options = content[start_pos:end_pos]
                                            games_by_id[app_id].launch_options = launch_options
                                            logger.debug(f"Found launch options for app {app_id}: {launch_options}")
                                    break
                            
                            if not found:
                                logger.debug(f"No configuration found for app {app_id}")
                except Exception as e:
                    logger.error(f"Error reading config file {config_file}: {e}")
    
    @staticmethod
    def get_available_proton_versions(steam_dir: Path) -> List[str]:
        """
        Get a list of available Proton versions installed in Steam.
        
        Args:
            steam_dir: Path to the Steam directory
            
        Returns:
            List[str]: List of available Proton versions
        """
        proton_versions = []
        
        # Check in the common directory
        common_dir = steam_dir / "steamapps" / "common"
        if common_dir.exists():
            for item in common_dir.iterdir():
                if item.is_dir() and "proton" in item.name.lower():
                    proton_versions.append(item.name)
        
        # Check in other library folders
        library_folders = []
        library_config = steam_dir / "steamapps" / "libraryfolders.vdf"
        if library_config.exists():
            try:
                with open(library_config, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '"path"' in line:
                            path_parts = line.split('"')
                            if len(path_parts) >= 4:
                                path = path_parts[3].replace('\\\\', '/')
                                library_path = Path(path)
                                if library_path.exists():
                                    library_folders.append(library_path)
            except Exception as e:
                logger.error(f"Error parsing libraryfolders.vdf: {e}")
        
        for library in library_folders:
            common_dir = library / "steamapps" / "common"
            if common_dir.exists():
                for item in common_dir.iterdir():
                    if item.is_dir() and "proton" in item.name.lower():
                        if item.name not in proton_versions:
                            proton_versions.append(item.name)
        
        # Check for custom Proton-GE installations
        custom_locations = [
            # Standard location for non-flatpak
            Path.home() / ".steam" / "root" / "compatibilitytools.d",
            # Alternative location
            Path.home() / ".steam" / "steam" / "compatibilitytools.d",
            # Flatpak location
            Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam" / "compatibilitytools.d",
            # Snap location
            Path.home() / "snap" / "steam" / "common" / ".steam" / "steam" / "compatibilitytools.d",
            # Custom GE-Proton local installation
            Path.home() / ".local" / "share" / "Steam" / "compatibilitytools.d",
            # Additional common locations
            Path("/usr/share/steam/compatibilitytools.d"),
            Path("/usr/local/share/steam/compatibilitytools.d")
        ]
        
        # Patterns to match for custom Proton versions
        ge_proton_patterns = [
            "GE-Proton", "proton-ge", "Proton-GE", "ge-proton", 
            "proton-tkg", "wine-ge", "Wine-GE", "Proton-Experimental"
        ]
        
        for location in custom_locations:
            if location.exists():
                logger.debug(f"Checking custom Proton location: {location}")
                try:
                    for item in location.iterdir():
                        if item.is_dir():
                            # Check if it's a Proton-GE or other custom Proton directory
                            name_lower = item.name.lower()
                            if any(pattern.lower() in name_lower for pattern in ge_proton_patterns):
                                logger.debug(f"Found custom Proton: {item.name}")
                                if item.name not in proton_versions:
                                    proton_versions.append(item.name)
                            # Look for standard Proton directory structure with proton executable
                            elif ((item / "proton").exists() or 
                                  (item / "proton.sh").exists() or 
                                  (item / "proton_dist" / "bin" / "wine").exists()):
                                logger.debug(f"Found proton executable in: {item.name}")
                                if item.name not in proton_versions:
                                    proton_versions.append(item.name)
                            # Also check one level deeper for nested structures
                            else:
                                try:
                                    for subitem in item.iterdir():
                                        if subitem.is_dir() and (
                                            any(pattern.lower() in subitem.name.lower() for pattern in ge_proton_patterns) or
                                            (subitem / "proton").exists() or 
                                            (subitem / "proton.sh").exists()
                                        ):
                                            logger.debug(f"Found nested Proton: {item.name}/{subitem.name}")
                                            nested_path = f"{item.name}/{subitem.name}"
                                            if nested_path not in proton_versions:
                                                proton_versions.append(nested_path)
                                except (PermissionError, OSError) as e:
                                    logger.debug(f"Error accessing subdirectory: {e}")
                except (PermissionError, OSError) as e:
                    logger.debug(f"Error accessing directory {location}: {e}")
        
        # Sort by version number if possible
        def version_key(name):
            match = re.search(r'(\d+(\.\d+)+)', name)
            if match:
                return [int(x) if x.isdigit() else x for x in match.group(1).split(".")]
            return [0]
        
        proton_versions.sort(key=version_key, reverse=True)
        return proton_versions
    
    @staticmethod
    def save_launch_options(steam_dir: Path, app_id: str, options: str) -> bool:
        """
        Save launch options for a game.
        
        This is a stub that would need a proper implementation to
        actually modify Steam's configuration files.
        
        Args:
            steam_dir: Steam directory
            app_id: Steam App ID
            options: Launch options to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.warning("Saving launch options directly to Steam config is not implemented")
        logger.info(f"Would save launch options for app {app_id}: {options}")
        
        # This would need to:
        # 1. Find the appropriate localconfig.vdf file
        # 2. Parse it properly
        # 3. Modify the launch options
        # 4. Write it back
        
        # For now, just return False
        return False 