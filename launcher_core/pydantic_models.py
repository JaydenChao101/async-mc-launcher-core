"""
Pydantic Models converted from TypedDict definitions
從 TypedDict 定義轉換而來的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Literal, Union, NewType, List, Dict, Any
import datetime
from uuid import UUID
from pathlib import Path

# 重新定義 MinecraftUUID
MinecraftUUID = NewType("MinecraftUUID", UUID)


class MinecraftOptions(BaseModel):
    """The options for the Minecraft Launcher"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )

    username: Optional[str] = Field(None, description="玩家用戶名")
    uuid: Optional[str] = Field(None, description="玩家 UUID")
    token: Optional[str] = Field(None, description="訪問令牌")
    executablePath: Optional[str] = Field(None, description="Minecraft 可執行文件路徑")
    defaultExecutablePath: Optional[str] = Field(None, description="默認可執行文件路徑")
    jvmArguments: List[str] = Field(default_factory=list, description="JVM 參數")
    launcherName: str = Field(default="AsyncMCLauncher", description="啟動器名稱")
    launcherVersion: str = Field(default="1.0.0", description="啟動器版本")
    gameDirectory: Optional[str] = Field(None, description="遊戲目錄")
    demo: bool = Field(default=False, description="是否為演示模式")
    customResolution: bool = Field(default=False, description="是否使用自定義解析度")
    resolutionWidth: Optional[Union[int, str]] = Field(None, description="解析度寬度")
    resolutionHeight: Optional[Union[int, str]] = Field(None, description="解析度高度")
    server: Optional[str] = Field(None, description="伺服器地址")
    port: Optional[str] = Field(None, description="伺服器端口")
    nativesDirectory: Optional[str] = Field(None, description="原生庫目錄")
    enableLoggingConfig: bool = Field(default=True, description="是否啟用日誌配置")
    disableMultiplayer: bool = Field(default=False, description="是否禁用多人遊戲")
    disableChat: bool = Field(default=False, description="是否禁用聊天")
    quickPlayPath: Optional[str] = Field(None, description="快速遊戲路徑")
    quickPlaySingleplayer: Optional[str] = Field(None, description="快速單人遊戲")
    quickPlayMultiplayer: Optional[str] = Field(None, description="快速多人遊戲")
    quickPlayRealms: Optional[str] = Field(None, description="快速 Realms 遊戲")
    gameDir: Optional[str] = Field(None, description="遊戲目錄別名")


class LatestMinecraftVersions(BaseModel):
    """The latest Minecraft versions"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    release: str = Field(..., description="最新正式版本")
    snapshot: str = Field(..., description="最新快照版本")


class MinecraftVersionInfo(BaseModel):
    """The Minecraft version information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(..., description="版本 ID")
    type: str = Field(..., description="版本類型")
    releaseTime: datetime.datetime = Field(..., description="發布時間")
    complianceLevel: int = Field(..., description="合規級別")


class FabricMinecraftVersion(BaseModel):
    """The Minecraft version information for Fabric"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    version: str = Field(..., description="Minecraft 版本")
    stable: bool = Field(..., description="是否為穩定版本")


class FabricLoader(BaseModel):
    """The Fabric loader information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    separator: str = Field(..., description="分隔符")
    build: int = Field(..., description="構建號")
    maven: str = Field(..., description="Maven 坐標")
    version: str = Field(..., description="版本號")
    stable: bool = Field(..., description="是否為穩定版本")


class QuiltMinecraftVersion(BaseModel):
    """The Minecraft version information for Quilt"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    version: str = Field(..., description="Minecraft 版本")
    stable: bool = Field(..., description="是否為穩定版本")


class QuiltLoader(BaseModel):
    """The Quilt loader information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    separator: str = Field(..., description="分隔符")
    build: int = Field(..., description="構建號")
    maven: str = Field(..., description="Maven 坐標")
    version: str = Field(..., description="版本號")


class JavaInformation(BaseModel):
    """The Java information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    path: str = Field(..., description="Java 安裝路徑")
    name: str = Field(..., description="Java 名稱")
    version: str = Field(..., description="Java 版本")
    javaPath: str = Field(..., description="java 可執行文件路徑")
    javawPath: Optional[str] = Field(None, description="javaw 可執行文件路徑")
    is64Bit: bool = Field(..., description="是否為 64 位")
    openjdk: bool = Field(..., description="是否為 OpenJDK")


class VanillaLauncherProfileResolution(BaseModel):
    """The resolution of the Vanilla Launcher profile"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    height: int = Field(..., description="解析度高度", gt=0)
    width: int = Field(..., description="解析度寬度", gt=0)


