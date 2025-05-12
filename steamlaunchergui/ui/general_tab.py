"""
General tab for SteamLauncherGUI.
"""

import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from steamlaunchergui.config.constants import GENERAL_OPTIONS, GENERAL_INPUTS, DX_LEVEL_PRESETS
from steamlaunchergui.utils.validation import validate_integer, validate_resolution

logger = logging.getLogger(__name__)

def create_general_tab(launch_options):
    """
    Create the general options tab.
    
    Args:
        launch_options: LaunchOptions model
        
    Returns:
        Gtk.Widget: The general tab content widget
    """
    # Create main container
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    
    # Display options section
    display_frame = create_display_section(launch_options)
    main_box.pack_start(display_frame, False, False, 0)
    
    # Performance options section
    performance_frame = create_performance_section(launch_options)
    main_box.pack_start(performance_frame, False, False, 0)
    
    # Debug options section
    debug_frame = create_debug_section(launch_options)
    main_box.pack_start(debug_frame, False, False, 0)
    
    # Audio options section
    audio_frame = create_audio_section(launch_options)
    main_box.pack_start(audio_frame, False, False, 0)
    
    # Specific inputs section
    inputs_frame = create_inputs_section(launch_options)
    main_box.pack_start(inputs_frame, False, False, 0)
    
    return main_box

def create_display_section(launch_options):
    """Create the display options section."""
    frame = Gtk.Frame(label="Display Options")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box.set_border_width(10)
    frame.add(box)
    
    # Add display mode options
    display_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(display_box, False, False, 0)
    
    # Fullscreen
    fullscreen_check = Gtk.CheckButton(label="Fullscreen")
    fullscreen_check.set_tooltip_text("-fullscreen")
    fullscreen_check.set_active(launch_options.general_toggles.get("-fullscreen", False))
    fullscreen_check.connect("toggled", on_toggle_toggled, "-fullscreen", launch_options)
    display_box.pack_start(fullscreen_check, False, False, 0)
    
    # Windowed
    windowed_check = Gtk.CheckButton(label="Windowed")
    windowed_check.set_tooltip_text("-windowed")
    windowed_check.set_active(launch_options.general_toggles.get("-windowed", False))
    windowed_check.connect("toggled", on_toggle_toggled, "-windowed", launch_options)
    display_box.pack_start(windowed_check, False, False, 0)
    
    # Borderless
    borderless_check = Gtk.CheckButton(label="Borderless")
    borderless_check.set_tooltip_text("-noborder")
    borderless_check.set_active(launch_options.general_toggles.get("-noborder", False))
    borderless_check.connect("toggled", on_toggle_toggled, "-noborder", launch_options)
    display_box.pack_start(borderless_check, False, False, 0)
    
    # Resolution settings
    res_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    box.pack_start(res_box, False, False, 5)
    
    # Width
    width_label = Gtk.Label(label="Width:")
    res_box.pack_start(width_label, False, False, 0)
    
    width_entry = Gtk.Entry()
    width_entry.set_placeholder_text("e.g., 1920")
    width_entry.set_width_chars(6)
    if "-w" in launch_options.general_inputs:
        width_entry.set_text(launch_options.general_inputs["-w"])
    width_entry.connect("changed", on_input_changed, "-w", launch_options)
    width_entry.connect("changed", on_resolution_changed, "width", launch_options)
    res_box.pack_start(width_entry, False, False, 0)
    
    # Height
    height_label = Gtk.Label(label="Height:")
    res_box.pack_start(height_label, False, False, 5)
    
    height_entry = Gtk.Entry()
    height_entry.set_placeholder_text("e.g., 1080")
    height_entry.set_width_chars(6)
    if "-h" in launch_options.general_inputs:
        height_entry.set_text(launch_options.general_inputs["-h"])
    height_entry.connect("changed", on_input_changed, "-h", launch_options)
    height_entry.connect("changed", on_resolution_changed, "height", launch_options)
    res_box.pack_start(height_entry, False, False, 0)
    
    # DX Level
    dx_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    box.pack_start(dx_box, False, False, 5)
    
    dx_label = Gtk.Label(label="DirectX Level:")
    dx_box.pack_start(dx_label, False, False, 0)
    
    dx_combo = Gtk.ComboBoxText()
    for level in DX_LEVEL_PRESETS:
        dx_combo.append_text(level)
    
    if "-dxlevel" in launch_options.general_inputs:
        level = launch_options.general_inputs["-dxlevel"]
        if level in DX_LEVEL_PRESETS:
            dx_combo.set_active(DX_LEVEL_PRESETS.index(level))
    
    dx_combo.connect("changed", on_dx_level_changed, launch_options)
    dx_box.pack_start(dx_combo, False, False, 0)
    
    return frame

