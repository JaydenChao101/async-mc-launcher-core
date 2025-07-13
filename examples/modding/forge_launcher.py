#!/usr/bin/env python3
"""
Forge Launcher Example

This example demonstrates how to install and launch Minecraft with
Forge mod loader using the async-mc-launcher-core library. It shows:

1. Forge version discovery and selection
2. Automatic Forge installation
3. Launching Minecraft with Forge
4. Managing Forge profiles

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Java installation (recommended: Java 17+ for modern versions)
- Internet connection for downloading Forge

Note: Please consider supporting Forge development through their Patreon
if you're using this for automated installations.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from launcher_core import forge, install, command, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound, UnsupportedVersion


class ForgeLauncher:
    """Minecraft launcher with Forge mod loader support."""
    
    def __init__(self, minecraft_dir: str):
        """
        Initialize the Forge launcher.
        
        Args:
            minecraft_dir: Path to the .minecraft directory
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.logger = setup_logger(enable_console=True, level=logging.INFO)
        
        # Create necessary directories
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)
        (self.minecraft_dir / "mods").mkdir(exist_ok=True)
    
    async def list_available_forge_versions(self, minecraft_version: Optional[str] = None) -> List[str]:
        """
        List available Forge versions.
        
        Args:
            minecraft_version: Filter by Minecraft version (optional)
            
        Returns:
            List of available Forge versions
        """
        try:
            self.logger.info("Fetching available Forge versions...")
            all_versions = await forge.list_forge_versions()
            
            if minecraft_version:
                # Filter versions for specific Minecraft version
                filtered_versions = [v for v in all_versions if minecraft_version in v]
                self.logger.info(f"Found {len(filtered_versions)} Forge versions for Minecraft {minecraft_version}")
                return filtered_versions
            
            self.logger.info(f"Found {len(all_versions)} total Forge versions")
            return all_versions
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Forge versions: {e}")
            return []
    
    async def find_recommended_forge_version(self, minecraft_version: str) -> Optional[str]:
        """
        Find the recommended Forge version for a Minecraft version.
        
        Args:
            minecraft_version: Minecraft version (e.g., "1.21.1")
            
        Returns:
            Recommended Forge version or None if not found
        """
        try:
            forge_version = await forge.find_forge_version(minecraft_version)
            if forge_version:
                self.logger.info(f"Recommended Forge version for {minecraft_version}: {forge_version}")
            else:
                self.logger.warning(f"No Forge version found for Minecraft {minecraft_version}")
            return forge_version
        except Exception as e:
            self.logger.error(f"Failed to find Forge version: {e}")
            return None
    
    async def is_forge_version_valid(self, forge_version: str) -> bool:
        """Check if a Forge version is valid."""
        try:
            return await forge.is_forge_version_valid(forge_version)
        except Exception as e:
            self.logger.error(f"Failed to validate Forge version: {e}")
            return False
    
    async def supports_automatic_install(self, forge_version: str) -> bool:
        """Check if Forge version supports automatic installation."""
        try:
            return await forge.supports_automatic_install(forge_version)
        except Exception as e:
            self.logger.error(f"Failed to check automatic install support: {e}")
            return False
    
    async def install_forge(self, forge_version: str) -> bool:
        """
        Install a specific Forge version.
        
        Args:
            forge_version: Forge version to install
            
        Returns:
            True if installation successful
        """
        try:
            # Validate version first
            if not await self.is_forge_version_valid(forge_version):
                self.logger.error(f"Invalid Forge version: {forge_version}")
                return False
            
            self.logger.info(f"Installing Forge {forge_version}...")
            
            # Check if automatic installation is supported
            auto_install = await self.supports_automatic_install(forge_version)
            self.logger.info(f"Automatic installation supported: {auto_install}")
            
            # Create progress callbacks
            def set_status(status: str) -> None:
                self.logger.info(f"Status: {status}")
            
            def set_progress(progress: int) -> None:
                self.logger.info(f"Progress: {progress}")
            
            def set_max(maximum: int) -> None:
                self.logger.info(f"Total: {maximum}")
            
            callback: _types.CallbackDict = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max,
            }
            
            if auto_install:
                # Use automatic installation
                await forge.install_forge_version(
                    forge_version, str(self.minecraft_dir), callback
                )
            else:
                # Run manual installer
                self.logger.info("Running Forge installer...")
                await forge.run_forge_installer(
                    forge_version, str(self.minecraft_dir), callback
                )
            
            self.logger.info(f"✅ Successfully installed Forge {forge_version}")
            return True
            
        except VersionNotFound:
            self.logger.error(f"❌ Forge version {forge_version} not found")
            return False
        except UnsupportedVersion:
            self.logger.error(f"❌ Forge version {forge_version} is unsupported")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to install Forge {forge_version}: {e}")
            return False
    
    async def get_installed_forge_versions(self) -> List[str]:
        """Get list of installed Forge versions."""
        installed = []
        versions_dir = self.minecraft_dir / "versions"
        
        if not versions_dir.exists():
            return installed
        
        for version_dir in versions_dir.iterdir():
            if version_dir.is_dir():
                # Check if it's a Forge version
                version_name = version_dir.name
                if "forge" in version_name.lower():
                    json_file = version_dir / f"{version_name}.json"
                    if json_file.exists():
                        installed.append(version_name)
        
        return sorted(installed)
    
    def create_offline_credential(self, username: str = "Player") -> _types.Credential:
        """Create offline credentials for testing."""
        import uuid
        fake_uuid = str(uuid.uuid4())
        
        return _types.Credential(
            access_token="offline",
            username=username,
            uuid=fake_uuid
        )
    
    async def launch_forge(
        self,
        forge_version: str,
        username: str = "Player",
        memory: int = 4096,
        additional_jvm_args: Optional[List[str]] = None,
        credentials: Optional[_types.Credential] = None
    ) -> bool:
        """
        Launch Minecraft with Forge.
        
        Args:
            forge_version: Forge version to launch
            username: Player username (for offline mode)
            memory: Memory allocation in MB
            additional_jvm_args: Additional JVM arguments
            credentials: Authentication credentials (uses offline if None)
            
        Returns:
            True if launch successful
        """
        try:
            # Get the installed version name
            installed_version = await forge.forge_to_installed_version(forge_version)
            
            # Check if version is installed
            installed_versions = await self.get_installed_forge_versions()
            if installed_version not in installed_versions:
                self.logger.warning(f"Forge version {forge_version} not installed")
                install_choice = input("Install it now? (Y/n): ").strip().lower()
                
                if install_choice != 'n':
                    if not await self.install_forge(forge_version):
                        return False
                else:
                    return False
            
            # Use provided credentials or create offline ones
            if not credentials:
                credentials = self.create_offline_credential(username)
            
            # Set up JVM arguments (Forge typically needs more memory)
            jvm_args = [f"-Xmx{memory}M", f"-Xms{memory//2}M"]
            
            # Add Forge-specific JVM arguments
            jvm_args.extend([
                "-XX:+UnlockExperimentalVMOptions",
                "-XX:+UseG1GC",
                "-XX:G1NewSizePercent=20",
                "-XX:G1ReservePercent=20",
                "-XX:MaxGCPauseMillis=50",
                "-XX:G1HeapRegionSize=32M"
            ])
            
            if additional_jvm_args:
                jvm_args.extend(additional_jvm_args)
            
            # Create natives directory
            natives_dir = self.minecraft_dir / "natives" / installed_version
            natives_dir.mkdir(parents=True, exist_ok=True)
            
            # Create launch options
            options: _types.MinecraftOptions = {
                "gameDirectory": str(self.minecraft_dir),
                "jvmArguments": jvm_args,
                "nativesDirectory": str(natives_dir),
            }
            
            self.logger.info(f"Generating launch command for Forge {forge_version}...")
            self.logger.info(f"Installed version: {installed_version}")
            self.logger.info(f"Memory allocation: {memory}MB")
            
            # Generate the launch command
            minecraft_command = await command.get_minecraft_command(
                installed_version,
                str(self.minecraft_dir),
                options,
                Credential=credentials
            )
            
            self.logger.info("✅ Launch command generated successfully!")
            
            # Show launch information
            mods_dir = self.minecraft_dir / "mods"
            mod_count = len(list(mods_dir.glob("*.jar"))) if mods_dir.exists() else 0
            
            print(f"\n🎮 Ready to launch Minecraft with Forge")
            print(f"   Forge Version: {forge_version}")
            print(f"   Minecraft Version: {installed_version}")
            print(f"   Player: {credentials.username}")
            print(f"   Memory: {memory}MB")
            print(f"   Mods Loaded: {mod_count}")
            
            # Ask user if they want to launch
            launch_choice = input("\nLaunch now? (Y/n): ").strip().lower()
            if launch_choice != 'n':
                print("🚀 Launching Minecraft with Forge...")
                
                import subprocess
                process = subprocess.Popen(
                    minecraft_command,
                    cwd=str(self.minecraft_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                print(f"✅ Minecraft launched with PID: {process.pid}")
                print("\n📝 Forge Notes:")
                print("   • Mods should be placed in the 'mods' folder")
                print("   • First launch may take longer (Forge setup)")
                print("   • Check logs if mods don't load properly")
                print("   • Some mods may require specific Forge versions")
                
                return True
            else:
                print("Launch cancelled.")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to launch Forge: {e}")
            return False


async def interactive_forge_launcher():
    """Interactive Forge launcher interface."""
    print("=== Minecraft Forge Launcher ===")
    print("\nForge is a popular mod loader for Minecraft.")
    print("This launcher helps you install and run Minecraft with Forge.")
    
    # Show Forge support note
    print("\n📝 Note from Forge developers:")
    print("Please consider supporting Forge development through:")
    print("https://www.patreon.com/LexManos/")
    
    # Get Minecraft directory
    minecraft_dir = input("\nEnter Minecraft directory (or press Enter for default): ").strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")
    
    print(f"Using directory: {minecraft_dir}")
    
    # Create launcher
    launcher = ForgeLauncher(minecraft_dir)
    
    while True:
        print("\n" + "="*50)
        print("Forge Launcher Options:")
        print("1. Browse available Forge versions")
        print("2. Find recommended Forge version")
        print("3. Install Forge version")
        print("4. List installed Forge versions")
        print("5. Launch Minecraft with Forge")
        print("6. Manage mods folder")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            # Browse Forge versions
            minecraft_version = input("Filter by Minecraft version (or press Enter for all): ").strip()
            minecraft_version = minecraft_version if minecraft_version else None
            
            versions = await launcher.list_available_forge_versions(minecraft_version)
            
            if versions:
                print(f"\n🔧 Available Forge Versions:")
                # Show recent versions (last 10)
                recent_versions = versions[:10] if len(versions) > 10 else versions
                for i, version in enumerate(recent_versions, 1):
                    print(f"   {i:2d}. {version}")
                
                if len(versions) > 10:
                    print(f"   ... and {len(versions) - 10} more versions")
            else:
                print("❌ No Forge versions found")
        
        elif choice == "2":
            # Find recommended version
            minecraft_version = input("Enter Minecraft version (e.g., 1.21.1): ").strip()
            
            if minecraft_version:
                recommended = await launcher.find_recommended_forge_version(minecraft_version)
                
                if recommended:
                    print(f"✅ Recommended Forge version: {recommended}")
                    
                    install_choice = input("Install this version? (y/N): ").strip().lower()
                    if install_choice == 'y':
                        await launcher.install_forge(recommended)
                else:
                    print(f"❌ No Forge version found for Minecraft {minecraft_version}")
        
        elif choice == "3":
            # Install Forge version
            forge_version = input("Enter Forge version to install: ").strip()
            
            if forge_version:
                success = await launcher.install_forge(forge_version)
                if not success:
                    print("❌ Installation failed")
        
        elif choice == "4":
            # List installed versions
            installed = await launcher.get_installed_forge_versions()
            
            print(f"\n💾 Installed Forge Versions ({len(installed)} total):")
            if installed:
                for version in installed:
                    print(f"   🟢 {version}")
            else:
                print("   No Forge versions installed")
        
        elif choice == "5":
            # Launch with Forge
            installed = await launcher.get_installed_forge_versions()
            
            if not installed:
                print("❌ No Forge versions installed")
                continue
            
            print(f"\nInstalled Forge versions:")
            for i, version in enumerate(installed, 1):
                print(f"{i}. {version}")
            
            # Get version selection
            version_choice = input("Enter version number or name: ").strip()
            
            if version_choice.isdigit() and 1 <= int(version_choice) <= len(installed):
                selected_version = installed[int(version_choice) - 1]
                # Extract forge version from installed version name
                forge_version = selected_version.split('-forge-')[1] if '-forge-' in selected_version else selected_version
            else:
                forge_version = version_choice
            
            # Get username
            username = input("Enter username (default: Player): ").strip()
            if not username:
                username = "Player"
            
            # Get memory
            memory_input = input("Enter memory in MB (default: 4096): ").strip()
            try:
                memory = int(memory_input) if memory_input else 4096
            except ValueError:
                memory = 4096
            
            # Launch
            success = await launcher.launch_forge(forge_version, username, memory)
            if not success:
                print("❌ Launch failed")
        
        elif choice == "6":
            # Manage mods folder
            mods_dir = launcher.minecraft_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            mod_files = list(mods_dir.glob("*.jar"))
            
            print(f"\n📁 Mods Folder: {mods_dir}")
            print(f"   Total mods: {len(mod_files)}")
            
            if mod_files:
                print("\n   Installed mods:")
                for mod_file in mod_files[:10]:  # Show first 10
                    size_mb = mod_file.stat().st_size / (1024 * 1024)
                    print(f"   • {mod_file.name} ({size_mb:.1f} MB)")
                
                if len(mod_files) > 10:
                    print(f"   ... and {len(mod_files) - 10} more mods")
            else:
                print("   No mods installed")
                print("\n   💡 To add mods:")
                print("   1. Download .jar mod files")
                print(f"   2. Place them in: {mods_dir}")
                print("   3. Launch Minecraft with Forge")
        
        elif choice == "7":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main example function."""
    try:
        await interactive_forge_launcher()
    except KeyboardInterrupt:
        print("\n\nForge launcher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in Forge launcher")


if __name__ == "__main__":
    asyncio.run(main())