# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""
runtime allows to install the java runtime. This module is used by
:func:`~launcher_core..install.install_minecraft_version`,
so you don't need to use it in your code most of the time.
"""
import subprocess
import datetime
import platform
import os
import asyncio
import aiohttp
import aiofiles

from ._helper import (
    get_user_agent,
    download_file,
    empty,
    get_sha1_hash,
    check_path_inside_minecraft_directory,
    get_client_json,
)
from ._internal_types.runtime_types import (
    RuntimeListJson,
    PlatformManifestJson,
    _PlatformManifestJsonFile,
)
from ._types import CallbackDict, JvmRuntimeInformation, VersionRuntimeInformation
from .exceptions import VersionNotFound, PlatformNotSupported


_JVM_MANIFEST_URL = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"


def _get_jvm_platform_string() -> str:
    """
    Get the name that is used the identify the platform
    """
    match platform.system():
        case "Windows":
            if platform.architecture()[0] == "32bit":
                return "windows-x86"
            else:
                return "windows-x64"
        case "Linux":
            if platform.architecture()[0] == "32bit":
                return "linux-i386"
            else:
                return "linux"
        case "Darwin":
            if platform.machine() == "arm64":
                return "mac-os-arm64"
            else:
                return "mac-os"
        case _:
            return "gamecore"


async def get_jvm_runtimes() -> list[str]:
    """
    Returns a list of all jvm runtimes

    Example:

    .. code:: python

        async for runtime in await launcher_coreruntime.get_jvm_runtimes():
            print(runtime)
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            _JVM_MANIFEST_URL, headers={"user-agent": get_user_agent()}
        ) as response:
            manifest_data: RuntimeListJson = await response.json()

    jvm_list = []
    for key in manifest_data[_get_jvm_platform_string()].keys():
        jvm_list.append(key)
    return jvm_list


async def get_installed_jvm_runtimes(
    minecraft_directory: str | os.PathLike,
) -> list[str]:
    """
    Returns a list of all installed jvm runtimes

    Example:

    .. code:: python

        for runtime in await launcher_coreruntime.get_installed_jvm_runtimes():
            print(runtime)

    :param minecraft_directory: The path to your Minecraft directory
    """
    try:
        return os.listdir(os.path.join(minecraft_directory, "runtime"))
    except FileNotFoundError:
        return []


async def install_jvm_runtime(
    jvm_version: str,
    minecraft_directory: str | os.PathLike,
    callback: CallbackDict | None = None,
    max_concurrency: int | None = None,
) -> None:
    """
    Installs the given jvm runtime. callback is the same dict as in the install module.

    Example:

    .. code:: python

        runtime_version = "java-runtime-gamma"
        minecraft_directory = launcher_coreutils.get_minecraft_directory()
        await launcher_coreruntime.install_jvm_runtime(runtime_version, minecraft_directory)

    :param jvm_version: The Name of the JVM version
    :param minecraft_directory: The path to your Minecraft directory
    :param callback: the same dict as for :func:`~launcher_core.install.install_minecraft_version`
    :param max_concurrency: number of concurrent tasks for asynchronous downloads. If None, it will be set automatically.
    :raises VersionNotFound: The given JVM Version was not found
    :raises FileOutsideMinecraftDirectory: A File should be placed outside the given Minecraft directory
    """
    if callback is None:
        callback = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            _JVM_MANIFEST_URL, headers={"user-agent": get_user_agent()}
        ) as response:
            manifest_data: RuntimeListJson = await response.json()

        platform_string = _get_jvm_platform_string()
        # Check if the jvm version exists
        if jvm_version not in manifest_data[platform_string]:
            raise VersionNotFound(jvm_version)
        # Check if there is a platform manifest
        if len(manifest_data[platform_string][jvm_version]) == 0:
            return

        async with session.get(
            manifest_data[platform_string][jvm_version][0]["manifest"]["url"],
            headers={"user-agent": get_user_agent()},
        ) as response:
            platform_manifest: PlatformManifestJson = await response.json()

    base_path = os.path.join(
        minecraft_directory, "runtime", jvm_version, platform_string, jvm_version
    )
    file_list: list[str] = []

    async def install_runtime_file(key: str, value: _PlatformManifestJsonFile) -> None:
        """Install the single runtime file."""
        current_path = os.path.join(base_path, key)
        check_path_inside_minecraft_directory(minecraft_directory, current_path)

        if value["type"] == "file":
            # Prefer downloading the compresses file
            if "lzma" in value["downloads"]:
                await download_file(
                    value["downloads"]["lzma"]["url"],
                    current_path,
                    sha1=value["downloads"]["raw"]["sha1"],
                    callback=callback,
                    lzma_compressed=True,
                )
            else:
                await download_file(
                    value["downloads"]["raw"]["url"],
                    current_path,
                    sha1=value["downloads"]["raw"]["sha1"],
                    callback=callback,
                )

            # Make files executable on unix systems
            if value["executable"]:
                try:
                    subprocess.run(["chmod", "+x", current_path], check=True)
                except FileNotFoundError:
                    pass
            file_list.append(key)

        elif value["type"] == "directory":
            try:
                os.makedirs(current_path)
            except Exception:
                pass

        elif value["type"] == "link":
            check_path_inside_minecraft_directory(
                minecraft_directory, os.path.join(base_path, value["target"])
            )
            os.makedirs(os.path.dirname(current_path), exist_ok=True)

            try:
                os.symlink(value["target"], current_path)
            except Exception:
                pass

    # Download all files of the runtime
    callback.get("setMax", empty)(len(platform_manifest["files"]) - 1)
    count = 0
    sem = asyncio.Semaphore(max_concurrency if max_concurrency else 10)

    async def bounded_install(key: str, value: _PlatformManifestJsonFile) -> None:
        nonlocal count
        async with sem:
            await install_runtime_file(key, value)
            count += 1
            callback.get("setProgress", empty)(count)

    # Create and run tasks for all files
    tasks = [
        bounded_install(key, value) for key, value in platform_manifest["files"].items()
    ]
    await asyncio.gather(*tasks)

    # Create the .version file
    version_path = os.path.join(
        minecraft_directory, "runtime", jvm_version, platform_string, ".version"
    )
    check_path_inside_minecraft_directory(minecraft_directory, version_path)
    async with aiofiles.open(version_path, "w", encoding="utf-8") as f:
        await f.write(manifest_data[platform_string][jvm_version][0]["version"]["name"])

    # Writes the .sha1 file
    # It has the structure {path} /#// {sha1} {creation time in nanoseconds}
    sha1_path = os.path.join(
        minecraft_directory,
        "runtime",
        jvm_version,
        platform_string,
        f"{jvm_version}.sha1",
    )
    check_path_inside_minecraft_directory(minecraft_directory, sha1_path)
    async with aiofiles.open(sha1_path, "w", encoding="utf-8") as f:
        for current_file in file_list:
            current_path = os.path.join(base_path, current_file)
            ctime = os.stat(current_path).st_ctime_ns
            sha1 = get_sha1_hash(current_path)
            await f.write(f"{current_file} /#// {sha1} {ctime}\n")


