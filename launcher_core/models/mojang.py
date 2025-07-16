"""
Mojang 相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


class SkinData(BaseModel):
    """Minecraft 皮膚數據模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(..., description="皮膚 ID")
    state: str = Field(..., description="皮膚狀態")
    url: str = Field(..., description="皮膚 URL")
    variant: str = Field(default="classic", description="皮膚變體")  # classic 或 slim
    alias: Optional[str] = Field(None, description="皮膚別名")


class MinecraftProfileResponse(BaseModel):
    """Minecraft 檔案回應模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(..., description="玩家 UUID")
    name: str = Field(..., description="玩家名稱")
    properties: List[Dict[str, str]] = Field(
        default_factory=list, description="檔案屬性"
    )
    legacy: bool = Field(default=False, description="是否為舊版檔案")
    demo: bool = Field(default=False, description="是否為演示檔案")
    skins: List[SkinData] = Field(default_factory=list, description="皮膚列表")
    capes: List[Dict[str, str]] = Field(default_factory=list, description="披風列表")
