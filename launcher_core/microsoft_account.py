"""
This code is used to login to a Microsoft account and get the access token.
"""

# This file is part of asyncio-minecraft-launcher-lib (https://github.com/JaydenChao101/asyncio-mc-lancher-lib)
# Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
import urllib.parse
import asyncio
import aiohttp
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
from ._types import AzureApplication
from ._types import Credential as AuthCredential
from .logging_utils import logger

__AUTH_URL__ = "https://login.live.com/oauth20_authorize.srf"
__TOKEN_URL__ = "https://login.live.com/oauth20_token.srf"
__DEVICE_TOKEN_URL__ = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
__SCOPE__ = "XboxLive.signin offline_access"
__DEVICE_CODE_URL__ = (
    "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
)


__all__ = [
    "Login",
    "device_code_login",
    "refresh_minecraft_token",
]


class Login:
    """
    This class is used to login to a Microsoft account and get the access token.
    It uses the Microsoft OAuth2.0 authentication flow to get the access token.
    """

    def __init__(
        self,
        azure_app: AzureApplication = AzureApplication(),
    ):
        self.client_id = azure_app.client_id
        self.redirect_uri = azure_app.redirect_uri
        self.client_secret = azure_app.client_secret

    async def get_login_url(self) -> str:
        """
        Generate a login url.
        :return: The url to the website on which the user logs in
        """
        parameters = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "response_mode": "query",
            "scope": __SCOPE__,
        }
        url = (
            urllib.parse.urlparse(__AUTH_URL__)
            ._replace(query=urllib.parse.urlencode(parameters))
            .geturl()
        )
        logger.info("Generated login URL for Microsoft account authentication: %s", url)

        return url

    @staticmethod
    async def extract_code_from_url(url: str) -> str:
        """
        Extract the code from the redirect url.

        :param url: The redirect url
        :return: The code
        """
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if "code" not in query_params:
            raise ValueError("No code found in the URL")
        return query_params["code"][0]

    async def get_ms_token(
        self,
        code: str,
    ) -> AuthorizationTokenResponse:
        """
        Get the Microsoft token using the code from the login url.

        :param code: The code from the login url
        :return: The Microsoft token
        """
        data = {
            "client_id": self.client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": __SCOPE__,
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                __TOKEN_URL__, data=urllib.parse.urlencode(data), headers=headers
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.info("Microsoft token response: %s", data)
                return data

    @staticmethod
    async def get_xbl_token(ms_access_token: str) -> XBLResponse:
        """Get the Xbox Live token using the Microsoft access token."""
        payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_access_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",  # 注意这里
            "TokenType": "JWT",
        }
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://user.auth.xboxlive.com/user/authenticate",
                json=payload,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.info("Xbox Token response: %s", data)
                return data

    @staticmethod
    async def get_xsts_token(xbl_token: str) -> XSTSResponse:
        """
        Get the XSTS token using the Xbox Live token.

        :param xbl_token: The Xbox Live token
        :return: The XSTS token
        """
        payload = {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbl_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        }
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://xsts.auth.xboxlive.com/xsts/authorize",
                json=payload,
                headers=headers,
            ) as resp:
                status = resp.status
                data = await resp.json()

                if status == 401:
                    error_code = data.get("XErr")
                    # The Redirect parameter usually will not resolve or go anywhere in a browser, likely they're targeting Xbox consoles.
                    # Noted XErr codes and their meanings:
                    # 2148916227:
                    # The account is banned from Xbox.
                    # 2148916233:
                    # The account doesn't have an Xbox account. Once they sign up for one (or login through minecraft.net to create one) then they can proceed with the login. This shouldn't happen with accounts that have purchased Minecraft with a Microsoft account, as they would've already gone through that Xbox signup process.
                    # 2148916235:
                    # The account is from a country where Xbox Live is not available/banned
                    # 2148916236:
                    # The account needs adult verification on Xbox page. (South Korea)
                    # 2148916237:
                    # The account needs adult verification on Xbox page. (South Korea)
                    # 2148916238:
                    # The account is a child (under 18) and cannot proceed unless the account is added to a Family by an adult. This only seems to occur when using a custom Microsoft Azure application. When using the Minecraft launchers client id, this doesn't trigger.
                    error_codes = {
                        "ban_from_Xbox": 2148916227,
                        "didnt_have_xbox": 2148916233,
                        "ban_contry": 2148916235,
                        "need_adult_verification": 2148916236,
                        "need_adult_verification_1": 2148916237,
                    }

                    # raise Error
                    if error_code == error_codes["ban_from_Xbox"]:
                        raise AccountBanFromXbox()
                    elif error_code == error_codes["didnt_have_xbox"]:
                        raise AccountNotHaveXbox()
                    elif error_code == error_codes["ban_contry"]:
                        raise XboxLiveNotAvailable()
                    elif (
                        error_code == error_codes["need_adult_verification"]
                        or error_code == error_codes["need_adult_verification_1"]
                    ):
                        raise AccountNeedAdultVerification()
                    else:
                        raise XErrNotFound(
                            f"Loginning of the XSTS token error: {error_code}, full response: {data}"
                        )

                logger.info("XSTS Token response: %s", data)
                return data

    @staticmethod
    async def get_minecraft_access_token(
        xsts_token: str, uhs: str
    ) -> MinecraftAuthenticateResponse:
        """
        Get the Minecraft access token using the XSTS token and user hash.

        :param xsts_token: The XSTS token
        :param uhs: The user hash
        :return: The Minecraft access token
        """
        identity_token = f"XBL3.0 x={uhs};{xsts_token}"
        payload = {"identityToken": identity_token}
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.minecraftservices.com/authentication/login_with_xbox",
                json=payload,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.info("Minecraft access token response: %s", data)
                required_keys = ["access_token", "expires_in"]
                for key in required_keys:
                    if key not in data:
                        raise KeyError(
                            f"Missing required key '{key}' in Minecraft access token response: {data}"
                        )
                return data


