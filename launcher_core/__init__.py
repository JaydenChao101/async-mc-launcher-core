# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

__version__ = "0.3.1"

from .logging_utils import logger
from ._types import (
    Credential,
    AzureApplication,
)
from .check_version import check_version
from .config.load_launcher_config import ConfigManager, LauncherConfig

# 導入 Pydantic 模型
from .pydantic_models import (
    MinecraftOptions,
    LoginCredentials,
    LaunchProfile,
    ServerInfo,
    ModInfo,
    LauncherSettings,
    JavaInformation,
    DownloadInfo,
    LibraryInfo,
    AssetInfo,
    LatestMinecraftVersions,
    MinecraftVersionInfo,
    FabricMinecraftVersion,
    FabricLoader,
    QuiltMinecraftVersion,
    QuiltLoader,
    VanillaLauncherProfile,
    VanillaLauncherProfileResolution,
    MrpackInformation,
    MinecraftUUID
)

from . import (
    command,
    install,
    microsoft_account,
    utils,
    java_utils,
    forge,
    fabric,
    quilt,
    news,
    runtime,
    mrpack,
    exceptions,
    _types,
    microsoft_types,
    config,
    pydantic_models,
)
from .utils import sync
from .mojang import verify_mojang_jwt

__all__ = [
    "command",
    "install",
    "microsoft_account",
    "utils",
    "news",
    "java_utils",
    "forge",
    "fabric",
    "quilt",
    "runtime",
    "mrpack",
    "exceptions",
    "_types",
    "microsoft_types",
    "config",
    "pydantic_models",
    "logger",
    "sync",
    "Credential",
    "AzureApplication",
    "ConfigManager",
    "LauncherConfig",
    # Pydantic 模型
    "MinecraftOptions",
    "LoginCredentials",
    "LaunchProfile",
    "ServerInfo",
    "ModInfo",
    "LauncherSettings",
    "JavaInformation",
    "DownloadInfo",
    "LibraryInfo",
    "AssetInfo",
    "LatestMinecraftVersions",
    "MinecraftVersionInfo",
    "FabricMinecraftVersion",
    "FabricLoader",
    "QuiltMinecraftVersion",
    "QuiltLoader",
    "VanillaLauncherProfile",
    "VanillaLauncherProfileResolution",
    "MrpackInformation",
    "MinecraftUUID",
    "__version__",
    "check_version",
]
