# 遷移指南

本指南幫助您從原版 minecraft-launcher-lib 遷移到 async-mc-launcher-core，包括同步到異步的轉換、API 差異對比和實際遷移範例。

## 📋 版本差異概覽

### 主要變更

| 特性 | 原版 minecraft-launcher-lib | async-mc-launcher-core |
|-----|---------------------------|----------------------|
| **異步支援** | 不支援 | 完全基於 asyncio |
| **Python 版本** | 3.7+ | 3.10+ |
| **類型註解** | 部分 | 完整 |
| **依賴項** | requests | aiohttp, aiofiles, requests |
| **Microsoft 認證** | 同步 | 異步 |
| **日誌系統** | 無內建 | 內建 setup_logger |
| **配置管理** | 無 | TOML 配置支援 |
| **錯誤處理** | 基本 | 增強的異常類型 |

### API 命名變更

| 原版 API | async-mc-launcher-core | 說明 |
|---------|----------------------|-----|
| `minecraft_launcher_lib.install` | `launcher_core.install` | 模組名稱變更 |
| `minecraft_launcher_lib.command` | `launcher_core.command` | 模組名稱變更 |
| `minecraft_launcher_lib.utils` | `launcher_core.utils` | 模組名稱變更 |
| `get_minecraft_command()` | `await get_minecraft_command()` | 轉為異步 |
| `install_minecraft_version()` | `await install_minecraft_version()` | 轉為異步 |

## 🔄 基本遷移步驟

### 步驟 1: 更新依賴項

#### 原版安裝
```bash
pip install minecraft-launcher-lib
```

#### 新版安裝
```bash
pip install async-mc-launcher-core
# 或使用 uv (推薦)
uv pip install async-mc-launcher-core
```

### 步驟 2: 更新 import 語句

#### 原版 import
```python
import minecraft_launcher_lib as launcher
from minecraft_launcher_lib import install, command, utils
```

#### 新版 import
```python
import launcher_core as launcher
from launcher_core import install, command, utils
```

### 步驟 3: 添加異步支援

#### 原版函數呼叫
```python
def main():
    versions = utils.get_version_list()
    install.install_minecraft_version("1.21.1", "./minecraft")
    cmd = command.get_minecraft_command("1.21.1", "./minecraft", {})
```

#### 新版異步呼叫
```python
import asyncio

async def main():
    versions = await utils.get_version_list()
    await install.install_minecraft_version("1.21.1", "./minecraft")
    cmd = await command.get_minecraft_command("1.21.1", "./minecraft", {})

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 詳細遷移範例

### Microsoft 認證遷移

#### 原版同步認證
```python
import minecraft_launcher_lib as launcher

def microsoft_login():
    # 原版的 Microsoft 登入 (同步)
    login = launcher.microsoft_account.Login()
    login_url = login.get_login_url()
    print(f"請開啟: {login_url}")
    
    code_url = input("請輸入重定向 URL: ")
    code = login.extract_code_from_url(code_url)
    
    auth_response = login.get_ms_token(code)
    xbl_token = login.get_xbl_token(auth_response["access_token"])
    xsts_token = login.get_xsts_token(xbl_token["Token"])
    uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    mc_token = login.get_minecraft_access_token(xsts_token["Token"], uhs)
    
    return mc_token["access_token"]

# 使用
access_token = microsoft_login()
```

#### 新版異步認證
```python
import asyncio
from launcher_core import microsoft_account

async def microsoft_login():
    # 新版的 Microsoft 登入 (異步)
    azure_app = microsoft_account.AzureApplication()
    login = microsoft_account.Login(azure_app=azure_app)
    
    login_url = await login.get_login_url()
    print(f"請開啟: {login_url}")
    
    code_url = input("請輸入重定向 URL: ")
    code = await microsoft_account.Login.extract_code_from_url(code_url)
    
    auth_response = await login.get_ms_token(code)
    xbl_token = await microsoft_account.Login.get_xbl_token(auth_response["access_token"])
    xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
    uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    mc_token = await microsoft_account.Login.get_minecraft_access_token(xsts_token["Token"], uhs)
    
    return mc_token["access_token"]

