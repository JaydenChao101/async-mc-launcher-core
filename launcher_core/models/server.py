"""
伺服器相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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
