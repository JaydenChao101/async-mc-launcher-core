# 快速開始

本指南將引導您完成 async-mc-launcher-core 的基本設置和使用，讓您快速上手這個強大的 Minecraft 啟動器函式庫。

## 🚀 第一個程式

讓我們從一個簡單的示例開始，展示如何使用 async-mc-launcher-core：

```python
import asyncio
from launcher_core import utils
from launcher_core.setting import setup_logger

async def main():
    # 設置日誌
    logger = setup_logger(enable_console=True)
    logger.info("歡迎使用 async-mc-launcher-core!")
    
    # 獲取 Minecraft 目錄
    minecraft_dir = utils.get_minecraft_directory()
    print(f"Minecraft 安裝目錄: {minecraft_dir}")
    
    # 獲取可用的 Minecraft 版本
    versions = await utils.get_version_list()
    print(f"可用版本數量: {len(versions)}")
    print(f"最新穩定版本: {versions[0]['id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔐 Microsoft 帳號登入流程

### 基本登入示例

以下是完整的 Microsoft 帳號登入流程：

```python
import asyncio
import logging
from launcher_core import microsoft_account
from launcher_core.setting import setup_logger
from launcher_core.mojang import have_minecraft

# 設置日誌
logger = setup_logger(enable_console=True, level=logging.INFO)

async def microsoft_login_example():
    """Microsoft 帳號登入示例"""
    try:
        # 1. 創建 Azure 應用程式實例
        azure_app = microsoft_account.AzureApplication()
        
        # 2. 創建登入實例
        login = microsoft_account.Login(azure_app=azure_app)
        
        # 3. 獲取登入 URL
        login_url = await login.get_login_url()
        print(f"請在瀏覽器中開啟以下連結進行登入:")
        print(f"{login_url}")
        print("\n登入完成後，請複製重定向的完整 URL 並貼到下方:")
        
        # 4. 用戶輸入重定向 URL
        redirect_url = input("重定向 URL: ")
        
        # 5. 從 URL 中提取授權碼
        code = await microsoft_account.Login.extract_code_from_url(redirect_url)
        
        # 6. 獲取 Microsoft Token
        auth_response = await login.get_ms_token(code)
        print(f"✅ Microsoft Token 獲取成功")
        
        # 7. 獲取 Xbox Live Token
        xbl_token = await microsoft_account.Login.get_xbl_token(
            auth_response["access_token"]
        )
        print(f"✅ Xbox Live Token 獲取成功")
        
        # 8. 獲取 XSTS Token
        xsts_token = await microsoft_account.Login.get_xsts_token(
            xbl_token["Token"]
        )
        print(f"✅ XSTS Token 獲取成功")
        
        # 9. 獲取使用者雜湊
        uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
        
        # 10. 獲取 Minecraft Access Token
        mc_token = await microsoft_account.Login.get_minecraft_access_token(
            xsts_token["Token"], uhs
        )
        print(f"✅ Minecraft Access Token 獲取成功")
        
        # 11. 驗證用戶是否擁有 Minecraft
        await have_minecraft(mc_token["access_token"])
        print(f"✅ Minecraft 所有權驗證通過")
        
        # 12. 保存登入資料
        login_data = {
            "access_token": mc_token["access_token"],
            "refresh_token": auth_response["refresh_token"],
            "expires_in": auth_response["expires_in"],
            "uhs": uhs,
            "xsts_token": xsts_token["Token"],
            "xbl_token": xbl_token["Token"]
        }
        
        print(f"🎉 登入流程完成！")
        print(f"Access Token: {login_data['access_token'][:50]}...")
        
        return login_data
        
    except Exception as e:
        logger.error(f"登入過程中發生錯誤: {e}")
        raise

if __name__ == "__main__":
    login_data = asyncio.run(microsoft_login_example())
```

### 簡化的設備代碼登入

對於無法使用瀏覽器重定向的環境，可以使用設備代碼登入：

```python
import asyncio
from launcher_core import microsoft_account

async def device_code_login_example():
    """設備代碼登入示例"""
    try:
        # 使用設備代碼登入方式
        result = await microsoft_account.device_code_login()
        
        print(f"✅ 設備代碼登入成功！")
        print(f"Access Token: {result['minecraft_access_token'][:50]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ 設備代碼登入失敗: {e}")
        raise

if __name__ == "__main__":
    result = asyncio.run(device_code_login_example())
```

## 🎮 啟動 Minecraft

獲得 Access Token 後，您可以啟動 Minecraft：

```python
import asyncio
from launcher_core import command, _types, mojang
from launcher_core.setting import setup_logger

