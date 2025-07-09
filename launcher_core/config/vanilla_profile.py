# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""
vanilla_launcher contains functions for interacting with the Vanilla Minecraft Launcher.

This module provides functionality to:
- Load and parse vanilla launcher profiles
- Convert profiles to minecraft options
- Add new profiles to the vanilla launcher
- Validate profile configurations
"""

import datetime
import json
import os
import uuid
from typing import Optional, Union

import aiofiles

from launcher_core._internal_types.vanilla_launcher_types import (
    VanillaLauncherProfilesJson,
    VanillaLauncherProfilesJsonProfile,
)
from launcher_core._types import VanillaLauncherProfile, MinecraftOptions
from launcher_core.exceptions import InvalidVanillaLauncherProfile
from launcher_core.utils import get_latest_version


__all__ = [
    "load_vanilla_launcher_profiles",
    "vanilla_launcher_profile_to_minecraft_options",
    "get_vanilla_launcher_profile_version",
    "add_vanilla_launcher_profile",
    "do_vanilla_launcher_profiles_exists",
]


# Constants for validation
VALID_VERSION_TYPES = {"latest-release", "latest-snapshot", "custom"}
LAUNCHER_PROFILES_FILE = "launcher_profiles.json"


class ProfileValidator:
    """Handles validation of vanilla launcher profiles."""

    @staticmethod
    async def is_valid(profile: VanillaLauncherProfile) -> bool:
        """
        Validates if the given profile structure is correct.

        Args:
            profile: The profile to validate

        Returns:
            True if profile is valid, False otherwise
        """
        try:
            # Validate name
            if not isinstance(profile.get("name"), str):
                return False

            # Validate version type
            version_type = profile.get("versionType")
            if version_type not in VALID_VERSION_TYPES:
                return False

            # Custom type must have version
            if version_type == "custom" and profile.get("version") is None:
                return False

            # Validate optional string fields
            optional_string_fields = ["gameDirectory", "javaExecutable"]
            for field in optional_string_fields:
                value = profile.get(field)
                if value is not None and not isinstance(value, str):
                    return False

            # Validate java arguments
            if not ProfileValidator._validate_java_arguments(
                profile.get("javaArguments")
            ):
                return False

            # Validate custom resolution
            if not ProfileValidator._validate_custom_resolution(
                profile.get("customResolution")
            ):
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def _validate_java_arguments(java_arguments: Optional[list]) -> bool:
        """Validate java arguments structure."""
        if java_arguments is None:
            return True
        return isinstance(java_arguments, list) and all(
            isinstance(arg, str) for arg in java_arguments
        )

    @staticmethod
    def _validate_custom_resolution(custom_resolution: Optional[dict]) -> bool:
        """Validate custom resolution structure."""
        if custom_resolution is None:
            return True

        try:
            return (
                len(custom_resolution) == 2
                and isinstance(custom_resolution.get("height"), int)
                and isinstance(custom_resolution.get("width"), int)
            )
        except (TypeError, AttributeError):
            return False


class ProfileFileHandler:
    """Handles reading and writing of launcher profiles JSON file."""

    def __init__(self, minecraft_directory: Union[str, os.PathLike]):
        self.minecraft_directory = minecraft_directory
        self.profiles_path = os.path.join(minecraft_directory, LAUNCHER_PROFILES_FILE)

    async def read_profiles(self) -> VanillaLauncherProfilesJson:
        """
        Reads launcher_profiles.json file.

        Returns:
            Parsed JSON data from the profiles file

        Raises:
            FileNotFoundError: If the profiles file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            async with aiofiles.open(self.profiles_path, "r", encoding="utf-8") as file:
                content = await file.read()
                return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Launcher profiles file not found: {self.profiles_path}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in profiles file: {e}")

    async def write_profiles(self, data: VanillaLauncherProfilesJson) -> None:
        """
        Writes data to launcher_profiles.json file.

        Args:
            data: The profiles data to write

        Raises:
            OSError: If file cannot be written
        """
        try:
            async with aiofiles.open(self.profiles_path, "w", encoding="utf-8") as file:
                await file.write(json.dumps(data, ensure_ascii=False, indent=4))
        except OSError as e:
            raise OSError(f"Cannot write to profiles file: {e}")

    def exists(self) -> bool:
        """Check if the profiles file exists."""
        return os.path.isfile(self.profiles_path)


