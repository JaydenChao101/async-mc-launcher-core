# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""
news includes functions to retrieve news about Minecraft using the official API from Mojang

.. warning::
    The format of the data returned by this API may change at any time
"""

# 標準庫導入
import datetime

# 本地導入
from .models import MinecraftNews, JavaPatchNotes
from ._helper import get_user_agent
from .http_client import HTTPClient


async def get_minecraft_news(category: str = None) -> MinecraftNews:
    "Returns general news about Minecraft"
    user_agent = await get_user_agent()
    headers = {"user-agent": user_agent}
    news = await HTTPClient.get_json(
        "https://launchercontent.mojang.com/news.json",
        headers=headers,
    )

    # 安全地處理日期，只處理有 date 字段的條目
    for entry in news["entries"]:
        if "date" in entry:
            entry["date"] = datetime.date.fromisoformat(entry["date"])

    # 如果指定了類別，進行過濾
    if category:
        filtered_entries = [
            entry for entry in news["entries"] if entry.get("category") == category
        ]
        news["entries"] = filtered_entries
        news["article_count"] = len(filtered_entries)

    return news


async def get_java_patch_notes() -> JavaPatchNotes:
    "Returns the patch notes for Minecraft Java Edition"
    user_agent = await get_user_agent()
    headers = {"user-agent": user_agent}
    return await HTTPClient.get_json(
        "https://launchercontent.mojang.com/javaPatchNotes.json",
        headers=headers,
    )
