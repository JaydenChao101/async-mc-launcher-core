# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""HTTP client utilities for making async requests"""

import urllib.parse
import aiohttp
from typing import Dict, Any, Optional

__all__ = ["HTTPClient"]


class HTTPClient:
    """通用HTTP客戶端，處理常見的請求模式"""

    @staticmethod
    async def post_json(
        url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """發送JSON POST請求"""
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=default_headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def post_form(
        url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """發送表單POST請求"""
        default_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if headers:
            default_headers.update(headers)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=urllib.parse.urlencode(data), headers=default_headers
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def get_json(
        url: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """發送GET請求並返回JSON響應"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def get_text(url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """發送GET請求並返回文本響應"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.text()

    @staticmethod
    async def get_bytes(url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
        """發送GET請求並返回二進制響應"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.read()

    @staticmethod
    async def download_file(
        url: str,
        file_path: str,
        headers: Optional[Dict[str, str]] = None,
        chunk_size: int = 8192,
    ) -> None:
        """下載文件到指定路徑"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(chunk_size):
                        f.write(chunk)
