# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
from typing import TypedDict
import datetime
from aiohttp.client_reqrep import ClientResponse


class RequestsResponseCache(TypedDict):
    response: ClientResponse
    datetime: datetime.datetime


class MavenMetadata(TypedDict):
    release: str
    latest: str
    versions: list[str]
