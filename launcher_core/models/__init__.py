"""
Pydantic Models Package
從 TypedDict 定義轉換而來的 Pydantic 模型包

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

# 認證相關模型
from .auth import AzureApplication, Credential, MinecraftUUID

# Minecraft 相關模型
from .minecraft import (
    MinecraftOptions,
    LatestMinecraftVersions,
    MinecraftVersionInfo,
    VanillaLauncherProfileResolution,
    VanillaLauncherProfile,
    AssetInfo,
)

# Java 相關模型
from .java import JavaInformation

# 模組和模組載入器相關模型
from .modding import (
    FabricMinecraftVersion,
    FabricLoader,
    QuiltMinecraftVersion,
    QuiltLoader,
    MrpackInformation,
    MrpackInstallOptions,
    ModInfo,
)

# 下載和庫文件相關模型
from .downloads import DownloadInfo, LibraryInfo, CallbackDict

# 運行時相關模型
from .runtime import JvmRuntimeInformation, VersionRuntimeInformation

# 新聞相關模型
from .news import MinecraftNews, JavaPatchNotes

# Mojang 相關模型
from .mojang import SkinData, MinecraftProfileResponse

# 設定檔相關模型
from .profiles import LaunchProfile

# 伺服器相關模型
from .server import ServerInfo

# 啟動器設定相關模型
from .launcher import LauncherSettings

# 導出所有模型
__all__ = [
    # 認證相關
    "AzureApplication",
    "Credential",
    "MinecraftUUID",
    # Minecraft 相關
    "MinecraftOptions",
    "LatestMinecraftVersions",
    "MinecraftVersionInfo",
    "VanillaLauncherProfileResolution",
    "VanillaLauncherProfile",
    "AssetInfo",
    # Java 相關
    "JavaInformation",
    # 模組相關
    "FabricMinecraftVersion",
    "FabricLoader",
    "QuiltMinecraftVersion",
    "QuiltLoader",
    "MrpackInformation",
    "MrpackInstallOptions",
    "ModInfo",
    # 下載相關
    "DownloadInfo",
    "LibraryInfo",
    "CallbackDict",
    # 運行時相關
    "JvmRuntimeInformation",
    "VersionRuntimeInformation",
    # 新聞相關
    "MinecraftNews",
    "JavaPatchNotes",
    # Mojang 相關
    "SkinData",
    "MinecraftProfileResponse",
    # 設定檔相關
    "LaunchProfile",
    # 伺服器相關
    "ServerInfo",
    # 啟動器設定相關
    "LauncherSettings",
]
