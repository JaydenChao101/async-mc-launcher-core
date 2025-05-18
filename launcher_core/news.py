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

# 第三方庫導入
import aiohttp

# 本地導入
from ._types import MinecraftNews, JavaPatchNotes
from ._helper import get_user_agent


async def get_minecraft_news() -> MinecraftNews:
    "Returns general news about Minecraft"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://launchercontent.mojang.com/news.json",
            headers={"user-agent": get_user_agent()},
        ) as response:
            news = await response.json()

    for entry in news["entries"]:
        entry["date"] = datetime.date.fromisoformat(entry["date"])

    return news


async def get_java_patch_notes() -> JavaPatchNotes:
    "Returns the patch notes for Minecraft Java Edition"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://launchercontent.mojang.com/javaPatchNotes.json",
            headers={"user-agent": get_user_agent()},
        ) as response:
            return await response.json()
