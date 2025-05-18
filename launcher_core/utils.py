# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"utils contains a few functions for helping you that doesn't fit in any other category"
from datetime import datetime
import platform
import pathlib
import random
import shutil
import uuid
import json
import os
from typing import Coroutine, Any
import asyncio
import aiofiles
from .logging_utils import logger
from ._types import MinecraftOptions, LatestMinecraftVersions, MinecraftVersionInfo
from ._internal_types.shared_types import ClientJson, VersionListManifestJson
from ._helper import get_requests_response_cache, assert_func




async def get_minecraft_directory() -> str:
    """
    Returns the default path to the .minecraft directory

    Example:

    .. code:: python

        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        print(f"The default minecraft directory is {minecraft_directory}")
    """
    if platform.system() == "Windows":
        return os.path.join(
            os.getenv(
                "APPDATA", os.path.join(pathlib.Path.home(), "AppData", "Roaming")
            ),
            ".minecraft",
        )
    elif platform.system() == "Darwin":
        return os.path.join(
            str(pathlib.Path.home()), "Library", "Application Support", "minecraft"
        )
    else:
        return os.path.join(str(pathlib.Path.home()), ".minecraft")


async def get_latest_version() -> LatestMinecraftVersions:
    """
    Returns the latest version of Minecraft

    Example:

    .. code:: python

        latest_version = await launcher_coreutils.get_latest_version()
        print("Latest Release " + latest_version["release"])
        print("Latest Snapshot " + latest_version["snapshot"])
    """
    response = await get_requests_response_cache(
        "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
    )

    data = json.loads(response["content"])
    return data["latest"]


async def get_version_list() -> list[MinecraftVersionInfo]:
    """
    Returns all versions that Mojang offers to download

    Example:

    .. code:: python

        async for version in launcher_coreutils.get_version_list():
            print(version["id"])
    """
    response = await get_requests_response_cache(
        "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
    )
    vlist: VersionListManifestJson = response
    returnlist: list[MinecraftVersionInfo] = []
    for i in vlist["versions"]:
        returnlist.append(
            {
                "id": i["id"],
                "type": i["type"],
                "releaseTime": datetime.fromisoformat(i["releaseTime"]),
                "complianceLevel": i["complianceLevel"],
            }
        )
    return returnlist


async def get_installed_versions(
    minecraft_directory: str | os.PathLike,
) -> list[MinecraftVersionInfo]:
    """
    Returns all installed versions

    Example:

    .. code:: python

        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        versions = await launcher_coreutils.get_installed_versions(minecraft_directory)
        for version in versions:
            print(version["id"])

    :param minecraft_directory: The path to your Minecraft directory
    """
    try:
        dir_list = await asyncio.to_thread(
            os.listdir, os.path.join(minecraft_directory, "versions")
        )
    except FileNotFoundError:
        return []

    version_list: list[MinecraftVersionInfo] = []
    for i in dir_list:
        json_path = os.path.join(minecraft_directory, "versions", i, i + ".json")
        if not await asyncio.to_thread(os.path.isfile, json_path):
            continue

        try:
            async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
                version_data: ClientJson = json.loads(await f.read())

            try:
                release_time = datetime.fromisoformat(version_data["releaseTime"])
            except ValueError:
                # In case some custom client has a invalid time
                release_time = datetime.fromtimestamp(0)

            version_list.append(
                {
                    "id": version_data["id"],
                    "type": version_data["type"],
                    "releaseTime": release_time,
                    "complianceLevel": version_data.get("complianceLevel", 0),
                }
            )
        except Exception:
            continue

    return version_list


async def get_available_versions(
    minecraft_directory: str | os.PathLike,
) -> list[MinecraftVersionInfo]:
    """
    Returns all installed versions and all versions that Mojang offers to download

    Example:

    .. code:: python

        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        versions = await launcher_coreutils.get_available_versions(minecraft_directory)
        for version in versions:
            print(version["id"])

    :param minecraft_directory: The path to your Minecraft directory
    """
    version_list = []
    version_check = []

    for i in await get_version_list():
        version_list.append(i)
        version_check.append(i["id"])

    for i in await get_installed_versions(minecraft_directory):
        if i["id"] not in version_check:
            version_list.append(i)

    return version_list


async def get_java_executable() -> str:
    """
    Tries the find out the path to the default java executable.
    Returns :code:`java`, if no path was found.

    Example:

    .. code:: python

        print("The path to Java is " + await launcher_coreutils.get_java_executable())
    """
    if platform.system() == "Windows":
        if (java_home := os.getenv("JAVA_HOME")) is not None:
            return os.path.join(java_home, "bin", "javaw.exe")
        elif await asyncio.to_thread(
            os.path.isfile,
            r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\javaw.exe",
        ):
            return r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\javaw.exe"
        else:
            return await asyncio.to_thread(shutil.which, "javaw") or "javaw"
    elif (java_home := os.getenv("JAVA_HOME")) is not None:
        return os.path.join(java_home, "bin", "java")
    elif platform.system() == "Darwin":
        return await asyncio.to_thread(shutil.which, "java") or "java"
    else:
        if await asyncio.to_thread(os.path.islink, "/etc/alternatives/java"):
            return await asyncio.to_thread(os.readlink, "/etc/alternatives/java")
        elif await asyncio.to_thread(os.path.islink, "/usr/lib/jvm/default-runtime"):
            return os.path.join(
                "/usr",
                "lib",
                "jvm",
                await asyncio.to_thread(os.readlink, "/usr/lib/jvm/default-runtime"),
                "bin",
                "java",
            )
        else:
            return await asyncio.to_thread(shutil.which, "java") or "java"


