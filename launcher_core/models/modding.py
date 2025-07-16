"""
模組和模組載入器相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


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


class MrpackInformation(BaseModel):
    """The MRPack information"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="模組包名稱")
    summary: Optional[str] = Field(None, description="模組包摘要")


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


class MrpackInstallOptions(BaseModel):
    """MRPack 安裝選項模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    overwrite_existing: bool = Field(default=False, description="是否覆蓋現有文件")
    install_dependencies: bool = Field(default=True, description="是否安裝依賴")
    target_directory: Optional[str] = Field(None, description="目標安裝目錄")
    loader_version: Optional[str] = Field(None, description="模組載入器版本")
    minecraft_version: Optional[str] = Field(None, description="Minecraft 版本")
