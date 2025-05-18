# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
from typing import TypedDict


class _AssetsJsonObject(TypedDict):
    hash: str
    size: int


class AssetsJson(TypedDict):
    objects: dict[str, _AssetsJsonObject]
