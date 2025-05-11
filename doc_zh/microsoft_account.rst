Microsoft 帳號驗證指南
======================

本指南說明如何使用 `microsoft_account.py` 模組來驗證 Microsoft 帳號並取得 Minecraft 的相關憑證。

前置需求
--------
- Python 3.10 或更高版本
- 已安裝 `aiohttp` 函式庫（`pip install aiohttp`）

使用步驟
--------

1. **初始化 Login 類別**

   使用 `AzureApplication` 物件建立 `Login` 類別的實例：

   ```python
   from launcher_core.microsoft_account import Login
   from launcher_core._types import AzureApplication

   AZURE_APP = AzureApplication(client_id="你的_client_id")
   login = Login(AZURE_APP=AZURE_APP)
   ```

2. **生成登入 URL**

    使用 `get_login_url` 方法生成 Microsoft 登入 URL：

    ```python
    login_url = await login.get_login_url()
    print(f"請在瀏覽器中打開此 URL: {login_url}")
    ```

3. **提取授權碼**

    登入後，複製重導向的 URL，並提取授權碼：

    ```python
    code_url = input("請貼上重導向的 URL: ")
    code = await login.extract_code_from_url(code_url)
    ```

4. **取得 Microsoft Token**

    使用 `get_ms_token` 方法取得 Microsoft Token：

    ```python
    ms_token = await login.get_ms_token(code)
    print(f"存取權杖: {ms_token['access_token']}")
    ```

5. **取得 Xbox 和 Minecraft Token**

    使用以下方法取得 Xbox 和 Minecraft 的憑證：

    ```python
    xbl_token = await login.get_xbl_token(ms_token["access_token"])
    xsts_token = await login.get_xsts_token(xbl_token["Token"])
    minecraft_token = await login.get_minecraft_access_token(
        xsts_token["Token"], xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    )
    print(f"Minecraft 存取權杖: {minecraft_token['access_token']}")
    ```