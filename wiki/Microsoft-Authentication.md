# Microsoft 認證

本指南詳細介紹 async-mc-launcher-core 中的 Microsoft 帳號認證流程，包括兩種主要的登入方式、Token 管理、錯誤處理和最佳實踐。

## 🔐 認證流程概述

Microsoft 認證流程包含以下步驟：

1. **Microsoft OAuth2 認證** - 獲取 Microsoft Access Token
2. **Xbox Live 認證** - 將 Microsoft Token 轉換為 Xbox Live Token
3. **XSTS 認證** - 獲取 Xbox Security Token Service Token
4. **Minecraft 認證** - 最終獲取 Minecraft Access Token

## 🚀 方式一：標準瀏覽器登入流程

### 基本流程

```python
import asyncio
import logging
from launcher_core import microsoft_account
from launcher_core.setting import setup_logger
from launcher_core.mojang import have_minecraft, get_minecraft_profile

# 設置日誌
logger = setup_logger(enable_console=True, level=logging.INFO)

async def browser_login_flow():
    """標準瀏覽器登入流程"""
    try:
        # 1. 創建 Azure 應用程式配置
        azure_app = microsoft_account.AzureApplication()
        # 使用預設設定，或自訂 client_id
        # azure_app = microsoft_account.AzureApplication(
        #     client_id="your-client-id"
        # )
        
        # 2. 創建登入實例
        login = microsoft_account.Login(azure_app=azure_app)
        
        # 3. 獲取登入 URL
        login_url = await login.get_login_url()
        print("=" * 60)
        print("請在瀏覽器中開啟以下連結進行登入：")
        print(f"{login_url}")
        print("=" * 60)
        print("登入完成後，您會被重定向到一個新頁面。")
        print("請複製該頁面的完整 URL 並貼到下方：")
        
        # 4. 用戶輸入重定向 URL
        redirect_url = input("\n重定向 URL: ").strip()
        
        # 5. 提取授權碼
        code = await microsoft_account.Login.extract_code_from_url(redirect_url)
        logger.info("✅ 授權碼提取成功")
        
        # 6. 獲取 Microsoft Token
        auth_response = await login.get_ms_token(code)
        logger.info("✅ Microsoft Access Token 獲取成功")
        
        # 7. 獲取 Xbox Live Token
        xbl_token = await microsoft_account.Login.get_xbl_token(
            auth_response["access_token"]
        )
        logger.info("✅ Xbox Live Token 獲取成功")
        
        # 8. 獲取 XSTS Token
        xsts_token = await microsoft_account.Login.get_xsts_token(
            xbl_token["Token"]
        )
        logger.info("✅ XSTS Token 獲取成功")
        
        # 9. 提取使用者雜湊
        uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
        
        # 10. 獲取 Minecraft Access Token
        mc_token = await microsoft_account.Login.get_minecraft_access_token(
            xsts_token["Token"], uhs
        )
        logger.info("✅ Minecraft Access Token 獲取成功")
        
        # 11. 驗證 Minecraft 所有權
        await have_minecraft(mc_token["access_token"])
        logger.info("✅ Minecraft 所有權驗證通過")
        
        # 12. 獲取玩家資訊
        profile = await get_minecraft_profile(mc_token["access_token"])
        logger.info(f"✅ 玩家資訊: {profile['name']} ({profile['id']})")
        
        # 13. 整理登入資料
        login_data = {
            "access_token": mc_token["access_token"],
            "refresh_token": auth_response["refresh_token"],
            "expires_in": auth_response["expires_in"],
            "uhs": uhs,
            "xsts_token": xsts_token["Token"],
            "xbl_token": xbl_token["Token"],
            "player_name": profile["name"],
            "player_uuid": profile["id"]
        }
        
        print("\n🎉 Microsoft 帳號登入完成！")
        print(f"玩家名稱: {login_data['player_name']}")
        print(f"Access Token: {login_data['access_token'][:50]}...")
        
        return login_data
        
    except Exception as e:
        logger.error(f"❌ 登入過程中發生錯誤: {e}")
        raise

if __name__ == "__main__":
    login_data = asyncio.run(browser_login_flow())
```

