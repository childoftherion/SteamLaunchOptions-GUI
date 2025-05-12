"""
Profile manager dialog for SteamLauncherGUI.
"""

import logging
import time
import gi
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from steamlaunchergui.models import Profile

logger = logging.getLogger(__name__)

class ProfileManagerDialog(Gtk.Dialog):
    """Dialog for managing profiles."""
    
    def __init__(self, parent, profile_manager, launch_options):
        """
        Initialize the profile manager dialog.
        
        Args:
            parent: Parent window
            profile_manager: ProfileManager instance
            launch_options: Current LaunchOptions instance
        """
        super().__init__(
            title="Profile Manager",
            transient_for=parent,
            flags=0
        )
        
        self.set_default_size(500, 400)
        self.profile_manager = profile_manager
        self.launch_options = launch_options
        
        # Add buttons
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.add_button("Apply Selected", Gtk.ResponseType.APPLY)
        
        # Set up the dialog content
        self._setup_ui()
        
        # Refresh the profile list
        self.refresh_profiles()
        
        # Show all widgets
        self.show_all()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        content_area = self.get_content_area()
        content_area.set_border_width(10)
        content_area.set_spacing(10)
        
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_area.add(main_box)
        
        # Create profile list
        self._create_profile_list(main_box)
        
        # Create action buttons
        self._create_action_buttons(main_box)
        
        # Create profile details section
        self._create_profile_details(main_box)
    
    def _create_profile_list(self, parent_box):
        """Create the profile list section."""
        # Create list frame
        list_frame = Gtk.Frame(label="Profiles")
        parent_box.pack_start(list_frame, True, True, 0)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        list_frame.add(scrolled)
        
        # Create list store
        self.profile_store = Gtk.ListStore(str, str, str)  # name, description, created_at
        
        # Create tree view
        self.profile_view = Gtk.TreeView(model=self.profile_store)
        self.profile_view.set_headers_visible(True)
        
        # Create columns
        name_column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        name_column.set_sort_column_id(0)
        name_column.set_resizable(True)
        name_column.set_expand(True)
        self.profile_view.append_column(name_column)
        
        desc_column = Gtk.TreeViewColumn("Description", Gtk.CellRendererText(), text=1)
        desc_column.set_resizable(True)
        desc_column.set_expand(True)
        self.profile_view.append_column(desc_column)
        
        date_column = Gtk.TreeViewColumn("Created", Gtk.CellRendererText(), text=2)
        date_column.set_sort_column_id(2)
        self.profile_view.append_column(date_column)
        
        # Connect selection signal
        select = self.profile_view.get_selection()
        select.connect("changed", self.on_profile_selection_changed)
        
        scrolled.add(self.profile_view)
    
    def _create_action_buttons(self, parent_box):
        """Create action buttons section."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        parent_box.pack_start(button_box, False, False, 0)
        
        # Add new profile button
        new_button = Gtk.Button(label="New")
        new_button.connect("clicked", self.on_new_profile_clicked)
        button_box.pack_start(new_button, True, True, 0)
        
        # Add save profile button
        save_button = Gtk.Button(label="Save Current")
        save_button.connect("clicked", self.on_save_profile_clicked)
        button_box.pack_start(save_button, True, True, 0)
        
        # Add delete profile button
        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self.on_delete_profile_clicked)
        button_box.pack_start(delete_button, True, True, 0)
        
        # Add export button
        export_button = Gtk.Button(label="Export")
        export_button.connect("clicked", self.on_export_profile_clicked)
        button_box.pack_start(export_button, True, True, 0)
        
        # Add import button
        import_button = Gtk.Button(label="Import")
        import_button.connect("clicked", self.on_import_profile_clicked)
        button_box.pack_start(import_button, True, True, 0)
    
    def _create_profile_details(self, parent_box):
        """Create profile details section."""
        details_frame = Gtk.Frame(label="Profile Details")
        parent_box.pack_start(details_frame, False, False, 0)
        
        # Create grid for details
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(5)
        grid.set_border_width(10)
        details_frame.add(grid)
        
        # Name row
        name_label = Gtk.Label(label="Name:")
        name_label.set_halign(Gtk.Align.START)
        grid.attach(name_label, 0, 0, 1, 1)
        
        self.name_entry = Gtk.Entry()
        self.name_entry.set_hexpand(True)
        grid.attach(self.name_entry, 1, 0, 1, 1)
        
        # Description row
        desc_label = Gtk.Label(label="Description:")
        desc_label.set_halign(Gtk.Align.START)
        grid.attach(desc_label, 0, 1, 1, 1)
        
        self.desc_entry = Gtk.Entry()
        self.desc_entry.set_hexpand(True)
        grid.attach(self.desc_entry, 1, 1, 1, 1)
        
        # Update button
        update_button = Gtk.Button(label="Update Details")
        update_button.connect("clicked", self.on_update_details_clicked)
        grid.attach(update_button, 1, 2, 1, 1)
    
    def refresh_profiles(self):
        """Refresh the profile list from the profile manager."""
        # Clear the list store
        self.profile_store.clear()
        
        # Load profiles
        profiles = self.profile_manager.get_profiles()
        
        # Add profiles to list store
        for profile in sorted(profiles, key=lambda p: p.name):
            # Format created_at date
            created_at = time.strftime(
                "%Y-%m-%d %H:%M", time.localtime(profile.created_at)
            )
            
            self.profile_store.append([profile.name, profile.description, created_at])
    
    # Event handlers
    def on_profile_selection_changed(self, selection):
        """Handle profile selection change."""
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            name = model[treeiter][0]
            profile = self.profile_manager.get_profile(name)
            if profile:
                self.name_entry.set_text(profile.name)
                self.desc_entry.set_text(profile.description)
    
    def on_new_profile_clicked(self, button):
        """Handle new profile button click."""
        # Create a dialog to get the profile name
        dialog = Gtk.Dialog(
            title="New Profile",
            transient_for=self,
            flags=0
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Create", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        # Add content
        content_area = dialog.get_content_area()
        content_area.set_border_width(10)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(5)
        content_area.add(grid)
        
        # Name field
        name_label = Gtk.Label(label="Profile Name:")
        name_label.set_halign(Gtk.Align.START)
        grid.attach(name_label, 0, 0, 1, 1)
        
        name_entry = Gtk.Entry()
        name_entry.set_activates_default(True)
        grid.attach(name_entry, 1, 0, 1, 1)
        
        # Description field
        desc_label = Gtk.Label(label="Description:")
        desc_label.set_halign(Gtk.Align.START)
        grid.attach(desc_label, 0, 1, 1, 1)
        
        desc_entry = Gtk.Entry()
        grid.attach(desc_entry, 1, 1, 1, 1)
        
        # Show dialog
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            name = name_entry.get_text()
            description = desc_entry.get_text()
            
            if name:
                # Create a new profile with current launch options
                profile = Profile(name, description)
                profile.update(self.launch_options)
                
                # Save the profile
                self.profile_manager.save_profile(profile)
                
                # Refresh the list
                self.refresh_profiles()
        
        dialog.destroy()
    
    def on_save_profile_clicked(self, button):
        """Handle save profile button click."""
        # Get selected profile
        selection = self.profile_view.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            # Update existing profile
            name = model[treeiter][0]
            profile = self.profile_manager.get_profile(name)
            
            if profile:
                # Update with current launch options
                profile.update(self.launch_options)
                
                # Save the profile
                self.profile_manager.save_profile(profile)
                
                # Show message
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Profile '{name}' updated"
                )
                dialog.run()
                dialog.destroy()
            else:
                logger.error(f"Profile not found: {name}")
        else:
            # No profile selected, prompt to create new
            self.on_new_profile_clicked(button)
    
    def on_delete_profile_clicked(self, button):
        """Handle delete profile button click."""
        # Get selected profile
        selection = self.profile_view.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            name = model[treeiter][0]
            
            # Confirm deletion
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Delete profile '{name}'?"
            )
            dialog.format_secondary_text(
                "This action cannot be undone."
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                # Delete the profile
                success = self.profile_manager.delete_profile(name)
                
                if success:
                    # Refresh the list
                    self.refresh_profiles()
                    
                    # Clear the detail fields
                    self.name_entry.set_text("")
                    self.desc_entry.set_text("")
                else:
                    # Show error
                    error_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text="Failed to delete profile"
                    )
                    error_dialog.run()
                    error_dialog.destroy()
    
    def on_export_profile_clicked(self, button):
        """Handle export profile button click."""
        # Get selected profile
        selection = self.profile_view.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            name = model[treeiter][0]
            
            # Create file chooser dialog
            dialog = Gtk.FileChooserDialog(
                title="Export Profile",
                parent=self,
                action=Gtk.FileChooserAction.SAVE
            )
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Export", Gtk.ResponseType.OK)
            
            # Add filters
            filter_json = Gtk.FileFilter()
            filter_json.set_name("JSON files")
            filter_json.add_pattern("*.json")
            dialog.add_filter(filter_json)
            
            # Set default filename
            dialog.set_current_name(f"{name}.json")
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                filepath = Path(dialog.get_filename())
                
                # Export the profile
                success = self.profile_manager.export_profile(name, filepath)
                
                if success:
                    # Show success message
                    success_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Profile exported to {filepath}"
                    )
                    success_dialog.run()
                    success_dialog.destroy()
                else:
                    # Show error
                    error_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text="Failed to export profile"
                    )
                    error_dialog.run()
                    error_dialog.destroy()
            
            dialog.destroy()
    
    def on_import_profile_clicked(self, button):
        """Handle import profile button click."""
        # Create file chooser dialog
        dialog = Gtk.FileChooserDialog(
            title="Import Profile",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Import", Gtk.ResponseType.OK)
        
        # Add filters
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = Path(dialog.get_filename())
            
            # Import the profile
            profile = self.profile_manager.import_profile(filepath)
            
            if profile:
                # Refresh the list
                self.refresh_profiles()
                
                # Show success message
                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Profile '{profile.name}' imported"
                )
                success_dialog.run()
                success_dialog.destroy()
            else:
                # Show error
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Failed to import profile"
                )
                error_dialog.run()
                error_dialog.destroy()
        
        dialog.destroy()
    
    def on_update_details_clicked(self, button):
        """Handle update details button click."""
        # Get selected profile
        selection = self.profile_view.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            old_name = model[treeiter][0]
            new_name = self.name_entry.get_text()
            new_desc = self.desc_entry.get_text()
            
            profile = self.profile_manager.get_profile(old_name)
            if profile:
                # Update profile
                if old_name != new_name:
                    # We need to create a new profile and delete the old one
                    # since the name is the key
                    new_profile = Profile(new_name, new_desc, profile.launch_options)
                    new_profile.created_at = profile.created_at
                    new_profile.updated_at = time.time()
                    
                    # Save new profile
                    self.profile_manager.save_profile(new_profile)
                    
                    # Delete old profile
                    self.profile_manager.delete_profile(old_name)
                else:
                    # Just update the description
                    profile.description = new_desc
                    profile.updated_at = time.time()
                    
                    # Save profile
                    self.profile_manager.save_profile(profile)
                
                # Refresh the list
                self.refresh_profiles()
            else:
                logger.error(f"Profile not found: {old_name}")
        else:
            # Show warning
            warning_dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No profile selected"
            )
            warning_dialog.run()
            warning_dialog.destroy()