# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"vanilla_launcher contains some functions for interacting with the Vanilla Minecraft Launcher"
import datetime
import json
import uuid
import os
import aiofiles
from ._internal_types.vanilla_launcher_types import (
    VanillaLauncherProfilesJson,
    VanillaLauncherProfilesJsonProfile,
)
from ._types import VanillaLauncherProfile, MinecraftOptions
from .exceptions import InvalidVanillaLauncherProfile
from .utils import get_latest_version


__all__ = [
    "load_vanilla_launcher_profiles",
    "vanilla_launcher_profile_to_minecraft_options",
    "get_vanilla_launcher_profile_version",
    "add_vanilla_launcher_profile",
    "do_vanilla_launcher_profiles_exists",
]


async def _is_vanilla_launcher_profile_valid(
    vanilla_profile: VanillaLauncherProfile,
) -> bool:
    "Checks if the given profile is valid"
    # 名稱必須是字符串
    if not isinstance(vanilla_profile.get("name"), str):
        return False

    # 版本類型檢查
    if vanilla_profile.get("versionType") not in (
        "latest-release",
        "latest-snapshot",
        "custom",
    ):
        return False

    # custom 類型必須有 version
    if (
        vanilla_profile["versionType"] == "custom"
        and vanilla_profile.get("version") is None
    ):
        return False

    # 檢查 gameDirectory 類型
    if vanilla_profile.get("gameDirectory") is not None and not isinstance(
        vanilla_profile.get("gameDirectory"), str
    ):
        return False

    # 檢查 javaExecutable 類型
    if vanilla_profile.get("javaExecutable") is not None and not isinstance(
        vanilla_profile.get("javaExecutable"), str
    ):
        return False

    # 檢查 javaArguments
    java_arguments = vanilla_profile.get("javaArguments")
    if java_arguments is not None:
        if not all(isinstance(arg, str) for arg in java_arguments):
            return False

    # 檢查自定義分辨率
    custom_resolution = vanilla_profile.get("customResolution")
    if custom_resolution is not None:
        try:
            if len(custom_resolution) != 2:
                return False
            if not isinstance(custom_resolution["height"], int):
                return False
            if not isinstance(custom_resolution["width"], int):
                return False
        except Exception:
            return False

    return True


async def _read_launcher_profiles_json(
    minecraft_directory: str | os.PathLike,
) -> VanillaLauncherProfilesJson:
    """讀取 launcher_profiles.json 文件"""
    async with aiofiles.open(
        os.path.join(minecraft_directory, "launcher_profiles.json"),
        "r",
        encoding="utf-8",
    ) as f:
        data_text = await f.read()
        return json.loads(data_text)


async def _write_launcher_profiles_json(
    minecraft_directory: str | os.PathLike,
    data: VanillaLauncherProfilesJson,
) -> None:
    """寫入 launcher_profiles.json 文件"""
    async with aiofiles.open(
        os.path.join(minecraft_directory, "launcher_profiles.json"),
        "w",
        encoding="utf-8",
    ) as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def load_vanilla_launcher_profiles(
    minecraft_directory: str | os.PathLike,
) -> list[VanillaLauncherProfile]:
    """
    Loads the profiles of the Vanilla Launcher from the given Minecraft directory

    :param minecraft_directory: The Minecraft directory
    :return: A List with the Profiles
    """
    data = await _read_launcher_profiles_json(minecraft_directory)

    profile_list: list[VanillaLauncherProfile] = []
    for value in data["profiles"].values():
        vanilla_profile: VanillaLauncherProfile = {}

        # 根據類型設置名稱
        vanilla_profile["name"] = (
            "Latest release"
            if value["type"] == "latest-release"
            else (
                "Latest snapshot"
                if value["type"] == "latest-snapshot"
                else value["name"]
            )
        )

        # 設置版本類型和版本
        version_id = value["lastVersionId"]
        if version_id == "latest-release":
            vanilla_profile["versionType"] = "latest-release"
            vanilla_profile["version"] = None
        elif version_id == "latest-snapshot":
            vanilla_profile["versionType"] = "latest-snapshot"
            vanilla_profile["version"] = None
        else:
            vanilla_profile["versionType"] = "custom"
            vanilla_profile["version"] = version_id

        # 設置額外屬性
        vanilla_profile["gameDirectory"] = value.get("gameDir")
        vanilla_profile["javaExecutable"] = value.get("javaDir")

        # 處理 Java 參數
        vanilla_profile["javaArguments"] = (
            value["javaArgs"].split(" ") if "javaArgs" in value else None
        )

        # 處理分辨率
        if "resolution" in value:
            vanilla_profile["customResolution"] = {
                "height": value["resolution"]["height"],
                "width": value["resolution"]["width"],
            }
        else:
            vanilla_profile["customResolution"] = None

        profile_list.append(vanilla_profile)

    return profile_list


