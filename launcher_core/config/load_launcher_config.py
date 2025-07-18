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
from typing import Optional, Union, List, Dict, Any
import datetime

# 兼容 Python 3.10 的 tomllib 導入
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.10 fallback

from tomli_w import dumps
import aiofiles
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from ..models import MinecraftOptions, Credential, LauncherSettings, ServerInfo, ModInfo


class CredentialConfig(BaseModel):
    """
    單個帳戶憑證配置
    對應 TOML 中的 [[Credentials]] 陣列項目
    """
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    username: str = Field(..., description="用戶名")
    uuid: str = Field(..., description="用戶 UUID")
    access_token: str = Field(..., description="訪問令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    account_type: str = Field(default="microsoft", description="帳戶類型")
    is_default: bool = Field(default=False, description="是否為預設帳戶")
    last_used: Optional[datetime.datetime] = Field(None, description="最後使用時間")
    display_name: Optional[str] = Field(None, description="顯示名稱")
    skin_url: Optional[str] = Field(None, description="皮膚 URL")
    cape_url: Optional[str] = Field(None, description="斗篷 URL")


class LauncherSettingConfig(BaseModel):
    """
    啟動器設定配置
    對應 TOML 中的 [LauncherSetting] 區塊
    """
    model_config = ConfigDict(extra="allow", validate_assignment=True)

    # 基本設定
    launcher_name: str = Field(default="AsyncMCLauncher", description="啟動器名稱")
    launcher_version: str = Field(default="1.0.0", description="啟動器版本")
    launcher_uuid: Optional[str] = Field(None, description="啟動器 UUID")

    # 目錄設定
    minecraft_directory: Optional[str] = Field(None, description="Minecraft 目錄")
    config_directory: Optional[str] = Field(None, description="配置目錄")
    cache_directory: Optional[str] = Field(None, description="緩存目錄")
    logs_directory: Optional[str] = Field(None, description="日誌目錄")

    # 帳戶設定
    auto_login: bool = Field(default=True, description="自動登入")
    remember_credentials: bool = Field(default=True, description="記住憑證")
    auto_refresh_token: bool = Field(default=True, description="自動刷新令牌")

    # 下載設定
    max_concurrent_downloads: int = Field(default=4, ge=1, le=16, description="最大並發下載數")
    download_timeout: int = Field(default=300, ge=30, description="下載超時時間（秒）")
    verify_checksums: bool = Field(default=True, description="驗證校驗和")
    verify_signatures: bool = Field(default=False, description="驗證簽名")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="重試次數")

    # 代理設定
    use_proxy: bool = Field(default=False, description="使用代理")
    proxy_host: Optional[str] = Field(None, description="代理主機")
    proxy_port: Optional[int] = Field(None, ge=1, le=65535, description="代理端口")
    proxy_username: Optional[str] = Field(None, description="代理用戶名")
    proxy_password: Optional[str] = Field(None, description="代理密碼")

    # 鏡像設定
    use_mirror: bool = Field(default=False, description="使用鏡像")
    mirror_url: Optional[str] = Field(None, description="鏡像 URL")

    # Java 設定
    java_executable: Optional[str] = Field(None, description="Java 可執行文件路徑")
    jvm_arguments: List[str] = Field(default_factory=list, description="JVM 參數")

    # 遊戲設定
    default_version: Optional[str] = Field(None, description="預設 Minecraft 版本")
    demo_mode: bool = Field(default=False, description="演示模式")
    custom_resolution: bool = Field(default=False, description="自定義解析度")
    resolution_width: Optional[int] = Field(None, description="解析度寬度")
    resolution_height: Optional[int] = Field(None, description="解析度高度")

    # UI 設定
    window_width: int = Field(default=1200, ge=800, description="窗口寬度")
    window_height: int = Field(default=800, ge=600, description="窗口高度")
    window_maximized: bool = Field(default=False, description="窗口最大化")
    window_position_x: Optional[int] = Field(None, description="窗口 X 位置")
    window_position_y: Optional[int] = Field(None, description="窗口 Y 位置")
    theme: str = Field(default="auto", description="主題")
    accent_color: str = Field(default="#0078d4", description="主題色")
    font_family: str = Field(default="System", description="字體")
    font_size: int = Field(default=12, ge=8, le=24, description="字體大小")
    language: str = Field(default="zh-TW", description="語言")

    # 功能設定
    show_news: bool = Field(default=True, description="顯示新聞")
    show_release_notes: bool = Field(default=True, description="顯示版本說明")
    show_advanced_options: bool = Field(default=False, description="顯示進階選項")
    auto_close_launcher: bool = Field(default=False, description="自動關閉啟動器")
    enable_logging: bool = Field(default=True, description="啟用日誌")
    log_level: str = Field(default="INFO", description="日誌級別")

    @field_validator("minecraft_directory", "config_directory", "cache_directory", "logs_directory", mode="before")
    @classmethod
    def validate_directories(cls, v):
        """驗證目錄路徑"""
        if v is not None:
            return str(Path(v).expanduser().resolve())
        return v