def create_performance_section(launch_options):
    """Create the performance options section."""
    frame = Gtk.Frame(label="Performance Options")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box.set_border_width(10)
    frame.add(box)
    
    # Process priority
    priority_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(priority_box, False, False, 0)
    
    priority_label = Gtk.Label(label="Process Priority:")
    priority_box.pack_start(priority_label, False, False, 0)
    
    # High priority
    high_check = Gtk.CheckButton(label="High")
    high_check.set_tooltip_text("-high")
    high_check.set_active(launch_options.general_toggles.get("-high", False))
    high_check.connect("toggled", on_toggle_toggled, "-high", launch_options)
    priority_box.pack_start(high_check, False, False, 0)
    
    # Very high priority
    veryhigh_check = Gtk.CheckButton(label="Very High")
    veryhigh_check.set_tooltip_text("-veryhigh")
    veryhigh_check.set_active(launch_options.general_toggles.get("-veryhigh", False))
    veryhigh_check.connect("toggled", on_toggle_toggled, "-veryhigh", launch_options)
    priority_box.pack_start(veryhigh_check, False, False, 0)
    
    # Low priority
    low_check = Gtk.CheckButton(label="Low")
    low_check.set_tooltip_text("-low")
    low_check.set_active(launch_options.general_toggles.get("-low", False))
    low_check.connect("toggled", on_toggle_toggled, "-low", launch_options)
    priority_box.pack_start(low_check, False, False, 0)
    
    # Background priority
    background_check = Gtk.CheckButton(label="Background")
    background_check.set_tooltip_text("-background")
    background_check.set_active(launch_options.general_toggles.get("-background", False))
    background_check.connect("toggled", on_toggle_toggled, "-background", launch_options)
    priority_box.pack_start(background_check, False, False, 0)
    
    # Graphics API
    api_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(api_box, False, False, 5)
    
    api_label = Gtk.Label(label="Graphics API:")
    api_box.pack_start(api_label, False, False, 0)
    
    # Vulkan
    vulkan_check = Gtk.CheckButton(label="Vulkan")
    vulkan_check.set_tooltip_text("-vulkan")
    vulkan_check.set_active(launch_options.general_toggles.get("-vulkan", False))
    vulkan_check.connect("toggled", on_toggle_toggled, "-vulkan", launch_options)
    api_box.pack_start(vulkan_check, False, False, 0)
    
    # Force OpenGL Core
    glcore_check = Gtk.CheckButton(label="OpenGL Core")
    glcore_check.set_tooltip_text("-force-glcore")
    glcore_check.set_active(launch_options.general_toggles.get("-force-glcore", False))
    glcore_check.connect("toggled", on_toggle_toggled, "-force-glcore", launch_options)
    api_box.pack_start(glcore_check, False, False, 0)
    
    # Software rendering
    soft_check = Gtk.CheckButton(label="Software Rendering")
    soft_check.set_tooltip_text("-soft")
    soft_check.set_active(launch_options.general_toggles.get("-soft", False))
    soft_check.connect("toggled", on_toggle_toggled, "-soft", launch_options)
    api_box.pack_start(soft_check, False, False, 0)
    
    # Additional performance options
    perf_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(perf_box, False, False, 5)
    
    # VSync
    vsync_check = Gtk.CheckButton(label="Disable VSync")
    vsync_check.set_tooltip_text("-novsync")
    vsync_check.set_active(launch_options.general_toggles.get("-novsync", False))
    vsync_check.connect("toggled", on_toggle_toggled, "-novsync", launch_options)
    perf_box.pack_start(vsync_check, False, False, 0)
    
    # Disable threading
    threading_check = Gtk.CheckButton(label="Disable Threading")
    threading_check.set_tooltip_text("-nothreading")
    threading_check.set_active(launch_options.general_toggles.get("-nothreading", False))
    threading_check.connect("toggled", on_toggle_toggled, "-nothreading", launch_options)
    perf_box.pack_start(threading_check, False, False, 0)
    
    # CPU Count
    cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    box.pack_start(cpu_box, False, False, 5)
    
    cpu_label = Gtk.Label(label="CPU Cores:")
    cpu_box.pack_start(cpu_label, False, False, 0)
    
    cpu_entry = Gtk.Entry()
    cpu_entry.set_placeholder_text("e.g., 4")
    cpu_entry.set_width_chars(4)
    if "-CpuCount" in launch_options.general_inputs:
        cpu_entry.set_text(launch_options.general_inputs["-CpuCount"])
    cpu_entry.connect("changed", on_input_changed, "-CpuCount", launch_options)
    cpu_entry.connect("changed", on_cpu_count_changed, launch_options)
    cpu_box.pack_start(cpu_entry, False, False, 0)
    
    return frame

