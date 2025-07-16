"""
下載和庫文件相關的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List, Any, Callable


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


# 回調字典類型，用於下載進度回調
CallbackDict = Dict[str, Callable[..., Any]]
