"""
Tab builder for SteamLauncherGUI.
"""

import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from steamlaunchergui.utils.validation import validate_path, validate_number, validate_color

logger = logging.getLogger(__name__)

def create_tab_content(tab_name, config, launch_options, software_available=True):
    """
    Create content for a specific tab.
    
    Args:
        tab_name: Name of the tab
        config: Tab configuration
        launch_options: LaunchOptions model
        software_available: Whether required software is available
        
    Returns:
        Gtk.Widget: The tab content widget
    """
    # Create main container
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    
    # Add warning if software is not available
    if not software_available:
        software_name = config.get("software_requirement", tab_name)
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning", Gtk.IconSize.MENU)
        warning_label = Gtk.Label(
            label=f"{software_name} is not installed. Some options may not work."
        )
        warning_label.get_style_context().add_class("warning-text")
        
        install_button = Gtk.Button(label=f"Install {software_name}")
        install_button.connect("clicked", on_install_clicked, software_name)
        
        warning_box.pack_start(warning_icon, False, False, 5)
        warning_box.pack_start(warning_label, False, False, 0)
        warning_box.pack_end(install_button, False, False, 0)
        
        main_box.pack_start(warning_box, False, False, 0)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(separator, False, False, 5)
    
    # Add enable checkbox
    enable_label = config.get("enable_label", f"Enable {tab_name}")
    enable_tooltip = config.get("enable_tooltip", f"Enable {tab_name} options")
    
    enable_check = Gtk.CheckButton(label=enable_label)
    enable_check.set_tooltip_text(enable_tooltip)
    
    # Set the active state based on current options
    enable_check.set_active(launch_options.tab_enabled.get(tab_name, False))
    
    # Connect the signal
    enable_check.connect(
        "toggled", on_tab_enabled_toggled, tab_name, launch_options
    )
    
    main_box.pack_start(enable_check, False, False, 0)
    
    # Create content box (for all options)
    content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    content_box.set_sensitive(launch_options.tab_enabled.get(tab_name, False))
    main_box.pack_start(content_box, True, True, 0)
    
    # Connect enable checkbox to content box
    enable_check.connect("toggled", on_content_sensitivity_toggled, content_box)
    
    # Add toggles section if present
    if "toggles" in config and config["toggles"]:
        toggles_frame = Gtk.Frame(label="Options")
        toggles_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        toggles_box.set_border_width(10)
        toggles_frame.add(toggles_box)
        
        for toggle_option, toggle_label in config["toggles"]:
            check = Gtk.CheckButton(label=toggle_label)
            check.set_tooltip_text(toggle_option)
            
            # Set the active state based on current options
            check.set_active(
                launch_options.tab_toggles.get(tab_name, {}).get(toggle_option, False)
            )
            
            # Connect the signal
            check.connect(
                "toggled", on_toggle_toggled, tab_name, toggle_option, launch_options
            )
            
            toggles_box.pack_start(check, False, False, 0)
        
        content_box.pack_start(toggles_frame, False, False, 0)
    
    # Add inputs section if present
    if "inputs" in config and config["inputs"]:
        inputs_frame = Gtk.Frame(label="Input Values")
        inputs_grid = Gtk.Grid()
        inputs_grid.set_border_width(10)
        inputs_grid.set_column_spacing(10)
        inputs_grid.set_row_spacing(5)
        inputs_frame.add(inputs_grid)
        
        for row, (input_option, input_label, input_placeholder) in enumerate(config["inputs"]):
            # Label
            label = Gtk.Label(label=input_label + ":")
            label.set_halign(Gtk.Align.START)
            
            # Entry
            entry = Gtk.Entry()
            entry.set_placeholder_text(input_placeholder)
            
            # Set the current value if any
            current_value = launch_options.tab_inputs.get(tab_name, {}).get(input_option, "")
            if current_value:
                entry.set_text(current_value)
            
            # Connect the signal
            entry.connect(
                "changed", on_input_changed, tab_name, input_option, launch_options
            )
            
            # Validate based on input type
            if "path" in input_label.lower():
                entry.connect("changed", validate_entry, "path")
            elif "color" in input_label.lower():
                entry.connect("changed", validate_entry, "color")
            elif any(x in input_label.lower() for x in ["size", "width", "height", "level"]):
                entry.connect("changed", validate_entry, "integer")
            
            # Add to grid
            inputs_grid.attach(label, 0, row, 1, 1)
            inputs_grid.attach(entry, 1, row, 1, 1)
        
        content_box.pack_start(inputs_frame, False, False, 0)
    
    # Add dropdowns section if present
    if "dropdowns" in config and config["dropdowns"]:
        dropdowns_frame = Gtk.Frame(label="Dropdown Values")
        dropdowns_grid = Gtk.Grid()
        dropdowns_grid.set_border_width(10)
        dropdowns_grid.set_column_spacing(10)
        dropdowns_grid.set_row_spacing(5)
        dropdowns_frame.add(dropdowns_grid)
        
        for row, (key, dropdown_config) in enumerate(config["dropdowns"].items()):
            # Label
            label = Gtk.Label(label=dropdown_config["label"])
            label.set_halign(Gtk.Align.START)
            
            # Dropdown (ComboBoxText)
            combo = Gtk.ComboBoxText()
            combo.set_tooltip_text(dropdown_config.get("tooltip", ""))
            
            # Add options
            for option in dropdown_config["options"]:
                combo.append_text(option)
            
            # Set active option based on current value or default
            current_value = launch_options.tab_dropdowns.get(tab_name, {}).get(key, "")
            default_value = dropdown_config.get("default", "")
            
            if current_value and current_value in dropdown_config["options"]:
                combo.set_active(dropdown_config["options"].index(current_value))
            elif default_value and default_value in dropdown_config["options"]:
                combo.set_active(dropdown_config["options"].index(default_value))
            
            # Connect the signal
            combo.connect(
                "changed", on_dropdown_changed, tab_name, key, dropdown_config["options"], 
                launch_options
            )
            
            # Add to grid
            dropdowns_grid.attach(label, 0, row, 1, 1)
            dropdowns_grid.attach(combo, 1, row, 1, 1)
        
        content_box.pack_start(dropdowns_frame, False, False, 0)
    
    # Add sliders section if present
    if "sliders" in config and config["sliders"]:
        sliders_frame = Gtk.Frame(label="Slider Values")
        sliders_grid = Gtk.Grid()
        sliders_grid.set_border_width(10)
        sliders_grid.set_column_spacing(10)
        sliders_grid.set_row_spacing(5)
        sliders_frame.add(sliders_grid)
        
        for row, (slider_option, slider_label, min_val, max_val) in enumerate(config["sliders"]):
            # Label
            label = Gtk.Label(label=slider_label + ":")
            label.set_halign(Gtk.Align.START)
            
            # Scale
            scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 0.1)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.set_hexpand(True)
            
            # Set the current value if any
            current_value = launch_options.tab_sliders.get(tab_name, {}).get(slider_option, 0.0)
            scale.set_value(current_value)
            
            # Connect the signal
            scale.connect(
                "value-changed", on_slider_changed, tab_name, slider_option, launch_options
            )
            
            # Add to grid
            sliders_grid.attach(label, 0, row, 1, 1)
            sliders_grid.attach(scale, 1, row, 1, 1)
        
        content_box.pack_start(sliders_frame, False, False, 0)
    
    return main_box

