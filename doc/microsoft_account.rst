Microsoft Account Authentication Guide
======================================

This guide explains how to use the `microsoft_account.py` module to authenticate a Microsoft account and retrieve tokens for Minecraft.

Prerequisites
-------------
- Python 3.10 or higher
- `aiohttp` library installed (`pip install aiohttp`)

Usage
-----

1. **Initialize the Login Class**

   Create an instance of the `Login` class with an `AzureApplication` object:

   ```python
   from launcher_core.microsoft_account import Login
   from launcher_core._types import AzureApplication

   AZURE_APP = AzureApplication(client_id="your_client_id")
   login = Login(AZURE_APP=AZURE_APP)
   ```

2. **Generate the Login URL**

    Use the `get_login_url` method to generate the Microsoft login URL:

    ```python
    login_url = await login.get_login_url()
    print(f"Open this URL in your browser: {login_url}")
    ```

3. **Extract the Authorization Code**

    After logging in, copy the redirect URL and extract the authorization code:

    ```python
    code_url = input("Paste the redirect URL here: ")
    code = await login.extract_code_from_url(code_url)
    ```

4. **Retrieve the Microsoft Token**
    Use the `get_ms_token` method to retrieve the Microsoft token:

    ```python
    ms_token = await login.get_ms_token(code)
    print(f"Access Token: {ms_token['access_token']}")
    ```

5. **Retrieve Xbox and Minecraft Tokens**

    Use the following methods to retrieve Xbox and Minecraft tokens:

    ```python
    xbl_token = await login.get_xbl_token(ms_token["access_token"])
    xsts_token = await login.get_xsts_token(xbl_token["Token"])
    minecraft_token = await login.get_minecraft_access_token(
        xsts_token["Token"], xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    )
    print(f"Minecraft Access Token: {minecraft_token['access_token']}")
    ```