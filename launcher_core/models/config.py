"""Minimal configuration models for async-mc-launcher-core.

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from typing import Optional
from pydantic import BaseModel, Field


class LauncherConfig(BaseModel):
    """Light-weight launcher configuration used by the test-suite."""

    launcher_name: str = "AsyncMCLauncher"
    launcher_version: str = "1.0.0"
    username: Optional[str] = None
    version: Optional[str] = None
    concurrent_downloads: int = Field(4, ge=1, le=16)
    download_timeout: int = Field(300, ge=1)
    verify_downloads: bool = True
    auto_refresh_token: bool = True
    log_level: str = "INFO"
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None


__all__ = ["LauncherConfig"]
