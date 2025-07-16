"""
新聞相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import datetime


class MinecraftNews(BaseModel):
    """Minecraft 新聞模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(..., description="新聞 ID")
    title: str = Field(..., description="新聞標題")
    content: str = Field(..., description="新聞內容")
    author: Optional[str] = Field(None, description="作者")
    category: str = Field(..., description="新聞分類")
    published_date: datetime.datetime = Field(..., description="發布日期")
    image_url: Optional[str] = Field(None, description="圖片 URL")
    tags: List[str] = Field(default_factory=list, description="標籤")


class JavaPatchNotes(BaseModel):
    """Java 版更新說明模型"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    version: str = Field(..., description="版本號")
    title: str = Field(..., description="更新標題")
    content: str = Field(..., description="更新內容")
    release_date: datetime.datetime = Field(..., description="發布日期")
    patch_type: str = Field(
        ..., description="更新類型"
    )  # release, snapshot, pre-release
    changes: List[str] = Field(default_factory=list, description="變更列表")
    fixes: List[str] = Field(default_factory=list, description="修復列表")
