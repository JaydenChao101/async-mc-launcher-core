import logging
from launcher_core import microsoft_account
import asyncio
from launcher_core.setting import setup_logger
from launcher_core.mojang import have_minecraft

logger = setup_logger(enable_console=False, level=logging.INFO, filename="microsoft_account.log")

async def login_microsoft_account():
    AZURE_APP = microsoft_account.AzureApplication()
    Login = microsoft_account.Login(AZURE_APP=AZURE_APP)
    login_url = await Login.get_login_url()
    print(f"Please open {login_url} in your browser and copy the URL you are redirected into the prompt below.")
    code_url = input()
    code = await microsoft_account.Login.extract_code_from_url(code_url)
    auth_code = await Login.get_ms_token(code)
    print(f"Refresh token: {auth_code['refresh_token']}")
    xbl_token = await microsoft_account.Login.get_xbl_token(auth_code["access_token"])
    xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
    uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    mc_token = await microsoft_account.Login.get_minecraft_access_token(xsts_token["Token"], uhs)
    await have_minecraft(mc_token["access_token"])
    login_data = {
        "access_token": mc_token["access_token"],
        "refresh_token": auth_code["refresh_token"],
        "expires_in": auth_code["expires_in"],
        "uhs": uhs,
        "xsts_token": xsts_token["Token"],
        "xbl_token": xbl_token["Token"]
    }
    return login_data["access_token"]

if __name__ == "__main__":
    access_token = asyncio.run(login_microsoft_account())
    print(f"Access token: {access_token}")