async def launch_minecraft_example():
    """啟動 Minecraft 示例"""
    # 注意：您需要有效的 access_token
    access_token = "your_access_token_here"
    
    try:
        # 1. 獲取玩家資訊
        profile = await mojang.get_minecraft_profile(access_token)
        
        # 2. 創建憑證物件
        credential = _types.Credential(
            access_token=access_token,
            username=profile["name"],
            uuid=profile["id"]
        )
        
        # 3. 驗證 Minecraft 所有權
        await mojang.have_minecraft(access_token)
        
        # 4. 設置 Minecraft 選項
        minecraft_options = _types.MinecraftOptions(
            game_directory="./minecraft",  # Minecraft 遊戲目錄
            version="1.21.1",             # 要啟動的版本
            memory=2048,                  # 記憶體配置 (MB)
            jvm_args=["-Xmx2048M", "-Xms1024M"],  # JVM 參數
        )
        
        # 5. 生成啟動指令
        command_list = await command.get_minecraft_command(
            version="1.21.1",
            minecraft_directory="./minecraft",
            options=minecraft_options,
            Credential=credential
        )
        
        print("✅ Minecraft 啟動指令生成成功！")
        print("指令預覽:")
        print(" ".join(command_list[:5]) + " ...")
        
        return command_list
        
    except Exception as e:
        print(f"❌ 啟動 Minecraft 時發生錯誤: {e}")
        raise

if __name__ == "__main__":
    setup_logger(enable_console=True)
    command_list = asyncio.run(launch_minecraft_example())
```

## 📁 基本文件操作

### 獲取 Minecraft 資訊

```python
import asyncio
from launcher_core import utils, install

async def minecraft_info_example():
    """獲取 Minecraft 相關資訊"""
    
    # 獲取 Minecraft 預設目錄
    minecraft_dir = utils.get_minecraft_directory()
    print(f"Minecraft 目錄: {minecraft_dir}")
    
    # 獲取版本清單
    versions = await utils.get_version_list()
    print(f"總共 {len(versions)} 個版本可用")
    
    # 顯示最新的 5 個版本
    print("\n最新版本:")
    for version in versions[:5]:
        print(f"  - {version['id']} ({version['type']})")
    
    # 檢查特定版本是否已安裝
    version_id = "1.21.1"
    is_installed = install.is_version_installed(version_id, minecraft_dir)
    print(f"\n版本 {version_id} 是否已安裝: {is_installed}")

if __name__ == "__main__":
    asyncio.run(minecraft_info_example())
```

### 安裝 Minecraft 版本

```python
import asyncio
from launcher_core import install
from launcher_core.setting import setup_logger

async def install_minecraft_example():
    """安裝 Minecraft 版本示例"""
    logger = setup_logger(enable_console=True)
    
    version_id = "1.21.1"
    minecraft_dir = "./minecraft"
    
    try:
        # 安裝指定版本
        await install.install_minecraft_version(
            version_id, 
            minecraft_dir
        )
        
        print(f"✅ Minecraft {version_id} 安裝成功！")
        
    except Exception as e:
        logger.error(f"安裝過程中發生錯誤: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(install_minecraft_example())
```

## 🛠️ 基本配置

### 設置日誌系統

```python
from launcher_core.setting import setup_logger
import logging

# 基本日誌設置
logger = setup_logger(
    enable_console=True,        # 啟用控制台輸出
    level=logging.INFO,         # 日誌級別
    filename="launcher.log"     # 日誌文件名
)

logger.info("這是一條資訊日誌")
logger.warning("這是一條警告日誌")
logger.error("這是一條錯誤日誌")
```

### 讀取和寫入 TOML 配置

```python
import asyncio
from launcher_core.config import read_toml_file, write_toml_file

async def config_example():
    """配置文件操作示例"""
    
    # 創建配置數據
    config_data = {
        "launcher": {
            "name": "我的啟動器",
            "version": "1.0.0",
            "memory": 2048
        },
        "minecraft": {
            "directory": "./minecraft",
            "version": "1.21.1"
        }
    }
    
    # 寫入配置文件
    await write_toml_file("config.toml", config_data)
    print("✅ 配置文件寫入成功")
    
    # 讀取配置文件
    loaded_config = await read_toml_file("config.toml")
    print(f"✅ 配置文件讀取成功")
    print(f"啟動器名稱: {loaded_config['launcher']['name']}")

if __name__ == "__main__":
    asyncio.run(config_example())
```

## 🎯 下一步

現在您已經掌握了基本用法，可以探索更多功能：

1. **[Microsoft 認證詳解](Microsoft-Authentication.md)** - 深入了解認證流程
2. **[API 參考](API-Reference.md)** - 查看所有可用的 API
3. **[高級示例](Advanced-Examples.md)** - 學習更複雜的使用場景
4. **[模組支持](Modding-Support.md)** - 了解如何安裝和管理模組

## ⚠️ 重要注意事項

1. **Access Token 安全性**: 請妥善保管您的 Access Token，不要在公開場所洩露
2. **Token 過期**: Access Token 有時效性，需要定期刷新
3. **異步編程**: 本函式庫基於 asyncio，確保在異步環境中使用
4. **錯誤處理**: 網路操作可能失敗，請適當處理異常

---

如果您在使用過程中遇到問題，請查看 [故障排除指南](Troubleshooting.md) 或瀏覽我們的 [範例代碼](https://github.com/JaydenChao101/async-mc-launcher-core/tree/main/examples)。