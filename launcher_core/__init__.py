# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

__version__ = "0.4-rc"

from .logging_utils import logger
from .check_version import check_version
from .config.load_launcher_config import ConfigManager, LauncherConfig
from .models.auth import Credential
from . import (
    exceptions,
    _helper,
    CustomClass,
    setting,
    microsoft_account,
    microsoft_types,
)

__all__ = [
    "exceptions",
    "_helper",
    "ConfigManager",
    "LauncherConfig",
    "Credential",
    "CustomClass",
    "setting",
    "microsoft_account",
    "microsoft_types",
    "logger",
    "__version__",
    "check_version",
]
