# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""
This module contains all Types for minecraft-launcher-lib.
If you are not interested in static typing just ignore it.
For more information about TypedDict see `PEP 589 <https://peps.python.org/pep-0589/>`_.
"""
from typing import Literal, TypedDict, Callable, Union, NewType
import datetime
from uuid import UUID
from dataclasses import dataclass

MinecraftUUID = NewType("MinecraftUUID", UUID)


class MinecraftOptions(TypedDict, total=False):
    """The options for the Minecraft Launcher"""

    username: str
    uuid: MinecraftUUID
    token: str
    executablePath: str
    defaultExecutablePath: str
    jvmArguments: list[str]
    launcherName: str
    launcherVersion: str
    gameDirectory: str
    demo: bool = False
    customResolution: bool
    resolutionWidth: Union[int, str, None]
    resolutionHeight: Union[int, str, None]
    server: str
    port: str
    nativesDirectory: str
    enableLoggingConfig: bool
    disableMultiplayer: bool
    disableChat: bool
    quickPlayPath: str | None
    quickPlaySingleplayer: str | None
    quickPlayMultiplayer: str | None
    quickPlayRealms: str | None
    gameDir: str | None


class CallbackDict(TypedDict, total=False):
    setStatus: Callable[[str], None]
    setProgress: Callable[[int], None]
    setMax: Callable[[int], None]


class LatestMinecraftVersions(TypedDict):
    """The latest Minecraft versions"""

    release: str
    snapshot: str


class MinecraftVersionInfo(TypedDict):
    """The Minecraft version information"""

    id: str
    type: str
    releaseTime: datetime.datetime
    complianceLevel: int


# fabric


class FabricMinecraftVersion(TypedDict):
    """The Minecraft version information"""

    version: str
    stable: bool


class FabricLoader(TypedDict):
    """The Fabric loader information"""

    separator: str
    build: int
    maven: str
    version: str
    stable: bool


# quilt


class QuiltMinecraftVersion(TypedDict):
    """The Minecraft version information"""

    version: str
    stable: bool


class QuiltLoader(TypedDict):
    """The Quilt loader information"""

    separator: str
    build: int
    maven: str
    version: str


# java_utils


class JavaInformation(TypedDict):
    """The Java information"""

    path: str
    name: str
    version: str
    javaPath: str
    javawPath: str | None
    is64Bit: bool
    openjdk: bool


# vanilla_launcher


class VanillaLauncherProfileResolution(TypedDict):
    """The resolution of the Vanilla Launcher profile"""

    height: int
    width: int


class VanillaLauncherProfile(TypedDict, total=False):
    """The Vanilla Launcher profile"""

    name: str
    version: str | None
    versionType: Literal["latest-release", "latest-snapshot", "custom"]
    gameDirectory: str | None
    javaExecutable: str | None
    javaArguments: list[str] | None
    customResolution: VanillaLauncherProfileResolution | None


# mrpack


class MrpackInformation(TypedDict):
    """The MRPack information"""

    name: str
    summary: str
    versionId: str
    formatVersion: int
    minecraftVersion: str
    optionalFiles: list[str]


class MrpackInstallOptions(TypedDict, total=False):
    """The MRPack install options"""

    optionalFiles: list[str]
    skipDependenciesInstall: bool


# runtime


class JvmRuntimeInformation(TypedDict):
    """The Java runtime information"""

    name: str
    released: datetime.datetime


class VersionRuntimeInformation(TypedDict):
    """The Minecraft version runtime information"""

    name: str
    javaMajorVersion: int


class _NewsEntryPlayPageImage(TypedDict):
    """The image for the play page"""

    title: str
    url: str


class _NewsEntryNewsPageImageDimensions(TypedDict):
    """The dimensions of the news page image"""

    width: int
    height: int


class _NewsEntryNewsPageImage(TypedDict):
    """The image for the news page"""

    title: str
    url: str
    dimensions: _NewsEntryNewsPageImageDimensions


class _NewsEntry(TypedDict):
    title: str
    category: str
    date: str
    text: str
    playPageImage: _NewsEntryPlayPageImage
    newsPageImage: _NewsEntryNewsPageImage
    readMoreLink: str
    newsType: list[str]
    id: str


class MinecraftNews(TypedDict):
    """The Minecraft news"""

    version: Literal[1]
    entries: list[_NewsEntry]


class _JavaPatchNoteEntryImage(TypedDict):
    url: str
    title: str


class _JavaPatchNoteEntry(TypedDict):
    title: str
    type: Literal["release", "snapshot"]
    version: str
    image: _JavaPatchNoteEntryImage
    body: str
    contentPath: str


class JavaPatchNotes(TypedDict):
    """The Java patch notes"""

    version: Literal[1]
    entries: list[_JavaPatchNoteEntry]


class SkinData(TypedDict):
    """The skin of the player"""

    skin: str
    cape: str


class MinecraftProfileProperty(TypedDict, total=False):
    """The property of the player"""

    name: str
    value: str
    signature: str


class MinecraftProfileSkin(TypedDict, total=False):
    """The skin of the player"""

    id: str
    state: str
    url: str
    variant: str
    alias: str


class MinecraftProfileCape(TypedDict, total=False):
    """The cape of the player"""

    id: str
    state: str
    url: str
    alias: str


class MinecraftProfileResponse(TypedDict, total=False):
    """The response of the player"""

    id: str
    name: str
    properties: list[MinecraftProfileProperty]  # 舊版
    skins: list[MinecraftProfileSkin]  # 新版
    capes: list[MinecraftProfileCape]  # 新版


@dataclass(frozen=True)
class AzureApplication:
    """The Azure Application ID and Secret"""

    # The client ID of the Azure Application
    client_id: str = "00000000402b5328"
    client_secret: str = None
    redirect_uri: str = "https://login.live.com/oauth20_desktop.srf"


@dataclass(frozen=True)
class Credential:
    """The credential of the player"""

    access_token: str = None
    username: str = None
    uuid: MinecraftUUID = None
    refresh_token: str = None
