"""
This module handles loading and saving TOML config files with Pydantic Settings support.
Enhanced with automatic environment variable support and type validation.
"""

# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2019-2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause

# 標準庫導入
import os
from pathlib import Path
from typing import Optional, Union

# 兼容 Python 3.10 的 tomllib 導入
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.10 fallback

from tomli_w import dumps
import aiofiles
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from ..models import MinecraftOptions


class LauncherConfig(BaseSettings):
    """
    Minecraft Launcher 配置模型
    自動處理環境變量和 TOML 文件加載
    """

    model_config = SettingsConfigDict(
        # 環境變量前綴
        env_prefix="MC_LAUNCHER_",
        # 支持嵌套環境變量，例如 MC_LAUNCHER_JAVA__HOME
        env_nested_delimiter="__",
        # 不區分大小寫
        case_sensitive=False,
        # 允許額外字段
        extra="allow",
        # 從 TOML 文件加載
        toml_file="config.toml",
        # 環境變量優先級高於文件
        env_file_encoding="utf-8",
    )

    # 基本啟動器設置
    launcher_name: str = Field(default="AsyncMCLauncher", description="啟動器名稱")
    launcher_version: str = Field(default="1.0.0", description="啟動器版本")

    # Minecraft 遊戲選項 - 使用現有的 Pydantic 模型
    minecraft_options: Optional[MinecraftOptions] = Field(
        default=None, description="Minecraft 遊戲選項"
    )

    # 額外的啟動器特定配置
    config_directory: Optional[str] = Field(default=None, description="配置目錄")
    cache_directory: Optional[str] = Field(default=None, description="緩存目錄")

    # 認證相關配置
    auto_refresh_token: bool = Field(default=True, description="自動刷新令牌")
    remember_Credential: bool = Field(default=True, description="記住登入憑證")

    # 下載和安裝配置
    concurrent_downloads: int = Field(
        default=4, description="並發下載數量", ge=1, le=16
    )
    download_timeout: int = Field(default=300, description="下載超時時間（秒）", ge=30)
    verify_downloads: bool = Field(default=True, description="驗證下載文件")

    # 日誌配置
    log_level: str = Field(default="INFO", description="日誌級別")
    log_file: Optional[str] = Field(default=None, description="日誌文件路徑")

    # 代理配置
    proxy_host: Optional[str] = Field(default=None, description="代理主機")
    proxy_port: Optional[int] = Field(default=None, description="代理端口")
    proxy_username: Optional[str] = Field(default=None, description="代理用戶名")
    proxy_password: Optional[str] = Field(default=None, description="代理密碼")

    # Java 設置
    java_executable: Optional[str] = Field(
        default=None, description="Java 可執行文件路徑"
    )
    jvm_arguments: list[str] = Field(default_factory=list, description="JVM 參數")

    # 帳戶設置
    username: Optional[str] = Field(default=None, description="用戶名")
    uuid: Optional[str] = Field(default=None, description="用戶 UUID")
    access_token: Optional[str] = Field(default=None, description="訪問令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")

    # 遊戲設置
    version: Optional[str] = Field(default=None, description="Minecraft 版本")
    demo_mode: bool = Field(default=False, description="演示模式")
    custom_resolution: bool = Field(default=False, description="自定義解析度")
    resolution_width: Optional[int] = Field(default=None, description="解析度寬度")
    resolution_height: Optional[int] = Field(default=None, description="解析度高度")

    # 網路設置
    server_address: Optional[str] = Field(default=None, description="伺服器地址")
    server_port: Optional[int] = Field(default=None, description="伺服器端口")

    # 高級設置
    enable_logging_config: bool = Field(default=True, description="啟用日誌配置")
    disable_multiplayer: bool = Field(default=False, description="禁用多人遊戲")
    disable_chat: bool = Field(default=False, description="禁用聊天")

    # 快速遊戲設置
    quick_play_path: Optional[str] = Field(default=None, description="快速遊戲路徑")
    quick_play_singleplayer: Optional[str] = Field(
        default=None, description="快速單人遊戲"
    )
    quick_play_multiplayer: Optional[str] = Field(
        default=None, description="快速多人遊戲"
    )
    quick_play_realms: Optional[str] = Field(
        default=None, description="快速 Realms 遊戲"
    )


class ConfigManager:
    """配置管理器，提供加載和保存配置的功能"""

    def __init__(self, config_path: Union[str, os.PathLike] = "config.toml"):
        self.config_path = Path(config_path)
        self._config: Optional[LauncherConfig] = None

    async def load_config(self, reload: bool = False) -> LauncherConfig:
        """
        加載配置

        Args:
            reload: 是否重新加載配置

        Returns:
            LauncherConfig: 配置對象
        """
        if self._config is None or reload:
            if self.config_path.exists():
                # 從 TOML 文件加載
                async with aiofiles.open(
                    self.config_path, mode="r", encoding="utf-8"
                ) as f:
                    toml_content = await f.read()
                    toml_data = tomllib.loads(toml_content)

                # 使用 Pydantic Settings 加載配置
                # 環境變量會自動覆蓋文件中的值
                self._config = LauncherConfig(**toml_data)
            else:
                # 如果文件不存在，只從環境變量加載
                self._config = LauncherConfig()

        return self._config

    async def save_config(self, config: Optional[LauncherConfig] = None) -> None:
        """
        保存配置到 TOML 文件

        Args:
            config: 要保存的配置對象，如果為 None 則保存當前加載的配置
        """
        if config is None:
            if self._config is None:
                raise ValueError("沒有配置可以保存，請先加載配置或提供配置對象")
            config = self._config

        # 轉換為字典並移除 None 值
        config_dict = config.model_dump(exclude_none=True, by_alias=True)

        # 生成 TOML 字符串
        toml_str = dumps(config_dict)

        # 確保目錄存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # 寫入文件
        async with aiofiles.open(self.config_path, mode="w", encoding="utf-8") as f:
            await f.write(toml_str)

    async def update_config(self, **kwargs) -> LauncherConfig:
        """
        更新配置

        Args:
            **kwargs: 要更新的配置項

        Returns:
            LauncherConfig: 更新後的配置對象
        """
        config = await self.load_config()

        # 更新配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # 保存配置
        await self.save_config(config)

        return config

    def get_config(self) -> Optional[LauncherConfig]:
        """獲取當前加載的配置（同步方法）"""
        return self._config


# 便利函數
async def create_default_config(
    config_path: Union[str, os.PathLike] = "config.toml",
) -> LauncherConfig:
    """
    創建默認配置文件

    Args:
        config_path: 配置文件路徑

    Returns:
        LauncherConfig: 默認配置對象
    """
    manager = ConfigManager(config_path)
    config = LauncherConfig()
    await manager.save_config(config)
    return config


def get_config_from_env() -> LauncherConfig:
    """
    僅從環境變量加載配置（同步方法）

    Returns:
        LauncherConfig: 配置對象
    """
    return LauncherConfig()


# 使用示例
async def example_usage():
    """配置管理使用示例"""

    # 創建配置管理器
    manager = ConfigManager("my_config.toml")

    # 加載配置（自動從文件和環境變量加載）
    config = await manager.load_config()

    # 更新配置
    config = await manager.update_config(
        username="player123",
        version="1.20.1",
        resolution_width=1920,
        resolution_height=1080,
    )

    # 保存配置
    await manager.save_config()

    print(f"用戶名: {config.username}")
    print(f"版本: {config.version}")
    print(f"解析度: {config.resolution_width}x{config.resolution_height}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
