"""
Minecraft 相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, Union, List
import datetime


class MinecraftOptions(BaseModel):
    """The options for the Minecraft Launcher"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
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
    versionType: Optional[Literal["latest-release", "latest-snapshot", "custom"]] = (
        Field(None, description="版本類型")
    )
    gameDirectory: Optional[str] = Field(None, description="遊戲目錄")
    javaExecutable: Optional[str] = Field(None, description="Java 可執行文件")
    javaArguments: Optional[List[str]] = Field(None, description="Java 參數")
    customResolution: Optional[VanillaLauncherProfileResolution] = Field(
        None, description="自定義解析度"
    )


class AssetInfo(BaseModel):
    """資源文件信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    hash: str = Field(..., description="文件哈希")
    size: int = Field(..., description="文件大小", ge=0)
