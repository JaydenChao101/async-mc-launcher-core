# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

"""定義啟動器核心中的標準掛鉤點。

這些掛鉤點允許插件擴展核心功能的關鍵部分，例如：
- 版本安裝過程
- 命令生成
- 配置文件處理
- 遊戲啟動過程
"""

from typing import Dict, List, Any, Union, Optional
import os

from .base import hook
from .._types import VanillaLauncherProfile, MinecraftOptions


# 版本安裝掛鉤點
@hook("pre_version_install")
async def pre_version_install(version: str, minecraft_directory: str) -> Dict[str, Any]:
    """在版本安裝開始前調用。

    Args:
        version: 要安裝的版本
        minecraft_directory: Minecraft 目錄

    Returns:
        包含額外安裝選項的字典
    """
    return {"allow_install": True}


@hook("post_version_install")
async def post_version_install(version: str, minecraft_directory: str, install_result: Dict[str, Any]) -> None:
    """在版本安裝完成後調用。

    Args:
        version: 已安裝的版本
        minecraft_directory: Minecraft 目錄
        install_result: 安裝結果信息
    """
    pass


# 命令生成掛鉤點
@hook("pre_command_generation")
async def pre_command_generation(version: str, options: MinecraftOptions) -> MinecraftOptions:
    """在生成 Minecraft 命令之前調用。

    Args:
        version: Minecraft 版本
        options: 原始選項字典

    Returns:
        可能被修改的選項字典
    """
    return options


@hook("post_command_generation")
async def post_command_generation(version: str, options: MinecraftOptions, command: List[str]) -> List[str]:
    """在生成 Minecraft 命令之後調用。

    Args:
        version: Minecraft 版本
        options: 使用的選項字典
        command: 生成的命令列表

    Returns:
        可能被修改的命令列表
    """
    return command


# 配置文件處理掛鉤點
@hook("pre_profile_load")
async def pre_profile_load(minecraft_directory: Union[str, os.PathLike]) -> Dict[str, Any]:
    """在加載 launcher_profiles.json 之前調用。

    Args:
        minecraft_directory: Minecraft 目錄

    Returns:
        包含選項的字典
    """
    return {"allow_load": True}


@hook("post_profile_load")
async def post_profile_load(
    minecraft_directory: Union[str, os.PathLike],
    profiles: List[VanillaLauncherProfile]
) -> List[VanillaLauncherProfile]:
    """在加載 launcher_profiles.json 之後調用。

    Args:
        minecraft_directory: Minecraft 目錄
        profiles: 加載的配置文件列表

    Returns:
        可能被修改的配置文件列表
    """
    return profiles


@hook("pre_profile_save")
async def pre_profile_save(
    minecraft_directory: Union[str, os.PathLike],
    vanilla_profile: VanillaLauncherProfile
) -> VanillaLauncherProfile:
    """在保存配置文件之前調用。

    Args:
        minecraft_directory: Minecraft 目錄
        vanilla_profile: 要保存的配置文件

    Returns:
        可能被修改的配置文件
    """
    return vanilla_profile


# 遊戲啟動掛鉤點
@hook("pre_game_launch")
async def pre_game_launch(minecraft_directory: str, version: str, options: MinecraftOptions) -> bool:
    """在遊戲啟動之前調用。

    Args:
        minecraft_directory: Minecraft 目錄
        version: Minecraft 版本
        options: 啟動選項

    Returns:
        如果允許啟動返回 True，否則返回 False
    """
    return True


@hook("post_game_launch")
async def post_game_launch(minecraft_directory: str, version: str, process_id: int) -> None:
    """在遊戲啟動之後調用。

    Args:
        minecraft_directory: Minecraft 目錄
        version: Minecraft 版本
        process_id: 遊戲進程 ID
    """
    pass
