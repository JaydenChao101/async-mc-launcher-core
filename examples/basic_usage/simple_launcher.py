#!/usr/bin/env python3
"""
Simple Minecraft Launcher Example

This example demonstrates the basic functionality of launching Minecraft
using the async-mc-launcher-core library. It shows how to:

1. Set up basic authentication (offline mode)
2. Configure launch options
3. Generate and execute the Minecraft command

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Java installation
- Valid Minecraft directory
"""

import asyncio
import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

from launcher_core import command, _types, install, utils
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound


class SimpleLauncher:
    """A simple Minecraft launcher with basic functionality."""

    def __init__(self, minecraft_dir: str, java_executable: Optional[str] = None):
        """
        Initialize the launcher.

        Args:
            minecraft_dir: Path to the .minecraft directory
            java_executable: Path to Java executable (auto-detected if None)
        """
        self.minecraft_dir = Path(minecraft_dir)
        self.java_executable = java_executable
        self.logger = setup_logger(enable_console=True, level=logging.INFO)

        # Create minecraft directory if it doesn't exist
        self.minecraft_dir.mkdir(parents=True, exist_ok=True)

    async def get_available_versions(self) -> list[str]:
        """Get list of available Minecraft versions."""
        try:
            versions = await install.get_version_list()
            return [v["id"] for v in versions["versions"]]
        except Exception as e:
            self.logger.error(f"Failed to get version list: {e}")
            return []

    async def ensure_version_installed(self, version: str) -> bool:
        """
        Ensure the specified Minecraft version is installed.

        Args:
            version: Minecraft version ID (e.g., "1.21.1")

        Returns:
            True if version is installed/downloaded successfully
        """
        version_path = self.minecraft_dir / "versions" / version / f"{version}.json"

        if version_path.exists():
            self.logger.info(f"Version {version} already installed")
            return True

        try:
            self.logger.info(f"Installing Minecraft version {version}...")

            # Create callback for installation progress
            def set_status(status: str) -> None:
                self.logger.info(f"Status: {status}")

            def set_progress(progress: int) -> None:
                self.logger.info(f"Progress: {progress}")

            def set_max(maximum: int) -> None:
                self.logger.info(f"Max progress: {maximum}")

            callback: _types.CallbackDict = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max,
            }

            await install.install_minecraft_version(
                version, str(self.minecraft_dir), callback
            )

            self.logger.info(f"Successfully installed version {version}")
            return True

        except VersionNotFound:
            self.logger.error(f"Version {version} not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to install version {version}: {e}")
            return False

    def create_offline_credential(self, username: str = "Player") -> _types.Credential:
        """
        Create offline mode Credential.

        Args:
            username: Player username for offline mode

        Returns:
            Credential object for offline play
        """
        # Generate a fake UUID for offline mode
        import uuid
        fake_uuid = str(uuid.uuid4())

        return _types.Credential(
            access_token="offline",
            username=username,
            uuid=fake_uuid
        )

    async def launch_minecraft(
        self,
        version: str,
        username: str = "Player",
        memory: int = 2048,
        additional_jvm_args: Optional[list[str]] = None
    ) -> bool:
        """
        Launch Minecraft with the specified configuration.

        Args:
            version: Minecraft version to launch
            username: Player username
            memory: Memory allocation in MB
            additional_jvm_args: Additional JVM arguments

        Returns:
            True if launch command was generated successfully
        """
        try:
            # Ensure version is installed
            if not await self.ensure_version_installed(version):
                return False

            # Create offline Credential
            Credential = self.create_offline_credential(username)

            # Set up launch options
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
            }

            self.logger.info(f"Generating launch command for {version}...")

            # Generate the Minecraft command
            minecraft_command = await command.get_minecraft_command(
                version,
                str(self.minecraft_dir),
                options,
                Credential=Credential
            )

            self.logger.info("Launch command generated successfully!")
            self.logger.info(f"Command: {' '.join(minecraft_command)}")

            # Optionally launch the game
            response = input("Launch Minecraft now? (y/N): ").strip().lower()
            if response == 'y':
                self.logger.info("Launching Minecraft...")
                process = subprocess.Popen(
                    minecraft_command,
                    cwd=str(self.minecraft_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.logger.info(f"Minecraft launched with PID: {process.pid}")
                self.logger.info("Game is running. Check the game window.")

            return True

        except Exception as e:
            self.logger.error(f"Failed to launch Minecraft: {e}")
            return False


async def main():
    """Main example function."""
    print("=== Simple Minecraft Launcher Example ===\n")

    # Configuration
    minecraft_dir = input("Enter Minecraft directory path (or press Enter for default): ").strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")

    print(f"Using Minecraft directory: {minecraft_dir}")

    # Create launcher instance
    launcher = SimpleLauncher(minecraft_dir)

    # Get available versions
    print("\nFetching available Minecraft versions...")
    versions = await launcher.get_available_versions()

    if not versions:
        print("Failed to fetch versions. Exiting.")
        return

    # Show some recent versions
    print("\nRecent Minecraft versions:")
    recent_versions = [v for v in versions[:10] if not any(x in v for x in ['snapshot', 'pre', 'rc'])]
    for i, version in enumerate(recent_versions[:5], 1):
        print(f"{i}. {version}")

    # Let user select version
    version_choice = input("\nEnter version number (1-5) or type a specific version: ").strip()

    if version_choice.isdigit() and 1 <= int(version_choice) <= 5:
        version = recent_versions[int(version_choice) - 1]
    else:
        version = version_choice

    print(f"Selected version: {version}")

    # Get username
    username = input("Enter username (or press Enter for 'Player'): ").strip()
    if not username:
        username = "Player"

    # Get memory allocation
    memory_input = input("Enter memory allocation in MB (or press Enter for 2048): ").strip()
    try:
        memory = int(memory_input) if memory_input else 2048
    except ValueError:
        memory = 2048

    print(f"\nConfiguration:")
    print(f"  Version: {version}")
    print(f"  Username: {username}")
    print(f"  Memory: {memory}MB")
    print(f"  Directory: {minecraft_dir}")

    # Launch Minecraft
    print("\n" + "="*50)
    success = await launcher.launch_minecraft(version, username, memory)

    if success:
        print("✅ Launch successful!")
    else:
        print("❌ Launch failed. Check the logs above.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in main")