class device_code_login:
    """
    This class is used to login to a Microsoft account using the device code flow.
    It uses the Microsoft OAuth2.0 authentication flow to get the access token.
    """

    def __init__(
        self,
        azure_app: AzureApplication = AzureApplication(),
        language: str = "en",
    ):
        self.client_id = azure_app.client_id
        self.language = language

    async def get_device_code(self) -> dict:
        """
        Get the device code using the client id and redirect uri.

        :return: The device code
        """
        data = {
            "client_id": self.client_id,
            "scope": __SCOPE__,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{__DEVICE_CODE_URL__}?mkt={self.language}", data=data, headers=headers
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def poll_device_code(self, device_code: str, interval: int, expires_in: int):
        """
        Poll the device code to get the access token.
        :param device_code: The device code
        :param interval: The interval to poll the device code
        :param expires_in: The expires in time
        :return: The ms_token
        :raises DeviceCodeExpiredError: If the device code is expired or not authorized in time.
        """
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": self.client_id,
            "device_code": device_code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        elapsed = 0
        max_interval = 60  # Set a maximum interval to prevent excessive delays
        while elapsed < expires_in:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    __DEVICE_TOKEN_URL__, data=data, headers=headers
                ) as resp:
                    result = await resp.json()
                    if "access_token" in result:
                        return result
                    elif result.get("error") == "authorization_pending":
                        await asyncio.sleep(interval)
                        elapsed += interval
                        interval = min(
                            interval * 2, max_interval
                        )  # Exponential backoff
                    elif result.get("error") == "slow_down":
                        interval = min(interval + 5, max_interval)
                        await asyncio.sleep(interval)
                        elapsed += interval
                    else:
                        raise DeviceCodeExpiredError(
                            "Device code expired or not authorized in time."
                        )


async def refresh_minecraft_token(
    Credential: AuthCredential,
    azure_app: AzureApplication = AzureApplication(),
) -> AuthorizationTokenResponse:
    """
    Refresh the Minecraft token using the refresh token.

    :param refresh_token: The refresh token
    :param azure_app: A dictionary containing Azure application details with keys:
                      - 'client_id': The client ID of the Azure application.
                      - 'client_secret': The client secret of the Azure application (optional).
    :return: The refreshed ms_token
    :raises ValueError: If the refresh token is not provided.
    """
    refresh_token = Credential.refresh_token if Credential else None
    if not refresh_token:
        raise ValueError("Refresh token is required to refresh the Minecraft token.")

    data = {
        "client_id": azure_app.client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "scope": __SCOPE__,
    }
    if azure_app.client_secret:
        data["client_secret"] = azure_app.client_secret
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            __TOKEN_URL__, data=urllib.parse.urlencode(data), headers=headers
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            logger.info("Refreshed Minecraft token response: %s", data)
            return data


# This example shows how to login to a Microsoft account and get the access token.
# async def login_minecraft():
#     import webbrowser
#     webbrowser.open_new_tab(await get_login_url())
#     url = input("Please open the URL in your browser and paste the redirect URL here: ")
#     code = await extract_code_from_url(url)
#     ms_token = await get_ms_token(code)
#     xbl_token = await get_xbl_token(ms_token["access_token"])
#     xsts_token = await get_xsts_token(xbl_token["Token"])
#     uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
#     minecraft_token = await get_minecraft_access_token(xsts_token["Token"], uhs)
#     await have_minecraft(minecraft_token["access_token"])
#     return {
#         "access_token": minecraft_token["access_token"],
#         "refresh_token": ms_token["refresh_token"],
#         "expires_in": ms_token["expires_in"],
#         "uhs": uhs,
#         "xsts_token": xsts_token["Token"],
#         "xbl_token": xbl_token["Token"]
#     }
#
# if __name__ == "__main__":
#     import asyncio
#     loop = asyncio.get_event_loop()
#     result = loop.run_until_complete(login_minecraft())
#     print(result)