class VersionCache:
    _version_cache = None

    @classmethod
    async def get_library_version(cls) -> str:
        """
        Returns the version of minecraft-launcher-lib

        Example:

        .. code:: python

            print(f"You are using version {await launcher_coreutils.get_library_version()} of minecraft-launcher-lib")
        """
        if cls._version_cache is not None:
            return cls._version_cache
        else:
            version_path = os.path.join(os.path.dirname(__file__), "version.txt")
            async with aiofiles.open(version_path, "r", encoding="utf-8") as f:
                cls._version_cache = (await f.read()).strip()
                return cls._version_cache


get_library_version = VersionCache.get_library_version


async def generate_test_options() -> MinecraftOptions:
    """
    Generates test options to launch minecraft.
    This includes a random name and a random uuid.

    .. note::
        This function is just for debugging and testing, if Minecraft works.
        The behavior of this function may change in the future.
        Do not use it in production.

    Example:

    .. code:: python

        version = "1.0"
        options = await launcher_coreutils.generate_test_options()
        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        command = await launcher_corecommand.get_minecraft_command(version, minecraft_directory, options)
        await asyncio.create_subprocess_exec(*command)
    """
    return {
        "username": f"Player{random.randrange(100, 1000)}",
        "uuid": str(uuid.uuid4()),
        "token": "",
    }


async def is_version_valid(
    version: str, minecraft_directory: str | os.PathLike
) -> bool:
    """
    Checks if the given version exists.
    This checks if the given version is installed or offered to download by Mojang.
    Basically you can use this tho check, if the given version can be used with :func:`~launcher_core.install.install_minecraft_version`.

    Example:

    .. code:: python

        version = "1.0"
        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        if await launcher_coreutils.is_version_valid(version, minecraft_directory):
            print(f"{version} is a valid version")
        else:
            print(f"{version} is not a valid version")

    :param version: A Minecraft version
    :param minecraft_directory: The path to your Minecraft directory
    """
    if await asyncio.to_thread(
        os.path.isdir, os.path.join(minecraft_directory, "versions", version)
    ):
        return True
    for i in await get_version_list():
        if i["id"] == version:
            return True
    return False


async def is_vanilla_version(version: str) -> bool:
    """
    Checks if the given version is a vanilla version

    Example:

    .. code:: python

        version = "1.0"
        if await launcher_coreutils.is_vanilla_version(version):
            print(f"{version} is a vanilla version")
        else:
            print(f"{version} is not a vanilla version")

    :param version: A Minecraft version
    """
    for i in await get_version_list():
        if i["id"] == version:
            return True
    return False


async def is_platform_supported() -> bool:
    """
    Checks if the current platform is supported

    Example:

    .. code:: python

        if not await launcher_coreutils.is_platform_supported():
            print("Your platform is not supported", file=sys.stderr)
            sys.exit(1)
    """
    if platform.system() not in ["Windows", "Darwin", "Linux"]:
        return False
    return True


async def is_minecraft_installed(minecraft_directory: str | os.PathLike) -> bool:
    """
    Checks, if there is already a existing Minecraft Installation in the given Directory

    Example:

    .. code:: python

        minecraft_directory = await launcher_coreutils.get_minecraft_directory()
        if await launcher_coreutils.is_minecraft_installed(minecraft_directory):
            print("Minecraft is installed")
        else:
            print("Minecraft is not installed")

    :param minecraft_directory: The path to your Minecraft directory
    :return: Is a Installation is found
    """
    try:
        versions_path = os.path.join(minecraft_directory, "versions")
        libraries_path = os.path.join(minecraft_directory, "libraries")
        assets_path = os.path.join(minecraft_directory, "assets")

        is_versions = await asyncio.to_thread(os.path.isdir, versions_path)
        is_libraries = await asyncio.to_thread(os.path.isdir, libraries_path)
        is_assets = await asyncio.to_thread(os.path.isdir, assets_path)

        await asyncio.to_thread(assert_func, is_versions)
        await asyncio.to_thread(assert_func, is_libraries)
        await asyncio.to_thread(assert_func, is_assets)
        return True
    except AssertionError:
        return False

def sync(coroutine: Coroutine[Any, Any, Any]) -> Any:
    """将异步函数/协程强制同步执行（仿 bilibili_api 设计）[6]
    
    Args:
        coroutine: 需要同步化的协程对象或异步函数调用
        
    Returns:
        同步执行后的结果
        
    Example:
        >>> async def async_func(): ...
        >>> result = sync(async_func())  # 同步执行异步函数
    """
    try:
        # 获取或创建事件循环
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coroutine)
    except Exception as e:
        logger.error("同步执行失败: %s", e)  # 使用现有日志系统[3][4]
        raise