def create_debug_section(launch_options):
    """Create the debug options section."""
    frame = Gtk.Frame(label="Debug and Troubleshooting")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box.set_border_width(10)
    frame.add(box)
    
    # Debug options
    debug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(debug_box, False, False, 0)
    
    # Console
    console_check = Gtk.CheckButton(label="Console")
    console_check.set_tooltip_text("-console")
    console_check.set_active(launch_options.general_toggles.get("-console", False))
    console_check.connect("toggled", on_toggle_toggled, "-console", launch_options)
    debug_box.pack_start(console_check, False, False, 0)
    
    # Debug
    debug_check = Gtk.CheckButton(label="Debug Mode")
    debug_check.set_tooltip_text("-debug")
    debug_check.set_active(launch_options.general_toggles.get("-debug", False))
    debug_check.connect("toggled", on_toggle_toggled, "-debug", launch_options)
    debug_box.pack_start(debug_check, False, False, 0)
    
    # No crash dialog
    nocrash_check = Gtk.CheckButton(label="No Crash Dialog")
    nocrash_check.set_tooltip_text("-nocrashdialog")
    nocrash_check.set_active(launch_options.general_toggles.get("-nocrashdialog", False))
    nocrash_check.connect("toggled", on_toggle_toggled, "-nocrashdialog", launch_options)
    debug_box.pack_start(nocrash_check, False, False, 0)
    
    # Network options
    network_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(network_box, False, False, 5)
    
    # Insecure
    insecure_check = Gtk.CheckButton(label="Insecure")
    insecure_check.set_tooltip_text("-insecure")
    insecure_check.set_active(launch_options.general_toggles.get("-insecure", False))
    insecure_check.connect("toggled", on_toggle_toggled, "-insecure", launch_options)
    network_box.pack_start(insecure_check, False, False, 0)
    
    # Secure
    secure_check = Gtk.CheckButton(label="Secure")
    secure_check.set_tooltip_text("-secure")
    secure_check.set_active(launch_options.general_toggles.get("-secure", False))
    secure_check.connect("toggled", on_toggle_toggled, "-secure", launch_options)
    network_box.pack_start(secure_check, False, False, 0)
    
    # LAN
    lan_check = Gtk.CheckButton(label="LAN Mode")
    lan_check.set_tooltip_text("-lan")
    lan_check.set_active(launch_options.general_toggles.get("-lan", False))
    lan_check.connect("toggled", on_toggle_toggled, "-lan", launch_options)
    network_box.pack_start(lan_check, False, False, 0)
    
    # Skip intro
    skip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(skip_box, False, False, 5)
    
    # No intro
    nointro_check = Gtk.CheckButton(label="Skip Intro")
    nointro_check.set_tooltip_text("-nointro")
    nointro_check.set_active(launch_options.general_toggles.get("-nointro", False))
    nointro_check.connect("toggled", on_toggle_toggled, "-nointro", launch_options)
    skip_box.pack_start(nointro_check, False, False, 0)
    
    # No logo
    nologo_check = Gtk.CheckButton(label="Skip Logo")
    nologo_check.set_tooltip_text("-nologo")
    nologo_check.set_active(launch_options.general_toggles.get("-nologo", False))
    nologo_check.connect("toggled", on_toggle_toggled, "-nologo", launch_options)
    skip_box.pack_start(nologo_check, False, False, 0)
    
    # No startup movie
    nostartup_check = Gtk.CheckButton(label="Skip Startup Movie")
    nostartup_check.set_tooltip_text("-nostartupmovie")
    nostartup_check.set_active(launch_options.general_toggles.get("-nostartupmovie", False))
    nostartup_check.connect("toggled", on_toggle_toggled, "-nostartupmovie", launch_options)
    skip_box.pack_start(nostartup_check, False, False, 0)
    
    return frame

