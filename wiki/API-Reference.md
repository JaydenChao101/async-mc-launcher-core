# API 參考

本文檔提供 async-mc-launcher-core 的完整 API 參考，包含所有模組、函數、類別和類型定義。

## 📦 模組總覽

async-mc-launcher-core 包含以下主要模組：

- **[microsoft_account](#microsoft_account)** - Microsoft 帳號認證
- **[command](#command)** - Minecraft 啟動指令生成
- **[install](#install)** - Minecraft 版本和資源安裝
- **[utils](#utils)** - 實用工具函數
- **[forge](#forge)** - Minecraft Forge 支援
- **[fabric](#fabric)** - Fabric 模組載入器支援  
- **[quilt](#quilt)** - Quilt 模組載入器支援
- **[mojang](#mojang)** - Mojang API 互動
- **[java_utils](#java_utils)** - Java 環境管理
- **[config](#config)** - 配置文件管理
- **[_types](#_types)** - 類型定義

---

## microsoft_account

Microsoft 帳號認證相關功能。

### 類別

#### `AzureApplication`
```python
class AzureApplication:
    client_id: str = "54fd49e4-2103-4044-9603-2b028c814ec3"
    redirect_url: str = "https://login.microsoftonline.com/common/oauth2/nativeclient"
```

Azure 應用程式配置，用於 Microsoft 帳號認證。

#### `Login`
```python
class Login:
    def __init__(self, azure_app: AzureApplication)
```

Microsoft 帳號登入處理器。

**方法：**

##### `get_login_url() -> str`
```python
async def get_login_url() -> str
```
獲取 Microsoft 登入 URL。

**返回值：** 登入 URL 字串

**範例：**
```python
azure_app = microsoft_account.AzureApplication()
login = microsoft_account.Login(azure_app)
login_url = await login.get_login_url()
```

##### `extract_code_from_url(url: str) -> str`
```python
@staticmethod
async def extract_code_from_url(url: str) -> str
```
從重定向 URL 中提取授權碼。

**參數：**
- `url`: 重定向後的完整 URL

**返回值：** 授權碼字串

##### `get_ms_token(code: str) -> AuthorizationTokenResponse`
```python
async def get_ms_token(code: str) -> AuthorizationTokenResponse
```
使用授權碼獲取 Microsoft Access Token。

**參數：**
- `code`: 從 URL 提取的授權碼

**返回值：** 包含 access_token 和 refresh_token 的字典

##### `get_xbl_token(access_token: str) -> XBLResponse`
```python
@staticmethod
async def get_xbl_token(access_token: str) -> XBLResponse
```
獲取 Xbox Live Token。

**參數：**
- `access_token`: Microsoft Access Token

**返回值：** Xbox Live Token 響應

##### `get_xsts_token(xbl_token: str) -> XSTSResponse`
```python
@staticmethod
async def get_xsts_token(xbl_token: str) -> XSTSResponse
```
獲取 XSTS Token。

**參數：**
- `xbl_token`: Xbox Live Token

**返回值：** XSTS Token 響應

##### `get_minecraft_access_token(xsts_token: str, uhs: str) -> MinecraftAuthenticateResponse`
```python
@staticmethod
async def get_minecraft_access_token(xsts_token: str, uhs: str) -> MinecraftAuthenticateResponse
```
獲取 Minecraft Access Token。

**參數：**
- `xsts_token`: XSTS Token
- `uhs`: 使用者雜湊

**返回值：** Minecraft 認證響應

### 函數

#### `device_code_login() -> dict`
```python
async def device_code_login() -> dict
```
使用設備代碼進行 Microsoft 帳號登入。

**返回值：** 包含完整認證資訊的字典

**範例：**
```python
login_data = await microsoft_account.device_code_login()
access_token = login_data['minecraft_access_token']
```

#### `refresh_minecraft_token(refresh_token: str) -> dict`
```python
async def refresh_minecraft_token(refresh_token: str) -> dict
```
刷新 Minecraft Access Token。

**參數：**
- `refresh_token`: 刷新令牌

**返回值：** 新的認證資訊

---

## command

Minecraft 啟動指令生成相關功能。

### 函數

#### `get_minecraft_command()`
```python
async def get_minecraft_command(
    version: str,
    minecraft_directory: str | os.PathLike,
    options: MinecraftOptions,
    Credential: Credential | None = None
) -> list[str]
```
生成 Minecraft 啟動指令。

**參數：**
- `version`: Minecraft 版本 ID
- `minecraft_directory`: Minecraft 安裝目錄
- `options`: 啟動選項配置
- `Credential`: 玩家認證資訊（可選）

**返回值：** 啟動指令列表

**範例：**
```python
credential = _types.Credential(
    access_token="token",
    username="player",
    uuid="uuid"
)

options = _types.MinecraftOptions(
    game_directory="./minecraft",
    memory=2048,
    jvm_args=["-Xmx2048M"]
)

cmd = await command.get_minecraft_command(
    "1.21.1",
    "./minecraft", 
    options,
    Credential=credential
)
```

---

## install

Minecraft 版本和資源安裝功能。

### 函數

#### `install_minecraft_version()`
```python
async def install_minecraft_version(
    version: str,
    minecraft_directory: str | os.PathLike,
    callback: CallbackDict | None = None,
    max_workers: int | None = None
) -> None
```
安裝指定的 Minecraft 版本。

**參數：**
- `version`: 要安裝的版本 ID
- `minecraft_directory`: Minecraft 安裝目錄  
- `callback`: 進度回調函數（可選）
- `max_workers`: 最大並發下載數（可選）

**範例：**
```python
def progress_callback(progress):
    print(f"安裝進度: {progress}%")

callback = {
    "setProgress": progress_callback,
    "setStatus": lambda status: print(f"狀態: {status}")
}

await install.install_minecraft_version(
    "1.21.1",
    "./minecraft",
    callback=callback
)
```

#### `is_version_installed()`
```python
def is_version_installed(
    version: str, 
    minecraft_directory: str | os.PathLike
) -> bool
```
檢查指定版本是否已安裝。

**參數：**
- `version`: 版本 ID
- `minecraft_directory`: Minecraft 目錄

**返回值：** 是否已安裝

---

## utils

實用工具函數。

### 函數

#### `get_minecraft_directory()`
```python
def get_minecraft_directory() -> str
```
獲取 Minecraft 的預設安裝目錄。

**返回值：** Minecraft 目錄路徑

#### `get_version_list()`
```python
async def get_version_list() -> list[MinecraftVersionInfo]
```
獲取所有可用的 Minecraft 版本列表。

**返回值：** 版本資訊列表

**範例：**
```python
versions = await utils.get_version_list()
for version in versions[:5]:
    print(f"{version['id']} - {version['type']}")
```

#### `sync()`
```python
def sync(func: Callable) -> Callable
```
將異步函數轉換為同步函數的裝飾器。

**參數：**
- `func`: 要轉換的異步函數

**返回值：** 同步版本的函數

---

## fabric

Fabric 模組載入器支援。

### 函數

#### `get_all_minecraft_versions()`
```python
async def get_all_minecraft_versions() -> list[FabricMinecraftVersion]
```
獲取所有支援 Fabric 的 Minecraft 版本。

#### `get_stable_minecraft_versions()`
```python
async def get_stable_minecraft_versions() -> list[str]
```
獲取支援 Fabric 的穩定版本列表。

#### `is_minecraft_version_supported()`
```python
async def is_minecraft_version_supported(version: str) -> bool
```
檢查指定版本是否支援 Fabric。

#### `get_all_loader_versions()`
```python
async def get_all_loader_versions() -> list[FabricLoader]
```
獲取所有可用的 Fabric 載入器版本。

#### `get_latest_loader_version()`
```python
async def get_latest_loader_version() -> str
```
獲取最新的 Fabric 載入器版本。

#### `install_fabric()`
```python
async def install_fabric(
    minecraft_version: str,
    minecraft_directory: str | os.PathLike,
    loader_version: str | None = None,
    callback: CallbackDict | None = None
) -> None
```
安裝 Fabric 載入器。

**參數：**
- `minecraft_version`: Minecraft 版本
- `minecraft_directory`: 安裝目錄
- `loader_version`: Fabric 載入器版本（可選，預設使用最新版）
- `callback`: 進度回調（可選）

**範例：**
```python
await fabric.install_fabric(
    "1.21.1",
    "./minecraft",
    loader_version="0.16.5"
)
```

---

## forge

Minecraft Forge 支援。

### 函數

#### `list_forge_versions()`
```python
async def list_forge_versions(minecraft_version: str) -> list[str]
```
列出指定 Minecraft 版本可用的 Forge 版本。

#### `install_forge_version()`
```python
async def install_forge_version(
    version: str,
    minecraft_directory: str | os.PathLike,
    callback: CallbackDict | None = None
) -> None
```
安裝指定的 Forge 版本。

---

## quilt

Quilt 模組載入器支援。

### 函數

#### `get_all_minecraft_versions()`
```python
async def get_all_minecraft_versions() -> list[QuiltMinecraftVersion]
```
獲取所有支援 Quilt 的 Minecraft 版本。

#### `install_quilt()`
```python
async def install_quilt(
    minecraft_version: str,
    minecraft_directory: str | os.PathLike,
    loader_version: str | None = None,
    callback: CallbackDict | None = None
) -> None
```
安裝 Quilt 載入器。

---

## mojang

Mojang API 互動功能。

### 函數

#### `have_minecraft()`
```python
async def have_minecraft(access_token: str, check: bool = True) -> bool
```
檢查用戶是否擁有 Minecraft。

**參數：**
- `access_token`: Minecraft Access Token
- `check`: 是否進行檢查（預設 True）

**返回值：** 是否擁有 Minecraft

#### `get_minecraft_profile()`
```python
async def get_minecraft_profile(access_token: str) -> MinecraftProfileResponse
```
獲取 Minecraft 玩家檔案。

**參數：**
- `access_token`: Minecraft Access Token

**返回值：** 玩家檔案資訊

**範例：**
```python
profile = await mojang.get_minecraft_profile(access_token)
print(f"玩家名稱: {profile['name']}")
print(f"玩家 UUID: {profile['id']}")
```

---

## java_utils

Java 環境管理功能。

### 函數

#### `get_java_information()`
```python
async def get_java_information(path: str | os.PathLike) -> JavaInformation
```
獲取指定路徑的 Java 資訊。

#### `find_system_java_versions()`
```python
async def find_system_java_versions(
    path: str | os.PathLike | None = None,
    check_others: bool = True
) -> list[str]
```
尋找系統中的 Java 版本。

---

## config

配置文件管理功能。

### 函數

#### `read_toml_file()`
```python
async def read_toml_file(path: str | os.PathLike) -> dict
```
讀取 TOML 配置文件。

#### `write_toml_file()`
```python
async def write_toml_file(path: str | os.PathLike, data: dict) -> None
```
寫入 TOML 配置文件。

---

## _types

類型定義模組，包含所有 TypedDict 和資料類別定義。

### 主要類型

#### `Credential`
```python
@dataclass
class Credential:
    access_token: str
    username: str
    uuid: str
```
玩家認證資訊。

#### `MinecraftOptions`
```python
class MinecraftOptions(TypedDict, total=False):
    username: str
    uuid: MinecraftUUID
    token: str
    executablePath: str
    jvmArguments: list[str]
    gameDirectory: str
    demo: bool
    customResolution: bool
    resolutionWidth: Union[int, str, None]
    resolutionHeight: Union[int, str, None]
    memory: int
    # ... 更多選項
```
Minecraft 啟動選項配置。

#### `CallbackDict`
```python
class CallbackDict(TypedDict, total=False):
    setStatus: Callable[[str], None]
    setProgress: Callable[[int], None]
    setMax: Callable[[int], None]
```
進度回調函數定義。

#### `MinecraftVersionInfo`
```python
class MinecraftVersionInfo(TypedDict):
    id: str
    type: str
    releaseTime: datetime.datetime
    complianceLevel: int
```
Minecraft 版本資訊。

#### `FabricLoader`
```python
class FabricLoader(TypedDict):
    separator: str
    build: int
    maven: str
    version: str
    stable: bool
```
Fabric 載入器資訊。

---

## 異常類別

### microsoft_account 相關異常

- `AccountBanFromXbox` - Xbox 帳號被封禁
- `AccountNeedAdultVerification` - 需要成人驗證
- `AccountNotHaveXbox` - 帳號沒有 Xbox 資格
- `XboxLiveNotAvailable` - Xbox Live 服務不可用
- `DeviceCodeExpiredError` - 設備代碼過期

### 通用異常

- `VersionNotFound` - 找不到指定版本
- `XErrNotFound` - 找不到指定資源

---

## 完整使用範例

### 完整的啟動器流程

```python
import asyncio
from launcher_core import microsoft_account, install, command, _types, mojang
from launcher_core.setting import setup_logger

async def complete_launcher_example():
    """完整的 Minecraft 啟動器流程"""
    
    # 1. 設置日誌
    logger = setup_logger(enable_console=True)
    
    # 2. Microsoft 帳號登入
    login_data = await microsoft_account.device_code_login()
    access_token = login_data['minecraft_access_token']
    
    # 3. 獲取玩家資訊
    profile = await mojang.get_minecraft_profile(access_token)
    
    # 4. 創建認證資訊
    credential = _types.Credential(
        access_token=access_token,
        username=profile['name'],
        uuid=profile['id']
    )
    
    # 5. 安裝 Minecraft 版本
    version = "1.21.1"
    minecraft_dir = "./minecraft"
    
    await install.install_minecraft_version(version, minecraft_dir)
    
    # 6. 配置啟動選項
    options = _types.MinecraftOptions(
        game_directory=minecraft_dir,
        memory=2048,
        jvm_args=["-Xmx2048M", "-Xms1024M"]
    )
    
    # 7. 生成啟動指令
    cmd = await command.get_minecraft_command(
        version,
        minecraft_dir,
        options,
        Credential=credential
    )
    
    # 8. 啟動 Minecraft
    import subprocess
    process = subprocess.Popen(cmd)
    
    logger.info("Minecraft 已成功啟動！")
    return process

if __name__ == "__main__":
    asyncio.run(complete_launcher_example())
```

---

## 注意事項

1. **異步編程**: 所有 API 函數都是異步的，需要使用 `await` 關鍵字
2. **錯誤處理**: 網路操作可能失敗，建議使用 try-except 處理異常
3. **類型提示**: 函式庫提供完整的類型註解，建議使用支援 TypeScript 的 IDE
4. **Token 管理**: Access Token 有時效性，需要定期刷新

更多詳細範例請參考 [範例代碼目錄](https://github.com/JaydenChao101/async-mc-launcher-core/tree/main/examples) 和 [高級示例文檔](Advanced-Examples.md)。