class ProfileConverter:
    """Handles conversion between different profile formats."""

    @staticmethod
    def from_json_profile(
        json_profile: VanillaLauncherProfilesJsonProfile,
    ) -> VanillaLauncherProfile:
        """
        Converts a JSON profile to a VanillaLauncherProfile.

        Args:
            json_profile: The profile from the JSON file

        Returns:
            Converted vanilla launcher profile
        """
        profile: VanillaLauncherProfile = {}

        # Handle name based on type
        profile_type = json_profile.get("type", "custom")
        if profile_type == "latest-release":
            profile["name"] = "Latest release"
        elif profile_type == "latest-snapshot":
            profile["name"] = "Latest snapshot"
        else:
            profile["name"] = json_profile.get("name", "Unknown Profile")

        # Handle version type and version
        last_version_id = json_profile.get("lastVersionId", "")
        if last_version_id == "latest-release":
            profile["versionType"] = "latest-release"
            profile["version"] = None
        elif last_version_id == "latest-snapshot":
            profile["versionType"] = "latest-snapshot"
            profile["version"] = None
        else:
            profile["versionType"] = "custom"
            profile["version"] = last_version_id

        # Set optional fields
        profile["gameDirectory"] = json_profile.get("gameDir")
        profile["javaExecutable"] = json_profile.get("javaDir")

        # Handle Java arguments
        java_args = json_profile.get("javaArgs")
        profile["javaArguments"] = java_args.split(" ") if java_args else None

        # Handle resolution
        resolution = json_profile.get("resolution")
        if resolution:
            profile["customResolution"] = {
                "height": resolution["height"],
                "width": resolution["width"],
            }
        else:
            profile["customResolution"] = None

        return profile

    @staticmethod
    def to_json_profile(
        vanilla_profile: VanillaLauncherProfile,
    ) -> VanillaLauncherProfilesJsonProfile:
        """
        Converts a VanillaLauncherProfile to a JSON profile format.

        Args:
            vanilla_profile: The vanilla launcher profile

        Returns:
            Profile in JSON format
        """
        now = datetime.datetime.now().isoformat()
        json_profile: VanillaLauncherProfilesJsonProfile = {
            "name": vanilla_profile["name"],
            "created": now,
            "lastUsed": now,
            "type": "custom",
        }

        # Set version ID based on type
        version_type = vanilla_profile["versionType"]
        if version_type in ("latest-release", "latest-snapshot"):
            json_profile["lastVersionId"] = version_type
        else:  # custom
            json_profile["lastVersionId"] = vanilla_profile["version"]  # type: ignore

        # Set optional fields if they exist
        if (game_dir := vanilla_profile.get("gameDirectory")) is not None:
            json_profile["gameDir"] = game_dir

        if (java_dir := vanilla_profile.get("javaExecutable")) is not None:
            json_profile["javaDir"] = java_dir

        if (java_args := vanilla_profile.get("javaArguments")) is not None:
            json_profile["javaArgs"] = " ".join(java_args)

        if (resolution := vanilla_profile.get("customResolution")) is not None:
            json_profile["resolution"] = {
                "height": resolution["height"],
                "width": resolution["width"],
            }

        return json_profile


# Public API functions
async def load_vanilla_launcher_profiles(
    minecraft_directory: Union[str, os.PathLike],
) -> list[VanillaLauncherProfile]:
    """
    Loads profiles from the Vanilla Launcher in the given Minecraft directory.

    Args:
        minecraft_directory: Path to the Minecraft directory

    Returns:
        List of vanilla launcher profiles

    Raises:
        FileNotFoundError: If launcher_profiles.json doesn't exist
        json.JSONDecodeError: If the profiles file contains invalid JSON
    """
    file_handler = ProfileFileHandler(minecraft_directory)
    data = await file_handler.read_profiles()

    profiles = []
    for json_profile in data["profiles"].values():
        profile = ProfileConverter.from_json_profile(json_profile)
        profiles.append(profile)

    return profiles