def create_audio_section(launch_options):
    """Create the audio options section."""
    frame = Gtk.Frame(label="Audio Options")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box.set_border_width(10)
    frame.add(box)
    
    # Audio options
    audio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(audio_box, False, False, 0)
    
    # No sound
    nosound_check = Gtk.CheckButton(label="No Sound")
    nosound_check.set_tooltip_text("-nosound")
    nosound_check.set_active(launch_options.general_toggles.get("-nosound", False))
    nosound_check.connect("toggled", on_toggle_toggled, "-nosound", launch_options)
    audio_box.pack_start(nosound_check, False, False, 0)
    
    # No audio
    noaudio_check = Gtk.CheckButton(label="No Audio")
    noaudio_check.set_tooltip_text("-noaudio")
    noaudio_check.set_active(launch_options.general_toggles.get("-noaudio", False))
    noaudio_check.connect("toggled", on_toggle_toggled, "-noaudio", launch_options)
    audio_box.pack_start(noaudio_check, False, False, 0)
    
    # Sound buffer
    buffer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    box.pack_start(buffer_box, False, False, 5)
    
    buffer_label = Gtk.Label(label="Sound Buffer Size:")
    buffer_box.pack_start(buffer_label, False, False, 0)
    
    buffer_entry = Gtk.Entry()
    buffer_entry.set_placeholder_text("e.g., 1024")
    buffer_entry.set_width_chars(6)
    if "-soundbuffer" in launch_options.general_inputs:
        buffer_entry.set_text(launch_options.general_inputs["-soundbuffer"])
    buffer_entry.connect("changed", on_input_changed, "-soundbuffer", launch_options)
    buffer_entry.connect("changed", validate_numeric_input, launch_options)
    buffer_box.pack_start(buffer_entry, False, False, 0)
    
    return frame

