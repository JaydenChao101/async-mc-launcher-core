# 這是一個示例插件，用於擴展 Minecraft 啟動器的配置文件功能

import os
from typing import List, Dict, Any, Optional

from launcher_core.plugins.base import LauncherPlugin
from launcher_core._types import VanillaLauncherProfile


class CustomProfilePlugin(LauncherPlugin):
    """自定義配置文件插件。

    此插件擴展啟動器配置文件功能，添加特殊的自定義模式配置。
    """

    @property
    def name(self) -> str:
        return "custom_profile_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "添加特殊的自定義配置文件功能"

    @property
    def author(self) -> str:
        return "JaydenChao101"

    async def initialize(self) -> None:
        """初始化插件。"""
        await super().initialize()
        print(f"[{self.name}] 插件已初始化")

    async def on_post_profile_load(self, minecraft_directory: str, profiles: List[VanillaLauncherProfile], result: List[VanillaLauncherProfile]) -> None:
        """在配置文件加載後添加自定義配置。

        Args:
            minecraft_directory: Minecraft 目錄
            profiles: 原始配置文件列表
            result: 當前結果
        """
        # 添加預定義的優化配置文件
        optimization_profile: VanillaLauncherProfile = {
            "name": "優化模式",
            "versionType": "custom",
            "version": "1.20.4",  # 確保這是一個有效的已安裝版本
            "gameDirectory": None,
            "javaExecutable": None,
            "javaArguments": [
                "-Xmx4G",  # 分配 4GB 內存
                "-XX:+UseG1GC",  # 使用 G1 垃圾收集器
                "-XX:+ParallelRefProcEnabled",
                "-XX:MaxGCPauseMillis=200",
                "-XX:+UnlockExperimentalVMOptions",
                "-XX:+DisableExplicitGC",
                "-XX:+AlwaysPreTouch",
                "-XX:G1NewSizePercent=30",
                "-XX:G1MaxNewSizePercent=40",
                "-XX:G1HeapRegionSize=8M",
                "-XX:G1ReservePercent=20",
                "-XX:G1HeapWastePercent=5",
                "-XX:G1MixedGCCountTarget=4",
                "-XX:InitiatingHeapOccupancyPercent=15",
                "-XX:G1MixedGCLiveThresholdPercent=90",
                "-XX:G1RSetUpdatingPauseTimePercent=5",
                "-XX:SurvivorRatio=32",
                "-XX:+PerfDisableSharedMem",
                "-XX:MaxTenuringThreshold=1"
            ],
            "customResolution": {
                "width": 1920,
                "height": 1080
            }
        }

        # 只有在列表中沒有同名配置時才添加
        if not any(p.get("name") == optimization_profile["name"] for p in result):
            result.append(optimization_profile)
            print(f"[{self.name}] 已添加優化模式配置文件")

    async def on_pre_profile_save(self, minecraft_directory: str, vanilla_profile: VanillaLauncherProfile, result: VanillaLauncherProfile) -> None:
        """在配置文件保存前可能修改配置。

        Args:
            minecraft_directory: Minecraft 目錄
            vanilla_profile: 要保存的配置文件
            result: 當前結果
        """
        # 如果是我們的優化配置文件，確保 Java 參數保持最新
        if vanilla_profile.get("name") == "優化模式":
            print(f"[{self.name}] 更新優化模式配置文件的 Java 參數")

            # 假設我們需要根據系統內存調整某些參數
            import psutil
            system_memory_gb = psutil.virtual_memory().total / (1024 ** 3)

            # 動態調整內存分配
            if system_memory_gb > 8:
                # 系統內存大於 8GB，分配 6GB 給 Minecraft
                for i, arg in enumerate(result["javaArguments"]):
                    if arg.startswith("-Xmx"):
                        result["javaArguments"][i] = "-Xmx6G"
                        break
            elif system_memory_gb > 4:
                # 系統內存 4-8GB，分配 3GB 給 Minecraft
                for i, arg in enumerate(result["javaArguments"]):
                    if arg.startswith("-Xmx"):
                        result["javaArguments"][i] = "-Xmx3G"
                        break

    async def cleanup(self) -> None:
        """清理插件資源。"""
        await super().cleanup()
        print(f"[{self.name}] 插件已清理")
