"""
啟動器設定相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


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