def create_inputs_section(launch_options):
    """Create the inputs section for other general options."""
    frame = Gtk.Frame(label="Additional Options")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box.set_border_width(10)
    frame.add(box)
    
    # Input options
    input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    box.pack_start(input_box, False, False, 0)
    
    # No joy
    nojoy_check = Gtk.CheckButton(label="No Joystick")
    nojoy_check.set_tooltip_text("-nojoy")
    nojoy_check.set_active(launch_options.general_toggles.get("-nojoy", False))
    nojoy_check.connect("toggled", on_toggle_toggled, "-nojoy", launch_options)
    input_box.pack_start(nojoy_check, False, False, 0)
    
    # No gamepad
    nogamepad_check = Gtk.CheckButton(label="No Gamepad")
    nogamepad_check.set_tooltip_text("-nogamepad")
    nogamepad_check.set_active(launch_options.general_toggles.get("-nogamepad", False))
    nogamepad_check.connect("toggled", on_toggle_toggled, "-nogamepad", launch_options)
    input_box.pack_start(nogamepad_check, False, False, 0)
    
    # No mouse
    nomouse_check = Gtk.CheckButton(label="No Mouse")
    nomouse_check.set_tooltip_text("-nomouse")
    nomouse_check.set_active(launch_options.general_toggles.get("-nomouse", False))
    nomouse_check.connect("toggled", on_toggle_toggled, "-nomouse", launch_options)
    input_box.pack_start(nomouse_check, False, False, 0)
    
    # Mouse acceleration
    mouseaccel_check = Gtk.CheckButton(label="No Mouse Accel")
    mouseaccel_check.set_tooltip_text("-nomouseaccel")
    mouseaccel_check.set_active(launch_options.general_toggles.get("-nomouseaccel", False))
    mouseaccel_check.connect("toggled", on_toggle_toggled, "-nomouseaccel", launch_options)
    input_box.pack_start(mouseaccel_check, False, False, 0)
    
    # Custom option entry
    custom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    box.pack_start(custom_box, False, False, 10)
    
    custom_label = Gtk.Label(label="Custom Launch Options:")
    custom_box.pack_start(custom_label, False, False, 0)
    
    custom_entry = Gtk.Entry()
    custom_entry.set_placeholder_text("Enter custom launch options here")
    custom_entry.set_tooltip_text("Custom options will be appended to the generated command")
    if "custom_options" in launch_options.general_inputs:
        custom_entry.set_text(launch_options.general_inputs["custom_options"])
    custom_entry.connect("changed", on_input_changed, "custom_options", launch_options)
    custom_box.pack_start(custom_entry, True, True, 0)
    
    return frame

# Signal handlers
def on_toggle_toggled(checkbutton, option, launch_options):
    """Handle checkbox toggle for general options."""
    enabled = checkbutton.get_active()
    launch_options.general_toggles[option] = enabled
    logger.debug(f"General option '{option}' set to: {enabled}")

def on_input_changed(entry, option, launch_options):
    """Handle input entry change for general options."""
    value = entry.get_text()
    if value:
        launch_options.general_inputs[option] = value
    else:
        if option in launch_options.general_inputs:
            del launch_options.general_inputs[option]
    logger.debug(f"General input '{option}' set to: {value}")

def on_dx_level_changed(combo, launch_options):
    """Handle DirectX level selection."""
    active = combo.get_active()
    if active < 0:
        return
    
    level = DX_LEVEL_PRESETS[active]
    launch_options.general_inputs["-dxlevel"] = level
    logger.debug(f"DirectX level set to: {level}")

def on_resolution_changed(entry, dimension, launch_options):
    """Handle resolution input changes and validation."""
    text = entry.get_text()
    
    if not text:
        entry.get_style_context().remove_class("error-text")
        return
    
    valid, error = validate_integer(text, 1, 16384)
    
    if valid:
        entry.get_style_context().remove_class("error-text")
    else:
        entry.get_style_context().add_class("error-text")
        entry.set_tooltip_text(error)

def on_cpu_count_changed(entry, launch_options):
    """Handle CPU count input validation."""
    text = entry.get_text()
    
    if not text:
        entry.get_style_context().remove_class("error-text")
        return
    
    valid, error = validate_integer(text, 1, 128)
    
    if valid:
        entry.get_style_context().remove_class("error-text")
    else:
        entry.get_style_context().add_class("error-text")
        entry.set_tooltip_text(error)

def validate_numeric_input(entry, launch_options):
    """Validate that input is numeric."""
    text = entry.get_text()
    
    if not text:
        entry.get_style_context().remove_class("error-text")
        return
    
    valid, error = validate_integer(text)
    
    if valid:
        entry.get_style_context().remove_class("error-text")
    else:
        entry.get_style_context().add_class("error-text")
        entry.set_tooltip_text(error)