async def vanilla_launcher_profile_to_minecraft_options(
    vanilla_profile: VanillaLauncherProfile,
) -> MinecraftOptions:
    """
    Converts a VanillaLauncherProfile into a Options dict, that can be used by :func:`~launcher_core.command.get_minecraft_command`.
    You still need to add the Login Data to the Options before you can use it.

    :param vanilla_profile: The profile as returned by :func:`load_vanilla_launcher_profiles`
    :raises InvalidVanillaLauncherProfile: The given Profile is invalid
    :return: The Options Dict
    """
    if not await _is_vanilla_launcher_profile_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    options: MinecraftOptions = {}

    # 只在值非 None 時添加到 options 字典中
    if (game_directory := vanilla_profile.get("gameDirectory")) is not None:
        options["gameDirectory"] = game_directory

    if (java_executable := vanilla_profile.get("javaExecutable")) is not None:
        options["executablePath"] = java_executable

    if (java_arguments := vanilla_profile.get("javaArguments")) is not None:
        options["jvmArguments"] = java_arguments

    if (custom_resolution := vanilla_profile.get("customResolution")) is not None:
        options["customResolution"] = True
        options["resolutionWidth"] = custom_resolution["width"]
        options["resolutionHeight"] = custom_resolution["height"]

    return options


async def get_vanilla_launcher_profile_version(
    vanilla_profile: VanillaLauncherProfile,
) -> str:
    """
    Returns the Minecraft version of the VanillaProfile. Handles ``latest-release`` and ``latest-snapshot``.

    :param vanilla_profile: The Profile
    :type vanilla_profile: VanillaLauncherProfile
    :raises InvalidVanillaLauncherProfile: The given Profile is invalid
    :return: The Minecraft version
    """
    if not await _is_vanilla_launcher_profile_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    version_type = vanilla_profile["versionType"]

    if version_type == "latest-release":
        latest_version = await get_latest_version()
        return latest_version["release"]
    elif version_type == "latest-snapshot":
        latest_version = await get_latest_version()
        return latest_version["snapshot"]
    else:  # custom
        return vanilla_profile["version"]  # type: ignore


async def add_vanilla_launcher_profile(
    minecraft_directory: str | os.PathLike, vanilla_profile: VanillaLauncherProfile
) -> None:
    """
    Adds a new Profile to the Vanilla Launcher

    :param minecraft_directory: The Minecraft directory
    :param vanilla_profile: The new Profile
    :raises InvalidVanillaLauncherProfile: The given Profile is invalid
    """
    if not await _is_vanilla_launcher_profile_valid(vanilla_profile):
        raise InvalidVanillaLauncherProfile(vanilla_profile)

    data = await _read_launcher_profiles_json(minecraft_directory)

    new_profile: VanillaLauncherProfilesJsonProfile = {
        "name": vanilla_profile["name"],
        "created": datetime.datetime.now().isoformat(),
        "lastUsed": datetime.datetime.now().isoformat(),
        "type": "custom",
    }

    # 根據版本類型設置 lastVersionId
    version_type = vanilla_profile["versionType"]
    if version_type in ("latest-release", "latest-snapshot"):
        new_profile["lastVersionId"] = version_type
    else:  # custom
        new_profile["lastVersionId"] = vanilla_profile["version"]  # type: ignore

    # 設置可選參數
    if (game_directory := vanilla_profile.get("gameDirectory")) is not None:
        new_profile["gameDir"] = game_directory

    if (java_executable := vanilla_profile.get("javaExecutable")) is not None:
        new_profile["javaDir"] = java_executable

    if (java_arguments := vanilla_profile.get("javaArguments")) is not None:
        new_profile["javaArgs"] = " ".join(java_arguments)

    if (custom_resolution := vanilla_profile.get("customResolution")) is not None:
        new_profile["resolution"] = {
            "height": custom_resolution["height"],
            "width": custom_resolution["width"],
        }

    # 生成唯一的 key
    key = str(uuid.uuid4())
    while key in data["profiles"]:
        key = str(uuid.uuid4())

    data["profiles"][key] = new_profile

    await _write_launcher_profiles_json(minecraft_directory, data)


def do_vanilla_launcher_profiles_exists(
    minecraft_directory: str | os.PathLike,
) -> bool:
    """
    Checks if profiles from the vanilla launcher can be found

    :param minecraft_directory: The Minecraft directory
    :return: If profiles exists
    """
    return os.path.isfile(os.path.join(minecraft_directory, "launcher_profiles.json"))
