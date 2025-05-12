"""
Validation utilities for user input.
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_path(path: str) -> Tuple[bool, str]:
    """
    Validate a file path input.
    
    Args:
        path: The path to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not path:
        return True, ""  # Empty path is valid (will use default)
    
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}"
    
    return True, ""

def validate_number(value: str, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
    """
    Validate a numeric input.
    
    Args:
        value: The value to validate
        min_val: Optional minimum value
        max_val: Optional maximum value
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not value:
        return True, ""  # Empty value is valid (will use default)
    
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            return False, f"Value must be at least {min_val}"
        
        if max_val is not None and num_val > max_val:
            return False, f"Value must be at most {max_val}"
        
        return True, ""
    except ValueError:
        return False, "Value must be a number"

def validate_integer(value: str, min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
    """
    Validate an integer input.
    
    Args:
        value: The value to validate
        min_val: Optional minimum value
        max_val: Optional maximum value
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not value:
        return True, ""  # Empty value is valid (will use default)
    
    try:
        num_val = int(value)
        
        if min_val is not None and num_val < min_val:
            return False, f"Value must be at least {min_val}"
        
        if max_val is not None and num_val > max_val:
            return False, f"Value must be at most {max_val}"
        
        return True, ""
    except ValueError:
        return False, "Value must be an integer"

def validate_color(value: str) -> Tuple[bool, str]:
    """
    Validate a color input (e.g., #FF0000).
    
    Args:
        value: The color value to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not value:
        return True, ""  # Empty value is valid (will use default)
    
    # Check for valid hex color format: #RRGGBB or #RGB
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(hex_pattern, value):
        return False, "Color must be in hex format (e.g., #FF0000)"
    
    return True, ""

def validate_resolution(width: str, height: str) -> Tuple[bool, str]:
    """
    Validate a resolution (width x height).
    
    Args:
        width: The width value
        height: The height value
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Validate width
    width_valid, width_error = validate_integer(width, 1, 16384)
    if not width_valid:
        return False, f"Invalid width: {width_error}"
    
    # Validate height
    height_valid, height_error = validate_integer(height, 1, 16384)
    if not height_valid:
        return False, f"Invalid height: {height_error}"
    
    return True, ""

def validate_option_combinations(options: Dict[str, Any]) -> List[str]:
    """
    Validate combinations of launch options for conflicts or issues.
    
    Args:
        options: Dictionary of options and their values
        
    Returns:
        List[str]: List of warning messages for conflicting options
    """
    warnings = []
    
    # Check for conflicting fullscreen/windowed options
    if options.get('-fullscreen') and options.get('-windowed'):
        warnings.append("Conflicting options: -fullscreen and -windowed cannot be used together")
    
    if options.get('-fullscreen') and options.get('-nofullscreen'):
        warnings.append("Conflicting options: -fullscreen and -nofullscreen cannot be used together")
    
    # Check for conflicting priority options
    priority_options = ['-high', '-low', '-veryhigh', '-background']
    active_priorities = [opt for opt in priority_options if options.get(opt)]
    if len(active_priorities) > 1:
        warnings.append(f"Conflicting priority options: {', '.join(active_priorities)}")
    
    # Check for conflicting sound options
    if options.get('-nosound') and options.get('-soundbuffer'):
        warnings.append("Conflicting sound options: -nosound will override -soundbuffer")
    
    # Check for potentially problematic combinations
    if options.get('-fullscreen') and options.get('-noborder'):
        warnings.append("Potentially unnecessary: -noborder has no effect in fullscreen mode")
    
    return warnings

def get_input_type_validator(input_type: str):
    """
    Get the appropriate validator function for an input type.
    
    Args:
        input_type: The type of input to validate
        
    Returns:
        function: The validator function
    """
    validators = {
        'path': validate_path,
        'number': validate_number,
        'integer': validate_integer,
        'color': validate_color,
        'resolution': lambda x: validate_integer(x, 1, 16384),
    }
    
    return validators.get(input_type, lambda x: (True, "")) 