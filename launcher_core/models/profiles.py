"""
設定檔相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from pathlib import Path
from .auth import Credential
from .minecraft import MinecraftOptions


class LaunchProfile(BaseModel):
    """啟動設定檔模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., description="設定檔名稱")
    version: str = Field(..., description="Minecraft 版本")
    game_directory: Optional[str] = Field(None, description="遊戲目錄")
    java_executable: Optional[str] = Field(None, description="Java 可執行文件")
    jvm_arguments: List[str] = Field(default_factory=list, description="JVM 參數")
    game_arguments: List[str] = Field(default_factory=list, description="遊戲參數")
    credential: Optional[Credential] = Field(None, description="登入憑證")
    minecraft_options: Optional[MinecraftOptions] = Field(
        None, description="Minecraft 選項"
    )

    @field_validator("game_directory", mode="before")
    @classmethod
    def validate_game_directory(cls, v):
        """驗證遊戲目錄"""
        if v is not None:
            path = Path(v)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        return v