# 使用（簡化版本）
async def simple_login():
    # 或使用簡化的設備代碼登入
    result = await microsoft_account.device_code_login()
    return result["minecraft_access_token"]

# 執行
if __name__ == "__main__":
    access_token = asyncio.run(microsoft_login())
    # 或
    access_token = asyncio.run(simple_login())
```

### 安裝流程遷移

#### 原版安裝
```python
import minecraft_launcher_lib as launcher

def install_minecraft(version, minecraft_dir):
    # 原版安裝 (同步)
    def progress_callback(status):
        print(f"狀態: {status}")
    
    callback = {
        "setStatus": progress_callback,
        "setProgress": lambda x: print(f"進度: {x}%"),
        "setMax": lambda x: None
    }
    
    launcher.install.install_minecraft_version(
        version, minecraft_dir, callback=callback
    )
    print("安裝完成")

# 使用
install_minecraft("1.21.1", "./minecraft")
```

#### 新版異步安裝
```python
import asyncio
from launcher_core import install

async def install_minecraft(version, minecraft_dir):
    # 新版安裝 (異步)
    def progress_callback(status):
        print(f"狀態: {status}")
    
    callback = {
        "setStatus": progress_callback,
        "setProgress": lambda x: print(f"進度: {x}%"),
        "setMax": lambda x: None
    }
    
    await install.install_minecraft_version(
        version, minecraft_dir, callback=callback
    )
    print("安裝完成")

# 使用
if __name__ == "__main__":
    asyncio.run(install_minecraft("1.21.1", "./minecraft"))
```

### 啟動指令生成遷移

#### 原版指令生成
```python
import minecraft_launcher_lib as launcher

def generate_launch_command():
    # 原版指令生成 (同步)
    options = {
        "username": "Player",
        "uuid": "player-uuid",
        "token": "access-token",
        "gameDirectory": "./minecraft",
        "jvmArguments": ["-Xmx2048M"]
    }
    
    cmd = launcher.command.get_minecraft_command(
        "1.21.1", "./minecraft", options
    )
    return cmd

# 使用
command_list = generate_launch_command()
```

#### 新版異步指令生成
```python
import asyncio
from launcher_core import command, _types

async def generate_launch_command():
    # 新版指令生成 (異步)
    credential = _types.Credential(
        access_token="access-token",
        username="Player",
        uuid="player-uuid"
    )
    
    options = _types.MinecraftOptions(
        game_directory="./minecraft",
        memory=2048,
        jvm_args=["-Xmx2048M"]
    )
    
    cmd = await command.get_minecraft_command(
        "1.21.1", "./minecraft", options, Credential=credential
    )
    return cmd

# 使用
if __name__ == "__main__":
    command_list = asyncio.run(generate_launch_command())
```

## 🛠️ 自動遷移工具

### 代碼轉換工具

```python
import re
import ast
from pathlib import Path
from typing import List, Tuple

