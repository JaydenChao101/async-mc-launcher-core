#!/usr/bin/env python3
"""
Version Management Example

This example demonstrates how to manage Minecraft versions using the
async-mc-launcher-core library. It shows how to:

1. List available versions with filtering
2. Get detailed version information
3. Download and install specific versions
4. Manage local version installations

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Internet connection for downloading
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from launcher_core import install, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound


class VersionManager:
    """Manages Minecraft versions - listing, downloading, and organizing."""
    
    def __init__(self, minecraft_dir: str):
        """
        Initialize the version manager.
        
        Args:
            minecraft_dir: Path to the .minecraft directory
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.versions_dir = self.minecraft_dir / "versions"
        self.logger = setup_logger(enable_console=True, level=logging.INFO)
        
        # Create directories if they don't exist
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_version_manifest(self) -> Dict:
        """Get the complete version manifest from Mojang."""
        try:
            manifest = await install.get_version_list()
            self.logger.info(f"Fetched manifest with {len(manifest['versions'])} versions")
            return manifest
        except Exception as e:
            self.logger.error(f"Failed to fetch version manifest: {e}")
            return {"versions": [], "latest": {}}
    
    def filter_versions(
        self, 
        versions: List[Dict], 
        version_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter versions by type and limit results.
        
        Args:
            versions: List of version dictionaries
            version_type: Filter by type ('release', 'snapshot', 'old_beta', 'old_alpha')
            limit: Maximum number of versions to return
            
        Returns:
            Filtered list of versions
        """
        filtered = versions
        
        if version_type:
            filtered = [v for v in filtered if v.get("type") == version_type]
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def format_version_info(self, version: Dict) -> str:
        """Format version information for display."""
        version_id = version.get("id", "Unknown")
        version_type = version.get("type", "unknown")
        release_time = version.get("releaseTime", "")
        
        # Parse and format release time
        try:
            if release_time:
                dt = datetime.fromisoformat(release_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d")
            else:
                formatted_time = "Unknown"
        except:
            formatted_time = "Unknown"
        
        # Create type indicator
        type_indicators = {
            "release": "🟢",
            "snapshot": "🟡", 
            "old_beta": "🔵",
            "old_alpha": "🟣"
        }
        indicator = type_indicators.get(version_type, "⚪")
        
        return f"{indicator} {version_id:<15} [{version_type:<8}] ({formatted_time})"
    
    async def list_available_versions(
        self, 
        version_type: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict]:
        """
        List available Minecraft versions.
        
        Args:
            version_type: Filter by version type
            limit: Maximum versions to show
            
        Returns:
            List of version dictionaries
        """
        manifest = await self.get_version_manifest()
        versions = manifest.get("versions", [])
        
        # Filter versions
        filtered_versions = self.filter_versions(versions, version_type, limit)
        
        print(f"\n📋 Available Minecraft Versions:")
        if version_type:
            print(f"   Filtered by type: {version_type}")
        print(f"   Showing {len(filtered_versions)} of {len(versions)} total versions\n")
        
        for version in filtered_versions:
            print(f"   {self.format_version_info(version)}")
        
        return filtered_versions
    
    def get_installed_versions(self) -> List[str]:
        """Get list of locally installed versions."""
        installed = []
        
        if not self.versions_dir.exists():
            return installed
        
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                json_file = version_dir / f"{version_dir.name}.json"
                if json_file.exists():
                    installed.append(version_dir.name)
        
        return sorted(installed)
    
    async def get_version_details(self, version_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific version.
        
        Args:
            version_id: The version ID to get details for
            
        Returns:
            Version details dictionary or None if not found
        """
        try:
            details = await install.get_version_info(version_id)
            return details
        except VersionNotFound:
            self.logger.error(f"Version {version_id} not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get version details for {version_id}: {e}")
            return None
    
    def display_version_details(self, details: Dict) -> None:
        """Display formatted version details."""
        version_id = details.get("id", "Unknown")
        version_type = details.get("type", "unknown")
        release_time = details.get("releaseTime", "")
        main_class = details.get("mainClass", "Unknown")
        
        # Format release time
        try:
            if release_time:
                dt = datetime.fromisoformat(release_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                formatted_time = "Unknown"
        except:
            formatted_time = "Unknown"
        
        # Count libraries
        libraries = details.get("libraries", [])
        library_count = len(libraries)
        
        # Get Java version requirement
        java_version = "Unknown"
        if "javaVersion" in details:
            java_version = details["javaVersion"].get("majorVersion", "Unknown")
        
        print(f"\n📦 Version Details: {version_id}")
        print(f"   Type: {version_type}")
        print(f"   Release Time: {formatted_time}")
        print(f"   Main Class: {main_class}")
        print(f"   Libraries: {library_count}")
        print(f"   Java Version: {java_version}")
        
        # Show assets info
        if "assetIndex" in details:
            assets = details["assetIndex"]
            print(f"   Assets: {assets.get('id', 'Unknown')} ({assets.get('totalSize', 0)} bytes)")
    
    async def install_version(self, version_id: str) -> bool:
        """
        Install a specific Minecraft version.
        
        Args:
            version_id: Version to install
            
        Returns:
            True if installation successful
        """
        try:
            # Check if already installed
            if version_id in self.get_installed_versions():
                self.logger.info(f"Version {version_id} already installed")
                return True
            
            self.logger.info(f"Installing Minecraft {version_id}...")
            
            # Create progress callbacks
            current_status = {"status": "", "progress": 0, "max": 0}
            
            def set_status(status: str) -> None:
                current_status["status"] = status
                print(f"Status: {status}")
            
            def set_progress(progress: int) -> None:
                current_status["progress"] = progress
                max_val = current_status["max"]
                if max_val > 0:
                    percentage = (progress / max_val) * 100
                    print(f"Progress: {progress}/{max_val} ({percentage:.1f}%)")
            
            def set_max(maximum: int) -> None:
                current_status["max"] = maximum
                print(f"Total items: {maximum}")
            
            callback: _types.CallbackDict = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max,
            }
            
            # Install the version
            await install.install_minecraft_version(
                version_id, str(self.minecraft_dir), callback
            )
            
            self.logger.info(f"✅ Successfully installed {version_id}")
            return True
            
        except VersionNotFound:
            self.logger.error(f"❌ Version {version_id} not found")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to install {version_id}: {e}")
            return False
    
    def uninstall_version(self, version_id: str) -> bool:
        """
        Uninstall a locally installed version.
        
        Args:
            version_id: Version to uninstall
            
        Returns:
            True if uninstallation successful
        """
        version_path = self.versions_dir / version_id
        
        if not version_path.exists():
            self.logger.warning(f"Version {version_id} not found locally")
            return False
        
        try:
            import shutil
            shutil.rmtree(version_path)
            self.logger.info(f"✅ Successfully uninstalled {version_id}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to uninstall {version_id}: {e}")
            return False


async def interactive_version_manager():
    """Interactive version management interface."""
    print("=== Minecraft Version Manager ===\n")
    
    # Get Minecraft directory
    minecraft_dir = input("Enter Minecraft directory (or press Enter for default): ").strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")
    
    print(f"Using directory: {minecraft_dir}")
    
    # Create version manager
    vm = VersionManager(minecraft_dir)
    
    while True:
        print("\n" + "="*50)
        print("Version Manager Options:")
        print("1. List available versions")
        print("2. List installed versions") 
        print("3. Get version details")
        print("4. Install version")
        print("5. Uninstall version")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            # List available versions
            type_filter = input("Filter by type (release/snapshot/old_beta/old_alpha) or press Enter for all: ").strip()
            if type_filter and type_filter not in ["release", "snapshot", "old_beta", "old_alpha"]:
                type_filter = None
            
            limit_input = input("Maximum versions to show (default 20): ").strip()
            try:
                limit = int(limit_input) if limit_input else 20
            except ValueError:
                limit = 20
            
            await vm.list_available_versions(type_filter, limit)
        
        elif choice == "2":
            # List installed versions
            installed = vm.get_installed_versions()
            print(f"\n💾 Locally Installed Versions ({len(installed)} total):")
            if installed:
                for version in installed:
                    print(f"   🟢 {version}")
            else:
                print("   No versions installed locally")
        
        elif choice == "3":
            # Get version details
            version_id = input("Enter version ID: ").strip()
            if version_id:
                details = await vm.get_version_details(version_id)
                if details:
                    vm.display_version_details(details)
                else:
                    print(f"❌ Could not get details for {version_id}")
        
        elif choice == "4":
            # Install version
            version_id = input("Enter version ID to install: ").strip()
            if version_id:
                print(f"\nInstalling {version_id}...")
                success = await vm.install_version(version_id)
                if not success:
                    print("Installation failed!")
        
        elif choice == "5":
            # Uninstall version
            installed = vm.get_installed_versions()
            if not installed:
                print("No versions installed to uninstall")
                continue
            
            print("\nInstalled versions:")
            for i, version in enumerate(installed, 1):
                print(f"{i}. {version}")
            
            choice_input = input("Enter version number or ID to uninstall: ").strip()
            
            if choice_input.isdigit() and 1 <= int(choice_input) <= len(installed):
                version_id = installed[int(choice_input) - 1]
            else:
                version_id = choice_input
            
            if version_id in installed:
                confirm = input(f"Really uninstall {version_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    vm.uninstall_version(version_id)
            else:
                print("Invalid version selection")
        
        elif choice == "6":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main example function."""
    try:
        await interactive_version_manager()
    except KeyboardInterrupt:
        print("\n\nVersion manager interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in version manager")


if __name__ == "__main__":
    asyncio.run(main())