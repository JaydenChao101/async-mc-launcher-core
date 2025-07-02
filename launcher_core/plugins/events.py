# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""事件系統用於插件間通信。

此模組提供：
- Event 基類用於定義事件
- EventManager 用於發布和訂閱事件
"""

import inspect
import asyncio
from typing import Dict, List, Callable, Any, Type, TypeVar, Optional, Set

T = TypeVar('T')
EventHandler = Callable[[Any], None]
AsyncEventHandler = Callable[[Any], asyncio.coroutines]


class Event:
    """所有事件的基類。

    插件可以定義自己的事件類型，繼承此類。
    """

    def __init__(self, source: Optional[str] = None) -> None:
        """初始化事件。

        Args:
            source: 事件源，通常是發布事件的插件名稱
        """
        self.source = source
        self.cancelled = False

    def cancel(self) -> None:
        """取消事件，阻止後續處理。"""
        self.cancelled = True


class EventManager:
    """事件管理器，處理事件的發布和訂閱。"""

    def __init__(self) -> None:
        """初始化事件管理器。"""
        self._handlers: Dict[Type[Event], List[Callable]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable[[Any], Any]) -> None:
        """訂閱一個事件類型。

        Args:
            event_type: 事件類型
            handler: 事件處理函數
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Any], Any]) -> None:
        """取消訂閱一個事件類型。

        Args:
            event_type: 事件類型
            handler: 事件處理函數
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def publish(self, event: Event) -> None:
        """發布一個事件。

        Args:
            event: 要發布的事件實例
        """
        event_type = type(event)

        # 獲取此事件類型的所有處理函數
        handlers = []
        for cls in self._handlers:
            if issubclass(event_type, cls):
                handlers.extend(self._handlers[cls])

        # 調用所有處理函數
        for handler in handlers:
            if event.cancelled:
                break

            is_async = inspect.iscoroutinefunction(handler)
            if is_async:
                await handler(event)
            else:
                handler(event)
