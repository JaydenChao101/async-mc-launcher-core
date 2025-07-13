#!/usr/bin/env python3
"""
Fabric Launcher Example

This example demonstrates how to install and launch Minecraft with
Fabric mod loader using the async-mc-launcher-core library. It shows:

1. Fabric version discovery and selection
2. Automatic Fabric installation
3. Launching Minecraft with Fabric
4. Managing Fabric profiles and mods

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Java installation (recommended: Java 17+ for modern versions)
- Internet connection for downloading Fabric

Fabric is known for:
- Fast updates to new Minecraft versions
- Lightweight and performance-focused
- Excellent mod ecosystem
- Developer-friendly modding API
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from launcher_core import fabric, install, command, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound, UnsupportedVersion


class FabricLauncher:
    """Minecraft launcher with Fabric mod loader support."""
    
    def __init__(self, minecraft_dir: str):
        """
        Initialize the Fabric launcher.
        
        Args:
            minecraft_dir: Path to the .minecraft directory
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.logger = setup_logger(enable_console=True, level=logging.INFO)
        
        # Create necessary directories
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)
        (self.minecraft_dir / "mods").mkdir(exist_ok=True)
    
    async def get_supported_minecraft_versions(self, stable_only: bool = True) -> List[str]:
        """
        Get Minecraft versions supported by Fabric.
        
        Args:
            stable_only: Return only stable versions
            
        Returns:
            List of supported Minecraft versions
        """
        try:
            if stable_only:
                versions = await fabric.get_stable_minecraft_versions()
                self.logger.info(f"Found {len(versions)} stable Minecraft versions for Fabric")
            else:
                all_versions = await fabric.get_all_minecraft_versions()
                versions = [v["version"] for v in all_versions]
                self.logger.info(f"Found {len(versions)} total Minecraft versions for Fabric")
            
            return versions
            
        except Exception as e:
            self.logger.error(f"Failed to fetch supported Minecraft versions: {e}")
            return []
    
    async def get_latest_minecraft_version(self, stable_only: bool = True) -> Optional[str]:
        """Get the latest Minecraft version supported by Fabric."""
        try:
            if stable_only:
                version = await fabric.get_latest_stable_minecraft_version()
            else:
                version = await fabric.get_latest_minecraft_version()
            
            self.logger.info(f"Latest {'stable ' if stable_only else ''}Minecraft version: {version}")
            return version
            
        except Exception as e:
            self.logger.error(f"Failed to get latest Minecraft version: {e}")
            return None
    
    async def is_minecraft_version_supported(self, version: str) -> bool:
        """Check if a Minecraft version is supported by Fabric."""
        try:
            supported = await fabric.is_minecraft_version_supported(version)
            self.logger.info(f"Minecraft {version} Fabric support: {supported}")
            return supported
        except Exception as e:
            self.logger.error(f"Failed to check version support: {e}")
            return False
    
    async def get_fabric_loader_versions(self) -> List[Dict]:
        """Get available Fabric loader versions."""
        try:
            loaders = await fabric.get_all_loader_versions()
            self.logger.info(f"Found {len(loaders)} Fabric loader versions")
            return loaders
        except Exception as e:
            self.logger.error(f"Failed to fetch Fabric loader versions: {e}")
            return []
    
    async def get_latest_fabric_loader(self) -> Optional[str]:
        """Get the latest Fabric loader version."""
        try:
            loader_version = await fabric.get_latest_loader_version()
            self.logger.info(f"Latest Fabric loader: {loader_version}")
            return loader_version
        except Exception as e:
            self.logger.error(f"Failed to get latest Fabric loader: {e}")
            return None
    
    async def install_fabric(
        self,
        minecraft_version: str,
        loader_version: Optional[str] = None
    ) -> bool:
        """
        Install Fabric for a specific Minecraft version.
        
        Args:
            minecraft_version: Minecraft version to install Fabric for
            loader_version: Fabric loader version (latest if None)
            
        Returns:
            True if installation successful
        """
        try:
            # Check if Minecraft version is supported
            if not await self.is_minecraft_version_supported(minecraft_version):
                self.logger.error(f"Minecraft {minecraft_version} is not supported by Fabric")
                return False
            
            # Use latest loader if none specified
            if not loader_version:
                loader_version = await self.get_latest_fabric_loader()
                if not loader_version:
                    self.logger.error("Failed to get Fabric loader version")
                    return False
            
            self.logger.info(f"Installing Fabric {loader_version} for Minecraft {minecraft_version}...")
            
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
            
            # Install Fabric
            await fabric.install_fabric(
                minecraft_version,
                str(self.minecraft_dir),
                loader_version=loader_version,
                callback=callback
            )
            
            self.logger.info(f"✅ Successfully installed Fabric {loader_version} for Minecraft {minecraft_version}")
            return True
            
        except VersionNotFound:
            self.logger.error(f"❌ Minecraft version {minecraft_version} not found")
            return False
        except UnsupportedVersion:
            self.logger.error(f"❌ Minecraft version {minecraft_version} is unsupported by Fabric")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to install Fabric: {e}")
            return False
    
    async def get_installed_fabric_versions(self) -> List[str]:
        """Get list of installed Fabric versions."""
        installed = []
        versions_dir = self.minecraft_dir / "versions"
        
        if not versions_dir.exists():
            return installed
        
        for version_dir in versions_dir.iterdir():
            if version_dir.is_dir():
                version_name = version_dir.name
                # Check if it's a Fabric version
                if "fabric" in version_name.lower():
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
    
    async def launch_fabric(
        self,
        minecraft_version: str,
        loader_version: Optional[str] = None,
        username: str = "Player",
        memory: int = 3072,
        additional_jvm_args: Optional[List[str]] = None,
        credentials: Optional[_types.Credential] = None
    ) -> bool:
        """
        Launch Minecraft with Fabric.
        
        Args:
            minecraft_version: Minecraft version to launch
            loader_version: Fabric loader version (latest if None)
            username: Player username (for offline mode)
            memory: Memory allocation in MB
            additional_jvm_args: Additional JVM arguments
            credentials: Authentication credentials (uses offline if None)
            
        Returns:
            True if launch successful
        """
        try:
            # Check if Fabric is installed for this version
            installed_versions = await self.get_installed_fabric_versions()
            
            # Find matching installed version
            fabric_version_name = None
            for installed in installed_versions:
                if minecraft_version in installed and "fabric" in installed.lower():
                    fabric_version_name = installed
                    break
            
            if not fabric_version_name:
                self.logger.warning(f"Fabric not installed for Minecraft {minecraft_version}")
                install_choice = input("Install Fabric now? (Y/n): ").strip().lower()
                
                if install_choice != 'n':
                    if not await self.install_fabric(minecraft_version, loader_version):
                        return False
                    
                    # Find the newly installed version
                    updated_versions = await self.get_installed_fabric_versions()
                    for installed in updated_versions:
                        if minecraft_version in installed and "fabric" in installed.lower():
                            fabric_version_name = installed
                            break
                else:
                    return False
            
            if not fabric_version_name:
                self.logger.error("Failed to find installed Fabric version")
                return False
            
            # Use provided credentials or create offline ones
            if not credentials:
                credentials = self.create_offline_credential(username)
            
            # Set up JVM arguments (Fabric is lighter than Forge)
            jvm_args = [f"-Xmx{memory}M", f"-Xms{memory//2}M"]
            
            # Add Fabric-optimized JVM arguments
            jvm_args.extend([
                "-XX:+UnlockExperimentalVMOptions",
                "-XX:+UseG1GC",
                "-XX:G1NewSizePercent=20",
                "-XX:G1ReservePercent=20",
                "-XX:MaxGCPauseMillis=50",
                "-XX:G1HeapRegionSize=16M"
            ])
            
            if additional_jvm_args:
                jvm_args.extend(additional_jvm_args)
            
            # Create natives directory
            natives_dir = self.minecraft_dir / "natives" / fabric_version_name
            natives_dir.mkdir(parents=True, exist_ok=True)
            
            # Create launch options
            options: _types.MinecraftOptions = {
                "gameDirectory": str(self.minecraft_dir),
                "jvmArguments": jvm_args,
                "nativesDirectory": str(natives_dir),
            }
            
            self.logger.info(f"Generating launch command for Fabric...")
            self.logger.info(f"Version: {fabric_version_name}")
            self.logger.info(f"Memory allocation: {memory}MB")
            
            # Generate the launch command
            minecraft_command = await command.get_minecraft_command(
                fabric_version_name,
                str(self.minecraft_dir),
                options,
                Credential=credentials
            )
            
            self.logger.info("✅ Launch command generated successfully!")
            
            # Show launch information
            mods_dir = self.minecraft_dir / "mods"
            mod_count = len(list(mods_dir.glob("*.jar"))) if mods_dir.exists() else 0
            
            print(f"\n🎮 Ready to launch Minecraft with Fabric")
            print(f"   Version: {fabric_version_name}")
            print(f"   Player: {credentials.username}")
            print(f"   Memory: {memory}MB")
            print(f"   Mods Loaded: {mod_count}")
            
            # Ask user if they want to launch
            launch_choice = input("\nLaunch now? (Y/n): ").strip().lower()
            if launch_choice != 'n':
                print("🚀 Launching Minecraft with Fabric...")
                
                import subprocess
                process = subprocess.Popen(
                    minecraft_command,
                    cwd=str(self.minecraft_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                print(f"✅ Minecraft launched with PID: {process.pid}")
                print("\n📝 Fabric Notes:")
                print("   • Fabric mods go in the 'mods' folder")
                print("   • Fabric has excellent performance")
                print("   • Many popular mods are available")
                print("   • Use Fabric API for mod compatibility")
                
                return True
            else:
                print("Launch cancelled.")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to launch Fabric: {e}")
            return False


async def interactive_fabric_launcher():
    """Interactive Fabric launcher interface."""
    print("=== Minecraft Fabric Launcher ===")
    print("\nFabric is a lightweight, fast-updating mod loader for Minecraft.")
    print("Known for excellent performance and quick updates to new versions.")
    
    # Get Minecraft directory
    minecraft_dir = input("\nEnter Minecraft directory (or press Enter for default): ").strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")
    
    print(f"Using directory: {minecraft_dir}")
    
    # Create launcher
    launcher = FabricLauncher(minecraft_dir)
    
    while True:
        print("\n" + "="*50)
        print("Fabric Launcher Options:")
        print("1. Browse supported Minecraft versions")
        print("2. Check latest Minecraft version")
        print("3. Browse Fabric loader versions")
        print("4. Install Fabric")
        print("5. List installed Fabric versions")
        print("6. Launch Minecraft with Fabric")
        print("7. Manage mods folder")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            # Browse supported versions
            stable_only = input("Show only stable versions? (Y/n): ").strip().lower() != 'n'
            
            versions = await launcher.get_supported_minecraft_versions(stable_only)
            
            if versions:
                print(f"\n🎯 Supported Minecraft Versions ({'stable only' if stable_only else 'all'}):")
                # Show recent versions (last 15)
                recent_versions = versions[:15] if len(versions) > 15 else versions
                for i, version in enumerate(recent_versions, 1):
                    print(f"   {i:2d}. {version}")
                
                if len(versions) > 15:
                    print(f"   ... and {len(versions) - 15} more versions")
            else:
                print("❌ No supported versions found")
        
        elif choice == "2":
            # Check latest version
            stable_only = input("Check latest stable version? (Y/n): ").strip().lower() != 'n'
            
            latest = await launcher.get_latest_minecraft_version(stable_only)
            
            if latest:
                print(f"✅ Latest {'stable ' if stable_only else ''}Minecraft version: {latest}")
                
                install_choice = input("Install Fabric for this version? (y/N): ").strip().lower()
                if install_choice == 'y':
                    await launcher.install_fabric(latest)
            else:
                print("❌ Failed to get latest version")
        
        elif choice == "3":
            # Browse loader versions
            loaders = await launcher.get_fabric_loader_versions()
            
            if loaders:
                print(f"\n🔧 Fabric Loader Versions:")
                # Show recent loaders (last 10)
                recent_loaders = loaders[:10] if len(loaders) > 10 else loaders
                for i, loader in enumerate(recent_loaders, 1):
                    version = loader.get("version", "Unknown")
                    stable = " (stable)" if loader.get("stable", False) else ""
                    print(f"   {i:2d}. {version}{stable}")
                
                if len(loaders) > 10:
                    print(f"   ... and {len(loaders) - 10} more versions")
                
                # Show latest
                latest_loader = await launcher.get_latest_fabric_loader()
                if latest_loader:
                    print(f"\n✨ Latest loader: {latest_loader}")
            else:
                print("❌ No loader versions found")
        
        elif choice == "4":
            # Install Fabric
            minecraft_version = input("Enter Minecraft version: ").strip()
            
            if minecraft_version:
                # Check if version is supported
                supported = await launcher.is_minecraft_version_supported(minecraft_version)
                
                if supported:
                    loader_version = input("Enter Fabric loader version (or press Enter for latest): ").strip()
                    loader_version = loader_version if loader_version else None
                    
                    success = await launcher.install_fabric(minecraft_version, loader_version)
                    if not success:
                        print("❌ Installation failed")
                else:
                    print(f"❌ Minecraft {minecraft_version} is not supported by Fabric")
        
        elif choice == "5":
            # List installed versions
            installed = await launcher.get_installed_fabric_versions()
            
            print(f"\n💾 Installed Fabric Versions ({len(installed)} total):")
            if installed:
                for version in installed:
                    print(f"   🟢 {version}")
            else:
                print("   No Fabric versions installed")
        
        elif choice == "6":
            # Launch with Fabric
            minecraft_version = input("Enter Minecraft version: ").strip()
            
            if not minecraft_version:
                print("❌ Minecraft version required")
                continue
            
            # Get username
            username = input("Enter username (default: Player): ").strip()
            if not username:
                username = "Player"
            
            # Get memory
            memory_input = input("Enter memory in MB (default: 3072): ").strip()
            try:
                memory = int(memory_input) if memory_input else 3072
            except ValueError:
                memory = 3072
            
            # Get loader version (optional)
            loader_version = input("Enter Fabric loader version (or press Enter for auto): ").strip()
            loader_version = loader_version if loader_version else None
            
            # Launch
            success = await launcher.launch_fabric(
                minecraft_version, loader_version, username, memory
            )
            if not success:
                print("❌ Launch failed")
        
        elif choice == "7":
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
                print("\n   💡 Popular Fabric mod sources:")
                print("   • Modrinth (modrinth.com)")
                print("   • CurseForge (curseforge.com)")
                print("   • GitHub releases")
                print("\n   🔧 Essential Fabric mods:")
                print("   • Fabric API (required for most mods)")
                print("   • Sodium (performance)")
                print("   • Lithium (optimization)")
                print("   • Phosphor (lighting)")
        
        elif choice == "8":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main example function."""
    try:
        await interactive_fabric_launcher()
    except KeyboardInterrupt:
        print("\n\nFabric launcher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in Fabric launcher")


if __name__ == "__main__":
    asyncio.run(main())