class GameProfileConfig(BaseModel):
    """
    遊戲設定檔配置
    對應 TOML 中的 [[GameProfiles]] 陣列項目
    """
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    profile_id: str = Field(..., description="設定檔 ID")
    profile_name: str = Field(..., description="設定檔名稱")
    minecraft_version: str = Field(..., description="Minecraft 版本")

    # 載入器設定
    loader_type: Optional[str] = Field(None, description="載入器類型 (forge, fabric, quilt, neoforge)")
    loader_version: Optional[str] = Field(None, description="載入器版本")

    # 時間資訊
    created_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="創建時間")
    last_used: Optional[datetime.datetime] = Field(None, description="最後使用時間")

    # Java 設定
    java_executable: Optional[str] = Field(None, description="Java 可執行文件")
    jvm_arguments: List[str] = Field(default_factory=list, description="JVM 參數")

    # 遊戲參數
    game_arguments: List[str] = Field(default_factory=list, description="遊戲參數")

    # 模組設定
    enabled_mods: List[str] = Field(default_factory=list, description="啟用的模組")
    disabled_mods: List[str] = Field(default_factory=list, description="禁用的模組")

    # 資源包設定
    enabled_resource_packs: List[str] = Field(default_factory=list, description="啟用的資源包")

    # 其他設定
    icon_path: Optional[str] = Field(None, description="圖標路徑")
    description: Optional[str] = Field(None, description="描述")
    is_default: bool = Field(default=False, description="是否為預設設定檔")


class ServerConfig(BaseModel):
    """
    伺服器配置
    對應 TOML 中的 [[Servers]] 陣列項目
    """
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="伺服器名稱")
    address: str = Field(..., description="伺服器地址")
    port: int = Field(default=25565, ge=1, le=65535, description="伺服器端口")
    icon: Optional[str] = Field(None, description="伺服器圖標")
    description: Optional[str] = Field(None, description="伺服器描述")
    version: Optional[str] = Field(None, description="伺服器版本")
    is_favorite: bool = Field(default=False, description="是否收藏")
    last_ping: Optional[datetime.datetime] = Field(None, description="最後 Ping 時間")
    last_players: Optional[int] = Field(None, description="最後玩家數")
    max_players: Optional[int] = Field(None, description="最大玩家數")