# Signal handlers
def on_tab_enabled_toggled(checkbutton, tab_name, launch_options):
    """Handle tab enable checkbox toggle."""
    enabled = checkbutton.get_active()
    launch_options.tab_enabled[tab_name] = enabled
    logger.debug(f"Tab '{tab_name}' enabled: {enabled}")

def on_content_sensitivity_toggled(checkbutton, content_box):
    """Handle content box sensitivity based on enable checkbox."""
    content_box.set_sensitive(checkbutton.get_active())

def on_toggle_toggled(checkbutton, tab_name, option, launch_options):
    """Handle option toggle checkbox."""
    enabled = checkbutton.get_active()
    
    # Ensure tab_toggles for this tab exists
    if tab_name not in launch_options.tab_toggles:
        launch_options.tab_toggles[tab_name] = {}
    
    launch_options.tab_toggles[tab_name][option] = enabled
    logger.debug(f"Option '{option}' in tab '{tab_name}' set to: {enabled}")

def on_input_changed(entry, tab_name, option, launch_options):
    """Handle input entry change."""
    value = entry.get_text()
    
    # Ensure tab_inputs for this tab exists
    if tab_name not in launch_options.tab_inputs:
        launch_options.tab_inputs[tab_name] = {}
    
    launch_options.tab_inputs[tab_name][option] = value
    logger.debug(f"Input '{option}' in tab '{tab_name}' set to: {value}")

def on_dropdown_changed(combo, tab_name, key, options, launch_options):
    """Handle dropdown selection change."""
    active = combo.get_active()
    if active < 0:
        return
    
    value = options[active]
    
    # Ensure tab_dropdowns for this tab exists
    if tab_name not in launch_options.tab_dropdowns:
        launch_options.tab_dropdowns[tab_name] = {}
    
    launch_options.tab_dropdowns[tab_name][key] = value
    logger.debug(f"Dropdown '{key}' in tab '{tab_name}' set to: {value}")

def on_slider_changed(scale, tab_name, option, launch_options):
    """Handle slider value change."""
    value = scale.get_value()
    
    # Ensure tab_sliders for this tab exists
    if tab_name not in launch_options.tab_sliders:
        launch_options.tab_sliders[tab_name] = {}
    
    launch_options.tab_sliders[tab_name][option] = value
    logger.debug(f"Slider '{option}' in tab '{tab_name}' set to: {value}")

def on_install_clicked(button, software_name):
    """Handle install button click."""
    from steamlaunchergui.utils.software_detection import get_install_command
    
    # Get the install command
    install_cmd = get_install_command(software_name)
    
    # Create a dialog with the command
    dialog = Gtk.MessageDialog(
        transient_for=button.get_toplevel(),
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=f"Install {software_name}"
    )
    dialog.format_secondary_text(
        f"Run the following command in your terminal to install {software_name}:\n\n{install_cmd}"
    )
    
    dialog.run()
    dialog.destroy()

def validate_entry(entry, input_type):
    """Validate entry input and show feedback."""
    text = entry.get_text()
    if not text:
        entry.remove_css_class("error-text")
        return
    
    if input_type == "path":
        valid, error = validate_path(text)
    elif input_type == "color":
        valid, error = validate_color(text)
    elif input_type == "integer":
        valid, error = validate_number(text)
    else:
        valid, error = True, ""
    
    if valid:
        entry.remove_css_class("error-text")
    else:
        entry.add_css_class("error-text")
        entry.set_tooltip_text(error)