async def vanilla_launcher_profile_to_minecraft_options(
    vanilla_profile: VanillaLauncherProfile,
) -> MinecraftOptions:
    """
    Converts a VanillaLauncherProfile to MinecraftOptions.

    Note: You still need to add login data to the options before use.

    Args:
        vanilla_profile: The profile to convert

    Returns:
        MinecraftOptions dictionary

    Raises:
        InvalidVanillaLauncherProfile: If the profile is invalid
    """
    if not await ProfileValidator.is_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    options: MinecraftOptions = {}

    # Map profile fields to options (only non-None values)
    field_mappings = {
        "gameDirectory": "gameDirectory",
        "javaExecutable": "executablePath",
        "javaArguments": "jvmArguments",
    }

    for profile_field, option_field in field_mappings.items():
        value = vanilla_profile.get(profile_field)
        if value is not None:
            options[option_field] = value

    # Handle custom resolution
    custom_resolution = vanilla_profile.get("customResolution")
    if custom_resolution is not None:
        options["customResolution"] = True
        options["resolutionWidth"] = custom_resolution["width"]
        options["resolutionHeight"] = custom_resolution["height"]

    return options


async def get_vanilla_launcher_profile_version(
    vanilla_profile: VanillaLauncherProfile,
) -> str:
    """
    Gets the Minecraft version for a profile, resolving latest-release and latest-snapshot.

    Args:
        vanilla_profile: The profile to get version for

    Returns:
        The concrete Minecraft version string

    Raises:
        InvalidVanillaLauncherProfile: If the profile is invalid
    """
    if not await ProfileValidator.is_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    version_type = vanilla_profile["versionType"]

    if version_type in ("latest-release", "latest-snapshot"):
        latest_version = await get_latest_version()
        return latest_version[
            "release" if version_type == "latest-release" else "snapshot"
        ]
    else:  # custom
        return vanilla_profile["version"]  # type: ignore


async def add_vanilla_launcher_profile(
    minecraft_directory: Union[str, os.PathLike],
    vanilla_profile: VanillaLauncherProfile,
) -> None:
    """
    Adds a new profile to the Vanilla Launcher.

    Args:
        minecraft_directory: Path to the Minecraft directory
        vanilla_profile: The profile to add

    Raises:
        InvalidVanillaLauncherProfile: If the profile is invalid
        FileNotFoundError: If launcher_profiles.json doesn't exist
        OSError: If the profiles file cannot be written
    """
    if not await ProfileValidator.is_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    file_handler = ProfileFileHandler(minecraft_directory)
    data = await file_handler.read_profiles()

    # Convert profile and generate unique key
    json_profile = ProfileConverter.to_json_profile(vanilla_profile)
    profile_key = ProfileFileHandler._generate_unique_key(data["profiles"])

    data["profiles"][profile_key] = json_profile
    await file_handler.write_profiles(data)


def do_vanilla_launcher_profiles_exists(
    minecraft_directory: Union[str, os.PathLike],
) -> bool:
    """
    Checks if vanilla launcher profiles can be found in the directory.

    Args:
        minecraft_directory: Path to the Minecraft directory

    Returns:
        True if launcher_profiles.json exists, False otherwise
    """
    file_handler = ProfileFileHandler(minecraft_directory)
    return file_handler.exists()


# Helper methods for ProfileFileHandler
def _generate_unique_key(existing_profiles: dict) -> str:
    """Generate a unique UUID key that doesn't conflict with existing profiles."""
    while True:
        key = str(uuid.uuid4())
        if key not in existing_profiles:
            return key


# Monkey patch the method to ProfileFileHandler
ProfileFileHandler._generate_unique_key = staticmethod(_generate_unique_key)
