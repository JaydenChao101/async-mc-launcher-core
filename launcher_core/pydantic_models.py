"""
Pydantic Models converted from TypedDict definitions
從 TypedDict 定義轉換而來的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, Callable, Union, NewType
import datetime
from uuid import UUID

# 重新定義 MinecraftUUID
MinecraftUUID = NewType("MinecraftUUID", UUID)

class MinecraftOptions(BaseModel):
    """The options for the Minecraft Launcher"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    username: Optional[str] = None
    uuid: Optional[MinecraftUUID] = None
    token: Optional[str] = None
    executablePath: Optional[str] = None
    defaultExecutablePath: Optional[str] = None
    jvmArguments: Optional[list[str]] = None
    launcherName: Optional[str] = None
    launcherVersion: Optional[str] = None
    gameDirectory: Optional[str] = None
    demo: Optional[bool] = False
    customResolution: Optional[bool] = None
    resolutionWidth: Union[int, str, None]
    resolutionHeight: Union[int, str, None]
    server: Optional[str] = None
    port: Optional[str] = None
    nativesDirectory: Optional[str] = None
    enableLoggingConfig: Optional[bool] = None
    disableMultiplayer: Optional[bool] = None
    disableChat: Optional[bool] = None
    quickPlayPath: str | None
    quickPlaySingleplayer: str | None
    quickPlayMultiplayer: str | None
    quickPlayRealms: str | None
    gameDir: str | None

class CallbackDict(BaseModel):
    """Pydantic model for CallbackDict"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    setStatus: Optional[Callable[[str], None]] = None
    setProgress: Optional[Callable[[int], None]] = None
    setMax: Optional[Callable[[int], None]] = None

class LatestMinecraftVersions(BaseModel):
    """The latest Minecraft versions"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    release: str
    snapshot: str

class MinecraftVersionInfo(BaseModel):
    """The Minecraft version information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    id: str
    type: str
    releaseTime: datetime.datetime
    complianceLevel: int

class FabricMinecraftVersion(BaseModel):
    """The Minecraft version information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    version: str
    stable: bool

class FabricLoader(BaseModel):
    """The Fabric loader information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    separator: str
    build: int
    maven: str
    version: str
    stable: bool

class QuiltMinecraftVersion(BaseModel):
    """The Minecraft version information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    version: str
    stable: bool

class QuiltLoader(BaseModel):
    """The Quilt loader information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    separator: str
    build: int
    maven: str
    version: str

class JavaInformation(BaseModel):
    """The Java information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    path: str
    name: str
    version: str
    javaPath: str
    javawPath: str | None
    is64Bit: bool
    openjdk: bool

class VanillaLauncherProfileResolution(BaseModel):
    """The resolution of the Vanilla Launcher profile"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    height: int
    width: int

class VanillaLauncherProfile(BaseModel):
    """The Vanilla Launcher profile"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    name: Optional[str] = None
    version: str | None
    versionType: Optional[Literal['latest-release', 'latest-snapshot', 'custom']] = None
    gameDirectory: str | None
    javaExecutable: str | None
    javaArguments: list[str] | None
    customResolution: VanillaLauncherProfileResolution | None

class MrpackInformation(BaseModel):
    """The MRPack information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    name: str
    summary: str
    versionId: str
    formatVersion: int
    minecraftVersion: str
    optionalFiles: list[str]

class MrpackInstallOptions(BaseModel):
    """The MRPack install options"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    optionalFiles: Optional[list[str]] = None
    skipDependenciesInstall: Optional[bool] = None

class JvmRuntimeInformation(BaseModel):
    """The Java runtime information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    name: str
    released: datetime.datetime

class VersionRuntimeInformation(BaseModel):
    """The Minecraft version runtime information"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    name: str
    javaMajorVersion: int

class _NewsEntryPlayPageImage(BaseModel):
    """The image for the play page"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    title: str
    url: str

class _NewsEntryNewsPageImageDimensions(BaseModel):
    """The dimensions of the news page image"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    width: int
    height: int

class _NewsEntryNewsPageImage(BaseModel):
    """The image for the news page"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    title: str
    url: str
    dimensions: _NewsEntryNewsPageImageDimensions

class _NewsEntry(BaseModel):
    """Pydantic model for _NewsEntry"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    title: str
    category: str
    date: str
    text: str
    playPageImage: _NewsEntryPlayPageImage
    newsPageImage: _NewsEntryNewsPageImage
    readMoreLink: str
    newsType: list[str]
    id: str

class MinecraftNews(BaseModel):
    """The Minecraft news"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    version: Literal[1]
    entries: list[_NewsEntry]

class _JavaPatchNoteEntryImage(BaseModel):
    """Pydantic model for _JavaPatchNoteEntryImage"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    url: str
    title: str

class _JavaPatchNoteEntry(BaseModel):
    """Pydantic model for _JavaPatchNoteEntry"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    title: str
    type: Literal['release', 'snapshot']
    version: str
    image: _JavaPatchNoteEntryImage
    body: str
    contentPath: str

class JavaPatchNotes(BaseModel):
    """The Java patch notes"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    version: Literal[1]
    entries: list[_JavaPatchNoteEntry]

class SkinData(BaseModel):
    """The skin of the player"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    skin: str
    cape: str

class MinecraftProfileProperty(BaseModel):
    """The property of the player"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    name: Optional[str] = None
    value: Optional[str] = None
    signature: Optional[str] = None

class MinecraftProfileSkin(BaseModel):
    """The skin of the player"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    id: Optional[str] = None
    state: Optional[str] = None
    url: Optional[str] = None
    variant: Optional[str] = None
    alias: Optional[str] = None

class MinecraftProfileCape(BaseModel):
    """The cape of the player"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    id: Optional[str] = None
    state: Optional[str] = None
    url: Optional[str] = None
    alias: Optional[str] = None

class MinecraftProfileResponse(BaseModel):
    """The response of the player"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    id: Optional[str] = None
    name: Optional[str] = None
    properties: Optional[list[MinecraftProfileProperty]] = None
    skins: Optional[list[MinecraftProfileSkin]] = None
    capes: Optional[list[MinecraftProfileCape]] = None