# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
from typing import Literal, TypedDict


class VanillaLauncherProfilesJsonProfile(TypedDict, total=False):
    created: str
    gameDir: str
    icon: str
    javaArgs: str
    javaDir: str
    lastUsed: str
    lastVersionId: str
    name: str
    resolution: dict[Literal["height", "width"], int]
    type: str


class VanillaLauncherProfilesJson(TypedDict):
    profiles: dict[str, VanillaLauncherProfilesJsonProfile]
    version: int
