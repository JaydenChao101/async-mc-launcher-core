from . import Credential as AuthCredential
from .exceptions import NeedAccountInfo, AccountNotOwnMinecraft
from .mojang import have_minecraft
from .models import (
    MinecraftOptions,
    Credential,
    LauncherSettings,
    ServerInfo,
    ModInfo,
)
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict
from pathlib import Path
import datetime


class MultipleCredential(BaseModel):
    """
    用於存儲多個帳戶憑證
    """

    AuthCredential: list[AuthCredential]


class AccountManager:
    """
    用於管理帳戶的自定義類別
    一行代碼直接管理帳戶的憑證
    """

    @staticmethod
    async def Checker(Credential: AuthCredential) -> bool:
        """
        檢查帳戶憑證是否有效
        """
        if not Credential.access_token:
            raise NeedAccountInfo("帳戶憑證無效或未提供")

        access_token = Credential.access_token
        try:
            await have_minecraft(access_token)
        except AccountNotOwnMinecraft:
            return False
        return True

    @staticmethod
    async def MultipleChecker(MultipleCredential: MultipleCredential) -> bool:
        """
        檢查多個帳戶憑證是否有效
        """
        if not MultipleCredential.AuthCredential:
            raise NeedAccountInfo("沒有提供任何帳戶憑證")

        for credential in MultipleCredential.AuthCredential:
            if not await AccountManager.Checker(credential):
                return False
        return True


class LauncherConfigModel(BaseModel):
    """
    啟動器配置模型
    包含所有啟動器相關的配置選項
    """

    model_config = ConfigDict(
        extra="allow", validate_assignment=True, str_strip_whitespace=True
    )

    # 基本配置
    launcher_name: str = Field(default="AsyncMCLauncher", description="啟動器名稱")
    launcher_version: str = Field(default="1.0.0", description="啟動器版本")
    launcher_uuid: Optional[str] = Field(default=None, description="啟動器唯一標識")

    # 目錄配置
    minecraft_directory: Optional[str] = Field(
        default=None, description="Minecraft 安裝目錄"
    )
    config_directory: Optional[str] = Field(default=None, description="配置文件目錄")
    cache_directory: Optional[str] = Field(default=None, description="緩存目錄")
    logs_directory: Optional[str] = Field(default=None, description="日誌目錄")

    # 帳戶配置
    current_account: Optional[Credential] = Field(
        default=None, description="當前使用的帳戶"
    )
    saved_accounts: List[Credential] = Field(
        default_factory=list, description="已保存的帳戶列表"
    )
    auto_login: bool = Field(default=True, description="自動登入")
    remember_account: bool = Field(default=True, description="記住帳戶")

    # 啟動器設定
    launcher_settings: LauncherSettings = Field(
        default_factory=LauncherSettings, description="啟動器設定"
    )

    # 遊戲配置
    default_minecraft_options: MinecraftOptions = Field(
        default_factory=MinecraftOptions, description="默認 Minecraft 選項"
    )

    # 伺服器配置
    saved_servers: List[ServerInfo] = Field(
        default_factory=list, description="已保存的伺服器列表"
    )

    # 模組配置
    installed_mods: List[ModInfo] = Field(
        default_factory=list, description="已安裝的模組列表"
    )

    @validator(
        "minecraft_directory",
        "config_directory",
        "cache_directory",
        "logs_directory",
        pre=True,
    )
    def validate_directories(cls, v):
        """驗證目錄路徑"""
        if v is not None:
            path = Path(v).expanduser().resolve()
            return str(path)
        return v


class GameProfileConfig(BaseModel):
    """
    遊戲設定檔配置模型
    """

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, str_strip_whitespace=True
    )

    # 基本信息
    profile_id: str = Field(..., description="設定檔 ID")
    profile_name: str = Field(..., description="設定檔名稱")
    created_time: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="創建時間"
    )
    last_used: Optional[datetime.datetime] = Field(
        default=None, description="最後使用時間"
    )

    # 版本信息
    minecraft_version: str = Field(..., description="Minecraft 版本")
    loader_type: Optional[str] = Field(
        default=None, description="模組加載器類型 (forge/fabric/quilt)"
    )
    loader_version: Optional[str] = Field(default=None, description="模組加載器版本")

    # 遊戲配置
    minecraft_options: MinecraftOptions = Field(
        default_factory=MinecraftOptions, description="Minecraft 選項"
    )

    # Java 配置
    java_executable: Optional[str] = Field(
        default=None, description="Java 可執行文件路徑"
    )
    java_arguments: List[str] = Field(default_factory=list, description="Java 參數")

    # 模組配置
    enabled_mods: List[str] = Field(
        default_factory=list, description="啟用的模組 ID 列表"
    )

    # 資源包配置
    enabled_resource_packs: List[str] = Field(
        default_factory=list, description="啟用的資源包列表"
    )

    # 其他設定
    icon_path: Optional[str] = Field(default=None, description="設定檔圖標路徑")
    description: Optional[str] = Field(default=None, description="設定檔描述")


