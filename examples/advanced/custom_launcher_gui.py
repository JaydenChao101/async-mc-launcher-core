#!/usr/bin/env python3
"""
Custom GUI Launcher Example

This example demonstrates how to create a custom GUI Minecraft launcher
using the async-mc-launcher-core library with tkinter. It shows:

1. Building a modern GUI interface
2. Integrating async operations with tkinter
3. Managing multiple authentication methods
4. Profile management and switching
5. Real-time progress updates

Requirements:
- Python 3.10+
- async-mc-launcher-core
- tkinter (usually included with Python)
- asyncio support for GUI operations

Features:
- Multiple authentication methods
- Profile switching
- Version management
- Mod loader support
- Progress tracking
- Settings management
"""

import asyncio
import json
import logging
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional, Callable

from launcher_core import (
    install,
    command,
    _types,
    microsoft_account,
    forge,
    fabric,
    quilt,
)
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound


class AsyncTkinterHelper:
    """Helper class to run async operations in tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.loop = None
        self.thread = None

    def start_async_loop(self):
        """Start the async event loop in a separate thread."""

        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def run_async(self, coro, callback: Optional[Callable] = None):
        """Run an async coroutine and optionally call callback with result."""

        def done_callback(future):
            try:
                result = future.result()
                if callback:
                    self.root.after(0, lambda: callback(result))
            except Exception as e:
                self.root.after(0, lambda: self.handle_error(e))

        if self.loop:
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            future.add_done_callback(done_callback)

    def handle_error(self, error):
        """Handle async errors in the main thread."""
        messagebox.showerror("Error", f"An error occurred: {error}")

    def cleanup(self):
        """Clean up the async loop."""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)


class MinecraftProfile:
    """Represents a Minecraft launch profile."""

    def __init__(
        self,
        name: str,
        minecraft_version: str,
        mod_loader: str = "vanilla",
        mod_loader_version: str = "",
        memory: int = 2048,
        jvm_args: List[str] = None,
        auth_type: str = "offline",
        username: str = "Player",
    ):
        self.name = name
        self.minecraft_version = minecraft_version
        self.mod_loader = mod_loader  # vanilla, forge, fabric, quilt
        self.mod_loader_version = mod_loader_version
        self.memory = memory
        self.jvm_args = jvm_args or []
        self.auth_type = auth_type  # offline, microsoft
        self.username = username

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for saving."""
        return {
            "name": self.name,
            "minecraft_version": self.minecraft_version,
            "mod_loader": self.mod_loader,
            "mod_loader_version": self.mod_loader_version,
            "memory": self.memory,
            "jvm_args": self.jvm_args,
            "auth_type": self.auth_type,
            "username": self.username,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MinecraftProfile":
        """Create profile from dictionary."""
        return cls(
            name=data["name"],
            minecraft_version=data["minecraft_version"],
            mod_loader=data.get("mod_loader", "vanilla"),
            mod_loader_version=data.get("mod_loader_version", ""),
            memory=data.get("memory", 2048),
            jvm_args=data.get("jvm_args", []),
            auth_type=data.get("auth_type", "offline"),
            username=data.get("username", "Player"),
        )


class CustomMinecraftLauncher:
    """Custom GUI Minecraft Launcher."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Custom Minecraft Launcher")
        self.root.geometry("800x600")

        # Initialize async helper
        self.async_helper = AsyncTkinterHelper(self.root)
        self.async_helper.start_async_loop()

        # Initialize logger
        self.logger = setup_logger(enable_console=True, level=logging.INFO)

        # Configuration
        self.config_file = Path("launcher_config.json")
        self.profiles_file = Path("launcher_profiles.json")
        self.config = self.load_config()
        self.profiles: Dict[str, MinecraftProfile] = self.load_profiles()

        # Current state
        self.current_profile: Optional[MinecraftProfile] = None
        self.available_versions: List[str] = []

        # Create GUI
        self.create_widgets()
        self.load_initial_data()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self) -> Dict:
        """Load launcher configuration."""
        default_config = {
            "minecraft_directory": os.path.join(os.path.expanduser("~"), ".minecraft"),
            "java_executable": "",
            "last_profile": "",
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")

        return default_config

    def save_config(self):
        """Save launcher configuration."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def load_profiles(self) -> Dict[str, MinecraftProfile]:
        """Load saved profiles."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, "r") as f:
                    data = json.load(f)
                return {
                    name: MinecraftProfile.from_dict(profile_data)
                    for name, profile_data in data.items()
                }
            except Exception as e:
                self.logger.warning(f"Failed to load profiles: {e}")

        # Create default profile
        default_profile = MinecraftProfile("Default", "1.21.1")
        return {"Default": default_profile}

    def save_profiles(self):
        """Save profiles to file."""
        try:
            data = {name: profile.to_dict() for name, profile in self.profiles.items()}
            with open(self.profiles_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")

    def create_widgets(self):
        """Create the GUI widgets."""
        # Create main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main launcher tab
        self.launcher_frame = ttk.Frame(notebook)
        notebook.add(self.launcher_frame, text="Launcher")
        self.create_launcher_tab()

        # Profiles tab
        self.profiles_frame = ttk.Frame(notebook)
        notebook.add(self.profiles_frame, text="Profiles")
        self.create_profiles_tab()

        # Settings tab
        self.settings_frame = ttk.Frame(notebook)
        notebook.add(self.settings_frame, text="Settings")
        self.create_settings_tab()

    def create_launcher_tab(self):
        """Create the main launcher interface."""
        # Profile selection
        profile_frame = ttk.LabelFrame(self.launcher_frame, text="Profile")
        profile_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(profile_frame, text="Current Profile:").pack(side=tk.LEFT, padx=5)

        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            profile_frame, textvariable=self.profile_var, state="readonly"
        )
        self.profile_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_selected)

        ttk.Button(profile_frame, text="Refresh", command=self.refresh_profiles).pack(
            side=tk.RIGHT, padx=5
        )

        # Launch section
        launch_frame = ttk.LabelFrame(self.launcher_frame, text="Launch")
        launch_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Profile info
        info_frame = ttk.Frame(launch_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.info_text = tk.Text(info_frame, height=8, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(
            info_frame, orient=tk.VERTICAL, command=self.info_text.yview
        )
        self.info_text.configure(yscrollcommand=scrollbar.set)

        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Launch controls
        controls_frame = ttk.Frame(launch_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        self.launch_button = ttk.Button(
            controls_frame,
            text="Launch Minecraft",
            command=self.launch_minecraft,
            state=tk.DISABLED,
        )
        self.launch_button.pack(side=tk.LEFT, padx=5)

        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(controls_frame, textvariable=self.progress_var).pack(
            side=tk.LEFT, padx=10
        )

        self.progress_bar = ttk.Progressbar(controls_frame, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)

    def create_profiles_tab(self):
        """Create the profiles management interface."""
        # Profile list
        list_frame = ttk.LabelFrame(self.profiles_frame, text="Profiles")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Profile listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.profiles_listbox = tk.Listbox(listbox_frame)
        profiles_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.profiles_listbox.configure(yscrollcommand=profiles_scrollbar.set)
        profiles_scrollbar.configure(command=self.profiles_listbox.yview)

        self.profiles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        profiles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.profiles_listbox.bind("<<ListboxSelect>>", self.on_profile_listbox_select)

        # Profile buttons
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttons_frame, text="New Profile", command=self.new_profile).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(buttons_frame, text="Edit Profile", command=self.edit_profile).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            buttons_frame, text="Delete Profile", command=self.delete_profile
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            buttons_frame, text="Duplicate Profile", command=self.duplicate_profile
        ).pack(side=tk.LEFT, padx=2)

    def create_settings_tab(self):
        """Create the settings interface."""
        # Minecraft directory
        dir_frame = ttk.LabelFrame(self.settings_frame, text="Minecraft Directory")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)

        self.dir_var = tk.StringVar(value=self.config["minecraft_directory"])
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        ttk.Button(dir_frame, text="Browse", command=self.browse_minecraft_dir).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

        # Java executable
        java_frame = ttk.LabelFrame(self.settings_frame, text="Java Executable")
        java_frame.pack(fill=tk.X, padx=5, pady=5)

        self.java_var = tk.StringVar(value=self.config["java_executable"])
        java_entry = ttk.Entry(java_frame, textvariable=self.java_var)
        java_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        ttk.Button(java_frame, text="Browse", command=self.browse_java_executable).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

        # Save settings button
        ttk.Button(
            self.settings_frame, text="Save Settings", command=self.save_settings
        ).pack(pady=10)

    def load_initial_data(self):
        """Load initial data asynchronously."""
        self.refresh_profiles()
        self.async_helper.run_async(self.fetch_versions(), self.on_versions_loaded)

    async def fetch_versions(self) -> List[str]:
        """Fetch available Minecraft versions."""
        try:
            version_data = await install.get_version_list()
            versions = [v["id"] for v in version_data["versions"]]
            return versions[:20]  # Limit to recent versions
        except Exception as e:
            self.logger.error(f"Failed to fetch versions: {e}")
            return []

    def on_versions_loaded(self, versions: List[str]):
        """Handle loaded versions."""
        self.available_versions = versions
        self.logger.info(f"Loaded {len(versions)} versions")

    def refresh_profiles(self):
        """Refresh the profiles display."""
        # Update combo box
        profile_names = list(self.profiles.keys())
        self.profile_combo["values"] = profile_names

        # Update listbox
        self.profiles_listbox.delete(0, tk.END)
        for name in profile_names:
            self.profiles_listbox.insert(tk.END, name)

        # Select current or first profile
        if self.config["last_profile"] in profile_names:
            self.profile_var.set(self.config["last_profile"])
            self.current_profile = self.profiles[self.config["last_profile"]]
        elif profile_names:
            self.profile_var.set(profile_names[0])
            self.current_profile = self.profiles[profile_names[0]]

        self.update_profile_info()

    def on_profile_selected(self, event=None):
        """Handle profile selection."""
        profile_name = self.profile_var.get()
        if profile_name in self.profiles:
            self.current_profile = self.profiles[profile_name]
            self.config["last_profile"] = profile_name
            self.update_profile_info()

    def on_profile_listbox_select(self, event=None):
        """Handle profile selection in listbox."""
        selection = self.profiles_listbox.curselection()
        if selection:
            profile_name = self.profiles_listbox.get(selection[0])
            self.profile_var.set(profile_name)
            self.on_profile_selected()

    def update_profile_info(self):
        """Update the profile information display."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        if self.current_profile:
            info = f"""Profile: {self.current_profile.name}
Minecraft Version: {self.current_profile.minecraft_version}
Mod Loader: {self.current_profile.mod_loader}
Mod Loader Version: {self.current_profile.mod_loader_version or 'Latest'}
Memory: {self.current_profile.memory} MB
Authentication: {self.current_profile.auth_type}
Username: {self.current_profile.username}
JVM Arguments: {' '.join(self.current_profile.jvm_args) or 'Default'}"""

            self.info_text.insert(tk.END, info)
            self.launch_button.config(state=tk.NORMAL)
        else:
            self.info_text.insert(tk.END, "No profile selected")
            self.launch_button.config(state=tk.DISABLED)

        self.info_text.config(state=tk.DISABLED)

    def new_profile(self):
        """Create a new profile."""
        ProfileDialog(
            self.root, self.available_versions, callback=self.on_profile_created
        )

    def edit_profile(self):
        """Edit the selected profile."""
        selection = self.profiles_listbox.curselection()
        if selection:
            profile_name = self.profiles_listbox.get(selection[0])
            profile = self.profiles[profile_name]
            ProfileDialog(
                self.root,
                self.available_versions,
                profile=profile,
                callback=self.on_profile_edited,
            )

    def delete_profile(self):
        """Delete the selected profile."""
        selection = self.profiles_listbox.curselection()
        if selection:
            profile_name = self.profiles_listbox.get(selection[0])
            if len(self.profiles) > 1:  # Keep at least one profile
                if messagebox.askyesno(
                    "Delete Profile", f"Delete profile '{profile_name}'?"
                ):
                    del self.profiles[profile_name]
                    self.save_profiles()
                    self.refresh_profiles()
            else:
                messagebox.showwarning(
                    "Cannot Delete", "Cannot delete the last profile"
                )

    def duplicate_profile(self):
        """Duplicate the selected profile."""
        selection = self.profiles_listbox.curselection()
        if selection:
            profile_name = self.profiles_listbox.get(selection[0])
            original = self.profiles[profile_name]

            # Create copy with new name
            copy_name = f"{profile_name} (Copy)"
            counter = 1
            while copy_name in self.profiles:
                copy_name = f"{profile_name} (Copy {counter})"
                counter += 1

            copy_profile = MinecraftProfile(
                copy_name,
                original.minecraft_version,
                original.mod_loader,
                original.mod_loader_version,
                original.memory,
                original.jvm_args.copy(),
                original.auth_type,
                original.username,
            )

            self.profiles[copy_name] = copy_profile
            self.save_profiles()
            self.refresh_profiles()

    def on_profile_created(self, profile: MinecraftProfile):
        """Handle new profile creation."""
        self.profiles[profile.name] = profile
        self.save_profiles()
        self.refresh_profiles()

    def on_profile_edited(self, profile: MinecraftProfile):
        """Handle profile editing."""
        self.profiles[profile.name] = profile
        self.save_profiles()
        self.refresh_profiles()

    def browse_minecraft_dir(self):
        """Browse for Minecraft directory."""
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)

    def browse_java_executable(self):
        """Browse for Java executable."""
        executable = filedialog.askopenfilename(
            initialdir=(
                os.path.dirname(self.java_var.get()) if self.java_var.get() else ""
            ),
            filetypes=[("Executable files", "*.exe" if os.name == "nt" else "*")],
        )
        if executable:
            self.java_var.set(executable)

    def save_settings(self):
        """Save the current settings."""
        self.config["minecraft_directory"] = self.dir_var.get()
        self.config["java_executable"] = self.java_var.get()
        self.save_config()
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")

    def launch_minecraft(self):
        """Launch Minecraft with the current profile."""
        if not self.current_profile:
            messagebox.showerror("No Profile", "Please select a profile first")
            return

        self.launch_button.config(state=tk.DISABLED)
        self.progress_var.set("Preparing launch...")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start()

        self.async_helper.run_async(self.perform_launch(), self.on_launch_complete)

    async def perform_launch(self) -> bool:
        """Perform the actual launch process."""
        try:
            profile = self.current_profile
            minecraft_dir = self.config["minecraft_directory"]

            # Create offline Credential (would need Microsoft auth for real launcher)
            import uuid

            fake_uuid = str(uuid.uuid4())
            Credential = _types.Credential(
                access_token="offline", username=profile.username, uuid=fake_uuid
            )

            # Determine version to launch
            version_to_launch = profile.minecraft_version

            # Install mod loader if needed
            if profile.mod_loader == "forge":
                # Check if Forge is installed, install if needed
                pass  # Implementation would go here
            elif profile.mod_loader == "fabric":
                # Check if Fabric is installed, install if needed
                pass  # Implementation would go here
            elif profile.mod_loader == "quilt":
                # Check if Quilt is installed, install if needed
                pass  # Implementation would go here

            # Set up launch options
            jvm_args = [f"-Xmx{profile.memory}M", f"-Xms{profile.memory//2}M"]
            jvm_args.extend(profile.jvm_args)

            natives_dir = os.path.join(minecraft_dir, "natives", version_to_launch)
            os.makedirs(natives_dir, exist_ok=True)

            options: _types.MinecraftOptions = {
                "gameDirectory": minecraft_dir,
                "jvmArguments": jvm_args,
                "nativesDirectory": natives_dir,
            }

            # Generate launch command
            minecraft_command = await command.get_minecraft_command(
                version_to_launch, minecraft_dir, options, Credential=Credential
            )

            # Launch the game
            import subprocess

            process = subprocess.Popen(
                minecraft_command,
                cwd=minecraft_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.logger.info(f"Minecraft launched with PID: {process.pid}")
            return True

        except Exception as e:
            self.logger.error(f"Launch failed: {e}")
            return False

    def on_launch_complete(self, success: bool):
        """Handle launch completion."""
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.launch_button.config(state=tk.NORMAL)

        if success:
            self.progress_var.set("Launch successful!")
            messagebox.showinfo(
                "Launch Successful", "Minecraft has been launched successfully!"
            )
        else:
            self.progress_var.set("Launch failed")
            messagebox.showerror(
                "Launch Failed",
                "Failed to launch Minecraft. Check the logs for details.",
            )

    def on_closing(self):
        """Handle window closing."""
        self.save_config()
        self.save_profiles()
        self.async_helper.cleanup()
        self.root.destroy()

    def run(self):
        """Run the launcher."""
        self.root.mainloop()


class ProfileDialog:
    """Dialog for creating/editing profiles."""

    def __init__(
        self,
        parent,
        available_versions: List[str],
        profile: Optional[MinecraftProfile] = None,
        callback: Optional[Callable] = None,
    ):
        self.parent = parent
        self.available_versions = available_versions
        self.callback = callback
        self.result = None

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Profile Editor" if profile else "New Profile")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Initialize with existing profile data or defaults
        if profile:
            self.name_var = tk.StringVar(value=profile.name)
            self.version_var = tk.StringVar(value=profile.minecraft_version)
            self.loader_var = tk.StringVar(value=profile.mod_loader)
            self.loader_version_var = tk.StringVar(value=profile.mod_loader_version)
            self.memory_var = tk.IntVar(value=profile.memory)
            self.auth_var = tk.StringVar(value=profile.auth_type)
            self.username_var = tk.StringVar(value=profile.username)
            self.jvm_args_var = tk.StringVar(value=" ".join(profile.jvm_args))
        else:
            self.name_var = tk.StringVar()
            self.version_var = tk.StringVar()
            self.loader_var = tk.StringVar(value="vanilla")
            self.loader_version_var = tk.StringVar()
            self.memory_var = tk.IntVar(value=2048)
            self.auth_var = tk.StringVar(value="offline")
            self.username_var = tk.StringVar(value="Player")
            self.jvm_args_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets."""
        # Profile name
        ttk.Label(self.dialog, text="Profile Name:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.name_var).pack(
            fill=tk.X, padx=10, pady=5
        )

        # Minecraft version
        ttk.Label(self.dialog, text="Minecraft Version:").pack(
            anchor=tk.W, padx=10, pady=5
        )
        version_combo = ttk.Combobox(self.dialog, textvariable=self.version_var)
        version_combo["values"] = self.available_versions
        version_combo.pack(fill=tk.X, padx=10, pady=5)

        # Mod loader
        ttk.Label(self.dialog, text="Mod Loader:").pack(anchor=tk.W, padx=10, pady=5)
        loader_combo = ttk.Combobox(
            self.dialog, textvariable=self.loader_var, state="readonly"
        )
        loader_combo["values"] = ["vanilla", "forge", "fabric", "quilt"]
        loader_combo.pack(fill=tk.X, padx=10, pady=5)

        # Mod loader version
        ttk.Label(self.dialog, text="Mod Loader Version (optional):").pack(
            anchor=tk.W, padx=10, pady=5
        )
        ttk.Entry(self.dialog, textvariable=self.loader_version_var).pack(
            fill=tk.X, padx=10, pady=5
        )

        # Memory
        ttk.Label(self.dialog, text="Memory (MB):").pack(anchor=tk.W, padx=10, pady=5)
        memory_frame = ttk.Frame(self.dialog)
        memory_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Entry(memory_frame, textvariable=self.memory_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Label(memory_frame, text="MB").pack(side=tk.RIGHT)

        # Authentication type
        ttk.Label(self.dialog, text="Authentication:").pack(
            anchor=tk.W, padx=10, pady=5
        )
        auth_combo = ttk.Combobox(
            self.dialog, textvariable=self.auth_var, state="readonly"
        )
        auth_combo["values"] = ["offline", "microsoft"]
        auth_combo.pack(fill=tk.X, padx=10, pady=5)

        # Username
        ttk.Label(self.dialog, text="Username:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.username_var).pack(
            fill=tk.X, padx=10, pady=5
        )

        # JVM arguments
        ttk.Label(self.dialog, text="JVM Arguments:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Entry(self.dialog, textvariable=self.jvm_args_var).pack(
            fill=tk.X, padx=10, pady=5
        )

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_profile).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )

    def save_profile(self):
        """Save the profile."""
        # Validate inputs
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Profile name is required")
            return

        if not self.version_var.get().strip():
            messagebox.showerror("Validation Error", "Minecraft version is required")
            return

        # Create profile
        jvm_args = (
            self.jvm_args_var.get().split() if self.jvm_args_var.get().strip() else []
        )

        profile = MinecraftProfile(
            name=self.name_var.get().strip(),
            minecraft_version=self.version_var.get().strip(),
            mod_loader=self.loader_var.get(),
            mod_loader_version=self.loader_version_var.get().strip(),
            memory=self.memory_var.get(),
            jvm_args=jvm_args,
            auth_type=self.auth_var.get(),
            username=self.username_var.get().strip(),
        )

        if self.callback:
            self.callback(profile)

        self.dialog.destroy()


def main():
    """Main function to run the GUI launcher."""
    try:
        launcher = CustomMinecraftLauncher()
        launcher.run()
    except Exception as e:
        print(f"Failed to start launcher: {e}")
        logging.exception("Failed to start launcher")


if __name__ == "__main__":
    main()
