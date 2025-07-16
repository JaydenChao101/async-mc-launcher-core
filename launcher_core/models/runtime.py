"""
運行時相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


class JvmRuntimeInformation(BaseModel):
    """JVM 運行時信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="JVM 運行時名稱")
    version: str = Field(..., description="JVM 版本")
    architecture: str = Field(..., description="架構")
    os: str = Field(..., description="操作系統")
    download_url: str = Field(..., description="下載 URL")
    sha1: Optional[str] = Field(None, description="SHA1 校驗和")
    size: Optional[int] = Field(None, description="文件大小", ge=0)


class VersionRuntimeInformation(BaseModel):
    """版本運行時信息模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    version: str = Field(..., description="Minecraft 版本")
    java_version: str = Field(..., description="所需 Java 版本")
    jvm_runtime: Optional[JvmRuntimeInformation] = Field(
        None, description="JVM 運行時信息"
    )
    arguments: List[str] = Field(default_factory=list, description="JVM 參數")
    environment: Dict[str, str] = Field(default_factory=dict, description="環境變量")