class VanillaLauncherProfile(BaseModel):
    """The Vanilla Launcher profile"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: Optional[str] = Field(None, description="設定檔名稱")
    version: Optional[str] = Field(None, description="Minecraft 版本")
    versionType: Optional[Literal["latest-release", "latest-snapshot", "custom"]] = Field(
        None, description="版本類型"
    )
    gameDirectory: Optional[str] = Field(None, description="遊戲目錄")
    javaExecutable: Optional[str] = Field(None, description="Java 可執行文件")
    javaArguments: Optional[List[str]] = Field(None, description="Java 參數")
    customResolution: Optional[VanillaLauncherProfileResolution] = Field(
        None, description="自定義解析度"
    )


class MrpackInformation(BaseModel):
    """The MRPack information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="模組包名稱")
    summary: Optional[str] = Field(None, description="模組包摘要")


class DownloadInfo(BaseModel):
    """下載信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    url: str = Field(..., description="下載 URL")
    sha1: Optional[str] = Field(None, description="SHA1 校驗和")
    size: Optional[int] = Field(None, description="文件大小", ge=0)
    path: Optional[str] = Field(None, description="本地路徑")


class LibraryInfo(BaseModel):
    """庫文件信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="庫名稱")
    downloads: Optional[Dict[str, DownloadInfo]] = Field(None, description="下載信息")
    natives: Optional[Dict[str, str]] = Field(None, description="原生庫映射")
    extract: Optional[Dict[str, Any]] = Field(None, description="提取規則")
    rules: Optional[List[Dict[str, Any]]] = Field(None, description="應用規則")


class AssetInfo(BaseModel):
    """資源文件信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    hash: str = Field(..., description="文件哈希")
    size: int = Field(..., description="文件大小", ge=0)


class LoginCredentials(BaseModel):
    """登入憑證模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    access_token: str = Field(..., description="訪問令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    username: str = Field(..., description="用戶名")
    uuid: str = Field(..., description="用戶 UUID")
    expires_in: Optional[int] = Field(None, description="令牌過期時間（秒）")
    token_type: str = Field(default="Bearer", description="令牌類型")


class LaunchProfile(BaseModel):
    """啟動設定檔模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="設定檔名稱")
    version: str = Field(..., description="Minecraft 版本")
    game_directory: Optional[str] = Field(None, description="遊戲目錄")
    java_executable: Optional[str] = Field(None, description="Java 可執行文件")
    jvm_arguments: List[str] = Field(default_factory=list, description="JVM 參數")
    game_arguments: List[str] = Field(default_factory=list, description="遊戲參數")
    credentials: Optional[LoginCredentials] = Field(None, description="登入憑證")
    minecraft_options: Optional[MinecraftOptions] = Field(None, description="Minecraft 選項")

    @validator('game_directory', pre=True)
    def validate_game_directory(cls, v):
        """驗證遊戲目錄"""
        if v is not None:
            path = Path(v)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        return v


class ModInfo(BaseModel):
    """模組信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(..., description="模組 ID")
    name: str = Field(..., description="模組名稱")
    version: str = Field(..., description="模組版本")
    description: Optional[str] = Field(None, description="模組描述")
    author: Optional[str] = Field(None, description="模組作者")
    download_url: Optional[str] = Field(None, description="下載 URL")
    file_path: Optional[str] = Field(None, description="本地文件路徑")
    enabled: bool = Field(default=True, description="是否啟用")
    dependencies: List[str] = Field(default_factory=list, description="依賴模組")


class ServerInfo(BaseModel):
    """伺服器信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="伺服器名稱")
    address: str = Field(..., description="伺服器地址")
    port: int = Field(default=25565, description="伺服器端口", ge=1, le=65535)
    version: Optional[str] = Field(None, description="伺服器版本")
    description: Optional[str] = Field(None, description="伺服器描述")
    icon: Optional[str] = Field(None, description="伺服器圖標路徑")
    auto_connect: bool = Field(default=False, description="自動連接")


class LauncherSettings(BaseModel):
    """啟動器設定模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    theme: Literal["light", "dark", "auto"] = Field(default="auto", description="主題")
    language: str = Field(default="zh-TW", description="語言")
    auto_update: bool = Field(default=True, description="自動更新")
    keep_launcher_open: bool = Field(default=True, description="保持啟動器開啟")
    show_snapshots: bool = Field(default=False, description="顯示快照版本")
    concurrent_downloads: int = Field(default=4, description="並發下載數", ge=1, le=16)
    memory_allocation: int = Field(default=4096, description="記憶體分配 (MB)", ge=512)


# 導出所有模型
__all__ = [
    "MinecraftOptions",
    "LatestMinecraftVersions",
    "MinecraftVersionInfo",
    "FabricMinecraftVersion",
    "FabricLoader",
    "QuiltMinecraftVersion",
    "QuiltLoader",
    "JavaInformation",
    "VanillaLauncherProfileResolution",
    "VanillaLauncherProfile",
    "MrpackInformation",
    "DownloadInfo",
    "LibraryInfo",
    "AssetInfo",
    "LoginCredentials",
    "LaunchProfile",
    "ModInfo",
    "ServerInfo",
    "LauncherSettings",
    "MinecraftUUID"
]
