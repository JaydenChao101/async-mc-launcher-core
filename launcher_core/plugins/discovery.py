# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""提供插件發現和管理的輔助功能。

此模組包含:
- 插件目錄的自動發現
- 內置插件的加載
- 使用者自定義插件的發現
"""

import os
import sys
import importlib
import pkgutil
import inspect
from typing import List, Type, Optional
from pathlib import Path

from .base import LauncherPlugin
from ..logging_utils import logger


def find_plugin_directories() -> List[str]:
    """尋找系統中可能包含插件的目錄。

    搜索順序:
    1. 環境變量 LAUNCHER_PLUGIN_DIRS 指定的目錄
    2. 用戶主目錄下的 .minecraft/plugins 目錄
    3. 當前工作目錄下的 plugins 目錄
    4. 啟動器包內置的 plugins/builtin 目錄

    Returns:
        找到的插件目錄列表
    """
    plugin_dirs = []

    # 檢查環境變量
    env_dirs = os.environ.get("LAUNCHER_PLUGIN_DIRS", "")
    if env_dirs:
        for dir_path in env_dirs.split(os.pathsep):
            if os.path.isdir(dir_path):
                plugin_dirs.append(dir_path)

    # 用戶主目錄下的插件
    user_plugin_dir = os.path.join(os.path.expanduser("~"), ".minecraft", "plugins")
    if os.path.isdir(user_plugin_dir):
        plugin_dirs.append(user_plugin_dir)

    # 當前工作目錄下的插件
    cwd_plugin_dir = os.path.join(os.getcwd(), "plugins")
    if os.path.isdir(cwd_plugin_dir):
        plugin_dirs.append(cwd_plugin_dir)

    # 內置插件目錄
    builtin_plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins", "builtin")
    if os.path.isdir(builtin_plugin_dir):
        plugin_dirs.append(builtin_plugin_dir)

    return plugin_dirs


async def load_plugin_from_path(plugin_path: str) -> Optional[Type[LauncherPlugin]]:
    """從指定路徑加載插件。

    Args:
        plugin_path: 插件模組路徑

    Returns:
        插件類，如果加載失敗則返回 None
    """
    try:
        # 獲取模組名
        module_name = os.path.basename(plugin_path)
        if module_name.endswith(".py"):
            module_name = module_name[:-3]

        # 創建模組規範
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            logger.error(f"無法為 {plugin_path} 創建模組規範")
            return None

        # 加載模組
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 尋找插件類
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (inspect.isclass(attr) and
                issubclass(attr, LauncherPlugin) and
                attr is not LauncherPlugin):
                logger.debug(f"從 {plugin_path} 加載了插件類 {attr_name}")
                return attr

        logger.warning(f"在 {plugin_path} 中沒有找到插件類")
        return None

    except Exception as e:
        logger.error(f"加載插件 {plugin_path} 時發生錯誤: {e}")
        return None


async def discover_plugins_in_directory(directory: str) -> List[Type[LauncherPlugin]]:
    """發現指定目錄中的所有插件。

    Args:
        directory: 要搜索的目錄

    Returns:
        發現的插件類列表
    """
    plugin_classes = []

    # 確保目錄存在於 Python 路徑中
    if directory not in sys.path:
        sys.path.insert(0, directory)

    try:
        # 搜索 .py 文件
        for file in os.listdir(directory):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_path = os.path.join(directory, file)
                plugin_class = await load_plugin_from_path(plugin_path)
                if plugin_class:
                    plugin_classes.append(plugin_class)

        # 搜索子目錄中的 __init__.py
        for item in os.listdir(directory):
            subdir = os.path.join(directory, item)
            if os.path.isdir(subdir) and not item.startswith("__"):
                init_file = os.path.join(subdir, "__init__.py")
                if os.path.isfile(init_file):
                    plugin_class = await load_plugin_from_path(init_file)
                    if plugin_class:
                        plugin_classes.append(plugin_class)

    except Exception as e:
        logger.error(f"搜索目錄 {directory} 中的插件時發生錯誤: {e}")

    return plugin_classes