class DownloadConfig(BaseModel):
    """
    下載配置模型
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # 下載設定
    max_concurrent_downloads: int = Field(
        default=4, description="最大並發下載數", ge=1, le=16
    )
    download_timeout: int = Field(default=300, description="下載超時時間（秒）", ge=30)
    retry_attempts: int = Field(default=3, description="重試次數", ge=0, le=10)

    # 驗證設定
    verify_checksums: bool = Field(default=True, description="驗證文件校驗和")
    verify_signatures: bool = Field(default=False, description="驗證文件簽名")

    # 代理設定
    use_proxy: bool = Field(default=False, description="使用代理")
    proxy_host: Optional[str] = Field(default=None, description="代理主機")
    proxy_port: Optional[int] = Field(
        default=None, description="代理端口", ge=1, le=65535
    )
    proxy_username: Optional[str] = Field(default=None, description="代理用戶名")
    proxy_password: Optional[str] = Field(default=None, description="代理密碼")

    # 鏡像設定
    use_mirror: bool = Field(default=False, description="使用鏡像源")
    mirror_url: Optional[str] = Field(default=None, description="鏡像源 URL")


class UIConfig(BaseModel):
    """
    用戶界面配置模型
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # 窗口設定
    window_width: int = Field(default=1200, description="窗口寬度", ge=800)
    window_height: int = Field(default=800, description="窗口高度", ge=600)
    window_maximized: bool = Field(default=False, description="窗口最大化")
    window_position_x: Optional[int] = Field(default=None, description="窗口 X 位置")
    window_position_y: Optional[int] = Field(default=None, description="窗口 Y 位置")

    # 主題設定
    theme: str = Field(default="auto", description="主題 (light/dark/auto)")
    accent_color: str = Field(default="#0078d4", description="主題色")
    font_family: str = Field(default="System", description="字體家族")
    font_size: int = Field(default=12, description="字體大小", ge=8, le=24)

    # 界面設定
    show_news: bool = Field(default=True, description="顯示新聞")
    show_release_notes: bool = Field(default=True, description="顯示版本說明")
    show_advanced_options: bool = Field(default=False, description="顯示高級選項")
    auto_close_launcher: bool = Field(
        default=False, description="遊戲啟動後自動關閉啟動器"
    )

    # 語言設定
    language: str = Field(default="zh-TW", description="界面語言")


class BasicLauncher(BaseModel):
    """
    基礎啟動器的自定義類別
    用於存儲啟動器的基本信息
    """

    LauncherName: str
    LauncherVersion: str
    MinecraftOptions: MinecraftOptions


class CompleteLauncherConfig(BaseModel):
    """
    完整的啟動器配置模型
    整合所有配置組件
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    # 主要配置組件
    launcher_config: LauncherConfigModel = Field(
        default_factory=LauncherConfigModel, description="啟動器主配置"
    )
    download_config: DownloadConfig = Field(
        default_factory=DownloadConfig, description="下載配置"
    )
    ui_config: UIConfig = Field(default_factory=UIConfig, description="UI 配置")

    # 設定檔列表
    game_profiles: Dict[str, GameProfileConfig] = Field(
        default_factory=dict, description="遊戲設定檔字典"
    )
    active_profile_id: Optional[str] = Field(
        default=None, description="當前活躍的設定檔 ID"
    )

    # 配置元數據
    config_version: str = Field(default="1.0.0", description="配置文件版本")
    last_modified: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="最後修改時間"
    )

    def get_active_profile(self) -> Optional[GameProfileConfig]:
        """獲取當前活躍的設定檔"""
        if self.active_profile_id and self.active_profile_id in self.game_profiles:
            return self.game_profiles[self.active_profile_id]
        return None

    def add_profile(self, profile: GameProfileConfig) -> None:
        """添加新的遊戲設定檔"""
        self.game_profiles[profile.profile_id] = profile
        if not self.active_profile_id:
            self.active_profile_id = profile.profile_id
        self.last_modified = datetime.datetime.now()

    def remove_profile(self, profile_id: str) -> bool:
        """移除遊戲設定檔"""
        if profile_id in self.game_profiles:
            del self.game_profiles[profile_id]
            if self.active_profile_id == profile_id:
                # 設置新的活躍設定檔
                self.active_profile_id = next(iter(self.game_profiles.keys()), None)
            self.last_modified = datetime.datetime.now()
            return True
        return False


class MinecraftLauncher:
    """
    Minecraft啟動器的自定義類別
    用於管理Minecraft帳戶和管理Launcher的設定等等
    """

    def __init__(self, config: Optional[CompleteLauncherConfig] = None):
        self.config = config or CompleteLauncherConfig()
        self.account_manager = AccountManager()

    async def initialize(self) -> None:
        """初始化啟動器"""
        # 確保必要的目錄存在
        for directory in [
            self.config.launcher_config.minecraft_directory,
            self.config.launcher_config.config_directory,
            self.config.launcher_config.cache_directory,
            self.config.launcher_config.logs_directory,
        ]:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)

    def get_config(self) -> CompleteLauncherConfig:
        """獲取完整配置"""
        return self.config

    def update_config(self, **kwargs) -> None:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.config.last_modified = datetime.datetime.now()

    async def add_account(self, Credential: Credential) -> None:
        """添加帳戶"""
        # 驗證帳戶
        auth_credential = AuthCredential(
            access_token=Credential.access_token,
            refresh_token=Credential.refresh_token,
        )

        if await self.account_manager.Checker(auth_credential):
            self.config.launcher_config.saved_accounts.append(Credential)
            if not self.config.launcher_config.current_account:
                self.config.launcher_config.current_account = Credential


# 導出所有配置模型
__all__ = [
    "MultipleCredential",
    "AccountManager",
    "LauncherConfigModel",
    "GameProfileConfig",
    "DownloadConfig",
    "UIConfig",
    "BasicLauncher",
    "CompleteLauncherConfig",
    "MinecraftLauncher",
]