### 自動保存登入資料

```python
import json
import asyncio
from datetime import datetime, timedelta

async def save_login_data(login_data: dict, filename: str = "minecraft_auth.json"):
    """保存登入資料到文件"""
    # 添加過期時間
    expires_at = datetime.now() + timedelta(seconds=login_data["expires_in"])
    login_data["expires_at"] = expires_at.isoformat()
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(login_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 登入資料已保存到 {filename}")

async def load_login_data(filename: str = "minecraft_auth.json") -> dict | None:
    """從文件載入登入資料"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 檢查是否過期
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() > expires_at:
            print("⚠️ 保存的 Token 已過期")
            return None
        
        print("✅ 登入資料載入成功")
        return data
        
    except FileNotFoundError:
        print("ℹ️ 找不到保存的登入資料")
        return None
    except Exception as e:
        print(f"❌ 載入登入資料時發生錯誤: {e}")
        return None
```

## 📱 方式二：設備代碼登入（推薦）

設備代碼登入適用於無法直接使用瀏覽器重定向的環境，如伺服器、腳本等。

### 基本設備代碼登入

```python
import asyncio
from launcher_core import microsoft_account
from launcher_core.setting import setup_logger

async def device_code_login_flow():
    """設備代碼登入流程"""
    logger = setup_logger(enable_console=True)
    
    try:
        # 使用內建的設備代碼登入功能
        result = await microsoft_account.device_code_login()
        
        print("🎉 設備代碼登入成功！")
        print(f"玩家名稱: {result['player_name']}")
        print(f"玩家 UUID: {result['player_uuid']}")
        print(f"Access Token: {result['minecraft_access_token'][:50]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 設備代碼登入失敗: {e}")
        raise

if __name__ == "__main__":
    result = asyncio.run(device_code_login_flow())
```

### 自訂設備代碼登入

```python
import asyncio
from launcher_core.microsoft_account import device_code_login, Login
from launcher_core import AzureApplication

async def custom_device_code_flow(client_id: str = None, language: str = "zh-Hant"):
    """自訂設備代碼登入流程"""
    try:
        # 1. 建立 Azure 應用程式配置
        if client_id:
            azure_app = AzureApplication(client_id=client_id)
        else:
            azure_app = AzureApplication()  # 使用預設
        
        # 2. 建立設備代碼登入實例
        login = device_code_login(azure_app, language)
        # 支援的語言: "zh-Hant" (繁體中文), "zh-Hans" (簡體中文), "en" (英文)
        
        # 3. 獲取設備代碼
        code_info = await login.get_device_code()
        print("=" * 60)
        print(code_info["message"])  # 顯示操作指示
        print("=" * 60)
        
        # 4. 輪詢授權狀態
        print("正在等待授權完成...")
        token_info = await login.poll_device_code(
            code_info["device_code"],
            code_info["interval"],
            code_info["expires_in"]
        )
        
        if token_info is None:
            print("❌ 授權失敗或超時")
            return None
        
        print("✅ Microsoft 授權成功")
        
        # 5. 獲取 Xbox Live Token
        xbl_token = await Login.get_xbl_token(token_info["access_token"])
        print("✅ Xbox Live Token 獲取成功")
        
        # 6. 獲取 XSTS Token
        xsts_token = await Login.get_xsts_token(xbl_token["Token"])
        print("✅ XSTS Token 獲取成功")
        
        # 7. 獲取 Minecraft Access Token
        minecraft_token = await Login.get_minecraft_access_token(
            xsts_token["Token"],
            xbl_token["DisplayClaims"]["xui"][0]["uhs"]
        )
        print("✅ Minecraft Access Token 獲取成功")
        
        # 8. 整理完整的登入資料
        login_data = {
            "access_token": minecraft_token["access_token"],
            "refresh_token": token_info["refresh_token"],
            "expires_in": token_info["expires_in"],
            "uhs": xbl_token["DisplayClaims"]["xui"][0]["uhs"],
            "xsts_token": xsts_token["Token"],
            "xbl_token": xbl_token["Token"]
        }
        
        print("🎉 設備代碼登入流程完成！")
        return login_data
        
    except Exception as e:
        print(f"❌ 設備代碼登入過程中發生錯誤: {e}")
        raise

if __name__ == "__main__":
    # 使用預設設定
    result = asyncio.run(custom_device_code_flow())
    
    # 或使用自訂 client_id
    # client_id = input("請輸入你的 Azure 應用程式 client_id: ")
    # result = asyncio.run(custom_device_code_flow(client_id))
```

