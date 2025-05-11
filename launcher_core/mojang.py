"""
The file is part of the minecraft_launcher_lib project.
It is licensed under the BSD-2-Clause license.
It contains functions for interacting with the Minecraft skin API.
It provides functions to get the skin URL, get the skin data, and download the skin.
Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
"""

from base64 import b64decode
import json
from typing import Optional
import aiohttp
import aiofiles
from ._types import SkinData, Credential, MinecraftProfileResponse
from .exceptions import AccountNotOwnMinecraft, NeedAccountInfo



class Skin:
    '''
    用于处理 Minecraft 皮肤的类。
    提供获取皮肤 URL、上传皮肤、重置皮肤等功能。
    '''
    def __init__(self, Credential: Credential):
        self.Credential = Credential

    async def get_skin_and_cape(self) -> Optional[SkinData]:
        """
        取得指定 UUID 的外觀與披風 URL。

        :param Credential: 玩家凭证，需包含 uuid
        :return: dict，包含 skin 和 cape（如无披風则 cape 为 None）
        """
        credential = self.Credential
        uuid = credential.uuid
        if not uuid:
            raise AccountNotOwnMinecraft
        # 使用 UUID 取得玩家的外觀與披風 URL
        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
        properties = data.get("properties", [])
        for prop in properties:
            if prop.get("name") == "textures":
                value = prop.get("value")
                decoded = b64decode(value).decode("utf-8")
                textures_json = json.loads(decoded)
                textures = textures_json.get("textures", {})
                skin_url = textures.get("SKIN", {}).get("url")
                cape_url = textures.get("CAPE", {}).get("url")
                return {"skin": skin_url, "cape": cape_url}
        return None

    async def change_skin(self, skin_url: str, model: str = "") -> bool:
        """
        更改玩家的外觀（通过URL）。

        :param Credential: 玩家凭证，需包含 uuid 和 access_token
        :param skin_url: 新的外觀 URL
        :param model: "slim" 或 ""，默认为 ""
        :param cape_url: 未使用，保留参数
        :return: bool，是否成功更改
        """
        credential = self.Credential
        uuid = credential.uuid
        access_token = credential.access_token
        url = f"https://api.mojang.com/user/profile/{uuid}/skin"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"model": model, "url": skin_url}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return response.status == 204

    async def upload_skin(self, file_path: str, model: str = "") -> bool:
        """
        上传本地外观文件。

        :param Credential: 玩家凭证，需包含 uuid 和 access_token
        :param file_path: 本地皮肤文件路径
        :param model: "slim" 或 ""，默认为 ""
        :return: bool，是否成功上传
        """
        credential = self.Credential
        uuid = credential.uuid
        access_token = credential.access_token

        if not uuid or not access_token:
            raise NeedAccountInfo("UUID and access token are required to upload skin.") 
        url = f"https://api.mojang.com/user/profile/{uuid}/skin"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()

        form = aiohttp.FormData()
        form.add_field("file", file_data, filename=file_path.split("/")[-1])
        form.add_field("model", model)

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, data=form) as response:
                return response.status == 204

    async def reset_skin(self) -> bool:
        """
        重设玩家外观为默认。

        :param Credential: 玩家凭证，需包含 uuid 和 access_token
        :return: bool，是否成功重设
        """
        credential = self.Credential
        uuid = credential.uuid
        access_token = credential.access_token
        if not uuid or not access_token:
            raise NeedAccountInfo("UUID and access token are required to reset skin.")       
        url = f"https://api.mojang.com/user/profile/{uuid}/skin"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                return response.status == 204


async def have_minecraft(access_token: str) -> bool:
    """
    Check if the user owns Minecraft using the access token.

    :param access_token: The Minecraft access token
    :return: True if the user owns Minecraft, Raise AccountNotOwnMinecraft otherwise
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.minecraftservices.com/entitlements/mcstore", headers=headers
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if not data.get("items"):
                raise AccountNotOwnMinecraft()
            return True


async def get_minecraft_profile(access_token: str) -> MinecraftProfileResponse:
    """
    Get the Minecraft profile using the access token.

    :param access_token: The Minecraft access token
    :return: The Minecraft profile
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.minecraftservices.com/minecraft/profile", headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def get_minecraft_player_attributes(
    access_token: str,
) -> MinecraftProfileResponse:
    """
    Get the Minecraft player attributes.

    :return: The Minecraft player attributes
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.minecraftservices.com/minecraft/profile/attributes",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
