#!/usr/bin/env python3
"""
Quilt Launcher Example

This example demonstrates how to install and launch Minecraft with
Quilt mod loader using the async-mc-launcher-core library. It shows:

1. Quilt version discovery and selection
2. Automatic Quilt installation
3. Launching Minecraft with Quilt
4. Managing Quilt profiles and mods

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Java installation (recommended: Java 17+ for modern versions)
- Internet connection for downloading Quilt

Quilt is known for:
- Being a Fabric fork with additional features
- Backward compatibility with most Fabric mods
- Enhanced modding capabilities
- Community-driven development
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from launcher_core import quilt, install, command, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound, UnsupportedVersion


class QuiltLauncher:
    """Minecraft launcher with Quilt mod loader support."""

    def __init__(self, minecraft_dir: str):
        """
        Initialize the Quilt launcher.

        Args:
            minecraft_dir: Path to the .minecraft directory
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.logger = setup_logger(enable_console=True, level=logging.INFO)

        # Create necessary directories
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)
        (self.minecraft_dir / "mods").mkdir(exist_ok=True)

    async def get_supported_minecraft_versions(
        self, stable_only: bool = True
    ) -> List[str]:
        """
        Get Minecraft versions supported by Quilt.

        Args:
            stable_only: Return only stable versions

        Returns:
            List of supported Minecraft versions
        """
        try:
            if stable_only:
                versions = await quilt.get_stable_minecraft_versions()
                self.logger.info(
                    f"Found {len(versions)} stable Minecraft versions for Quilt"
                )
            else:
                all_versions = await quilt.get_all_minecraft_versions()
                versions = [v["version"] for v in all_versions]
                self.logger.info(
                    f"Found {len(versions)} total Minecraft versions for Quilt"
                )

            return versions

        except Exception as e:
            self.logger.error(f"Failed to fetch supported Minecraft versions: {e}")
            return []

    async def get_latest_minecraft_version(
        self, stable_only: bool = True
    ) -> Optional[str]:
        """Get the latest Minecraft version supported by Quilt."""
        try:
            if stable_only:
                version = await quilt.get_latest_stable_minecraft_version()
            else:
                version = await quilt.get_latest_minecraft_version()

            self.logger.info(
                f"Latest {'stable ' if stable_only else ''}Minecraft version: {version}"
            )
            return version

        except Exception as e:
            self.logger.error(f"Failed to get latest Minecraft version: {e}")
            return None

    async def is_minecraft_version_supported(self, version: str) -> bool:
        """Check if a Minecraft version is supported by Quilt."""
        try:
            supported = await quilt.is_minecraft_version_supported(version)
            self.logger.info(f"Minecraft {version} Quilt support: {supported}")
            return supported
        except Exception as e:
            self.logger.error(f"Failed to check version support: {e}")
            return False

    async def get_quilt_loader_versions(self) -> List[Dict]:
        """Get available Quilt loader versions."""
        try:
            loaders = await quilt.get_all_loader_versions()
            self.logger.info(f"Found {len(loaders)} Quilt loader versions")
            return loaders
        except Exception as e:
            self.logger.error(f"Failed to fetch Quilt loader versions: {e}")
            return []

    async def get_latest_quilt_loader(self) -> Optional[str]:
        """Get the latest Quilt loader version."""
        try:
            loader_version = await quilt.get_latest_loader_version()
            self.logger.info(f"Latest Quilt loader: {loader_version}")
            return loader_version
        except Exception as e:
            self.logger.error(f"Failed to get latest Quilt loader: {e}")
            return None

    async def install_quilt(
        self, minecraft_version: str, loader_version: Optional[str] = None
    ) -> bool:
        """
        Install Quilt for a specific Minecraft version.

        Args:
            minecraft_version: Minecraft version to install Quilt for
            loader_version: Quilt loader version (latest if None)

        Returns:
            True if installation successful
        """
        try:
            # Check if Minecraft version is supported
            if not await self.is_minecraft_version_supported(minecraft_version):
                self.logger.error(
                    f"Minecraft {minecraft_version} is not supported by Quilt"
                )
                return False

            # Use latest loader if none specified
            if not loader_version:
                loader_version = await self.get_latest_quilt_loader()
                if not loader_version:
                    self.logger.error("Failed to get Quilt loader version")
                    return False

            self.logger.info(
                f"Installing Quilt {loader_version} for Minecraft {minecraft_version}..."
            )

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

            # Install Quilt
            await quilt.install_quilt(
                minecraft_version,
                str(self.minecraft_dir),
                loader_version=loader_version,
                callback=callback,
            )

            self.logger.info(
                f"✅ Successfully installed Quilt {loader_version} for Minecraft {minecraft_version}"
            )
            return True

        except VersionNotFound:
            self.logger.error(f"❌ Minecraft version {minecraft_version} not found")
            return False
        except UnsupportedVersion:
            self.logger.error(
                f"❌ Minecraft version {minecraft_version} is unsupported by Quilt"
            )
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to install Quilt: {e}")
            return False

    async def get_installed_quilt_versions(self) -> List[str]:
        """Get list of installed Quilt versions."""
        installed = []
        versions_dir = self.minecraft_dir / "versions"

        if not versions_dir.exists():
            return installed

        for version_dir in versions_dir.iterdir():
            if version_dir.is_dir():
                version_name = version_dir.name
                # Check if it's a Quilt version
                if "quilt" in version_name.lower():
                    json_file = version_dir / f"{version_name}.json"
                    if json_file.exists():
                        installed.append(version_name)

        return sorted(installed)

    def create_offline_credential(self, username: str = "Player") -> _types.Credential:
        """Create offline Credential for testing."""
        import uuid

        fake_uuid = str(uuid.uuid4())

        return _types.Credential(
            access_token="offline", username=username, uuid=fake_uuid
        )

    async def launch_quilt(
        self,
        minecraft_version: str,
        loader_version: Optional[str] = None,
        username: str = "Player",
        memory: int = 3072,
        additional_jvm_args: Optional[List[str]] = None,
        Credential: Optional[_types.Credential] = None,
    ) -> bool:
        """
        Launch Minecraft with Quilt.

        Args:
            minecraft_version: Minecraft version to launch
            loader_version: Quilt loader version (latest if None)
            username: Player username (for offline mode)
            memory: Memory allocation in MB
            additional_jvm_args: Additional JVM arguments
            Credential: Authentication Credential (uses offline if None)

        Returns:
            True if launch successful
        """
        try:
            # Check if Quilt is installed for this version
            installed_versions = await self.get_installed_quilt_versions()

            # Find matching installed version
            quilt_version_name = None
            for installed in installed_versions:
                if minecraft_version in installed and "quilt" in installed.lower():
                    quilt_version_name = installed
                    break

            if not quilt_version_name:
                self.logger.warning(
                    f"Quilt not installed for Minecraft {minecraft_version}"
                )
                install_choice = input("Install Quilt now? (Y/n): ").strip().lower()

                if install_choice != "n":
                    if not await self.install_quilt(minecraft_version, loader_version):
                        return False

                    # Find the newly installed version
                    updated_versions = await self.get_installed_quilt_versions()
                    for installed in updated_versions:
                        if (
                            minecraft_version in installed
                            and "quilt" in installed.lower()
                        ):
                            quilt_version_name = installed
                            break
                else:
                    return False

            if not quilt_version_name:
                self.logger.error("Failed to find installed Quilt version")
                return False

            # Use provided Credential or create offline ones
            if not Credential:
                Credential = self.create_offline_credential(username)

            # Set up JVM arguments (Quilt inherits Fabric's efficiency)
            jvm_args = [f"-Xmx{memory}M", f"-Xms{memory//2}M"]

            # Add Quilt-optimized JVM arguments
            jvm_args.extend(
                [
                    "-XX:+UnlockExperimentalVMOptions",
                    "-XX:+UseG1GC",
                    "-XX:G1NewSizePercent=20",
                    "-XX:G1ReservePercent=20",
                    "-XX:MaxGCPauseMillis=50",
                    "-XX:G1HeapRegionSize=16M",
                ]
            )

            if additional_jvm_args:
                jvm_args.extend(additional_jvm_args)

            # Create natives directory
            natives_dir = self.minecraft_dir / "natives" / quilt_version_name
            natives_dir.mkdir(parents=True, exist_ok=True)

            # Create launch options
            options: _types.MinecraftOptions = {
                "gameDirectory": str(self.minecraft_dir),
                "jvmArguments": jvm_args,
                "nativesDirectory": str(natives_dir),
            }

            self.logger.info(f"Generating launch command for Quilt...")
            self.logger.info(f"Version: {quilt_version_name}")
            self.logger.info(f"Memory allocation: {memory}MB")

            # Generate the launch command
            minecraft_command = await command.get_minecraft_command(
                quilt_version_name,
                str(self.minecraft_dir),
                options,
                Credential=Credential,
            )

            self.logger.info("✅ Launch command generated successfully!")

            # Show launch information
            mods_dir = self.minecraft_dir / "mods"
            mod_count = len(list(mods_dir.glob("*.jar"))) if mods_dir.exists() else 0

            print(f"\n🎮 Ready to launch Minecraft with Quilt")
            print(f"   Version: {quilt_version_name}")
            print(f"   Player: {Credential.username}")
            print(f"   Memory: {memory}MB")
            print(f"   Mods Loaded: {mod_count}")

            # Ask user if they want to launch
            launch_choice = input("\nLaunch now? (Y/n): ").strip().lower()
            if launch_choice != "n":
                print("🚀 Launching Minecraft with Quilt...")

                import subprocess

                process = subprocess.Popen(
                    minecraft_command,
                    cwd=str(self.minecraft_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                print(f"✅ Minecraft launched with PID: {process.pid}")
                print("\n📝 Quilt Notes:")
                print("   • Quilt supports most Fabric mods")
                print("   • Enhanced modding capabilities over Fabric")
                print("   • Community-driven development")
                print("   • Use Quilted Fabric API for best compatibility")

                return True
            else:
                print("Launch cancelled.")
                return True

        except Exception as e:
            self.logger.error(f"❌ Failed to launch Quilt: {e}")
            return False


async def interactive_quilt_launcher():
    """Interactive Quilt launcher interface."""
    print("=== Minecraft Quilt Launcher ===")
    print("\nQuilt is a Fabric fork with enhanced modding capabilities.")
    print("It supports most Fabric mods while providing additional features.")

    # Get Minecraft directory
    minecraft_dir = input(
        "\nEnter Minecraft directory (or press Enter for default): "
    ).strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")

    print(f"Using directory: {minecraft_dir}")

    # Create launcher
    launcher = QuiltLauncher(minecraft_dir)

    while True:
        print("\n" + "=" * 50)
        print("Quilt Launcher Options:")
        print("1. Browse supported Minecraft versions")
        print("2. Check latest Minecraft version")
        print("3. Browse Quilt loader versions")
        print("4. Install Quilt")
        print("5. List installed Quilt versions")
        print("6. Launch Minecraft with Quilt")
        print("7. Manage mods folder")
        print("8. Quilt vs Fabric information")
        print("9. Exit")

        choice = input("\nEnter your choice (1-9): ").strip()

        if choice == "1":
            # Browse supported versions
            stable_only = (
                input("Show only stable versions? (Y/n): ").strip().lower() != "n"
            )

            versions = await launcher.get_supported_minecraft_versions(stable_only)

            if versions:
                print(
                    f"\n🎯 Supported Minecraft Versions ({'stable only' if stable_only else 'all'}):"
                )
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
            stable_only = (
                input("Check latest stable version? (Y/n): ").strip().lower() != "n"
            )

            latest = await launcher.get_latest_minecraft_version(stable_only)

            if latest:
                print(
                    f"✅ Latest {'stable ' if stable_only else ''}Minecraft version: {latest}"
                )

                install_choice = (
                    input("Install Quilt for this version? (y/N): ").strip().lower()
                )
                if install_choice == "y":
                    await launcher.install_quilt(latest)
            else:
                print("❌ Failed to get latest version")

        elif choice == "3":
            # Browse loader versions
            loaders = await launcher.get_quilt_loader_versions()

            if loaders:
                print(f"\n🧵 Quilt Loader Versions:")
                # Show recent loaders (last 10)
                recent_loaders = loaders[:10] if len(loaders) > 10 else loaders
                for i, loader in enumerate(recent_loaders, 1):
                    version = loader.get("version", "Unknown")
                    stable = " (stable)" if loader.get("stable", False) else ""
                    print(f"   {i:2d}. {version}{stable}")

                if len(loaders) > 10:
                    print(f"   ... and {len(loaders) - 10} more versions")

                # Show latest
                latest_loader = await launcher.get_latest_quilt_loader()
                if latest_loader:
                    print(f"\n✨ Latest loader: {latest_loader}")
            else:
                print("❌ No loader versions found")

        elif choice == "4":
            # Install Quilt
            minecraft_version = input("Enter Minecraft version: ").strip()

            if minecraft_version:
                # Check if version is supported
                supported = await launcher.is_minecraft_version_supported(
                    minecraft_version
                )

                if supported:
                    loader_version = input(
                        "Enter Quilt loader version (or press Enter for latest): "
                    ).strip()
                    loader_version = loader_version if loader_version else None

                    success = await launcher.install_quilt(
                        minecraft_version, loader_version
                    )
                    if not success:
                        print("❌ Installation failed")
                else:
                    print(f"❌ Minecraft {minecraft_version} is not supported by Quilt")

        elif choice == "5":
            # List installed versions
            installed = await launcher.get_installed_quilt_versions()

            print(f"\n💾 Installed Quilt Versions ({len(installed)} total):")
            if installed:
                for version in installed:
                    print(f"   🟢 {version}")
            else:
                print("   No Quilt versions installed")

        elif choice == "6":
            # Launch with Quilt
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
            loader_version = input(
                "Enter Quilt loader version (or press Enter for auto): "
            ).strip()
            loader_version = loader_version if loader_version else None

            # Launch
            success = await launcher.launch_quilt(
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
                print("\n   💡 Quilt mod compatibility:")
                print("   • Most Fabric mods work with Quilt")
                print("   • Quilted Fabric API recommended")
                print("   • Some Quilt-specific mods available")
                print("\n   📦 Where to find mods:")
                print("   • Modrinth (modrinth.com)")
                print("   • CurseForge (curseforge.com)")
                print("   • Quilt forum and Discord")

        elif choice == "8":
            # Quilt vs Fabric information
            print("\n🧵 Quilt vs Fabric Comparison:")
            print("\n✅ Quilt Advantages:")
            print("   • Enhanced modding capabilities")
            print("   • Better mod compatibility layers")
            print("   • More flexible mod loading")
            print("   • Community-driven development")
            print("   • Backward compatibility with Fabric")

            print("\n🔧 Fabric Advantages:")
            print("   • Wider mod ecosystem")
            print("   • Faster updates typically")
            print("   • More established community")
            print("   • Simpler architecture")

            print("\n🔄 Compatibility:")
            print("   • Most Fabric mods work on Quilt")
            print("   • Quilted Fabric API provides compatibility")
            print("   • Some performance may vary")
            print("   • Quilt-specific features require Quilt")

            print("\n💡 Recommendation:")
            print("   • Use Fabric for maximum mod compatibility")
            print("   • Use Quilt for enhanced features and future-proofing")
            print("   • Both are excellent choices")

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main example function."""
    try:
        await interactive_quilt_launcher()
    except KeyboardInterrupt:
        print("\n\nQuilt launcher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in Quilt launcher")


if __name__ == "__main__":
    asyncio.run(main())
