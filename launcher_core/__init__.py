# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

__version__ = "0.3.1"

from .logging_utils import logger
from ._types import (
    Credential,
    AzureApplication,
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
    "logger",
    "sync",
    "Credential",
    "AzureApplication",
    "verify_mojang_jwt",
]
