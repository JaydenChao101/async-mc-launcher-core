# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""定義啟動器核心中的標準事件類型。

這些事件在啟動器核心的關鍵操作中發布，例如：
- 版本管理
- 遊戲啟動
- 配置文件變更
- 登錄狀態變更
"""

from typing import Dict, List, Any, Optional, Union
import os

from .events import Event
from .._types import VanillaLauncherProfile, MinecraftOptions


# 版本相關事件
class VersionEvent(Event):
    """與 Minecraft 版本相關的事件基類。"""
    def __init__(self, version: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.version = version


class VersionInstallStartEvent(VersionEvent):
    """版本安裝開始事件。"""
    def __init__(self, version: str, minecraft_directory: str, source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.minecraft_directory = minecraft_directory


class VersionInstallProgressEvent(VersionEvent):
    """版本安裝進度事件。"""
    def __init__(self, version: str, progress: float, message: str, source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.progress = progress  # 0.0 到 1.0
        self.message = message


class VersionInstallCompleteEvent(VersionEvent):
    """版本安裝完成事件。"""
    def __init__(self, version: str, minecraft_directory: str, success: bool, source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.minecraft_directory = minecraft_directory
        self.success = success


# 遊戲啟動事件
class GameLaunchEvent(Event):
    """與遊戲啟動相關的事件基類。"""
    def __init__(self, version: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.version = version


class PreLaunchEvent(GameLaunchEvent):
    """遊戲啟動前事件。"""
    def __init__(self, version: str, options: MinecraftOptions, source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.options = options


class PostLaunchEvent(GameLaunchEvent):
    """遊戲啟動後事件。"""
    def __init__(self, version: str, process_id: int, command: List[str], source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.process_id = process_id
        self.command = command


class GameExitEvent(GameLaunchEvent):
    """遊戲退出事件。"""
    def __init__(self, version: str, exit_code: int, source: Optional[str] = None) -> None:
        super().__init__(version, source)
        self.exit_code = exit_code


# 配置文件事件
class ProfileEvent(Event):
    """與啟動器配置文件相關的事件基類。"""
    def __init__(self, minecraft_directory: Union[str, os.PathLike], source: Optional[str] = None) -> None:
        super().__init__(source)
        self.minecraft_directory = minecraft_directory


class ProfilesLoadedEvent(ProfileEvent):
    """配置文件加載完成事件。"""
    def __init__(self, minecraft_directory: Union[str, os.PathLike], profiles: List[VanillaLauncherProfile], source: Optional[str] = None) -> None:
        super().__init__(minecraft_directory, source)
        self.profiles = profiles


class ProfileAddedEvent(ProfileEvent):
    """添加新配置文件事件。"""
    def __init__(self, minecraft_directory: Union[str, os.PathLike], profile: VanillaLauncherProfile, source: Optional[str] = None) -> None:
        super().__init__(minecraft_directory, source)
        self.profile = profile


class ProfileModifiedEvent(ProfileEvent):
    """配置文件修改事件。"""
    def __init__(self, minecraft_directory: Union[str, os.PathLike], profile: VanillaLauncherProfile, source: Optional[str] = None) -> None:
        super().__init__(minecraft_directory, source)
        self.profile = profile


# 登錄相關事件
class LoginEvent(Event):
    """與登錄相關的事件基類。"""
    pass


class LoginStartEvent(LoginEvent):
    """登錄開始事件。"""
    def __init__(self, login_type: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.login_type = login_type  # 例如 "microsoft", "mojang", "offline"


class LoginSuccessEvent(LoginEvent):
    """登錄成功事件。"""
    def __init__(self, username: str, uuid: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.username = username
        self.uuid = uuid


class LoginFailureEvent(LoginEvent):
    """登錄失敗事件。"""
    def __init__(self, reason: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.reason = reason


class LogoutEvent(LoginEvent):
    """登出事件。"""
    def __init__(self, username: str, source: Optional[str] = None) -> None:
        super().__init__(source)
        self.username = username
