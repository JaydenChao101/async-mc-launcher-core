# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""插件管理器負責插件的加載、初始化和生命週期管理。

此模組提供：
- 插件發現和加載機制
- 插件依賴解析
- 插件啟動和停止管理
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
import pkgutil
import asyncio
from typing import Dict, List, Set, Optional, Type, Any, cast

from .base import LauncherPlugin
from .events import EventManager, Event
from ..logging_utils import logger


class PluginLoadError(Exception):
    """插件加載過程中的錯誤。"""
    pass


class DependencyError(PluginLoadError):
    """插件依賴解析錯誤。"""
    pass


class PluginManager:
    """插件管理器，負責插件的發現、加載和生命週期管理。"""

    def __init__(self) -> None:
        """初始化插件管理器。"""
        self._plugins: Dict[str, LauncherPlugin] = {}
        self._loaded_plugins: Set[str] = set()
        self._event_manager = EventManager()
        self._plugin_dirs: List[str] = []

    @property
    def event_manager(self) -> EventManager:
        """獲取事件管理器。"""
        return self._event_manager

    def add_plugin_directory(self, directory: str) -> None:
        """添加一個插件目錄。

        Args:
            directory: 插件目錄路徑
        """
        if os.path.isdir(directory) and directory not in self._plugin_dirs:
            self._plugin_dirs.append(directory)

    async def discover_plugins(self) -> List[Type[LauncherPlugin]]:
        """發現所有可用的插件類。

        Returns:
            可用的插件類列表
        """
        plugin_classes: List[Type[LauncherPlugin]] = []

        # 先將插件目錄添加到 Python 路徑中
        for plugin_dir in self._plugin_dirs:
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

        # 掃描所有插件目錄
        for plugin_dir in self._plugin_dirs:
            logger.debug(f"正在掃描插件目錄: {plugin_dir}")

            # 遍歷目錄中的所有 Python 模組
            for _, name, ispkg in pkgutil.iter_modules([plugin_dir]):
                module_name = name

                try:
                    # 導入模組
                    module = importlib.import_module(module_name)

                    # 查找模組中的插件類
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # 檢查是否是 LauncherPlugin 的子類，但不是 LauncherPlugin 本身
                        if (inspect.isclass(attr) and
                            issubclass(attr, LauncherPlugin) and
                            attr is not LauncherPlugin):
                            plugin_classes.append(cast(Type[LauncherPlugin], attr))
                            logger.debug(f"發現插件類: {attr_name} 在 {module_name}")

                except Exception as e:
                    logger.error(f"無法加載插件模組 {module_name}: {e}")

        return plugin_classes

    async def load_plugin(self, plugin_class: Type[LauncherPlugin]) -> None:
        """加載並初始化一個插件。

        Args:
            plugin_class: 插件類

        Raises:
            PluginLoadError: 插件加載失敗
        """
        try:
            # 實例化插件
            plugin = plugin_class()

            # 檢查是否已經加載
            if plugin.name in self._plugins:
                logger.warning(f"插件已經加載: {plugin.name}")
                return

            # 添加到插件字典
            self._plugins[plugin.name] = plugin
            logger.info(f"插件已加載: {plugin.name} v{plugin.version}")

        except Exception as e:
            raise PluginLoadError(f"無法加載插件 {plugin_class.__name__}: {e}")

    async def _initialize_plugin(self, plugin_name: str, initialized: Set[str]) -> None:
        """初始化插件及其依賴。

        Args:
            plugin_name: 插件名稱
            initialized: 已初始化的插件集合

        Raises:
            DependencyError: 插件依賴解析失敗
        """
        # 防止循環依賴
        if plugin_name in initialized:
            return

        if plugin_name not in self._plugins:
            raise DependencyError(f"找不到插件: {plugin_name}")

        plugin = self._plugins[plugin_name]

        # 初始化所有依賴
        for dep_name in plugin.dependencies:
            if dep_name not in self._plugins:
                raise DependencyError(f"插件 {plugin_name} 依賴 {dep_name}，但找不到該插件")

            await self._initialize_plugin(dep_name, initialized)

        # 初始化插件本身
        try:
            await plugin.initialize()
            initialized.add(plugin_name)
            self._loaded_plugins.add(plugin_name)
            logger.info(f"插件已初始化: {plugin_name}")

            # 發布插件已加載事件
            class PluginLoadedEvent(Event):
                def __init__(self, plugin_name: str) -> None:
                    super().__init__("plugin_manager")
                    self.plugin_name = plugin_name

            await self._event_manager.publish(PluginLoadedEvent(plugin_name))

        except Exception as e:
            logger.error(f"初始化插件 {plugin_name} 失敗: {e}")
            raise

    async def initialize_plugins(self) -> None:
        """初始化所有已加載的插件。

        遵循依賴順序初始化。
        """
        initialized: Set[str] = set()

        # 按照依賴順序初始化所有插件
        for plugin_name in list(self._plugins.keys()):
            try:
                await self._initialize_plugin(plugin_name, initialized)
            except Exception as e:
                logger.error(f"初始化插件失敗: {e}")

    async def unload_plugin(self, plugin_name: str) -> None:
        """卸載一個插件。

        Args:
            plugin_name: 插件名稱
        """
        if plugin_name not in self._plugins:
            logger.warning(f"插件不存在: {plugin_name}")
            return

        plugin = self._plugins[plugin_name]

        # 檢查是否有其他插件依賴這個插件
        dependent_plugins = []
        for name, p in self._plugins.items():
            if plugin_name in p.dependencies:
                dependent_plugins.append(name)

        if dependent_plugins:
            logger.warning(f"無法卸載插件 {plugin_name}，因為它被以下插件依賴: {', '.join(dependent_plugins)}")
            return

        # 清理插件資源
        try:
            await plugin.cleanup()

            # 從加載的插件集合中移除
            if plugin_name in self._loaded_plugins:
                self._loaded_plugins.remove(plugin_name)

            # 從插件字典中移除
            del self._plugins[plugin_name]
            logger.info(f"插件已卸載: {plugin_name}")

            # 發布插件已卸載事件
            class PluginUnloadedEvent(Event):
                def __init__(self, plugin_name: str) -> None:
                    super().__init__("plugin_manager")
                    self.plugin_name = plugin_name

            await self._event_manager.publish(PluginUnloadedEvent(plugin_name))

        except Exception as e:
            logger.error(f"卸載插件 {plugin_name} 失敗: {e}")

    async def shutdown(self) -> None:
        """關閉所有插件。

        按照依賴順序的反向順序關閉。
        """
        # 創建插件依賴圖
        dep_graph: Dict[str, List[str]] = {}
        for name, plugin in self._plugins.items():
            dep_graph[name] = plugin.dependencies

        # 計算關閉順序
        shutdown_order: List[str] = []
        visited: Set[str] = set()

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in dep_graph.get(node, []):
                visit(dep)
            shutdown_order.append(node)

        for plugin_name in self._plugins:
            visit(plugin_name)

        # 按照計算的順序關閉插件
        for plugin_name in reversed(shutdown_order):
            if plugin_name in self._plugins:
                await self.unload_plugin(plugin_name)

    def get_plugin(self, name: str) -> Optional[LauncherPlugin]:
        """獲取一個已加載的插件。

        Args:
            name: 插件名稱

        Returns:
            插件實例，如果找不到則返回 None
        """
        return self._plugins.get(name)

    @property
    def loaded_plugins(self) -> List[str]:
        """獲取所有已加載的插件名稱。

        Returns:
            插件名稱列表
        """
        return list(self._loaded_plugins)

    async def publish_event(self, event: Event) -> None:
        """發布一個事件。

        Args:
            event: 要發布的事件
        """
        await self._event_manager.publish(event)
