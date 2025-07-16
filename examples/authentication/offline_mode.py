#!/usr/bin/env python3
"""
Offline Mode Example

This example demonstrates how to launch Minecraft in offline mode
using the async-mc-launcher-core library. Offline mode allows you to:

1. Play without Microsoft authentication
2. Use custom usernames
3. Test launcher functionality without internet
4. Access singleplayer and LAN multiplayer

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Java installation
- Downloaded Minecraft version

Note: Offline mode cannot access official multiplayer servers.
"""

import asyncio
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from launcher_core import command, install, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound


class OfflineLauncher:
    """Minecraft launcher for offline mode play."""

    def __init__(self, minecraft_dir: str, profiles_file: str = "offline_profiles.json"):
        """
        Initialize the offline launcher.

        Args:
            minecraft_dir: Path to the .minecraft directory
            profiles_file: File to store offline profiles
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.profiles_file = Path(profiles_file)
        self.logger = setup_logger(enable_console=True, level=logging.INFO)

        # Create directories
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)

        # Load existing profiles
        self.profiles = self.load_profiles()

    def load_profiles(self) -> Dict[str, Dict]:
        """Load offline profiles from file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load profiles: {e}")
        return {}

    def save_profiles(self) -> None:
        """Save profiles to file."""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")

    def create_offline_profile(self, username: str, custom_uuid: Optional[str] = None) -> Dict:
        """
        Create an offline profile.

        Args:
            username: Player username
            custom_uuid: Custom UUID (generated if None)

        Returns:
            Profile dictionary
        """
        if not custom_uuid:
            # Generate deterministic UUID from username for consistency
            namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
            custom_uuid = str(uuid.uuid5(namespace, username.lower()))

        profile = {
            "username": username,
            "uuid": custom_uuid,
            "access_token": "offline",
            "created_at": asyncio.get_event_loop().time(),
            "type": "offline"
        }

        self.profiles[username] = profile
        self.save_profiles()

        self.logger.info(f"Created offline profile for {username} ({custom_uuid})")
        return profile

    def get_profile(self, username: str) -> Optional[Dict]:
        """Get existing profile or create new one."""
        if username in self.profiles:
            return self.profiles[username]
        return None

    def list_profiles(self) -> List[str]:
        """Get list of available profile usernames."""
        return list(self.profiles.keys())

    def delete_profile(self, username: str) -> bool:
        """Delete a profile."""
        if username in self.profiles:
            del self.profiles[username]
            self.save_profiles()
            self.logger.info(f"Deleted profile for {username}")
            return True
        return False

    def create_offline_credential(self, username: str) -> _types.Credential:
        """
        Create offline Credential for launching.

        Args:
            username: Player username

        Returns:
            Credential object for offline play
        """
        profile = self.get_profile(username)
        if not profile:
            profile = self.create_offline_profile(username)

        return _types.Credential(
            access_token=profile["access_token"],
            username=profile["username"],
            uuid=profile["uuid"]
        )

    async def get_installed_versions(self) -> List[str]:
        """Get list of locally installed Minecraft versions."""
        versions_dir = self.minecraft_dir / "versions"
        installed = []

        if versions_dir.exists():
            for version_dir in versions_dir.iterdir():
                if version_dir.is_dir():
                    json_file = version_dir / f"{version_dir.name}.json"
                    if json_file.exists():
                        installed.append(version_dir.name)

        return sorted(installed)

    async def ensure_version_available(self, version: str) -> bool:
        """
        Ensure version is available for offline play.

        Args:
            version: Minecraft version ID

        Returns:
            True if version is available
        """
        installed = await self.get_installed_versions()

        if version in installed:
            self.logger.info(f"Version {version} already available")
            return True

        # Offer to download the version
        print(f"\n⚠️  Version {version} is not installed locally.")
        download = input("Download it now? (Y/n): ").strip().lower()

        if download == 'n':
            return False

        try:
            self.logger.info(f"Downloading Minecraft {version}...")

            def set_status(status: str) -> None:
                print(f"Status: {status}")

            def set_progress(progress: int) -> None:
                print(f"Progress: {progress}")

            def set_max(maximum: int) -> None:
                print(f"Total: {maximum}")

            callback: _types.CallbackDict = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max,
            }

            await install.install_minecraft_version(
                version, str(self.minecraft_dir), callback
            )

            self.logger.info(f"✅ Successfully downloaded {version}")
            return True

        except VersionNotFound:
            self.logger.error(f"❌ Version {version} not found")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to download {version}: {e}")
            return False

    async def launch_offline(
        self,
        username: str,
        version: str,
        memory: int = 2048,
        demo_mode: bool = False,
        custom_resolution: Optional[tuple[int, int]] = None,
        additional_jvm_args: Optional[List[str]] = None
    ) -> bool:
        """
        Launch Minecraft in offline mode.

        Args:
            username: Player username
            version: Minecraft version to launch
            memory: Memory allocation in MB
            demo_mode: Enable demo mode
            custom_resolution: Custom resolution (width, height)
            additional_jvm_args: Additional JVM arguments

        Returns:
            True if launch successful
        """
        try:
            # Ensure version is available
            if not await self.ensure_version_available(version):
                return False

            # Create offline Credential
            Credential = self.create_offline_credential(username)

            # Set up JVM arguments
            jvm_args = [f"-Xmx{memory}M", f"-Xms{memory//2}M"]
            if additional_jvm_args:
                jvm_args.extend(additional_jvm_args)

            # Create natives directory
            natives_dir = self.minecraft_dir / "natives" / version
            natives_dir.mkdir(parents=True, exist_ok=True)

            # Create launch options
            options: _types.MinecraftOptions = {
                "gameDirectory": str(self.minecraft_dir),
                "jvmArguments": jvm_args,
                "nativesDirectory": str(natives_dir),
                "demo": demo_mode,
            }

            # Add custom resolution if specified
            if custom_resolution:
                options["customResolution"] = True
                options["resolutionWidth"] = custom_resolution[0]
                options["resolutionHeight"] = custom_resolution[1]

            self.logger.info(f"Generating launch command for {version}...")
            self.logger.info(f"Player: {username} (Offline Mode)")
            if demo_mode:
                self.logger.info("Demo mode enabled")

            # Generate the launch command
            minecraft_command = await command.get_minecraft_command(
                version,
                str(self.minecraft_dir),
                options,
                Credential=Credential
            )

            self.logger.info("✅ Launch command generated successfully!")

            # Show launch info
            print(f"\n🎮 Ready to launch Minecraft {version}")
            print(f"   Player: {username}")
            print(f"   Mode: {'Demo' if demo_mode else 'Offline'}")
            print(f"   Memory: {memory}MB")
            if custom_resolution:
                print(f"   Resolution: {custom_resolution[0]}x{custom_resolution[1]}")

            # Ask user if they want to launch
            launch_choice = input("\nLaunch now? (Y/n): ").strip().lower()
            if launch_choice != 'n':
                print("🚀 Launching Minecraft...")

                import subprocess
                process = subprocess.Popen(
                    minecraft_command,
                    cwd=str(self.minecraft_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                print(f"✅ Minecraft launched with PID: {process.pid}")
                print("\n📝 Offline Mode Notes:")
                print("   • Singleplayer worlds work normally")
                print("   • LAN multiplayer is available")
                print("   • Official multiplayer servers won't work")
                print("   • Some features may require online authentication")

                return True
            else:
                print("Launch cancelled.")
                return True

        except Exception as e:
            self.logger.error(f"❌ Failed to launch: {e}")
            return False


def display_offline_limitations():
    """Display information about offline mode limitations."""
    print("\n📋 Offline Mode Information:")
    print("\n✅ What works in offline mode:")
    print("   • Singleplayer worlds")
    print("   • LAN multiplayer")
    print("   • Mods and modpacks")
    print("   • Resource packs")
    print("   • Custom skins (in some versions)")

    print("\n❌ What doesn't work in offline mode:")
    print("   • Official multiplayer servers")
    print("   • Realms")
    print("   • Skin changes")
    print("   • Achievements/statistics sync")
    print("   • Some mod authentication")


async def interactive_offline_launcher():
    """Interactive offline launcher interface."""
    print("=== Minecraft Offline Mode Launcher ===")
    display_offline_limitations()

    # Get Minecraft directory
    minecraft_dir = input("\nEnter Minecraft directory (or press Enter for default): ").strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")

    print(f"Using directory: {minecraft_dir}")

    # Create launcher
    launcher = OfflineLauncher(minecraft_dir)

    while True:
        print("\n" + "="*50)
        print("Offline Launcher Options:")
        print("1. Launch Minecraft")
        print("2. Manage profiles")
        print("3. List installed versions")
        print("4. Advanced launch options")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            # Quick launch
            profiles = launcher.list_profiles()

            # Get username
            if profiles:
                print(f"\nExisting profiles: {', '.join(profiles)}")
                username = input("Enter username (new or existing): ").strip()
            else:
                username = input("Enter username: ").strip()

            if not username:
                print("❌ Username required")
                continue

            # Get version
            installed = await launcher.get_installed_versions()
            if installed:
                print(f"\nInstalled versions: {', '.join(installed[:5])}...")
                version = input("Enter version: ").strip()
            else:
                version = input("Enter version to download and launch: ").strip()

            if not version:
                print("❌ Version required")
                continue

            # Launch
            success = await launcher.launch_offline(username, version)
            if not success:
                print("❌ Launch failed")

        elif choice == "2":
            # Manage profiles
            while True:
                profiles = launcher.list_profiles()
                print(f"\n👥 Offline Profiles ({len(profiles)} total):")

                if profiles:
                    for i, username in enumerate(profiles, 1):
                        profile = launcher.get_profile(username)
                        print(f"   {i}. {username} ({profile['uuid'][:8]}...)")
                else:
                    print("   No profiles created yet")

                print("\nProfile Options:")
                print("1. Create new profile")
                print("2. Delete profile")
                print("3. Back to main menu")

                profile_choice = input("Enter choice (1-3): ").strip()

                if profile_choice == "1":
                    username = input("Enter username: ").strip()
                    if username:
                        custom_uuid = input("Enter custom UUID (or press Enter for auto): ").strip()
                        if not custom_uuid:
                            custom_uuid = None
                        launcher.create_offline_profile(username, custom_uuid)

                elif profile_choice == "2":
                    if not profiles:
                        print("No profiles to delete")
                        continue

                    username = input("Enter username to delete: ").strip()
                    if launcher.delete_profile(username):
                        print(f"✅ Deleted profile for {username}")
                    else:
                        print(f"❌ Profile {username} not found")

                elif profile_choice == "3":
                    break

        elif choice == "3":
            # List installed versions
            installed = await launcher.get_installed_versions()
            print(f"\n💾 Installed Versions ({len(installed)} total):")

            if installed:
                for version in installed:
                    print(f"   🟢 {version}")
            else:
                print("   No versions installed")
                print("   Use option 1 to download and install versions")

        elif choice == "4":
            # Advanced launch
            profiles = launcher.list_profiles()

            if profiles:
                print(f"\nProfiles: {', '.join(profiles)}")
            username = input("Username: ").strip()

            installed = await launcher.get_installed_versions()
            if installed:
                print(f"Installed: {', '.join(installed[:5])}...")
            version = input("Version: ").strip()

            if not username or not version:
                print("❌ Username and version required")
                continue

            # Advanced options
            try:
                memory = int(input("Memory in MB (default 2048): ") or "2048")
            except ValueError:
                memory = 2048

            demo = input("Demo mode? (y/N): ").strip().lower() == 'y'

            resolution_input = input("Custom resolution WxH (or press Enter): ").strip()
            custom_resolution = None
            if resolution_input and 'x' in resolution_input:
                try:
                    w, h = resolution_input.split('x')
                    custom_resolution = (int(w), int(h))
                except ValueError:
                    print("⚠️  Invalid resolution format")

            jvm_args_input = input("Additional JVM args (or press Enter): ").strip()
            additional_jvm_args = jvm_args_input.split() if jvm_args_input else None

            # Launch with advanced options
            success = await launcher.launch_offline(
                username, version, memory, demo,
                custom_resolution, additional_jvm_args
            )

            if not success:
                print("❌ Launch failed")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


async def main():
    """Main example function."""
    try:
        await interactive_offline_launcher()
    except KeyboardInterrupt:
        print("\n\nOffline launcher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in offline launcher")


if __name__ == "__main__":
    asyncio.run(main())
