"""
Launch options model for SteamLauncherGUI.
"""

import os
import shlex
import logging
from typing import Dict, List, Optional, Tuple, Any, Set

logger = logging.getLogger(__name__)

class LaunchOptions:
    """
    Model class for Steam launch options.
    
    This class handles the business logic for generating and parsing
    launch commands, separate from the UI layer.
    """
    
    def __init__(self):
        """Initialize an empty launch options configuration."""
        # General options
        self.general_toggles: Dict[str, bool] = {}
        self.general_inputs: Dict[str, str] = {}
        self.general_dropdowns: Dict[str, str] = {}
        
        # Tab-specific options
        self.tab_enabled: Dict[str, bool] = {}
        self.tab_toggles: Dict[str, Dict[str, bool]] = {}
        self.tab_inputs: Dict[str, Dict[str, str]] = {}
        self.tab_dropdowns: Dict[str, Dict[str, str]] = {}
        self.tab_sliders: Dict[str, Dict[str, float]] = {}
    
    def reset(self) -> None:
        """Reset all options to their default state."""
        self.general_toggles.clear()
        self.general_inputs.clear()
        self.general_dropdowns.clear()
        
        self.tab_enabled.clear()
        self.tab_toggles.clear()
        self.tab_inputs.clear()
        self.tab_dropdowns.clear()
        self.tab_sliders.clear()
    
    def generate_command(self, tab_configs: Dict[str, Any]) -> str:
        """
        Generate a Steam launch command from the current options.
        
        Args:
            tab_configs: Dictionary of tab configurations
            
        Returns:
            str: The generated launch command
        """
        command_parts = []
        env_vars = []
        
        # Process general toggles
        for flag, enabled in self.general_toggles.items():
            if enabled:
                command_parts.append(flag)
        
        # Process general inputs
        for flag, value in self.general_inputs.items():
            if value:
                command_parts.append(f"{flag} {value}")
        
        # Process general dropdowns
        for flag, value in self.general_dropdowns.items():
            if value:
                command_parts.append(f"{flag} {value}")
        
        # Process tab-specific options
        for tab_name, enabled in self.tab_enabled.items():
            if not enabled:
                continue
                
            config = tab_configs.get(tab_name, {})
            
            # Command prefix
            if "command_prefix" in config:
                command_parts.insert(0, config["command_prefix"])
            
            # Toggles
            for option, toggle_enabled in self.tab_toggles.get(tab_name, {}).items():
                if toggle_enabled:
                    if option.startswith('-'):
                        command_parts.append(option)
                    else:
                        env_vars.append(f"{option}=1")
            
            # Inputs
            for option, value in self.tab_inputs.get(tab_name, {}).items():
                if value:
                    env_vars.append(f"{option}={value}")
            
            # Dropdowns
            for key, value in self.tab_dropdowns.get(tab_name, {}).items():
                if value:
                    env_vars.append(f"{key}={value}")
            
            # Sliders
            for option, value in self.tab_sliders.get(tab_name, {}).items():
                if value != 0:
                    env_vars.append(f"{option}={value:.2f}")
            
            # Command suffix
            if "command_suffix" in config:
                command_parts.append(config["command_suffix"])
        
        # Build final command
        command = ""
        if env_vars:
            command += " ".join(env_vars) + " "
        command += " ".join(command_parts)
        if command:
            command += " %command%"
        
        return command.strip()
    
    def parse_command(self, command: str, tab_configs: Dict[str, Any]) -> None:
        """
        Parse a Steam launch command and update the model.
        
        Args:
            command: The command string to parse
            tab_configs: Dictionary of tab configurations
        """
        if not command:
            return
        
        # Reset current settings
        self.reset()
        
        # Build mappings for quick lookup
        tab_toggle_mappings = self._build_tab_toggle_mappings(tab_configs)
        tab_input_mappings = self._build_tab_input_mappings(tab_configs)
        tab_dropdown_mappings = self._build_tab_dropdown_mappings(tab_configs)
        tab_slider_mappings = self._build_tab_slider_mappings(tab_configs)
        
        try:
            # Split command, preserving quoted strings
            parts = shlex.split(command.replace('%command%', ''))
            env_vars = {}
            flags = []
            
            for part in parts:
                if '=' in part and not part.startswith('-'):
                    # Handle environment variables
                    key, value = part.split('=', 1)
                    env_vars[key] = value
                elif part in self._get_command_suffixes(tab_configs):
                    continue
                else:
                    # Handle flags and command prefixes
                    flags.append(part)
            
            # Process environment variables
            for key, value in env_vars.items():
                if key in tab_toggle_mappings:
                    tab_name, option = tab_toggle_mappings[key]
                    if value == "1":
                        self._ensure_tab_toggles(tab_name)[option] = True
                        self.tab_enabled[tab_name] = True
                elif key in tab_input_mappings:
                    tab_name, option = tab_input_mappings[key]
                    self._ensure_tab_inputs(tab_name)[option] = value
                    self.tab_enabled[tab_name] = True
                elif key in tab_dropdown_mappings:
                    tab_name, key_name = tab_dropdown_mappings[key]
                    self._ensure_tab_dropdowns(tab_name)[key_name] = value
                    self.tab_enabled[tab_name] = True
                elif key in tab_slider_mappings:
                    tab_name, option = tab_slider_mappings[key]
                    try:
                        self._ensure_tab_sliders(tab_name)[option] = float(value)
                        self.tab_enabled[tab_name] = True
                    except ValueError:
                        logger.warning(f"Invalid slider value: {value}")
            
            # Process flags
            for i, flag in enumerate(flags):
                # Check for general toggles
                if flag in self._get_general_toggles(tab_configs):
                    self.general_toggles[flag] = True
                    continue
                
                # Check for general inputs
                if flag in self._get_general_inputs(tab_configs):
                    if i + 1 < len(flags):
                        next_part = flags[i + 1]
                        # Skip if next part is another flag
                        if not next_part.startswith('-') and not next_part.startswith('+'):
                            self.general_inputs[flag] = next_part
                    continue
                
                # Check for special cases like -dxlevel
                if flag == "-dxlevel" and i + 1 < len(flags):
                    self.general_dropdowns[flag] = flags[i + 1]
                    continue
                
                # Check for command prefixes
                for tab_name, config in tab_configs.items():
                    if "command_prefix" in config and flag == config["command_prefix"]:
                        self.tab_enabled[tab_name] = True
                        break
                
                # Check for tab-specific toggles
                for tab_name, config in tab_configs.items():
                    for toggle_option, _ in config.get("toggles", []):
                        if toggle_option == flag:
                            self._ensure_tab_toggles(tab_name)[toggle_option] = True
                            self.tab_enabled[tab_name] = True
                            break
        
        except Exception as e:
            logger.error(f"Error parsing command: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary for storage.
        
        Returns:
            Dict: Dictionary representation of the model
        """
        return {
            "general_toggles": self.general_toggles,
            "general_inputs": self.general_inputs,
            "general_dropdowns": self.general_dropdowns,
            "tab_enabled": self.tab_enabled,
            "tab_toggles": self.tab_toggles,
            "tab_inputs": self.tab_inputs,
            "tab_dropdowns": self.tab_dropdowns,
            "tab_sliders": self.tab_sliders,
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load the model from a dictionary.
        
        Args:
            data: Dictionary with model data
        """
        self.general_toggles = data.get("general_toggles", {})
        self.general_inputs = data.get("general_inputs", {})
        self.general_dropdowns = data.get("general_dropdowns", {})
        self.tab_enabled = data.get("tab_enabled", {})
        self.tab_toggles = data.get("tab_toggles", {})
        self.tab_inputs = data.get("tab_inputs", {})
        self.tab_dropdowns = data.get("tab_dropdowns", {})
        self.tab_sliders = data.get("tab_sliders", {})
    
    # Helper methods to ensure dictionaries exist
    def _ensure_tab_toggles(self, tab_name: str) -> Dict[str, bool]:
        """Ensure the tab toggles dictionary exists."""
        if tab_name not in self.tab_toggles:
            self.tab_toggles[tab_name] = {}
        return self.tab_toggles[tab_name]
    
    def _ensure_tab_inputs(self, tab_name: str) -> Dict[str, str]:
        """Ensure the tab inputs dictionary exists."""
        if tab_name not in self.tab_inputs:
            self.tab_inputs[tab_name] = {}
        return self.tab_inputs[tab_name]
    
    def _ensure_tab_dropdowns(self, tab_name: str) -> Dict[str, str]:
        """Ensure the tab dropdowns dictionary exists."""
        if tab_name not in self.tab_dropdowns:
            self.tab_dropdowns[tab_name] = {}
        return self.tab_dropdowns[tab_name]
    
    def _ensure_tab_sliders(self, tab_name: str) -> Dict[str, float]:
        """Ensure the tab sliders dictionary exists."""
        if tab_name not in self.tab_sliders:
            self.tab_sliders[tab_name] = {}
        return self.tab_sliders[tab_name]
    
    # Helper methods for parsing
    def _build_tab_toggle_mappings(self, tab_configs: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
        """Build mappings for tab toggles."""
        mappings = {}
        for tab_name, config in tab_configs.items():
            for toggle_option, _ in config.get("toggles", []):
                if not toggle_option.startswith('-'):
                    mappings[toggle_option] = (tab_name, toggle_option)
        return mappings
    
    def _build_tab_input_mappings(self, tab_configs: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
        """Build mappings for tab inputs."""
        mappings = {}
        for tab_name, config in tab_configs.items():
            for input_option, _, _ in config.get("inputs", []):
                mappings[input_option] = (tab_name, input_option)
        return mappings
    
    def _build_tab_dropdown_mappings(self, tab_configs: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
        """Build mappings for tab dropdowns."""
        mappings = {}
        for tab_name, config in tab_configs.items():
            for key in config.get("dropdowns", {}):
                mappings[key] = (tab_name, key)
        return mappings
    
    def _build_tab_slider_mappings(self, tab_configs: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
        """Build mappings for tab sliders."""
        mappings = {}
        for tab_name, config in tab_configs.items():
            for slider_option, _, _, _ in config.get("sliders", []):
                mappings[slider_option] = (tab_name, slider_option)
        return mappings
    
    def _get_command_suffixes(self, tab_configs: Dict[str, Any]) -> Set[str]:
        """Get all command suffixes."""
        suffixes = set()
        for config in tab_configs.values():
            if "command_suffix" in config:
                suffixes.add(config["command_suffix"])
        return suffixes
    
    def _get_general_toggles(self, tab_configs: Dict[str, Any]) -> Set[str]:
        """Get all general toggles."""
        from steamlaunchergui.config.constants import GENERAL_OPTIONS
        return {option for option, _ in GENERAL_OPTIONS}
    
    def _get_general_inputs(self, tab_configs: Dict[str, Any]) -> Set[str]:
        """Get all general inputs."""
        from steamlaunchergui.config.constants import GENERAL_INPUTS
        return {option for option, _, _ in GENERAL_INPUTS} 