async def get_executable_path(
    jvm_version: str, minecraft_directory: str | os.PathLike
) -> str | None:
    """
    Returns the path to the executable. Returns None if none is found.

    Example:

    .. code:: python

        runtime_version = "java-runtime-gamma"
        minecraft_directory = launcher_coreutils.get_minecraft_directory()
        executable_path = await launcher_coreruntime.get_executable_path(runtime_version, minecraft_directory)
        if executable_path is not None:
            print(f"Executable path: {executable_path}")
        else:
            print("The executable path was not found")

    :param jvm_version: The Name of the JVM version
    :param minecraft_directory: The path to your Minecraft directory
    """
    javaPath = os.path.join(
        minecraft_directory,
        "runtime",
        jvm_version,
        _get_jvm_platform_string(),
        jvm_version,
        "bin",
        "java",
    )
    if os.path.isfile(javaPath):
        return javaPath
    elif os.path.isfile(javaPath + ".exe"):
        return javaPath + ".exe"
    javaPath = javaPath.replace(
        os.path.join("bin", "java"),
        os.path.join("jre.bundle", "Contents", "Home", "bin", "java"),
    )
    if os.path.isfile(javaPath):
        return javaPath
    else:
        return None


async def get_jvm_runtime_information(jvm_version: str) -> JvmRuntimeInformation:
    """
    Returns some Information about a JVM Version

    Example:

    .. code:: python

        runtime_version = "java-runtime-gamma"
        information = await launcher_coreruntime.get_jvm_runtime_information(runtime_version)
        print("Java version: " + information["name"])
        print("Release date: " + information["released"].isoformat())

    :param jvm_version: A JVM Version
    :raises VersionNotFound: The given JVM Version was not found
    :raises VersionNotFound: The given JVM Version is not available on this Platform
    :return: A Dict with Information
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            _JVM_MANIFEST_URL, headers={"user-agent": get_user_agent()}
        ) as response:
            manifest_data: RuntimeListJson = await response.json()

    platform_string = _get_jvm_platform_string()

    # Check if the jvm version exists
    if jvm_version not in manifest_data[platform_string]:
        raise VersionNotFound(jvm_version)

    if len(manifest_data[platform_string][jvm_version]) == 0:
        raise PlatformNotSupported()

    return {
        "name": manifest_data[platform_string][jvm_version][0]["version"]["name"],
        "released": datetime.datetime.fromisoformat(
            manifest_data[platform_string][jvm_version][0]["version"]["released"]
        ),
    }


async def get_version_runtime_information(
    version: str, minecraft_directory: str | os.PathLike
) -> VersionRuntimeInformation | None:
    """
    Returns information about the runtime used by a version

    Example:

    .. code:: python

        minecraft_version = "1.20"
        minecraft_directory = launcher_coreutils.get_minecraft_directory()
        information = await launcher_coreruntime.get_version_runtime_information(minecraft_version, minecraft_directory)
        print("Name: " + information["name"])
        print("Java version: " + str(information["javaMajorVersion"]))

    :param minecraft_directory: The path to your Minecraft directory
    :raises VersionNotFound: The Minecraft version was not found
    :return: A Dict with Information. None if the version has no runtime information.
    """
    data = await get_client_json(version, minecraft_directory)

    if "javaVersion" not in data:
        return None

    return {
        "name": data["javaVersion"]["component"],
        "javaMajorVersion": data["javaVersion"]["majorVersion"],
    }
