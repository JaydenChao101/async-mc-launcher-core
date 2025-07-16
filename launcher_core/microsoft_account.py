"""
This code is used to login to a Microsoft account and get the access token.
"""

# This file is part of asyncio-minecraft-launcher-lib (https://github.com/JaydenChao101/asyncio-mc-lancher-lib)
# Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
import urllib.parse
import asyncio
import aiohttp
from typing import Dict, Any
from .http_client import HTTPClient
from .microsoft_types import (
    AuthorizationTokenResponse,
    XBLResponse,
    XSTSResponse,
    MinecraftAuthenticateResponse,
)
from .exceptions import (
    AccountBanFromXbox,
    AccountNeedAdultVerification,
    AccountNotHaveXbox,
    XboxLiveNotAvailable,
    XErrNotFound,
    DeviceCodeExpiredError,
)
from .models import AzureApplication
from .models import Credential as AuthCredential
from .logging_utils import logger

# API 端點常量
AUTH_URL = "https://login.live.com/oauth20_authorize.srf"
TOKEN_URL = "https://login.live.com/oauth20_token.srf"
DEVICE_TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
DEVICE_CODE_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
XBL_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
MINECRAFT_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"

SCOPE = "XboxLive.signin offline_access"

# XSTS 錯誤代碼映射
XSTS_ERROR_CODES = {
    2148916227: AccountBanFromXbox,
    2148916233: AccountNotHaveXbox,
    2148916235: XboxLiveNotAvailable,
    2148916236: AccountNeedAdultVerification,
    2148916237: AccountNeedAdultVerification,
}

__all__ = [
    "Login",
    "DeviceCodeLogin",
    "refresh_minecraft_token",
]


