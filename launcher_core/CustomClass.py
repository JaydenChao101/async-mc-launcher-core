from typing import Optional, List, Dict, TYPE_CHECKING
from pathlib import Path
import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from . import Credential as AuthCredential
from .exceptions import NeedAccountInfo, AccountNotOwnMinecraft
from .mojang import have_minecraft
from .models import MinecraftOptions, Credential, LauncherSettings, ServerInfo, ModInfo

if TYPE_CHECKING:
    CredentialType = AuthCredential
else:
    CredentialType = AuthCredential


class MultipleCredential(BaseModel):
    """
    存儲多個帳戶憑證
    """

    AuthCredential: List[CredentialType]


class AccountManager:
    """
    帳戶管理類
    """

    @staticmethod
    async def Checker(Credential: CredentialType) -> bool:
        """
        檢查帳戶憑證是否有效
        """
        if not Credential.access_token:
            raise NeedAccountInfo("帳戶憑證無效或未提供")

        try:
            await have_minecraft(Credential.access_token)
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

        return all(
            [await AccountManager.Checker(c) for c in MultipleCredential.AuthCredential]
        )


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
    launcher_uuid: Optional[str] = None

    # 目錄配置
    minecraft_directory: Optional[str] = None
    config_directory: Optional[str] = None
    cache_directory: Optional[str] = None
    logs_directory: Optional[str] = None

    # 帳戶配置
    current_account: Optional[Credential] = None
    saved_accounts: List[Credential] = Field(default_factory=list)
    auto_login: bool = True
    remember_account: bool = True

    # 啟動器設定
    launcher_settings: LauncherSettings = Field(default_factory=LauncherSettings)

    # 遊戲配置
    default_minecraft_options: MinecraftOptions = Field(
        default_factory=MinecraftOptions
    )

    # 伺服器配置
    saved_servers: List[ServerInfo] = Field(default_factory=list)

    # 模組配置
    installed_mods: List[ModInfo] = Field(default_factory=list)

    @field_validator(
        "minecraft_directory",
        "config_directory",
        "cache_directory",
        "logs_directory",
        mode="before",
    )
    @classmethod
    def validate_directories(cls, v):
        """驗證目錄路徑"""
        if v is not None:
            return str(Path(v).expanduser().resolve())
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
    last_used: Optional[datetime.datetime] = None

    # 版本信息
    minecraft_version: str = Field(..., description="Minecraft 版本")
    loader_type: Optional[str] = None
    loader_version: Optional[str] = None

    # 遊戲配置
    minecraft_options: MinecraftOptions = Field(default_factory=MinecraftOptions)

    # Java 配置
    java_executable: Optional[str] = None
    java_arguments: List[str] = Field(default_factory=list)

    # 模組配置
    enabled_mods: List[str] = Field(
        default_factory=list, description="啟用的模組 ID 列表"
    )

    # 資源包配置
    enabled_resource_packs: List[str] = Field(
        default_factory=list, description="啟用的資源包列表"
    )

    # 其他設定
    icon_path: Optional[str] = None
    description: Optional[str] = None


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
    verify_checksums: bool = True
    verify_signatures: bool = False

    # 代理設定
    use_proxy: bool = False
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = Field(default=None, ge=1, le=65535)
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None

    # 鏡像設定
    use_mirror: bool = False
    mirror_url: Optional[str] = None


class UIConfig(BaseModel):
    """
    用戶界面配置模型
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # 窗口設定
    window_width: int = Field(default=1200, description="窗口寬度", ge=800)
    window_height: int = Field(default=800, description="窗口高度", ge=600)
    window_maximized: bool = False
    window_position_x: Optional[int] = None
    window_position_y: Optional[int] = None

    # 主題設定
    theme: str = Field(default="auto", description="主題 (light/dark/auto)")
    accent_color: str = Field(default="#0078d4", description="主題色")
    font_family: str = Field(default="System", description="字體家族")
    font_size: int = Field(default=12, description="字體大小", ge=8, le=24)

    # 界面設定
    show_news: bool = True
    show_release_notes: bool = True
    show_advanced_options: bool = False
    auto_close_launcher: bool = False

    # 語言設定
    language: str = Field(default="zh-TW", description="界面語言")


class BasicLauncher(BaseModel):
    """
    基礎啟動器類
    """

    LauncherName: str
    LauncherVersion: str
    MinecraftOptions: MinecraftOptions


class CompleteLauncherConfig(BaseModel):
    """
    完整啟動器配置模型
    整合所有配置組件
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    # 主要配置組件
    launcher_config: LauncherConfigModel = Field(default_factory=LauncherConfigModel)
    download_config: DownloadConfig = Field(default_factory=DownloadConfig)
    ui_config: UIConfig = Field(default_factory=UIConfig)

    # 設定檔列表
    game_profiles: Dict[str, GameProfileConfig] = Field(default_factory=dict)
    active_profile_id: Optional[str] = None

    # 配置元數據
    config_version: str = Field(default="1.0.0", description="配置文件版本")
    last_modified: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="最後修改時間"
    )

    def get_active_profile(self) -> Optional[GameProfileConfig]:
        """獲取當前活躍的設定檔"""
        if self.active_profile_id:
            return self.game_profiles.get(self.active_profile_id)
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
    Minecraft啟動器管理類
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