## 🔄 Token 刷新機制

Access Token 有時效性（通常 1 小時），需要定期刷新。

### 自動刷新 Token

```python
import asyncio
from datetime import datetime, timedelta
from launcher_core import microsoft_account

async def refresh_token_example(refresh_token: str):
    """刷新 Access Token 示例"""
    try:
        # 使用 refresh_token 獲取新的 tokens
        new_tokens = await microsoft_account.refresh_minecraft_token(refresh_token)
        
        print("✅ Token 刷新成功")
        print(f"新的 Access Token: {new_tokens['minecraft_access_token'][:50]}...")
        print(f"新的 Refresh Token: {new_tokens['refresh_token'][:50]}...")
        
        return new_tokens
        
    except Exception as e:
        print(f"❌ Token 刷新失敗: {e}")
        raise

async def smart_token_manager(login_data: dict):
    """智能 Token 管理器"""
    # 檢查 Token 是否即將過期（剩餘時間少於 10 分鐘）
    if "expires_at" in login_data:
        expires_at = datetime.fromisoformat(login_data["expires_at"])
        time_left = expires_at - datetime.now()
        
        if time_left.total_seconds() < 600:  # 少於 10 分鐘
            print("⚠️ Access Token 即將過期，正在刷新...")
            new_tokens = await refresh_token_example(login_data["refresh_token"])
            
            # 更新登入資料
            login_data.update(new_tokens)
            login_data["expires_at"] = (
                datetime.now() + timedelta(seconds=new_tokens["expires_in"])
            ).isoformat()
            
            return login_data
    
    print("✅ Token 仍然有效")
    return login_data
```

## 🛡️ 錯誤處理

### 常見錯誤和處理方式

```python
import asyncio
from launcher_core import microsoft_account
from launcher_core.exceptions import (
    AccountBanFromXbox,
    AccountNeedAdultVerification,
    AccountNotHaveXbox,
    XboxLiveNotAvailable,
    DeviceCodeExpiredError
)

async def robust_login_with_error_handling():
    """包含完整錯誤處理的登入流程"""
    try:
        result = await microsoft_account.device_code_login()
        return result
        
    except AccountBanFromXbox:
        print("❌ 您的 Xbox 帳號已被封禁，無法使用 Minecraft")
        
    except AccountNeedAdultVerification:
        print("❌ 您的帳號需要成人驗證才能使用 Minecraft")
        print("請前往 Xbox 官網完成驗證：https://account.xbox.com/")
        
    except AccountNotHaveXbox:
        print("❌ 您的 Microsoft 帳號沒有 Xbox 資格")
        print("請前往 Xbox 官網註冊：https://www.xbox.com/")
        
    except XboxLiveNotAvailable:
        print("❌ Xbox Live 服務目前不可用，請稍後再試")
        
    except DeviceCodeExpiredError:
        print("❌ 設備代碼已過期，請重新開始登入流程")
        
    except Exception as e:
        print(f"❌ 發生未知錯誤: {e}")
        
    return None
```

### 網路錯誤處理

