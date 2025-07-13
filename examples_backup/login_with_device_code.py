import asyncio
from launcher_core.microsoft_account import device_code_login, Login
from launcher_core import AzureApplication


async def device_code_login_flow(client_id: str):
    # 建立 device_code_login 實例
    login = device_code_login(
        AzureApplication(client_id=client_id), "zh-Hant"
    )  # zh-Hant 是繁體中文，zh-Hans 是簡體中文，en 是英文
    # 這裡可以選擇使用者的語言，預設為英文

    # 取得 device code
    code_info = await login.get_device_code()
    print(code_info["message"])  # 顯示提示訊息給使用者

    # 輪詢授權狀態
    token_info = await login.poll_device_code(
        code_info["device_code"], code_info["interval"], code_info["expires_in"]
    )
    if token_info is None:
        print("授權失敗或超時")
        return
    print(token_info["refresh_token"])  # 顯示授權結果
    # 這裡可以繼續呼叫 get_xbl_token、get_xsts_token、get_minecraft_access_token 等
    # 來獲取 Xbox Live Token、XSTS Token 和 Minecraft Access Token
    xbl_token = await Login.get_xbl_token(token_info["access_token"])
    xsts_token = await Login.get_xsts_token(xbl_token["Token"])
    minecraft_token = await Login.get_minecraft_access_token(
        xsts_token["Token"],  # xsts_token
        xsts_token["DisplayClaims"]["xui"][0]["uhs"],  # uhs
    )
    print("Minecraft Access Token:", minecraft_token["access_token"])


if __name__ == "__main__":
    client_id = input("請輸入你的 Azure 應用程式 client_id：")
    asyncio.run(device_code_login_flow(client_id))
