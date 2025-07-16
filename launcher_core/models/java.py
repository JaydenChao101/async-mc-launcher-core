"""
Java 相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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
