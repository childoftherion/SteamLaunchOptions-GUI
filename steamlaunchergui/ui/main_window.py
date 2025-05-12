"""
Main window of the SteamLauncherGUI application.
"""

import logging
import gi
import os
import subprocess
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from steamlaunchergui.config import TAB_CONFIGS, ConfigManager
from steamlaunchergui.models import LaunchOptions, SteamGame, ProfileManager
from steamlaunchergui.utils.software_detection import check_software, detect_steam_location
from steamlaunchergui.ui.styles import load_css, apply_theme
from steamlaunchergui.ui.tab_builder import create_tab_content
from steamlaunchergui.ui.general_tab import create_general_tab
from steamlaunchergui.ui.profile_manager_dialog import ProfileManagerDialog
from steamlaunchergui.utils.validation import validate_option_combinations

logger = logging.getLogger(__name__)

class SteamLauncherWindow(Gtk.Window):
    """
    Main application window for SteamLauncherGUI.
    
    This class handles the UI presentation logic, while business logic
    is delegated to the model classes.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__(title="Steam Game Launcher")
        logger.info("Initializing Steam Launcher window")
        
        # Set up window properties
        self.set_border_width(10)
        self.set_default_size(1000, 700)
        
        # Initialize models
        self._init_models()
        
        # Initialize CSS styling
        self.css_provider = load_css()
        
        # Set up the UI
        self._setup_ui()
        
        # Connect signals
        self.connect("destroy", self.on_destroy)
        
        # Apply theme based on settings
        theme = self.config_manager.get_setting("theme", "dark")
        apply_theme(self, theme)
        
        logger.info("Steam Launcher window initialized")
    
    def _init_models(self):
        """Initialize the model components."""
        # Create configuration manager
        self.config_manager = ConfigManager()
        
        # Create launch options model
        self.launch_options = LaunchOptions()
        
        # Create profile manager
        self.profile_manager = ProfileManager()
        
        # Detect Steam location
        steam_dir = detect_steam_location()
        self.steam_directory = steam_dir
        
        if steam_dir:
            # Load installed games
            self.steam_games = SteamGame.find_steam_games(steam_dir)
            logger.info(f"Found {len(self.steam_games)} Steam games")
            
            # Get available Proton versions
            self.proton_versions = SteamGame.get_available_proton_versions(steam_dir)
            logger.info(f"Found {len(self.proton_versions)} Proton versions")
        else:
            self.steam_games = []
            self.proton_versions = []
            logger.warning("Steam directory not found, game detection disabled")
        
        # Currently selected game
        self.selected_game = None
        
        logger.info("Models initialized")
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Create main vertical box
        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_vbox)
        
        # Add header
        self._create_header()
        
        # Create a horizontal box for game selection and details
        game_details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.main_vbox.pack_start(game_details_box, False, False, 0)
        
        # Left side: Game selection
        game_select_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        game_details_box.pack_start(game_select_box, True, True, 0)
        
        # Add game selection combobox if games were found
        if self.steam_games:
            self._create_game_selector(game_select_box)
        
        # Right side: Game details and Proton controls
        self.game_details_frame = Gtk.Frame(label="Game Details")
        game_details_box.pack_start(self.game_details_frame, True, True, 0)
        
        # Create game details content
        self._create_game_details()
        
        # Add notebook (tabbed interface)
        self.notebook = Gtk.Notebook()
        self.main_vbox.pack_start(self.notebook, True, True, 0)
        
        # Add General tab
        self._add_general_tab()
        
        # Add a tab for each configuration in TAB_CONFIGS
        for tab_name, config in TAB_CONFIGS.items():
            self._add_tab(tab_name, config)
        
        # Add command display
        self._create_command_display()
        
        # Add Launch with Proton section (moved from game details)
        self._create_launch_section()
        
        # Add bottom button bar
        self._create_button_bar()
        
        # Add status bar
        self.status_bar = Gtk.Statusbar()
        self.status_bar.get_style_context().add_class("status-bar")
        self.status_context = self.status_bar.get_context_id("info")
        self.main_vbox.pack_end(self.status_bar, False, False, 0)
        
        # Update status
        self.status_bar.push(self.status_context, "Ready")
        
        logger.info("UI setup complete")
    
    def _create_header(self):
        """Create the header section."""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.main_vbox.pack_start(header_box, False, False, 0)
        
        # Title
        title_label = Gtk.Label(label="Steam Launch Options")
        title_label.get_style_context().add_class("header-label")
        header_box.pack_start(title_label, False, False, 0)
        
        # Subtitle
        subtitle_label = Gtk.Label(
            label="Customize your game launch command with tabs for overlays and enhancements"
        )
        header_box.pack_start(subtitle_label, False, False, 0)
    
    def _create_game_selector(self, parent_box):
        """Create the game selection combobox."""
        game_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        parent_box.pack_start(game_box, False, False, 5)
        
        # Label
        game_label = Gtk.Label(label="Selected Game:")
        game_box.pack_start(game_label, False, False, 5)
        
        # Create combobox for game selection
        game_store = Gtk.ListStore(str, str)  # name, app_id
        for game in sorted(self.steam_games, key=lambda g: g.name):
            game_store.append([game.name, game.app_id])
        
        self.game_combo = Gtk.ComboBox.new_with_model(game_store)
        renderer_text = Gtk.CellRendererText()
        self.game_combo.pack_start(renderer_text, True)
        self.game_combo.add_attribute(renderer_text, "text", 0)
        self.game_combo.connect("changed", self.on_game_selected)
        game_box.pack_start(self.game_combo, True, True, 0)
        
        # Add refresh button
        refresh_button = Gtk.Button(label="Refresh Games")
        refresh_button.connect("clicked", self.on_refresh_games)
        game_box.pack_start(refresh_button, False, False, 0)
    
    def _create_game_details(self):
        """Create the game details section."""
        # Create a vertical box for the details
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        details_box.set_border_width(10)
        self.game_details_frame.add(details_box)
        
        # Create a grid for displaying game details
        details_grid = Gtk.Grid()
        details_grid.set_column_spacing(10)
        details_grid.set_row_spacing(5)
        details_box.pack_start(details_grid, False, False, 0)
        
        # App ID
        app_id_label = Gtk.Label(label="Steam App ID:")
        app_id_label.set_halign(Gtk.Align.START)
        details_grid.attach(app_id_label, 0, 0, 1, 1)
        
        self.app_id_value = Gtk.Label(label="")
        self.app_id_value.set_halign(Gtk.Align.START)
        details_grid.attach(self.app_id_value, 1, 0, 1, 1)
        
        # Install directory
        install_dir_label = Gtk.Label(label="Install Directory:")
        install_dir_label.set_halign(Gtk.Align.START)
        details_grid.attach(install_dir_label, 0, 1, 1, 1)
        
        self.install_dir_value = Gtk.Label(label="")
        self.install_dir_value.set_halign(Gtk.Align.START)
        self.install_dir_value.set_ellipsize(2)  # Middle ellipsization
        details_grid.attach(self.install_dir_value, 1, 1, 1, 1)
        
        # Proton prefix
        proton_prefix_label = Gtk.Label(label="Proton Prefix:")
        proton_prefix_label.set_halign(Gtk.Align.START)
        details_grid.attach(proton_prefix_label, 0, 2, 1, 1)
        
        self.proton_prefix_value = Gtk.Label(label="")
        self.proton_prefix_value.set_halign(Gtk.Align.START)
        self.proton_prefix_value.set_ellipsize(2)  # Middle ellipsization
        details_grid.attach(self.proton_prefix_value, 1, 2, 1, 1)
        
        # Current Proton version
        proton_version_label = Gtk.Label(label="Current Proton:")
        proton_version_label.set_halign(Gtk.Align.START)
        details_grid.attach(proton_version_label, 0, 3, 1, 1)
        
        self.proton_version_value = Gtk.Label(label="")
        self.proton_version_value.set_halign(Gtk.Align.START)
        details_grid.attach(self.proton_version_value, 1, 3, 1, 1)
        
        # Open prefix button
        open_prefix_button = Gtk.Button(label="Open Prefix Folder")
        open_prefix_button.connect("clicked", self.on_open_prefix)
        details_box.pack_start(open_prefix_button, False, False, 5)
    
    def _add_general_tab(self):
        """Add the general options tab."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_border_width(10)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        tab_content = create_general_tab(self.launch_options)
        tab_content.get_style_context().add_class("tab-content")
        scrolled.add(tab_content)
        
        label = Gtk.Label(label="General")
        self.notebook.append_page(scrolled, label)
    
    def _add_tab(self, tab_name, config):
        """Add a tab to the notebook."""
        # Create a scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_border_width(10)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Check if required software is installed
        software_available = True
        if "software_requirement" in config:
            software = config["software_requirement"]
            software_available = check_software(software)
        
        # Create tab content
        tab_content = create_tab_content(tab_name, config, self.launch_options, software_available)
        tab_content.get_style_context().add_class("tab-content")
        scrolled.add(tab_content)
        
        # Add the tab to the notebook
        self.notebook.append_page(scrolled, Gtk.Label(label=tab_name))
    
    def _create_command_display(self):
        """Create the command display area."""
        # Create frame
        frame = Gtk.Frame(label="Generated Command")
        self.main_vbox.pack_start(frame, False, False, 5)
        
        # Create scrolled window for command text
        command_scroll = Gtk.ScrolledWindow()
        command_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        frame.add(command_scroll)
        
        # Create command text view
        self.command_textview = Gtk.TextView()
        self.command_textview.set_editable(False)
        self.command_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.command_textview.get_style_context().add_class("command-display")
        command_scroll.add(self.command_textview)
        
        # Create text buffer
        self.command_buffer = self.command_textview.get_buffer()
        
        # Add warnings area
        self.warnings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.main_vbox.pack_start(self.warnings_box, False, False, 0)
    
    def _create_launch_section(self):
        """Create the section for launching with Proton."""
        # Create frame
        frame = Gtk.Frame(label="Launch with Proton")
        self.main_vbox.pack_start(frame, False, False, 5)
        
        # Create box for contents
        launch_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        launch_box.set_border_width(10)
        frame.add(launch_box)
        
        # Create a horizontal box for Proton selection and launch button
        proton_launch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        launch_box.pack_start(proton_launch_box, False, False, 0)
        
        # Proton selection label
        proton_label = Gtk.Label(label="Proton Version:")
        proton_launch_box.pack_start(proton_label, False, False, 5)
        
        # Proton version combobox
        proton_store = Gtk.ListStore(str)
        for version in self.proton_versions:
            proton_store.append([version])
        
        self.proton_combo = Gtk.ComboBox.new_with_model(proton_store)
        renderer_text = Gtk.CellRendererText()
        self.proton_combo.pack_start(renderer_text, True)
        self.proton_combo.add_attribute(renderer_text, "text", 0)
        
        # Select the first item
        if len(self.proton_versions) > 0:
            self.proton_combo.set_active(0)
        
        proton_launch_box.pack_start(self.proton_combo, True, True, 0)
        
        # Use current command checkbox
        self.use_command_checkbox = Gtk.CheckButton(label="Use generated command options")
        self.use_command_checkbox.set_active(True)
        launch_box.pack_start(self.use_command_checkbox, False, False, 0)
        
        # Launch button
        launch_button = Gtk.Button(label="Launch Game")
        launch_button.connect("clicked", self.on_launch_with_proton)
        proton_launch_box.pack_start(launch_button, False, False, 0)
    
    def _create_button_bar(self):
        """Create the bottom button bar."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.main_vbox.pack_start(button_box, False, False, 0)
        
        # Add theme toggle button
        theme_button = Gtk.Button(label="Toggle Theme")
        theme_button.connect("clicked", self.on_theme_toggled)
        button_box.pack_start(theme_button, False, False, 0)
        
        # Add profiles button
        profiles_button = Gtk.Button(label="Profiles")
        profiles_button.connect("clicked", self.on_profiles_clicked)
        button_box.pack_start(profiles_button, False, False, 0)
        
        # Add reset button
        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.on_reset_clicked)
        button_box.pack_end(reset_button, False, False, 0)
        
        # Add save button
        save_button = Gtk.Button(label="Save to Steam")
        save_button.connect("clicked", self.on_save_clicked)
        button_box.pack_end(save_button, False, False, 0)
        
        # Add generate button
        generate_button = Gtk.Button(label="Generate Command")
        generate_button.connect("clicked", self.on_generate_clicked)
        button_box.pack_end(generate_button, False, False, 0)
    
    def update_command_display(self):
        """Update the command display with the current command."""
        command = self.launch_options.generate_command(TAB_CONFIGS)
        self.command_buffer.set_text(command)
        logger.info(f"Generated command: {command}")
        
        # Check for conflicts and issues
        self.update_warnings()
    
    def update_warnings(self):
        """Update the warnings display based on current options."""
        # Clear existing warnings
        for child in self.warnings_box.get_children():
            self.warnings_box.remove(child)
        
        # Get warnings for current options
        option_dict = {}
        
        # Add general toggles
        for key, value in self.launch_options.general_toggles.items():
            option_dict[key] = value
        
        # Add general inputs
        for key, value in self.launch_options.general_inputs.items():
            option_dict[key] = value
        
        warnings = validate_option_combinations(option_dict)
        
        # Display warnings
        for warning in warnings:
            label = Gtk.Label(label=f"⚠️ {warning}")
            label.get_style_context().add_class("warning-text")
            label.set_halign(Gtk.Align.START)
            self.warnings_box.pack_start(label, False, False, 0)
        
        self.warnings_box.show_all()
    
    def update_game_details(self, game):
        """Update the game details display."""
        if not game:
            self.app_id_value.set_text("")
            self.install_dir_value.set_text("")
            self.proton_prefix_value.set_text("")
            self.proton_version_value.set_text("")
            return
            
        # Update app ID - ensure it's a string
        self.app_id_value.set_text(str(game.app_id) if game.app_id else "")
        
        # Update install directory
        self.install_dir_value.set_text(game.install_dir if game.install_dir else "")
        
        # Update Proton prefix
        if self.steam_directory:
            proton_prefix = game.get_proton_prefix(self.steam_directory)
            self.proton_prefix_value.set_text(proton_prefix if proton_prefix else "None")
            
            # Update current Proton version
            proton_version = game.get_current_proton_version(self.steam_directory)
            self.proton_version_value.set_text(proton_version if proton_version else "Unknown")
            
        # Log the values for debugging
        logger.debug(f"Updating game details - App ID: {game.app_id}, Install Dir: {game.install_dir}, "
                    f"Prefix: {game.get_proton_prefix(self.steam_directory) if self.steam_directory else 'N/A'}")
    
    def load_game_options(self, game):
        """Load launch options for the selected game."""
        logger.debug(f"Loading options for game: {game.name if game else 'None'}, "
                    f"App ID: {game.app_id if game else 'None'}")
        
        self.selected_game = game
        
        # Always update game details first
        self.update_game_details(game)
        
        if game and game.launch_options:
            try:
                self.launch_options.parse_command(game.launch_options, TAB_CONFIGS)
                self.update_command_display()
                self.status_bar.push(
                    self.status_context, f"Loaded options for {game.name}"
                )
            except Exception as e:
                logger.error(f"Error parsing game launch options: {e}")
                self.status_bar.push(
                    self.status_context, f"Error loading options for {game.name}"
                )
        else:
            # Reset launch options if none exist
            self.launch_options.reset()
            self.update_command_display()
            if game:
                self.status_bar.push(
                    self.status_context, f"No saved options for {game.name}"
                )
    
    # Event handlers
    def on_game_selected(self, combo):
        """Handle game selection."""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            name, app_id = model[tree_iter][:2]
            
            # Find the game
            game = next((g for g in self.steam_games if g.app_id == app_id), None)
            if game:
                self.load_game_options(game)
    
    def on_refresh_games(self, button):
        """Handle refresh games button click."""
        logger.info("Refreshing games list")
        self.status_bar.push(self.status_context, "Refreshing games list...")
        
        # Re-detect Steam location
        steam_dir = detect_steam_location()
        self.steam_directory = steam_dir
        
        if steam_dir:
            # Reload games
            self.steam_games = SteamGame.find_steam_games(steam_dir)
            logger.info(f"Found {len(self.steam_games)} games")
            
            # Reload Proton versions
            self.proton_versions = SteamGame.get_available_proton_versions(steam_dir)
            logger.info(f"Found {len(self.proton_versions)} Proton versions")
            
            # Update game combobox
            game_store = self.game_combo.get_model()
            game_store.clear()
            
            for game in sorted(self.steam_games, key=lambda g: g.name):
                game_store.append([game.name, game.app_id])
            
            # Update Proton combobox
            proton_store = self.proton_combo.get_model()
            proton_store.clear()
            
            for version in self.proton_versions:
                proton_store.append([version])
            
            # Select the first Proton version
            if len(self.proton_versions) > 0:
                self.proton_combo.set_active(0)
            
            # Reset current game selection
            if len(self.steam_games) > 0:
                self.game_combo.set_active(0)
            else:
                # No games found, clear details
                self.update_game_details(None)
                self.selected_game = None
            
            self.status_bar.push(
                self.status_context, f"Found {len(self.steam_games)} games and {len(self.proton_versions)} Proton versions"
            )
        else:
            self.steam_games = []
            self.proton_versions = []
            
            # Clear game combobox
            if hasattr(self, 'game_combo'):
                game_store = self.game_combo.get_model()
                game_store.clear()
            
            # Clear Proton combobox
            if hasattr(self, 'proton_combo'):
                proton_store = self.proton_combo.get_model()
                proton_store.clear()
            
            # Clear game details
            self.update_game_details(None)
            self.selected_game = None
            
            self.status_bar.push(
                self.status_context, "Steam directory not found"
            )
    
    def on_theme_toggled(self, button):
        """Handle theme toggle button click."""
        # Get current theme
        current_theme = self.config_manager.get_setting("theme", "dark")
        
        # Toggle theme
        new_theme = "light" if current_theme == "dark" else "dark"
        
        # Apply new theme
        apply_theme(self, new_theme)
        
        # Save setting
        self.config_manager.set_setting("theme", new_theme)
        
        logger.info(f"Theme changed to {new_theme}")
        self.status_bar.push(self.status_context, f"Theme changed to {new_theme}")
    
    def on_profiles_clicked(self, button):
        """Handle profiles button click."""
        dialog = ProfileManagerDialog(self, self.profile_manager, self.launch_options)
        response = dialog.run()
        
        if response == Gtk.ResponseType.APPLY:
            # Profile was applied, update UI
            self.update_command_display()
            self.status_bar.push(self.status_context, "Profile applied")
        
        dialog.destroy()
    
    def on_generate_clicked(self, button):
        """Handle generate command button click."""
        self.update_command_display()
        self.status_bar.push(self.status_context, "Command generated")
    
    def on_save_clicked(self, button):
        """Handle save button click."""
        # Get the current game
        active_iter = self.game_combo.get_active_iter()
        if active_iter is None:
            self.status_bar.push(self.status_context, "No game selected")
            return
        
        model = self.game_combo.get_model()
        name, app_id = model[active_iter][:2]
        
        # Generate command
        command = self.launch_options.generate_command(TAB_CONFIGS)
        
        # Find the game
        game = next((g for g in self.steam_games if g.app_id == app_id), None)
        if game:
            # Update the game's launch options
            game.set_launch_options(command)
            
            # Save to Steam
            if self.steam_directory:
                success = SteamGame.save_launch_options(
                    self.steam_directory, app_id, command
                )
                if success:
                    self.status_bar.push(
                        self.status_context, f"Options saved for {name}"
                    )
                else:
                    self.status_bar.push(
                        self.status_context, 
                        f"Options updated in memory but could not save to Steam config"
                    )
            else:
                self.status_bar.push(
                    self.status_context,
                    "Steam directory not found, cannot save options"
                )
    
    def on_reset_clicked(self, button):
        """Handle reset button click."""
        # Reset launch options
        self.launch_options.reset()
        
        # Update command display
        self.update_command_display()
        
        self.status_bar.push(self.status_context, "Options reset")
    
    def on_launch_with_proton(self, button):
        """Handle launch with Proton button click."""
        if not self.selected_game:
            self.status_bar.push(self.status_context, "No game selected")
            return
        
        # Get selected Proton version
        active_iter = self.proton_combo.get_active_iter()
        if active_iter is None:
            self.status_bar.push(self.status_context, "No Proton version selected")
            return
            
        proton_version = self.proton_combo.get_model()[active_iter][0]
        
        # Create environment variables from current launch options
        env_vars = {}
        
        # Check if we should use the generated command options
        if self.use_command_checkbox.get_active():
            # Get the current generated command
            command = self.launch_options.generate_command(TAB_CONFIGS)
            
            # Extract environment variables from the command
            # This extracts variables in the format VAR=value from the command
            for part in command.split():
                if '=' in part:
                    key, value = part.split('=', 1)
                    if key.startswith("PROTON_") or key.startswith("STEAM_"):
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        env_vars[key] = value
        else:
            # Add environment variables from tab toggles
            for tab_name, toggles in self.launch_options.tab_toggles.items():
                for option, enabled in toggles.items():
                    if enabled and option.startswith("PROTON_"):
                        env_vars[option] = "1"
            
            # Add environment variables from tab inputs
            for tab_name, inputs in self.launch_options.tab_inputs.items():
                for option, value in inputs.items():
                    if option.startswith("PROTON_") and value:
                        env_vars[option] = value
        
        # Launch the game
        if self.steam_directory:
            logger.info(f"Launching game with env vars: {env_vars}")
            success = self.selected_game.launch_with_proton(
                proton_version, 
                self.steam_directory,
                env_vars
            )
            
            if success:
                self.status_bar.push(
                    self.status_context, 
                    f"Launched {self.selected_game.name} with {proton_version}"
                )
            else:
                self.status_bar.push(
                    self.status_context, 
                    f"Failed to launch {self.selected_game.name}"
                )
        else:
            self.status_bar.push(
                self.status_context,
                "Steam directory not found, cannot launch game"
            )
    
    def on_open_prefix(self, button):
        """Handle open prefix folder button click."""
        if not self.selected_game:
            self.status_bar.push(self.status_context, "No game selected")
            return
            
        if not self.steam_directory:
            self.status_bar.push(self.status_context, "Steam directory not found")
            return
            
        # Get the prefix path
        prefix_path = self.selected_game.get_proton_prefix(self.steam_directory)
        if not prefix_path:
            self.status_bar.push(self.status_context, "No Proton prefix found for this game")
            return
            
        # Open the prefix in the file manager
        try:
            # Try using xdg-open first (Linux standard)
            subprocess.Popen(["xdg-open", prefix_path])
            self.status_bar.push(self.status_context, f"Opened prefix folder: {prefix_path}")
        except Exception as e:
            logger.error(f"Error opening prefix folder: {e}")
            self.status_bar.push(self.status_context, f"Error opening prefix folder: {e}")
    
    def on_destroy(self, window):
        """Handle window close."""
        logger.info("Window closed")
        Gtk.main_quit()