class CodeMigrator:
    """代碼自動遷移工具"""
    
    def __init__(self):
        self.conversions = [
            # Import 語句轉換
            (r'import minecraft_launcher_lib', 'import launcher_core'),
            (r'from minecraft_launcher_lib', 'from launcher_core'),
            (r'minecraft_launcher_lib\.', 'launcher_core.'),
            
            # 函數呼叫轉換（添加 await）
            (r'utils\.get_version_list\(\)', 'await utils.get_version_list()'),
            (r'install\.install_minecraft_version\(', 'await install.install_minecraft_version('),
            (r'command\.get_minecraft_command\(', 'await command.get_minecraft_command('),
            (r'fabric\.install_fabric\(', 'await fabric.install_fabric('),
            (r'forge\.install_forge_version\(', 'await forge.install_forge_version('),
            
            # Microsoft 認證轉換
            (r'login\.get_login_url\(\)', 'await login.get_login_url()'),
            (r'login\.get_ms_token\(', 'await login.get_ms_token('),
            (r'Login\.get_xbl_token\(', 'await Login.get_xbl_token('),
            (r'Login\.get_xsts_token\(', 'await Login.get_xsts_token('),
            (r'Login\.get_minecraft_access_token\(', 'await Login.get_minecraft_access_token('),
        ]
    
    def migrate_file(self, file_path: str) -> Tuple[str, List[str]]:
        """遷移單個文件"""
        path = Path(file_path)
        
        if not path.exists() or path.suffix != '.py':
            return None, ["文件不存在或不是 Python 文件"]
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            modified_content = original_content
            changes = []
            
            # 應用轉換規則
            for pattern, replacement in self.conversions:
                if re.search(pattern, modified_content):
                    modified_content = re.sub(pattern, replacement, modified_content)
                    changes.append(f"應用轉換: {pattern} -> {replacement}")
            
            # 檢查是否需要添加 asyncio import
            if 'await ' in modified_content and 'import asyncio' not in modified_content:
                lines = modified_content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_index = i + 1
                
                lines.insert(import_index, 'import asyncio')
                modified_content = '\n'.join(lines)
                changes.append("添加 asyncio import")
            
            # 檢查主函數是否需要轉換為異步
            if 'def main(' in modified_content and 'await ' in modified_content:
                modified_content = modified_content.replace('def main(', 'async def main(')
                changes.append("將 main 函數轉換為異步")
                
                # 添加 asyncio.run 如果需要
                if 'if __name__ == "__main__":' in modified_content:
                    modified_content = re.sub(
                        r'if __name__ == "__main__":\s*\n\s*main\(\)',
                        'if __name__ == "__main__":\n    asyncio.run(main())',
                        modified_content
                    )
                    changes.append("添加 asyncio.run 呼叫")
            
            return modified_content, changes
            
        except Exception as e:
            return None, [f"遷移失敗: {e}"]
    
    def migrate_directory(self, directory_path: str, backup: bool = True) -> dict:
        """遷移整個目錄"""
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            return {"error": "目錄不存在"}
        
        results = {
            "migrated_files": [],
            "skipped_files": [],
            "errors": []
        }
        
        # 創建備份目錄
        if backup:
            backup_dir = dir_path.parent / f"{dir_path.name}_backup"
            if backup_dir.exists():
                import shutil
                shutil.rmtree(backup_dir)
            shutil.copytree(dir_path, backup_dir)
            print(f"✅ 創建備份: {backup_dir}")
        
        # 遷移所有 Python 文件
        for py_file in dir_path.rglob("*.py"):
            try:
                modified_content, changes = self.migrate_file(str(py_file))
                
                if modified_content and changes:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    results["migrated_files"].append({
                        "file": str(py_file),
                        "changes": changes
                    })
                else:
                    results["skipped_files"].append(str(py_file))
                    
            except Exception as e:
                results["errors"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        return results
    
    def generate_migration_report(self, results: dict) -> str:
        """生成遷移報告"""
        report_lines = [
            "=== 代碼遷移報告 ===",
            f"生成時間: {datetime.now()}",
            "",
            f"已遷移文件: {len(results['migrated_files'])}",
            f"跳過文件: {len(results['skipped_files'])}",
            f"錯誤文件: {len(results['errors'])}",
            ""
        ]
        
        if results["migrated_files"]:
            report_lines.append("已遷移的文件:")
            for file_info in results["migrated_files"]:
                report_lines.append(f"  📁 {file_info['file']}")
                for change in file_info["changes"]:
                    report_lines.append(f"    - {change}")
                report_lines.append("")
        
        if results["errors"]:
            report_lines.append("錯誤:")
            for error_info in results["errors"]:
                report_lines.append(f"  ❌ {error_info['file']}: {error_info['error']}")
        
        return "\n".join(report_lines)

# 使用範例
async def migrate_project_example():
    """遷移專案示例"""
    migrator = CodeMigrator()
    
    # 遷移單個文件
    print("🔄 遷移單個文件...")
    modified_content, changes = migrator.migrate_file("old_launcher.py")
    
    if modified_content:
        print("✅ 文件遷移成功")
        for change in changes:
            print(f"  - {change}")
        
        # 保存遷移後的文件
        with open("new_launcher.py", "w", encoding="utf-8") as f:
            f.write(modified_content)
    
    # 遷移整個目錄
    print("\n🔄 遷移整個專案...")
    results = migrator.migrate_directory("./old_project", backup=True)
    
    # 生成報告
    report = migrator.generate_migration_report(results)
    print(report)
    
    # 保存報告
    with open("migration_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    asyncio.run(migrate_project_example())
```

### 配置遷移工具

```python
import json
import asyncio
from pathlib import Path
from launcher_core.config.load_launcher_config import save_config

class ConfigMigrator:
    """配置文件遷移工具"""
    
    async def migrate_launcher_profiles(self, minecraft_dir: str):
        """遷移 Vanilla 啟動器設定檔"""
        from launcher_core.config import vanilla_profile
        
        try:
            # 讀取 Vanilla 設定檔
            profiles = await vanilla_profile.load_profiles(minecraft_dir)
            
            if not profiles:
                print("❌ 找不到 Vanilla 啟動器設定檔")
                return
            
            # 轉換為新格式
            migrated_profiles = {}
            
            for profile_id, profile_data in profiles.items():
                migrated_profile = {
                    "name": profile_data.get("name", profile_id),
                    "minecraft_version": profile_data.get("lastVersionId", "1.21.1"),
                    "modloader": "none",
                    "memory_override": None,
                    "jvm_args_override": [],
                    "game_directory_override": profile_data.get("gameDir"),
                    "resolution": profile_data.get("resolution", {}),
                    "server": {
                        "auto_connect": False,
                        "host": "",
                        "port": 25565
                    }
                }
                
                # 解析 JVM 參數
                java_args = profile_data.get("javaArgs", "")
                if java_args:
                    migrated_profile["jvm_args_override"] = java_args.split()
                
                # 檢測模組載入器
                version = profile_data.get("lastVersionId", "")
                if "fabric" in version.lower():
                    migrated_profile["modloader"] = "fabric"
                elif "forge" in version.lower():
                    migrated_profile["modloader"] = "forge"
                elif "quilt" in version.lower():
                    migrated_profile["modloader"] = "quilt"
                
                migrated_profiles[profile_id] = migrated_profile
            
            # 創建新的配置文件
            new_config = {
                "launcher": {
                    "name": "Migrated Launcher",
                    "version": "1.0.0",
                    "language": "zh-TW",
                    "theme": "dark"
                },
                "minecraft": {
                    "directory": minecraft_dir,
                    "memory": 2048,
                    "java_executable": "auto"
                },
                "profiles": migrated_profiles
            }
            
            # 保存新配置
            await save_config("migrated_config.toml", new_config)
            print(f"✅ 成功遷移 {len(migrated_profiles)} 個設定檔")
            print("📄 配置已保存到: migrated_config.toml")
            
            return new_config
            
        except Exception as e:
            print(f"❌ 設定檔遷移失敗: {e}")
            raise
    
    async def create_default_config(self, minecraft_dir: str = "./minecraft"):
        """創建預設配置文件"""
        default_config = {
            "launcher": {
                "name": "async-mc-launcher",
                "version": "1.0.0",
                "language": "zh-TW",
                "theme": "dark",
                "auto_update": True,
                "close_on_launch": False
            },
            "minecraft": {
                "directory": minecraft_dir,
                "memory": 2048,
                "memory_auto": True,
                "java_executable": "auto",
                "jvm_args": [
                    "-XX:+UseG1GC",
                    "-XX:+UnlockExperimentalVMOptions",
                    "-XX:G1NewSizePercent=20",
                    "-XX:G1ReservePercent=20",
                    "-XX:MaxGCPauseMillis=50"
                ],
                "show_snapshots": False,
                "show_alpha_beta": False
            },
            "network": {
                "download_threads": 8,
                "timeout": 30,
                "retry_count": 3,
                "use_proxy": False
            },
            "profiles": {
                "default": {
                    "name": "預設設定檔",
                    "minecraft_version": "latest-release",
                    "modloader": "none",
                    "memory_override": None,
                    "jvm_args_override": [],
                    "game_directory_override": None
                }
            },
            "logging": {
                "level": "INFO",
                "file_logging": True,
                "console_logging": True,
                "log_file": "launcher.log"
            }
        }
        
        await save_config("launcher_config.toml", default_config)
        print("✅ 預設配置文件已創建: launcher_config.toml")
        
        return default_config

# 使用範例
async def config_migration_example():
    config_migrator = ConfigMigrator()
    
    # 遷移現有設定檔
    await config_migrator.migrate_launcher_profiles("./minecraft")
    
    # 或創建預設配置
    await config_migrator.create_default_config()

if __name__ == "__main__":
    asyncio.run(config_migration_example())
```

## 🔍 遷移檢查清單

### 程式碼檢查

- [ ] **Import 語句**: 已更新所有 import 語句
- [ ] **異步函數**: 已添加 `async` 關鍵字到需要的函數
- [ ] **Await 呼叫**: 已添加 `await` 到所有異步函數呼叫
- [ ] **主函數**: 已使用 `asyncio.run()` 運行主函數
- [ ] **例外處理**: 已更新例外處理以匹配新的例外類型
- [ ] **類型註解**: 已使用新的類型定義（可選）

### 功能檢查

- [ ] **基本安裝**: Minecraft 版本安裝功能正常
- [ ] **認證系統**: Microsoft 帳號登入功能正常
- [ ] **啟動指令**: 遊戲啟動指令生成正常
- [ ] **模組載入器**: Fabric/Forge/Quilt 安裝功能正常
- [ ] **配置管理**: 配置文件讀寫功能正常
- [ ] **日誌系統**: 日誌記錄功能正常

### 效能檢查

- [ ] **下載速度**: 異步下載比同步版本更快
- [ ] **記憶體使用**: 記憶體使用量在合理範圍內
- [ ] **錯誤處理**: 錯誤處理和重試機制正常工作
- [ ] **並發操作**: 多個異步操作可以同時執行

## 🚀 遷移後的優勢

### 效能改進

```python
import asyncio
import time
from launcher_core import install

async def performance_comparison():
    """效能比較示例"""
    
    # 並行安裝多個版本（新版優勢）
    versions = ["1.21.1", "1.20.1", "1.19.4"]
    minecraft_dir = "./minecraft"
    
    print("🚀 並行安裝多個版本...")
    start_time = time.time()
    
    # 並行執行多個安裝任務
    tasks = []
    for version in versions:
        task = install.install_minecraft_version(version, minecraft_dir)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"✅ 並行安裝完成，耗時: {end_time - start_time:.2f} 秒")
    
    # 這在原版中需要依序執行，會花費更多時間

if __name__ == "__main__":
    asyncio.run(performance_comparison())
```

### 更好的錯誤處理

```python
import asyncio
from launcher_core import microsoft_account
from launcher_core.exceptions import (
    AccountBanFromXbox,
    AccountNeedAdultVerification,
    DeviceCodeExpiredError
)

async def robust_authentication():
    """健全的認證系統示例"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = await microsoft_account.device_code_login()
            print("✅ 認證成功")
            return result
            
        except AccountBanFromXbox:
            print("❌ Xbox 帳號被封禁")
            break
            
        except AccountNeedAdultVerification:
            print("❌ 需要成人驗證")
            break
            
        except DeviceCodeExpiredError:
            print(f"⚠️ 設備代碼過期 (嘗試 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue
            else:
                print("❌ 所有嘗試都失敗")
                break
                
        except Exception as e:
            print(f"❌ 未知錯誤: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue
            else:
                raise
    
    return None

if __name__ == "__main__":
    asyncio.run(robust_authentication())
```

## 📝 常見遷移陷阱

### 1. 忘記添加 await

```python
# ❌ 錯誤: 忘記 await
versions = utils.get_version_list()  # 這會返回 coroutine 物件

# ✅ 正確: 添加 await
versions = await utils.get_version_list()
```

### 2. 混用同步和異步代碼

```python
# ❌ 錯誤: 在同步函數中呼叫異步函數
def main():
    result = await some_async_function()  # SyntaxError

# ✅ 正確: 使用異步函數
async def main():
    result = await some_async_function()
```

### 3. 忘記使用 asyncio.run

```python
# ❌ 錯誤: 直接呼叫異步函數
main()  # 會返回 coroutine 物件而不執行

# ✅ 正確: 使用 asyncio.run
asyncio.run(main())
```

### 4. 類型註解不匹配

```python
# ❌ 錯誤: 使用舊的類型定義
options = {
    "username": "player",
    "uuid": "uuid",
    "token": "token"
}

# ✅ 正確: 使用新的類型定義
from launcher_core import _types

credential = _types.Credential(
    access_token="token",
    username="player",
    uuid="uuid"
)

options = _types.MinecraftOptions(
    game_directory="./minecraft"
)
```

## 🆘 需要幫助？

如果在遷移過程中遇到問題：

1. **檢查遷移檢查清單**: 確保完成了所有必要步驟
2. **參考範例代碼**: 查看 [examples 目錄](https://github.com/JaydenChao101/async-mc-launcher-core/tree/main/examples)
3. **閱讀 API 文檔**: 參考 [API 參考文檔](API-Reference.md)
4. **使用自動遷移工具**: 運行本指南提供的遷移工具
5. **提交 Issue**: 在 [GitHub Issues](https://github.com/JaydenChao101/async-mc-launcher-core/issues) 尋求幫助

### 遷移支援工具

```python
async def migration_helper():
    """遷移助手工具"""
    print("🔧 async-mc-launcher-core 遷移助手")
    print("=" * 50)
    
    print("1. 程式碼遷移")
    print("2. 配置遷移")
    print("3. 檢查遷移狀態")
    print("4. 生成遷移報告")
    print("5. 測試新版功能")
    
    choice = input("\n請選擇操作 (1-5): ").strip()
    
    if choice == "1":
        migrator = CodeMigrator()
        directory = input("請輸入專案目錄: ").strip()
        results = migrator.migrate_directory(directory)
        report = migrator.generate_migration_report(results)
        print(report)
    
    elif choice == "2":
        config_migrator = ConfigMigrator()
        minecraft_dir = input("請輸入 Minecraft 目錄: ").strip()
        await config_migrator.migrate_launcher_profiles(minecraft_dir)
    
    elif choice == "3":
        # 運行診斷工具
        from .Troubleshooting import DiagnosticTool
        tool = DiagnosticTool()
        await tool.run_full_diagnosis()
    
    elif choice == "4":
        print("📋 生成詳細的遷移報告...")
        # 生成遷移報告邏輯
    
    elif choice == "5":
        print("🧪 測試新版功能...")
        # 測試新功能
        await test_new_features()
    
    else:
        print("❌ 無效選擇")

async def test_new_features():
    """測試新版功能"""
    try:
        # 測試異步版本列表
        from launcher_core import utils
        versions = await utils.get_version_list()
        print(f"✅ 版本列表獲取成功: {len(versions)} 個版本")
        
        # 測試設備代碼登入
        from launcher_core import microsoft_account
        print("🔐 測試 Microsoft 認證 (將開始設備代碼流程)...")
        # result = await microsoft_account.device_code_login()
        # print("✅ 認證測試成功")
        
        print("✅ 所有新功能測試通過")
        
    except Exception as e:
        print(f"❌ 功能測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(migration_helper())
```

---

通過本遷移指南，您應該能夠順利地從原版 minecraft-launcher-lib 遷移到 async-mc-launcher-core，並享受異步編程帶來的效能提升和更好的使用者體驗。