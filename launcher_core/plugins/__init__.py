# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""插件系統允許擴展啟動器核心的功能。

此模組提供：
- 插件註冊和發現機制
- 事件系統用於插件間通信
- 插件掛鉤點用於擴展核心功能
"""

from .manager import PluginManager
from .base import LauncherPlugin, hook
from .events import EventManager, Event

__all__ = [
    "PluginManager",
    "LauncherPlugin",
    "hook",
    "EventManager",
    "Event",
]