class CompleteLauncherConfig(BaseModel):
    """
    完整的啟動器配置
    對應整個 TOML 檔案結構
    """
    model_config = ConfigDict(extra="allow", validate_assignment=True)

    # 多帳戶憑證 - 對應 [[Credentials]]
    Credentials: List[CredentialConfig] = Field(default_factory=list, description="帳戶憑證列表")

    # 啟動器設定 - 對應 [LauncherSetting]
    LauncherSetting: LauncherSettingConfig = Field(default_factory=LauncherSettingConfig, description="啟動器設定")

    # 遊戲設定檔 - 對應 [[GameProfiles]]
    GameProfiles: List[GameProfileConfig] = Field(default_factory=list, description="遊戲設定檔列表")

    # 伺服器列表 - 對應 [[Servers]]
    Servers: List[ServerConfig] = Field(default_factory=list, description="伺服器列表")

    # 其他設定 - 對應 [Other] - 給調用這個 lib 的程式使用
    Other: Dict[str, Any] = Field(default_factory=dict, description="其他自定義設定")

    # 配置元數據
    config_version: str = Field(default="2.0.0", description="配置版本")
    last_modified: datetime.datetime = Field(default_factory=datetime.datetime.now, description="最後修改時間")

    def get_default_credential(self) -> Optional[CredentialConfig]:
        """獲取預設帳戶憑證"""
        for credential in self.Credentials:
            if credential.is_default:
                return credential
        return self.Credentials[0] if self.Credentials else None

    def get_default_profile(self) -> Optional[GameProfileConfig]:
        """獲取預設遊戲設定檔"""
        for profile in self.GameProfiles:
            if profile.is_default:
                return profile
        return self.GameProfiles[0] if self.GameProfiles else None

    def add_credential(self, credential: CredentialConfig, set_as_default: bool = False) -> None:
        """添加帳戶憑證"""
        if set_as_default:
            # 清除其他預設設定
            for cred in self.Credentials:
                cred.is_default = False
            credential.is_default = True

        # 檢查是否已存在相同 UUID 的帳戶
        for i, existing in enumerate(self.Credentials):
            if existing.uuid == credential.uuid:
                self.Credentials[i] = credential
                return

        self.Credentials.append(credential)
        self.last_modified = datetime.datetime.now()

    def remove_credential(self, uuid: str) -> bool:
        """移除帳戶憑證"""
        for i, credential in enumerate(self.Credentials):
            if credential.uuid == uuid:
                was_default = credential.is_default
                del self.Credentials[i]

                # 如果刪除的是預設帳戶，設定第一個為預設
                if was_default and self.Credentials:
                    self.Credentials[0].is_default = True

                self.last_modified = datetime.datetime.now()
                return True
        return False

    def add_profile(self, profile: GameProfileConfig, set_as_default: bool = False) -> None:
        """添加遊戲設定檔"""
        if set_as_default:
            # 清除其他預設設定
            for prof in self.GameProfiles:
                prof.is_default = False
            profile.is_default = True

        # 檢查是否已存在相同 ID 的設定檔
        for i, existing in enumerate(self.GameProfiles):
            if existing.profile_id == profile.profile_id:
                self.GameProfiles[i] = profile
                return

        self.GameProfiles.append(profile)
        self.last_modified = datetime.datetime.now()

    def remove_profile(self, profile_id: str) -> bool:
        """移除遊戲設定檔"""
        for i, profile in enumerate(self.GameProfiles):
            if profile.profile_id == profile_id:
                was_default = profile.is_default
                del self.GameProfiles[i]

                # 如果刪除的是預設設定檔，設定第一個為預設
                if was_default and self.GameProfiles:
                    self.GameProfiles[0].is_default = True

                self.last_modified = datetime.datetime.now()
                return True
        return False

    def add_server(self, server: ServerConfig) -> None:
        """添加伺服器"""
        # 檢查是否已存在相同地址和端口的伺服器
        for i, existing in enumerate(self.Servers):
            if existing.address == server.address and existing.port == server.port:
                self.Servers[i] = server
                return

        self.Servers.append(server)
        self.last_modified = datetime.datetime.now()

    def remove_server(self, address: str, port: int = 25565) -> bool:
        """移除伺服器"""
        for i, server in enumerate(self.Servers):
            if server.address == address and server.port == port:
                del self.Servers[i]
                self.last_modified = datetime.datetime.now()
                return True
        return False


