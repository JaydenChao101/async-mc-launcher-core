# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""定義插件系統的基礎類型和裝飾器。

此模組包含：
- LauncherPlugin 抽象基類，所有插件必須繼承
- hook 裝飾器，用於標記插件掛鉤點
"""

import abc
import inspect
import functools
from typing import Dict, Callable, Any, Optional, TypeVar, List, Set, Union, cast

# 掛鉤註冊表
_HOOKS: Dict[str, List[Callable]] = {}

T = TypeVar('T')
HookFunction = Callable[..., Any]


def hook(name: str) -> Callable[[HookFunction], HookFunction]:
    """定義一個可以被插件擴展的掛鉤點。

    Args:
        name: 掛鉤點的名稱，插件將使用此名稱註冊處理函數

    Returns:
        裝飾器函數
    """
    def decorator(func: HookFunction) -> HookFunction:
        # 初始化掛鉤點列表
        if name not in _HOOKS:
            _HOOKS[name] = []

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 首先執行原始函數
            result = await func(*args, **kwargs)

            # 然後執行所有註冊的掛鉤處理程序
            for handler in _HOOKS[name]:
                is_async = inspect.iscoroutinefunction(handler)
                if is_async:
                    await handler(*args, result=result, **kwargs)
                else:
                    handler(*args, result=result, **kwargs)

            return result

        # 存儲原始函數以便在需要時可以訪問
        wrapper.__original__ = func  # type: ignore
        return cast(HookFunction, wrapper)

    return decorator


def register_hook(name: str, handler: Callable) -> None:
    """註冊一個掛鉤處理函數。

    Args:
        name: 掛鉤點名稱
        handler: 處理函數
    """
    if name not in _HOOKS:
        _HOOKS[name] = []

    if handler not in _HOOKS[name]:
        _HOOKS[name].append(handler)


def unregister_hook(name: str, handler: Callable) -> None:
    """取消註冊一個掛鉤處理函數。

    Args:
        name: 掛鉤點名稱
        handler: 處理函數
    """
    if name in _HOOKS and handler in _HOOKS[name]:
        _HOOKS[name].remove(handler)


class LauncherPlugin(abc.ABC):
    """所有啟動器插件必須繼承的基類。

    提供插件標準界面，包括生命週期管理、元數據等。
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """插件名稱。"""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """插件版本。"""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """插件描述。"""
        pass

    @property
    def author(self) -> str:
        """插件作者，可選。"""
        return "匿名"

    @property
    def dependencies(self) -> List[str]:
        """插件依賴的其他插件列表。"""
        return []

    @property
    def hooks(self) -> Dict[str, List[Callable]]:
        """此插件實現的掛鉤點處理函數。

        格式: {"hook_name": [handler1, handler2, ...], ...}
        """
        hooks_dict: Dict[str, List[Callable]] = {}

        # 自動搜索類中以 'on_' 開頭的方法作為掛鉤處理函數
        for attr_name in dir(self):
            if attr_name.startswith('on_'):
                hook_name = attr_name[3:]  # 去掉 'on_' 前綴
                method = getattr(self, attr_name)
                if callable(method):
                    if hook_name not in hooks_dict:
                        hooks_dict[hook_name] = []
                    hooks_dict[hook_name].append(method)

        return hooks_dict

    async def initialize(self) -> None:
        """初始化插件，由插件管理器調用。

        註冊所有掛鉤處理函數。
        """
        for hook_name, handlers in self.hooks.items():
            for handler in handlers:
                register_hook(hook_name, handler)

    async def cleanup(self) -> None:
        """清理插件資源，由插件管理器調用。

        取消註冊所有掛鉤處理函數。
        """
        for hook_name, handlers in self.hooks.items():
            for handler in handlers:
                unregister_hook(hook_name, handler)