class XboxAuthenticator:
    """Xbox認證處理器"""

    @staticmethod
    async def get_xbl_token(ms_access_token: str) -> XBLResponse:
        """獲取Xbox Live令牌"""
        payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_access_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }

        data = await HTTPClient.post_json(XBL_AUTH_URL, payload)
        logger.info("Xbox Token response: %s", data)
        return data

    @staticmethod
    async def get_xsts_token(xbl_token: str) -> XSTSResponse:
        """獲取XSTS令牌"""
        payload = {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbl_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                XSTS_AUTH_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                data = await resp.json()

                if resp.status == 401:
                    XboxAuthenticator._handle_xsts_error(data)

                resp.raise_for_status()
                logger.info("XSTS Token response: %s", data)
                return data

    @staticmethod
    def _handle_xsts_error(data: Dict[str, Any]) -> None:
        """處理XSTS認證錯誤"""
        error_code = data.get("XErr")

        if error_code in XSTS_ERROR_CODES:
            raise XSTS_ERROR_CODES[error_code]()
        else:
            raise XErrNotFound(f"XSTS token error: {error_code}, full response: {data}")

    @staticmethod
    async def get_minecraft_access_token(
        xsts_token: str, uhs: str
    ) -> MinecraftAuthenticateResponse:
        """獲取Minecraft訪問令牌"""
        identity_token = f"XBL3.0 x={uhs};{xsts_token}"
        payload = {"identityToken": identity_token}

        data = await HTTPClient.post_json(MINECRAFT_AUTH_URL, payload)
        logger.info("Minecraft access token response: %s", data)

        # 驗證必需的字段
        required_keys = ["access_token", "expires_in"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing required key '{key}' in response: {data}")

        return data


class Login:
    """Microsoft帳戶登入處理器"""

    def __init__(self, azure_app: AzureApplication = AzureApplication()):
        self.azure_app = azure_app

    async def get_login_url(self) -> str:
        """生成登入URL"""
        parameters = {
            "client_id": self.azure_app.client_id,
            "response_type": "code",
            "redirect_uri": self.azure_app.redirect_uri,
            "response_mode": "query",
            "scope": SCOPE,
        }

        url = (
            urllib.parse.urlparse(AUTH_URL)
            ._replace(query=urllib.parse.urlencode(parameters))
            .geturl()
        )
        logger.info("Generated login URL: %s", url)
        return url

    @staticmethod
    def extract_code_from_url(url: str) -> str:
        """從重定向URL中提取授權代碼"""
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if "code" not in query_params:
            raise ValueError("No code found in the URL")

        return query_params["code"][0]

    async def get_ms_token(self, code: str) -> AuthorizationTokenResponse:
        """使用授權代碼獲取Microsoft令牌"""
        data = {
            "client_id": self.azure_app.client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.azure_app.redirect_uri,
            "scope": SCOPE,
        }

        if self.azure_app.client_secret:
            data["client_secret"] = self.azure_app.client_secret

        result = await HTTPClient.post_form(TOKEN_URL, data)
        logger.info("Microsoft token response: %s", result)
        return result

    async def complete_login(self, code: str) -> AuthCredential:
        """完成完整的登入流程"""
        # 獲取Microsoft令牌
        ms_token = await self.get_ms_token(code)

        # 獲取Xbox Live令牌
        xbl_token = await XboxAuthenticator.get_xbl_token(ms_token["access_token"])

        # 獲取XSTS令牌
        xsts_token = await XboxAuthenticator.get_xsts_token(xbl_token["Token"])

        # 獲取用戶哈希
        uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]

        # 獲取Minecraft訪問令牌
        minecraft_token = await XboxAuthenticator.get_minecraft_access_token(
            xsts_token["Token"], uhs
        )

        return AuthCredential(
            access_token=minecraft_token["access_token"],
            refresh_token=ms_token["refresh_token"],
            expires_in=minecraft_token["expires_in"],
        )


class DeviceCodeLogin:
    """設備代碼登入處理器"""

    def __init__(
        self, azure_app: AzureApplication = AzureApplication(), language: str = "en"
    ):
        self.azure_app = azure_app
        self.language = language

    async def get_device_code(self) -> Dict[str, Any]:
        """獲取設備代碼"""
        data = {
            "client_id": self.azure_app.client_id,
            "scope": SCOPE,
        }

        url = f"{DEVICE_CODE_URL}?mkt={self.language}"
        return await HTTPClient.post_form(url, data)

    async def poll_device_code(
        self, device_code: str, interval: int, expires_in: int
    ) -> AuthorizationTokenResponse:
        """輪詢設備代碼狀態"""
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": self.azure_app.client_id,
            "device_code": device_code,
        }

        elapsed = 0
        max_interval = 60
        current_interval = interval

        while elapsed < expires_in:
            try:
                result = await HTTPClient.post_form(DEVICE_TOKEN_URL, data)
                if "access_token" in result:
                    return result
            except aiohttp.ClientResponseError as e:
                if e.status == 400:
                    # 由於 ClientResponseError 沒有 response 屬性，我們需要手動處理
                    try:
                        # 嘗試從錯誤消息中提取錯誤信息
                        if "authorization_pending" in str(e):
                            await asyncio.sleep(current_interval)
                            elapsed += current_interval
                            current_interval = min(current_interval * 2, max_interval)
                        elif "slow_down" in str(e):
                            current_interval = min(current_interval + 5, max_interval)
                            await asyncio.sleep(current_interval)
                            elapsed += current_interval
                        else:
                            raise DeviceCodeExpiredError(
                                "Device code expired or not authorized in time."
                            )
                    except Exception:
                        # 如果無法解析錯誤，使用通用處理
                        await asyncio.sleep(current_interval)
                        elapsed += current_interval
                        current_interval = min(current_interval * 2, max_interval)
                else:
                    raise

        raise DeviceCodeExpiredError("Device code expired.")


async def refresh_minecraft_token(
    credential: AuthCredential,
    azure_app: AzureApplication = AzureApplication(),
) -> AuthorizationTokenResponse:
    """刷新Minecraft令牌"""
    if not credential or not credential.refresh_token:
        raise ValueError("Refresh token is required to refresh the Minecraft token.")

    data = {
        "client_id": azure_app.client_id,
        "refresh_token": credential.refresh_token,
        "grant_type": "refresh_token",
        "scope": SCOPE,
    }

    if azure_app.client_secret:
        data["client_secret"] = azure_app.client_secret

    result = await HTTPClient.post_form(TOKEN_URL, data)
    logger.info("Refreshed Minecraft token response: %s", result)
    return result
