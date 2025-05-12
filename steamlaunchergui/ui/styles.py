"""
CSS styling for the SteamLauncherGUI application.
"""

import os
import logging
from pathlib import Path
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

logger = logging.getLogger(__name__)

# CSS style definitions
DEFAULT_STYLE = """
/* Base styling */
window {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

label {
    color: #e0e0e0;
}

button {
    background-color: #3d3d3d;
    border-color: #555555;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 6px 12px;
}

button:hover {
    background-color: #4d4d4d;
}

button:active {
    background-color: #555555;
}

entry {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border-color: #555555;
    border-radius: 4px;
    padding: 4px 8px;
}

checkbutton {
    color: #e0e0e0;
}

notebook {
    background-color: #2d2d2d;
}

notebook tab {
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 6px 12px;
}

notebook tab:checked {
    background-color: #4d4d4d;
}

scrolledwindow {
    border-color: #555555;
}

.header-label {
    font-size: 16px;
    font-weight: bold;
    margin: 8px 0;
}

.section-label {
    font-weight: bold;
    margin: 4px 0;
}

.status-bar {
    font-size: 12px;
    padding: 4px 8px;
}

.warning-text {
    color: #ffcc00;
}

.error-text {
    color: #ff6666;
}

.success-text {
    color: #66cc66;
}

.tab-content {
    padding: 12px;
}

.command-display {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    font-family: monospace;
}

/* Light theme overrides */
.light-theme window {
    background-color: #f8f8f8;
    color: #202020;
}

.light-theme label {
    color: #202020;
}

.light-theme button {
    background-color: #e8e8e8;
    border-color: #acacac;
    color: #202020;
    border-width: 1px;
}

.light-theme button:hover {
    background-color: #d8d8d8;
    border-color: #999999;
}

.light-theme button:active {
    background-color: #c8c8c8;
    border-color: #888888;
}

.light-theme button:focus {
    outline: 2px solid #4a90d9;
    outline-offset: 1px;
}

.light-theme entry {
    background-color: #ffffff;
    color: #202020;
    border-color: #acacac;
    border-width: 1px;
}

.light-theme entry:focus {
    border-color: #4a90d9;
    outline: 1px solid #4a90d9;
}

.light-theme checkbutton {
    color: #202020;
}

.light-theme checkbutton:focus {
    outline: 1px solid #4a90d9;
}

.light-theme notebook {
    background-color: #f8f8f8;
}

.light-theme notebook tab {
    background-color: #e8e8e8;
    color: #202020;
    border-color: #acacac;
}

.light-theme notebook tab:checked {
    background-color: #d0d0d0;
    font-weight: bold;
}

.light-theme scrolledwindow {
    border-color: #acacac;
}

.light-theme .header-label {
    color: #101010;
}

.light-theme .section-label {
    color: #101010;
}

.light-theme .status-bar {
    color: #303030;
    background-color: #e0e0e0;
}

.light-theme .warning-text {
    color: #a05000;
    font-weight: bold;
}

.light-theme .error-text {
    color: #c00000;
    font-weight: bold;
}

.light-theme .success-text {
    color: #006600;
    font-weight: bold;
}

.light-theme .command-display {
    background-color: #ffffff;
    color: #101010;
    border-color: #acacac;
    border-width: 1px;
}

.light-theme frame {
    border-color: #acacac;
    border-width: 1px;
    border-radius: 3px;
}

.light-theme frame > label {
    color: #101010;
    font-weight: bold;
}

.light-theme combobox button {
    background-color: #ffffff;
    border-color: #acacac;
    color: #202020;
}

.light-theme combobox button:hover {
    background-color: #f0f0f0;
}

.light-theme combobox:focus button {
    border-color: #4a90d9;
    outline: 1px solid #4a90d9;
}

.light-theme treeview {
    background-color: #ffffff;
    color: #202020;
}

.light-theme treeview:selected {
    background-color: #4a90d9;
    color: #ffffff;
}

.light-theme treeview:selected:focus {
    background-color: #3a80c9;
    color: #ffffff;
    outline: 1px solid #103060;
}

.light-theme treeview header button {
    background-color: #e8e8e8;
    color: #202020;
    font-weight: bold;
}

.light-theme tooltip {
    background-color: #ffffcc;
    color: #000000;
    border: 1px solid #c0c060;
}

.light-theme scale {
    color: #202020;
}

.light-theme scale trough {
    background-color: #d8d8d8;
    border-color: #acacac;
}

.light-theme scale highlight {
    background-color: #4a90d9;
}

.light-theme scale:focus trough {
    border-color: #4a90d9;
    outline: 1px solid #4a90d9;
}

.light-theme progressbar trough {
    background-color: #d8d8d8;
}

.light-theme progressbar progress {
    background-color: #4a90d9;
}

.light-theme separator {
    background-color: #d0d0d0;
}

.light-theme scrollbar {
    background-color: #e8e8e8;
}

.light-theme scrollbar slider {
    background-color: #a0a0a0;
    border-radius: 4px;
}

.light-theme scrollbar slider:hover {
    background-color: #808080;
}

.light-theme scrollbar slider:active {
    background-color: #606060;
}
"""

def load_css():
    """
    Load CSS styling for the application.
    
    Returns:
        Gtk.CssProvider: The configured CSS provider
    """
    try:
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(DEFAULT_STYLE.encode())
        
        # Apply the CSS
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        logger.info("CSS styling loaded successfully")
        return css_provider
    except Exception as e:
        logger.error(f"Error loading CSS: {e}")
        return None

def apply_theme(widget, theme_name="dark"):
    """
    Apply a theme to a widget.
    
    Args:
        widget: The widget to apply the theme to
        theme_name: The theme name ('dark' or 'light')
    """
    if theme_name == "light":
        widget.get_style_context().add_class("light-theme")
    else:
        widget.get_style_context().remove_class("light-theme") 