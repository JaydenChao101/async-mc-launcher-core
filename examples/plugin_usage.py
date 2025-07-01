#!/usr/bin/env python3
# 這是一個示例腳本，展示如何使用插件系統

import os
import sys
import asyncio
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from launcher_core.plugins import PluginManager
from launcher_core.plugins.events import Event
from launcher_core.utils import get_minecraft_directory
from launcher_core.logging_utils import logger, setup_logger


class CustomEvent(Event):
    """自定義事件示例。"""
    def __init__(self, message: str) -> None:
        super().__init__("example_script")
        self.message = message


async def main():
    # 設置日誌
    setup_logger(level="INFO", enable_console=True)
    logger.info("啟動插件系統示例")

    # 創建插件管理器
    plugin_manager = PluginManager()

    # 添加插件目錄
    plugin_dir = Path(__file__).parent / "plugins"
    plugin_manager.add_plugin_directory(str(plugin_dir))
    logger.info(f"添加插件目錄: {plugin_dir}")

    # 發現可用插件
    available_plugins = await plugin_manager.discover_plugins()
    logger.info(f"發現 {len(available_plugins)} 個可用插件:")
    for plugin_class in available_plugins:
        logger.info(f"  - {plugin_class.__name__}")

    # 加載所有發現的插件
    for plugin_class in available_plugins:
        try:
            await plugin_manager.load_plugin(plugin_class)
        except Exception as e:
            logger.error(f"加載插件 {plugin_class.__name__} 失敗: {e}")

    # 初始化所有插件
    await plugin_manager.initialize_plugins()
    logger.info(f"已加載插件: {', '.join(plugin_manager.loaded_plugins)}")

    # 使用插件功能 - 加載配置文件
    minecraft_dir = get_minecraft_directory()
    logger.info(f"Minecraft 目錄: {minecraft_dir}")

    # 發布自定義事件
    custom_event = CustomEvent("這是一個測試事件")
    await plugin_manager.publish_event(custom_event)
    logger.info(f"已發布自定義事件: {custom_event.message}")

    # 等待一段時間讓插件處理事件
    await asyncio.sleep(1)

    # 關閉插件系統
    logger.info("正在關閉插件系統...")
    await plugin_manager.shutdown()
    logger.info("插件系統已關閉")


if __name__ == "__main__":
    asyncio.run(main())