class ConfigManager:
    """配置管理器，提供加載和保存配置的功能"""

    def __init__(self, config_path: Union[str, os.PathLike] = "config.toml"):
        self.config_path = Path(config_path)
        self._config: Optional[CompleteLauncherConfig] = None

    async def load_config(self, reload: bool = False) -> CompleteLauncherConfig:
        """
        加載配置

        Args:
            reload: 是否重新加載配置

        Returns:
            CompleteLauncherConfig: 配置對象
        """
        if self._config is None or reload:
            if self.config_path.exists():
                # 從 TOML 文件加載
                async with aiofiles.open(
                    self.config_path, mode="r", encoding="utf-8"
                ) as f:
                    toml_content = await f.read()
                    toml_data = tomllib.loads(toml_content)

                self._config = CompleteLauncherConfig(**toml_data)
            else:
                # 如果文件不存在，創建預設配置
                self._config = CompleteLauncherConfig()

        return self._config

    async def save_config(self, config: Optional[CompleteLauncherConfig] = None) -> None:
        """
        保存配置到 TOML 文件

        Args:
            config: 要保存的配置對象，如果為 None 則保存當前加載的配置
        """
        if config is None:
            if self._config is None:
                raise ValueError("沒有配置可以保存，請先加載配置或提供配置對象")
            config = self._config

        # 更新最後修改時間
        config.last_modified = datetime.datetime.now()

        # 轉換為字典
        config_dict = config.model_dump(exclude_none=True, by_alias=True)

        # 生成 TOML 字符串
        toml_str = dumps(config_dict)

        # 確保目錄存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # 寫入文件
        async with aiofiles.open(self.config_path, mode="w", encoding="utf-8") as f:
            await f.write(toml_str)

    async def update_launcher_setting(self, **kwargs) -> CompleteLauncherConfig:
        """
        更新啟動器設定

        Args:
            **kwargs: 要更新的設定項

        Returns:
            CompleteLauncherConfig: 更新後的配置對象
        """
        config = await self.load_config()

        # 更新啟動器設定
        for key, value in kwargs.items():
            if hasattr(config.LauncherSetting, key):
                setattr(config.LauncherSetting, key, value)

        # 保存配置
        await self.save_config(config)

        return config

    async def add_credential(self, credential: CredentialConfig, set_as_default: bool = False) -> CompleteLauncherConfig:
        """添加帳戶憑證"""
        config = await self.load_config()
        config.add_credential(credential, set_as_default)
        await self.save_config(config)
        return config

    async def add_profile(self, profile: GameProfileConfig, set_as_default: bool = False) -> CompleteLauncherConfig:
        """添加遊戲設定檔"""
        config = await self.load_config()
        config.add_profile(profile, set_as_default)
        await self.save_config(config)
        return config

    async def add_server(self, server: ServerConfig) -> CompleteLauncherConfig:
        """添加伺服器"""
        config = await self.load_config()
        config.add_server(server)
        await self.save_config(config)
        return config

    def get_config(self) -> Optional[CompleteLauncherConfig]:
        """獲取當前加載的配置（同步方法）"""
        return self._config


# 便利函數
async def create_default_config(
    config_path: Union[str, os.PathLike] = "config.toml",
) -> CompleteLauncherConfig:
    """
    創建默認配置文件

    Args:
        config_path: 配置文件路徑

    Returns:
        CompleteLauncherConfig: 默認配置對象
    """
    manager = ConfigManager(config_path)
    config = CompleteLauncherConfig()
    await manager.save_config(config)
    return config


# 導出所有配置模型
__all__ = [
    "CredentialConfig",
    "LauncherSettingConfig",
    "GameProfileConfig",
    "ServerConfig",
    "CompleteLauncherConfig",
    "ConfigManager",
    "create_default_config",
]
