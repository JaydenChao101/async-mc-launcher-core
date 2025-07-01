# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

import os
import asyncio
import importlib.util
import sys
from pathlib import Path

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
    plugins,
)
from .utils import sync
from .mojang import verify_mojang_jwt

# 創建全局事件管理器實例供插件使用
from .plugins.events import EventManager
EVENT_MANAGER = EventManager()

# 創建全局插件管理器實例
from .plugins import PluginManager
PLUGIN_MANAGER = PluginManager()

# 定義默認的插件目錄
DEFAULT_PLUGIN_DIRS = [
    os.path.join(os.path.expanduser("~"), ".minecraft", "plugins"),  # 用戶主目錄下的插件
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins", "builtin"),  # 內置插件
]

# 自動發現並加載插件的函數
async def _auto_discover_and_load_plugins():
    """自動發現並加載可用的插件。"""
    try:
        # 添加默認插件目錄
        for plugin_dir in DEFAULT_PLUGIN_DIRS:
            if os.path.isdir(plugin_dir):
                PLUGIN_MANAGER.add_plugin_directory(plugin_dir)

        # 檢查環境變量中的額外插件目錄
        extra_dirs = os.environ.get("LAUNCHER_PLUGIN_DIRS", "")
        if extra_dirs:
            for directory in extra_dirs.split(os.pathsep):
                if os.path.isdir(directory):
                    PLUGIN_MANAGER.add_plugin_directory(directory)

        # 發現可用插件
        plugin_classes = await PLUGIN_MANAGER.discover_plugins()
        logger.info(f"發現 {len(plugin_classes)} 個可用插件")

        # 加載所有發現的插件
        for plugin_class in plugin_classes:
            try:
                await PLUGIN_MANAGER.load_plugin(plugin_class)
            except Exception as e:
                logger.error(f"加載插件失敗: {e}")

        # 初始化已加載的插件
        await PLUGIN_MANAGER.initialize_plugins()
        logger.info(f"已成功初始化 {len(PLUGIN_MANAGER.loaded_plugins)} 個插件")

        # 發布插件系統初始化完成事件
        from .plugins.events import Event
        class PluginSystemInitializedEvent(Event):
            def __init__(self):
                super().__init__("plugin_system")

        await EVENT_MANAGER.publish(PluginSystemInitializedEvent())

    except Exception as e:
        logger.error(f"插件自動發現和加載過程中發生錯誤: {e}")

# 設置一個標誌，確保只運行一次自動加載
_plugins_auto_loaded = False

# 提供公開API用於手動觸發插件加載
async def load_plugins():
    """手動觸發插件發現和加載過程。"""
    global _plugins_auto_loaded
    if not _plugins_auto_loaded:
        await _auto_discover_and_load_plugins()
        _plugins_auto_loaded = True

# 啟動異步任務自動加載插件
# 我們使用 sync 函數確保即使在同步上下文中也能正常工作
try:
    sync(_auto_discover_and_load_plugins())
    _plugins_auto_loaded = True
    logger.info("插件自動加載完成")
except Exception as e:
    logger.warning(f"插件自動加載失敗: {e}，將等待手動加載")

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
    "plugins",
    "exceptions",
    "_types",
    "microsoft_types",
    "logger",
    "sync",
    "Credential",
    "AzureApplication",
    "verify_mojang_jwt",
    "EVENT_MANAGER",
    "PLUGIN_MANAGER",
    "load_plugins",  # 添加手動加載函數到公開API
]
