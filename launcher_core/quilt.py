# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""
quilt contains functions for dealing with the `Quilt modloader <https://quiltmc.org>`_.

You may have noticed, that the Functions are the same as in the :doc:`fabric` module.
That's because Quilt is a Fork of Fabric. This module behaves exactly the same as the fabric module.
"""
import asyncio
import tempfile
import os

from ._helper import (
    download_file,
    get_requests_response_cache,
    parse_maven_metadata,
    empty,
    SUBPROCESS_STARTUP_INFO,
)
from .exceptions import VersionNotFound, UnsupportedVersion, ExternalProgramError
from ._types import QuiltMinecraftVersion, QuiltLoader, CallbackDict
from .install import install_minecraft_version
from .utils import is_version_valid


async def get_all_minecraft_versions() -> list[QuiltMinecraftVersion]:
    """
    Returns all available Minecraft Versions for Quilt

    Example:

    .. code:: python

        for version in await launcher_corequilt.get_all_minecraft_versions():
            print(version["version"])
    """
    quilt_minecraft_versions_url = "https://meta.quiltmc.org/v3/versions/game"
    return await get_requests_response_cache(quilt_minecraft_versions_url)


async def get_stable_minecraft_versions() -> list[str]:
    """
    Returns a list which only contains the stable Minecraft versions that supports Quilt

    Example:

    .. code:: python

        for version in await launcher_corequilt.get_stable_minecraft_versions():
            print(version)
    """
    minecraft_versions = await get_all_minecraft_versions()
    stable_versions = []
    for i in minecraft_versions:
        if i["stable"] is True:
            stable_versions.append(i["version"])
    return stable_versions


async def get_latest_minecraft_version() -> str:
    """
    Returns the latest unstable Minecraft versions that supports Quilt. This could be a snapshot.

    Example:

    .. code:: python

        print("Latest Minecraft version: " +
            await launcher_corequilt.get_latest_minecraft_version())
    """
    minecraft_versions = await get_all_minecraft_versions()
    return minecraft_versions[0]["version"]


async def get_latest_stable_minecraft_version() -> str:
    """
    Returns the latest stable Minecraft version that supports Quilt

    Example:

    .. code:: python

        print("Latest stable Minecraft version: " +
            await launcher_corequilt.get_latest_stable_minecraft_version())
    """
    stable_versions = await get_stable_minecraft_versions()
    return stable_versions[0]


async def is_minecraft_version_supported(version: str) -> bool:
    """
    Checks if a Minecraft version supported by Quilt

    Example:

    .. code:: python

        version = "1.20"
        if await launcher_corequilt.is_minecraft_version_supported(version):
            print(f"{version} is supported by quilt")
        else:
            print(f"{version} is not supported by quilt")

    :param version: A vanilla version
    """
    minecraft_versions = await get_all_minecraft_versions()
    for i in minecraft_versions:
        if i["version"] == version:
            return True
    return False


async def get_all_loader_versions() -> list[QuiltLoader]:
    """
    Returns all loader versions

    Example:

    .. code:: python

        for version in await launcher_corequilt.get_all_loader_versions():
            print(version["version"])
    """
    quilt_loader_versions_url = "https://meta.quiltmc.org/v3/versions/loader"
    return await get_requests_response_cache(quilt_loader_versions_url)


async def get_latest_loader_version() -> str:
    """
    Get the latest loader version


    Example:

    .. code:: python

        print("Latest loader version: " + await launcher_corequilt.get_latest_loader_version())
    """
    loader_versions = await get_all_loader_versions()
    return loader_versions[0]["version"]


async def get_latest_installer_version() -> str:
    """
    Returns the latest installer version

    Example:

    .. code:: python

        print("Latest installer version: " +
            await launcher_corequilt.get_latest_installer_version())
    """
    quilt_installer_maven_url = "https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-installer/maven-metadata.xml"
    result = await parse_maven_metadata(quilt_installer_maven_url)
    return result["latest"]


async def install_quilt(
    minecraft_version: str,
    minecraft_directory: str | os.PathLike,
    loader_version: str | None = None,
    callback: CallbackDict | None = None,
    java: str | os.PathLike | None = None,
) -> None:
    """
    Installs the Quilt modloader.

    Example:

    .. code:: python

        minecraft_version = "1.20"
        minecraft_directory = launcher_coreutils.get_minecraft_directory()
        await launcher_corequilt.install_quilt(minecraft_version, minecraft_directory)

    :param minecraft_version: A vanilla version that is supported by Quilt
    :param minecraft_directory: The path to your Minecraft directory
    :param loader_version: The Quilt loader version. If not given it will use the latest
    :param callback: The same dict as for :func:`~launcher_core.install.install_minecraft_version`
    :param java: A Path to a custom Java executable
    :raises VersionNotFound: The given Minecraft does not exists
    :raises UnsupportedVersion: The given Minecraft version is not supported by Quilt
    """
    path = str(minecraft_directory)
    if not callback:
        callback = {}

    # Check if the given version exists
    if not await is_version_valid(minecraft_version, minecraft_directory):
        raise VersionNotFound(minecraft_version)

    # Check if the given Minecraft version supported
    if not await is_minecraft_version_supported(minecraft_version):
        raise UnsupportedVersion(minecraft_version)

    # Get latest loader version if not given
    if not loader_version:
        loader_version = await get_latest_loader_version()

    # Make sure the Minecraft version is installed
    await install_minecraft_version(minecraft_version, path, callback=callback)

    # Get installer version
    installer_version = await get_latest_installer_version()
    installer_download_url = (
        f"https://maven.quiltmc.org/repository/release/org/quiltmc/"
        f"quilt-installer/{installer_version}/quilt-installer-{installer_version}.jar"
    )

    with tempfile.TemporaryDirectory(
        prefix="minecraft-launcher-lib-quilt-install-"
    ) as tempdir:
        installer_path = os.path.join(tempdir, "quit-installer.jar")

        # Download the installer
        await download_file(
            installer_download_url, installer_path, callback=callback, overwrite=True
        )

        # Run the installer
        callback.get("setStatus", empty)("Running quilt installer")
        command = [
            "java" if java is None else str(java),
            "-jar",
            installer_path,
            "install",
            "client",
            minecraft_version,
            loader_version,
            f"--install-dir={path}",
            "--no-profile",
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            startupinfo=SUBPROCESS_STARTUP_INFO,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise ExternalProgramError(command, stdout, stderr)

    # Install all libs of quilt
    quilt_minecraft_version = f"quilt-loader-{loader_version}-{minecraft_version}"
    await install_minecraft_version(quilt_minecraft_version, path, callback=callback)