```python
import asyncio
import aiohttp
from launcher_core import microsoft_account

async def login_with_retry(max_retries: int = 3):
    """帶重試機制的登入流程"""
    for attempt in range(max_retries):
        try:
            result = await microsoft_account.device_code_login()
            return result
            
        except aiohttp.ClientError as e:
            print(f"⚠️ 網路錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指數退避
            else:
                print("❌ 網路連接失敗，請檢查您的網路設定")
                raise
                
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
            raise
    
    return None
```

## 🔧 Azure 應用程式配置

### 使用自訂 Azure 應用程式

如果您想使用自己的 Azure 應用程式（推薦用於生產環境）：

```python
from launcher_core import AzureApplication

# 自訂 Azure 應用程式配置
custom_azure_app = AzureApplication(
    client_id="your-client-id-here",
    redirect_url="https://login.microsoftonline.com/common/oauth2/nativeclient"
)

# 在登入時使用
login = microsoft_account.Login(azure_app=custom_azure_app)
```

### 創建 Azure 應用程式

1. 前往 [Azure Portal](https://portal.azure.com/)
2. 導航到「Azure Active Directory」→「應用程式註冊」
3. 點擊「新增註冊」
4. 設定應用程式：
   - 名稱：您的啟動器名稱
   - 支援的帳戶類型：任何組織目錄中的帳戶和個人 Microsoft 帳戶
   - 重定向 URI：選擇「公用用戶端」，輸入 `https://login.microsoftonline.com/common/oauth2/nativeclient`
5. 記下「應用程式 (用戶端) ID」

## 📊 完整的認證管理類

```python
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from launcher_core import microsoft_account
from launcher_core.setting import setup_logger

class MinecraftAuthManager:
    """Minecraft 認證管理器"""
    
    def __init__(self, auth_file: str = "minecraft_auth.json"):
        self.auth_file = Path(auth_file)
        self.logger = setup_logger(enable_console=True)
        self.login_data = None
    
    async def login(self, use_device_code: bool = True) -> dict:
        """執行登入流程"""
        try:
            if use_device_code:
                self.login_data = await microsoft_account.device_code_login()
            else:
                # 使用瀏覽器登入流程
                azure_app = microsoft_account.AzureApplication()
                login = microsoft_account.Login(azure_app=azure_app)
                # ... 瀏覽器登入邏輯
            
            await self.save_auth_data()
            self.logger.info("✅ 登入成功並已保存")
            return self.login_data
            
        except Exception as e:
            self.logger.error(f"❌ 登入失敗: {e}")
            raise
    
    async def load_auth_data(self) -> bool:
        """載入保存的認證資料"""
        try:
            if not self.auth_file.exists():
                return False
            
            with open(self.auth_file, "r", encoding="utf-8") as f:
                self.login_data = json.load(f)
            
            # 檢查是否過期
            if "expires_at" in self.login_data:
                expires_at = datetime.fromisoformat(self.login_data["expires_at"])
                if datetime.now() > expires_at:
                    self.logger.warning("⚠️ 保存的認證已過期")
                    return False
            
            self.logger.info("✅ 認證資料載入成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 載入認證資料失敗: {e}")
            return False
    
    async def save_auth_data(self):
        """保存認證資料"""
        if not self.login_data:
            return
        
        # 添加過期時間
        if "expires_in" in self.login_data:
            expires_at = datetime.now() + timedelta(
                seconds=self.login_data["expires_in"]
            )
            self.login_data["expires_at"] = expires_at.isoformat()
        
        with open(self.auth_file, "w", encoding="utf-8") as f:
            json.dump(self.login_data, f, indent=2, ensure_ascii=False)
    
    async def refresh_if_needed(self) -> bool:
        """如果需要則刷新 Token"""
        if not self.login_data:
            return False
        
        # 檢查是否需要刷新（剩餘時間少於 10 分鐘）
        if "expires_at" in self.login_data:
            expires_at = datetime.fromisoformat(self.login_data["expires_at"])
            time_left = expires_at - datetime.now()
            
            if time_left.total_seconds() < 600:
                try:
                    self.logger.info("🔄 正在刷新 Access Token...")
                    new_tokens = await microsoft_account.refresh_minecraft_token(
                        self.login_data["refresh_token"]
                    )
                    
                    self.login_data.update(new_tokens)
                    await self.save_auth_data()
                    self.logger.info("✅ Token 刷新成功")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"❌ Token 刷新失敗: {e}")
                    return False
        
        return True
    
    async def get_valid_token(self) -> str:
        """獲取有效的 Access Token"""
        # 嘗試載入保存的認證
        if not await self.load_auth_data():
            # 如果沒有有效認證，執行登入
            await self.login()
        
        # 檢查並刷新 Token
        if not await self.refresh_if_needed():
            # 如果刷新失敗，重新登入
            await self.login()
        
        return self.login_data["minecraft_access_token"]

# 使用範例
async def main():
    auth_manager = MinecraftAuthManager()
    
    try:
        access_token = await auth_manager.get_valid_token()
        print(f"✅ 獲取到有效的 Access Token: {access_token[:50]}...")
        
    except Exception as e:
        print(f"❌ 認證失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔒 安全最佳實踐

### 1. Token 安全存儲

```python
import base64
import os
from cryptography.fernet import Fernet

class SecureAuthStorage:
    """安全的認證資料存儲"""
    
    def __init__(self, key_file: str = "auth.key"):
        self.key_file = key_file
        self.cipher = self._get_or_create_key()
    
    def _get_or_create_key(self):
        """獲取或創建加密金鑰"""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # 限制檔案權限
        
        return Fernet(key)
    
    def save_auth_data(self, data: dict, filename: str):
        """加密保存認證資料"""
        json_data = json.dumps(data).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        
        with open(filename, "wb") as f:
            f.write(encrypted_data)
        
        os.chmod(filename, 0o600)  # 限制檔案權限
    
    def load_auth_data(self, filename: str) -> dict:
        """載入並解密認證資料"""
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
```

### 2. 環境變數管理

```python
import os
from dotenv import load_dotenv

# 從 .env 文件載入環境變數
load_dotenv()

# 敏感資訊使用環境變數
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
REDIRECT_URL = os.getenv("AZURE_REDIRECT_URL")

if CLIENT_ID:
    azure_app = microsoft_account.AzureApplication(
        client_id=CLIENT_ID,
        redirect_url=REDIRECT_URL
    )
```

### 3. Token 驗證

```python
from launcher_core.mojang import have_minecraft, get_minecraft_profile

async def validate_token(access_token: str) -> bool:
    """驗證 Access Token 是否有效"""
    try:
        await have_minecraft(access_token)
        profile = await get_minecraft_profile(access_token)
        print(f"✅ Token 有效，玩家: {profile['name']}")
        return True
    except Exception as e:
        print(f"❌ Token 無效: {e}")
        return False
```

## ⚠️ 注意事項

1. **Token 過期時間**：Access Token 通常 1 小時過期，Refresh Token 可能幾個月過期
2. **網路依賴**：認證過程需要穩定的網路連接
3. **錯誤處理**：應妥善處理各種認證錯誤
4. **安全存儲**：不要在程式碼中硬編碼敏感資訊
5. **使用者體驗**：提供清楚的操作指示和錯誤訊息

## 📚 相關文檔

- [API 參考 - microsoft_account](API-Reference.md#microsoft_account)
- [快速開始 - Microsoft 登入](Quick-Start.md#🔐-microsoft-帳號登入流程)
- [故障排除 - 認證問題](Troubleshooting.md#microsoft-認證問題)

---

通過本指南，您應該能夠在您的應用程式中實現完整且安全的 Microsoft 帳號認證流程。如有任何問題，請參考相關文檔或提交 Issue。