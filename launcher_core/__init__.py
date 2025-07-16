# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

__version__ = "0.4-rc"

from .logging_utils import logger
from .check_version import check_version
from .config.load_launcher_config import ConfigManager, LauncherConfig

# 導入 Pydantic 模型
from .models.auth import MinecraftUUID, Credential, AzureApplication

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
    microsoft_types,
    config,
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
    "models",
    "microsoft_types",
    "config",
    "logger",
    "sync",
    "Credential",
    "AzureApplication",
    "ConfigManager",
    "LauncherConfig",
    "MinecraftUUID",
    "__version__",
    "check_version",
    "verify_mojang_jwt",
]
