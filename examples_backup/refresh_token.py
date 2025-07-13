from launcher_core import microsoft_account
from launcher_core._types import AzureApplication, Credential


async def main():
    # refresh my token
    client_id = input("請輸入你的 Azure 應用程式 client_id：")
    refresh_token = input("請輸入你的 refresh token：")
    AZURE_APP = AzureApplication(client_id=client_id)
    Credential1 = Credential(refresh_token=refresh_token)
    token = await microsoft_account.refresh_minecraft_token(
        azure_app=AZURE_APP, Credential=Credential1
    )
    xbl_token = await microsoft_account.Login.get_xbl_token(token["access_token"])
    xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
    minecraft_token = await microsoft_account.Login.get_minecraft_access_token(
        xsts_token["Token"], xsts_token["DisplayClaims"]["xui"][0]["uhs"]
    )
    print("Minecraft Access Token:", minecraft_token["access_token"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
