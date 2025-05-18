# minecraft-launcher-lib
> [English version see README.md](./README.md)

[![Test](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/test.yml/badge.svg)](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/test.yml)
[![Build Python Package](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/uv_build.yaml/badge.svg)](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/uv_build.yaml)

> 本專案為 [JakobDev/minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib) 的 fork。

一個用於自訂 Minecraft 啟動器的 Python 函式庫，支援安裝、執行 Minecraft 及與 Mojang/Microsoft 帳號互動。

## 特色

- 簡單安裝
- 取得執行 Minecraft 的指令
- 支援 Microsoft 帳號登入
- 支援 [Forge](https://minecraftforge.net)、[Fabric](https://fabricmc.net)、[Quilt](https://quiltmc.org) 及 Liteloader
- 支援 alpha/beta 等舊版本
- 所有函式皆有型別註解與說明
- 僅依賴 [requests](https://pypi.org/project/requests)
- 支援 [PyPy](https://www.pypy.org)
- 完整線上文件與教學
- 支援 Vanilla 啟動器的 profiles 讀寫
- 支援 [mrpack modpacks](https://docs.modrinth.com/docs/modpacks/format_definition)
- 所有公開 API 皆為靜態型別
- 範例豐富
- 開源

## 安裝

使用 pip：
```bash
pip install minecraft-launcher-lib
```

或使用 uv（推薦，速度更快）：
```bash
uv pip install minecraft-launcher-lib
```

## Microsoft 帳號登入範例

```python
import logging
from launcher_core import microsoft_account
import asyncio
from launcher_core.setting import setup_logger
from launcher_core.mojang import have_minecraft

logger = setup_logger(enable_console=False, level=logging.INFO, filename="microsoft_account.log")

async def login_microsoft_account():
    AZURE_APP = microsoft_account.AzureApplication()
    Login = microsoft_account.Login(azure_app=AZURE_APP)
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
```

## 文件與更多範例

- [線上文件](https://minecraft-launcher-lib.readthedocs.io)
- [更多範例](https://codeberg.org/JakobDev/minecraft-launcher-lib/src/branch/master/examples)

## Fork 與原專案（[JakobDev/minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib)）差異對比

| 功能/設計                | 本 Fork 版                                             | JakobDev 原版                                      |
|--------------------------|-------------------------------------------------------|----------------------------------------------------|
| Python 版本支援          | 3.10 以上，型別註解更完整                              | 3.7+，部分型別註解                                 |
| 日誌系統                 | 內建 `setup_logger`，可自訂檔案與 console 輸出         | 無內建日誌系統，需自行設計                         |
| Microsoft 登入流程       | 範例與 API 皆支援 async/await，流程更現代化             | 傳統同步/非同步混用                                |
| 依賴                     | aiofiles、aiohttp、requests、requests-mock             | requests                                           |
| 測試覆蓋                 | 增加 requests-mock，方便單元測試                       | 測試較少                                           |
| 文件                     | 中文為主，說明更貼近台灣/華語圈開發者                   | 英文為主                                           |
| 開發分支策略             | main/dev 分支自動同步（GitHub Actions）                | 單一主分支                                         |
| 版本管理                 | 版本號動態讀取自 `version.txt`                         | setup.py 內手動維護                                |
| 其他                     | 針對 async/await 與型別註解最佳化                      | 著重於廣泛相容性                                   |

> 歡迎參考原專案與本 fork 版，選擇最適合自己需求的版本！

> 歡迎參考原專案與本 fork 版，選擇最適合自己需求的版本！

## 貢獻

歡迎 PR 與 Issue！

## 致謝

感謝 [tomsik68](https://github.com/tomsik68/mclauncher-api/wiki) 對 Minecraft 啟動器原理的整理。

感謝 [JakobDev](https://github.com/JakobDev) 的代碼(BSD-2)