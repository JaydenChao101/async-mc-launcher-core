# 配置管理

async-mc-launcher-core 提供完整的配置管理系統，支援 TOML 格式配置文件、環境變數、啟動器設定和日誌配置。本指南將詳細介紹如何使用這些配置功能。

## 📁 TOML 配置文件

### 基本 TOML 操作

```python
import asyncio
from launcher_core.config.load_launcher_config import load_config, save_config
from launcher_core.setting import setup_logger

async def basic_toml_example():
    """基本 TOML 配置操作示例"""
    logger = setup_logger(enable_console=True)
    
    # 創建基本配置
    config_data = {
        "launcher": {
            "name": "My Minecraft Launcher",
            "version": "1.0.0",
            "theme": "dark"
        },
        "minecraft": {
            "directory": "./minecraft",
            "memory": 2048,
            "java_args": ["-Xmx2048M", "-Xms1024M"]
        },
        "accounts": {
            "current_user": "player123",
            "auto_login": True
        }
    }
    
    config_file = "launcher_config.toml"
    
    try:
        # 保存配置到文件
        await save_config(config_file, config_data)
        logger.info(f"✅ 配置已保存到 {config_file}")
        
        # 從文件讀取配置
        loaded_config = await load_config(config_file)
        logger.info("✅ 配置已從文件讀取")
        
        # 顯示配置內容
        print("=== 配置內容 ===")
        print(f"啟動器名稱: {loaded_config['launcher']['name']}")
        print(f"Minecraft 目錄: {loaded_config['minecraft']['directory']}")
        print(f"記憶體配置: {loaded_config['minecraft']['memory']} MB")
        print(f"當前用戶: {loaded_config['accounts']['current_user']}")
        
        return loaded_config
        
    except Exception as e:
        logger.error(f"❌ 配置操作失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(basic_toml_example())
```

### 環境變數支援

async-mc-launcher-core 支援在 TOML 配置中使用環境變數：

#### 配置文件示例 (config.toml)

```toml
[launcher]
name = "Advanced Launcher"
data_directory = "{LAUNCHER_DATA_DIR:-./launcher_data}"

[minecraft]
directory = "{MC_DIR:-./minecraft}"
memory = "{MC_MEMORY:-2048}"

[credentials]
username = "{MC_USERNAME}"
access_token = "{MC_ACCESS_TOKEN}"
uuid = "{MC_UUID}"

[java]
executable = "{JAVA_HOME}/bin/java"
additional_args = ["{JVM_ARGS:--XX:+UseG1GC}"]
```

#### 環境變數使用範例

```python
import os
import asyncio
from launcher_core.config.load_launcher_config import load_config

async def environment_variables_example():
    """環境變數配置示例"""
    
    # 設置環境變數
    os.environ["MC_USERNAME"] = "TestPlayer"
    os.environ["MC_ACCESS_TOKEN"] = "test_access_token_123"
    os.environ["MC_UUID"] = "12345678-1234-1234-1234-123456789abc"
    os.environ["MC_MEMORY"] = "4096"
    os.environ["LAUNCHER_DATA_DIR"] = "/custom/launcher/path"
    
    try:
        # 讀取帶有環境變數的配置
        config = await load_config("config.toml")
        
        print("=== 環境變數解析結果 ===")
        print(f"用戶名: {config['credentials']['username']}")
        print(f"Access Token: {config['credentials']['access_token'][:20]}...")
        print(f"UUID: {config['credentials']['uuid']}")
        print(f"記憶體: {config['minecraft']['memory']} MB")
        print(f"啟動器目錄: {config['launcher']['data_directory']}")
        
        # 展示預設值功能
        print(f"Minecraft 目錄: {config['minecraft']['directory']}")  # 使用預設值
        
        return config
        
    except Exception as e:
        print(f"❌ 環境變數配置讀取失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(environment_variables_example())
```

### 動態配置管理

```python
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from launcher_core.config.load_launcher_config import load_config, save_config
from launcher_core.setting import setup_logger

class ConfigManager:
    """動態配置管理器"""
    
    def __init__(self, config_file: str = "launcher_config.toml"):
        self.config_file = Path(config_file)
        self.config = {}
        self.logger = setup_logger(enable_console=True)
        self._defaults = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """獲取預設配置"""
        return {
            "launcher": {
                "name": "async-mc-launcher",
                "version": "1.0.0",
                "language": "zh-TW",
                "theme": "dark",
                "auto_update": True,
                "close_on_launch": False
            },
            "minecraft": {
                "directory": "./minecraft",
                "memory": 2048,
                "memory_auto": True,
                "java_executable": "auto",
                "jvm_args": [
                    "-XX:+UseG1GC",
                    "-XX:+UnlockExperimentalVMOptions"
                ],
                "show_snapshots": False,
                "show_alpha_beta": False
            },
            "network": {
                "download_threads": 8,
                "timeout": 30,
                "retry_count": 3,
                "use_proxy": False,
                "proxy_host": "",
                "proxy_port": 0
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
                "log_file": "launcher.log",
                "max_log_size": 10485760,  # 10MB
                "backup_count": 5
            }
        }
    
    async def load_config(self):
        """載入配置文件"""
        try:
            if self.config_file.exists():
                self.config = await load_config(str(self.config_file))
                self.logger.info("✅ 配置文件載入成功")
            else:
                self.config = self._defaults.copy()
                await self.save_config()
                self.logger.info("✅ 創建預設配置文件")
            
            # 合併預設值（確保新選項存在）
            self._merge_defaults()
            
        except Exception as e:
            self.logger.error(f"❌ 載入配置失敗: {e}")
            self.config = self._defaults.copy()
    
    async def save_config(self):
        """保存配置文件"""
        try:
            await save_config(str(self.config_file), self.config)
            self.logger.info("✅ 配置文件保存成功")
        except Exception as e:
            self.logger.error(f"❌ 保存配置失敗: {e}")
            raise
    
    def _merge_defaults(self):
        """合併預設值到現有配置"""
        def merge_dict(target: Dict, source: Dict):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    merge_dict(target[key], value)
        
        merge_dict(self.config, self._defaults)
    
    def get(self, path: str, default: Any = None) -> Any:
        """獲取配置值（支援點分路徑）"""
        keys = path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    async def set(self, path: str, value: Any, save: bool = True):
        """設置配置值（支援點分路徑）"""
        keys = path.split(".")
        config = self.config
        
        # 導航到最後一層
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 設置值
        config[keys[-1]] = value
        
        if save:
            await self.save_config()
    
    def get_profile(self, profile_name: str = "default") -> Optional[Dict]:
        """獲取遊戲設定檔"""
        profiles = self.get("profiles", {})
        return profiles.get(profile_name)
    
    async def create_profile(self, name: str, base_profile: str = "default", 
                           settings: Dict = None):
        """創建新的遊戲設定檔"""
        profiles = self.get("profiles", {})
        
        # 複製基礎設定檔
        if base_profile in profiles:
            new_profile = profiles[base_profile].copy()
        else:
            new_profile = self._defaults["profiles"]["default"].copy()
        
        new_profile["name"] = name
        
        # 應用自訂設定
        if settings:
            new_profile.update(settings)
        
        # 保存新設定檔
        await self.set(f"profiles.{name}", new_profile)
        self.logger.info(f"✅ 創建設定檔: {name}")
    
    async def delete_profile(self, name: str):
        """刪除遊戲設定檔"""
        if name == "default":
            raise ValueError("不能刪除預設設定檔")
        
        profiles = self.get("profiles", {})
        if name in profiles:
            del profiles[name]
            await self.save_config()
            self.logger.info(f"✅ 刪除設定檔: {name}")
        else:
            raise ValueError(f"設定檔不存在: {name}")
    
    def list_profiles(self) -> List[str]:
        """列出所有設定檔"""
        profiles = self.get("profiles", {})
        return list(profiles.keys())
    
    async def backup_config(self, backup_path: str = None):
        """備份配置文件"""
        if not backup_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"config_backup_{timestamp}.toml"
        
        try:
            import shutil
            shutil.copy2(self.config_file, backup_path)
            self.logger.info(f"✅ 配置已備份到: {backup_path}")
        except Exception as e:
            self.logger.error(f"❌ 配置備份失敗: {e}")
            raise
    
    async def restore_config(self, backup_path: str):
        """從備份恢復配置"""
        try:
            import shutil
            shutil.copy2(backup_path, self.config_file)
            await self.load_config()
            self.logger.info(f"✅ 配置已從 {backup_path} 恢復")
        except Exception as e:
            self.logger.error(f"❌ 配置恢復失敗: {e}")
            raise

# 使用範例
async def config_manager_example():
    config_mgr = ConfigManager("advanced_config.toml")
    
    # 載入配置
    await config_mgr.load_config()
    
    # 修改配置
    await config_mgr.set("launcher.theme", "light")
    await config_mgr.set("minecraft.memory", 4096)
    await config_mgr.set("network.download_threads", 16)
    
    # 獲取配置
    theme = config_mgr.get("launcher.theme")
    memory = config_mgr.get("minecraft.memory")
    print(f"當前主題: {theme}")
    print(f"記憶體配置: {memory} MB")
    
    # 創建新設定檔
    await config_mgr.create_profile("fabric_1.21.1", settings={
        "minecraft_version": "1.21.1",
        "modloader": "fabric",
        "memory_override": 3072
    })
    
    # 列出設定檔
    profiles = config_mgr.list_profiles()
    print(f"可用設定檔: {profiles}")
    
    # 備份配置
    await config_mgr.backup_config()

if __name__ == "__main__":
    asyncio.run(config_manager_example())
```

## 📋 啟動器設定檔

### Vanilla 啟動器設定檔支援

```python
import asyncio
from launcher_core.config import vanilla_profile
from launcher_core.setting import setup_logger

async def vanilla_profile_example():
    """Vanilla 啟動器設定檔操作示例"""
    logger = setup_logger(enable_console=True)
    
    minecraft_directory = "./minecraft"
    
    try:
        # 讀取 Vanilla 啟動器設定檔
        profiles = await vanilla_profile.load_profiles(minecraft_directory)
        
        if profiles:
            print("=== Vanilla 啟動器設定檔 ===")
            for profile_id, profile_data in profiles.items():
                print(f"設定檔 ID: {profile_id}")
                print(f"名稱: {profile_data.get('name', 'Unknown')}")
                print(f"版本: {profile_data.get('lastVersionId', 'Unknown')}")
                print(f"創建時間: {profile_data.get('created', 'Unknown')}")
                print("-" * 40)
        else:
            print("❌ 找不到 Vanilla 啟動器設定檔")
        
        # 創建新的設定檔
        new_profile = {
            "name": "async-mc-launcher Profile",
            "lastVersionId": "1.21.1",
            "gameDir": minecraft_directory,
            "javaArgs": "-Xmx2048M -Xms1024M",
            "type": "custom"
        }
        
        await vanilla_profile.save_profile(
            minecraft_directory, 
            "async_mc_profile", 
            new_profile
        )
        
        logger.info("✅ 新設定檔已創建")
        
    except Exception as e:
        logger.error(f"❌ Vanilla 設定檔操作失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(vanilla_profile_example())
```

### 設定檔遷移工具

```python
import asyncio
import json
from pathlib import Path
from typing import Dict, List
from launcher_core.config import vanilla_profile
from launcher_core.setting import setup_logger

class ProfileMigrator:
    """設定檔遷移工具"""
    
    def __init__(self, minecraft_directory: str = "./minecraft"):
        self.minecraft_dir = Path(minecraft_directory)
        self.logger = setup_logger(enable_console=True)
    
    async def export_vanilla_profiles(self, export_path: str):
        """匯出 Vanilla 啟動器設定檔"""
        try:
            profiles = await vanilla_profile.load_profiles(str(self.minecraft_dir))
            
            if not profiles:
                self.logger.warning("⚠️ 找不到 Vanilla 啟動器設定檔")
                return
            
            # 轉換為可讀格式
            export_data = {
                "export_version": "1.0",
                "export_date": datetime.now().isoformat(),
                "profiles": {}
            }
            
            for profile_id, profile_data in profiles.items():
                export_data["profiles"][profile_id] = {
                    "name": profile_data.get("name", profile_id),
                    "minecraft_version": profile_data.get("lastVersionId", "unknown"),
                    "game_directory": profile_data.get("gameDir", ""),
                    "java_args": profile_data.get("javaArgs", ""),
                    "resolution": {
                        "width": profile_data.get("resolution", {}).get("width"),
                        "height": profile_data.get("resolution", {}).get("height")
                    },
                    "created": profile_data.get("created", ""),
                    "last_used": profile_data.get("lastUsed", ""),
                    "type": profile_data.get("type", "custom")
                }
            
            # 保存到文件
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 設定檔已匯出到: {export_path}")
            self.logger.info(f"匯出了 {len(profiles)} 個設定檔")
            
        except Exception as e:
            self.logger.error(f"❌ 匯出設定檔失敗: {e}")
            raise
    
    async def import_profiles(self, import_path: str, 
                            target_format: str = "async_mc"):
        """匯入設定檔到指定格式"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            profiles = import_data.get("profiles", {})
            
            if target_format == "async_mc":
                await self._import_to_async_mc(profiles)
            elif target_format == "vanilla":
                await self._import_to_vanilla(profiles)
            else:
                raise ValueError(f"不支援的目標格式: {target_format}")
            
        except Exception as e:
            self.logger.error(f"❌ 匯入設定檔失敗: {e}")
            raise
    
    async def _import_to_async_mc(self, profiles: Dict):
        """匯入到 async-mc-launcher 格式"""
        config_mgr = ConfigManager()
        await config_mgr.load_config()
        
        imported_count = 0
        
        for profile_id, profile_data in profiles.items():
            try:
                # 轉換為 async-mc-launcher 格式
                new_profile = {
                    "name": profile_data["name"],
                    "minecraft_version": profile_data["minecraft_version"],
                    "modloader": "none",  # 預設無模組載入器
                    "memory_override": None,
                    "jvm_args_override": profile_data["java_args"].split() if profile_data["java_args"] else [],
                    "game_directory_override": profile_data["game_directory"] or None,
                    "resolution": profile_data["resolution"]
                }
                
                # 檢測模組載入器
                version = profile_data["minecraft_version"]
                if "fabric" in version.lower():
                    new_profile["modloader"] = "fabric"
                elif "forge" in version.lower():
                    new_profile["modloader"] = "forge"
                elif "quilt" in version.lower():
                    new_profile["modloader"] = "quilt"
                
                await config_mgr.set(f"profiles.{profile_id}", new_profile, save=False)
                imported_count += 1
                
            except Exception as e:
                self.logger.warning(f"⚠️ 跳過設定檔 {profile_id}: {e}")
        
        await config_mgr.save_config()
        self.logger.info(f"✅ 成功匯入 {imported_count} 個設定檔到 async-mc-launcher")
    
    async def _import_to_vanilla(self, profiles: Dict):
        """匯入到 Vanilla 啟動器格式"""
        imported_count = 0
        
        for profile_id, profile_data in profiles.items():
            try:
                # 轉換為 Vanilla 格式
                vanilla_profile_data = {
                    "name": profile_data["name"],
                    "lastVersionId": profile_data["minecraft_version"],
                    "gameDir": profile_data["game_directory"],
                    "javaArgs": " ".join(profile_data.get("jvm_args_override", [])),
                    "type": "custom",
                    "created": profile_data.get("created", datetime.now().isoformat()),
                    "lastUsed": profile_data.get("last_used", datetime.now().isoformat())
                }
                
                # 添加解析度設定
                if profile_data.get("resolution"):
                    resolution = profile_data["resolution"]
                    if resolution.get("width") and resolution.get("height"):
                        vanilla_profile_data["resolution"] = {
                            "width": resolution["width"],
                            "height": resolution["height"]
                        }
                
                await vanilla_profile.save_profile(
                    str(self.minecraft_dir),
                    profile_id,
                    vanilla_profile_data
                )
                
                imported_count += 1
                
            except Exception as e:
                self.logger.warning(f"⚠️ 跳過設定檔 {profile_id}: {e}")
        
        self.logger.info(f"✅ 成功匯入 {imported_count} 個設定檔到 Vanilla 啟動器")

# 使用範例
async def profile_migration_example():
    migrator = ProfileMigrator("./minecraft")
    
    # 匯出 Vanilla 設定檔
    await migrator.export_vanilla_profiles("vanilla_profiles_backup.json")
    
    # 匯入到 async-mc-launcher
    await migrator.import_profiles("vanilla_profiles_backup.json", "async_mc")

if __name__ == "__main__":
    asyncio.run(profile_migration_example())
```

## 📊 日誌配置

### 高級日誌配置

```python
import logging
import asyncio
from pathlib import Path
from launcher_core.setting import setup_logger

def advanced_logging_setup():
    """高級日誌配置示例"""
    
    # 創建日誌目錄
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # 設置主日誌記錄器
    main_logger = setup_logger(
        name="main",
        enable_console=True,
        level=logging.INFO,
        filename=str(log_dir / "main.log")
    )
    
    # 設置錯誤日誌記錄器
    error_logger = setup_logger(
        name="error",
        enable_console=False,
        level=logging.ERROR,
        filename=str(log_dir / "error.log")
    )
    
    # 設置調試日誌記錄器
    debug_logger = setup_logger(
        name="debug",
        enable_console=False,
        level=logging.DEBUG,
        filename=str(log_dir / "debug.log")
    )
    
    # 設置網路日誌記錄器
    network_logger = setup_logger(
        name="network",
        enable_console=False,
        level=logging.INFO,
        filename=str(log_dir / "network.log")
    )
    
    return {
        "main": main_logger,
        "error": error_logger,
        "debug": debug_logger,
        "network": network_logger
    }

class LogManager:
    """日誌管理器"""
    
    def __init__(self, log_directory: str = "./logs"):
        self.log_dir = Path(log_directory)
        self.log_dir.mkdir(exist_ok=True)
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """設置所有日誌記錄器"""
        
        # 主日誌
        self.loggers["main"] = setup_logger(
            name="launcher.main",
            enable_console=True,
            level=logging.INFO,
            filename=str(self.log_dir / "launcher.log")
        )
        
        # 認證日誌
        self.loggers["auth"] = setup_logger(
            name="launcher.auth",
            enable_console=False,
            level=logging.INFO,
            filename=str(self.log_dir / "auth.log")
        )
        
        # 安裝日誌
        self.loggers["install"] = setup_logger(
            name="launcher.install",
            enable_console=False,
            level=logging.INFO,
            filename=str(self.log_dir / "install.log")
        )
        
        # 網路日誌
        self.loggers["network"] = setup_logger(
            name="launcher.network",
            enable_console=False,
            level=logging.WARNING,
            filename=str(self.log_dir / "network.log")
        )
        
        # 錯誤日誌
        self.loggers["error"] = setup_logger(
            name="launcher.error",
            enable_console=True,
            level=logging.ERROR,
            filename=str(self.log_dir / "error.log")
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """獲取指定的日誌記錄器"""
        return self.loggers.get(name, self.loggers["main"])
    
    def log_action(self, category: str, action: str, details: str = None, 
                  level: int = logging.INFO):
        """記錄動作日誌"""
        logger = self.get_logger(category)
        message = f"[{action}]"
        if details:
            message += f" {details}"
        logger.log(level, message)
    
    def log_error(self, category: str, error: Exception, context: str = None):
        """記錄錯誤日誌"""
        error_logger = self.get_logger("error")
        main_logger = self.get_logger(category)
        
        message = f"錯誤: {type(error).__name__}: {error}"
        if context:
            message = f"{context} - {message}"
        
        error_logger.error(message)
        main_logger.error(message)
    
    async def cleanup_old_logs(self, max_age_days: int = 30):
        """清理舊日誌文件"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                self.loggers["main"].warning(f"清理日誌文件失敗: {e}")
        
        if deleted_count > 0:
            self.loggers["main"].info(f"清理了 {deleted_count} 個舊日誌文件")
    
    def get_log_statistics(self) -> Dict:
        """獲取日誌統計資訊"""
        stats = {
            "log_files": [],
            "total_size": 0,
            "file_count": 0
        }
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                file_size = log_file.stat().st_size
                stats["log_files"].append({
                    "name": log_file.name,
                    "size": file_size,
                    "size_mb": round(file_size / 1024 / 1024, 2)
                })
                stats["total_size"] += file_size
                stats["file_count"] += 1
            except Exception:
                continue
        
        stats["total_size_mb"] = round(stats["total_size"] / 1024 / 1024, 2)
        return stats

# 使用範例
async def logging_example():
    log_mgr = LogManager("./launcher_logs")
    
    # 記錄不同類型的日誌
    log_mgr.log_action("main", "啟動器啟動", "版本 1.0.0")
    log_mgr.log_action("auth", "用戶登入", "玩家: TestUser")
    log_mgr.log_action("install", "版本安裝", "Minecraft 1.21.1")
    
    # 記錄錯誤
    try:
        raise ValueError("這是一個測試錯誤")
    except Exception as e:
        log_mgr.log_error("main", e, "測試錯誤處理")
    
    # 獲取日誌統計
    stats = log_mgr.get_log_statistics()
    print("=== 日誌統計 ===")
    print(f"日誌文件數量: {stats['file_count']}")
    print(f"總大小: {stats['total_size_mb']} MB")
    
    for file_info in stats["log_files"]:
        print(f"  {file_info['name']}: {file_info['size_mb']} MB")
    
    # 清理舊日誌
    await log_mgr.cleanup_old_logs(max_age_days=7)

if __name__ == "__main__":
    asyncio.run(logging_example())
```

## 🔧 配置最佳實踐

### 配置驗證

```python
import asyncio
from typing import Any, Dict, List
from launcher_core.setting import setup_logger

class ConfigValidator:
    """配置驗證器"""
    
    def __init__(self):
        self.logger = setup_logger(enable_console=True)
        self.validation_rules = self._get_validation_rules()
    
    def _get_validation_rules(self) -> Dict:
        """獲取驗證規則"""
        return {
            "launcher.memory": {
                "type": int,
                "min": 512,
                "max": 16384,
                "description": "記憶體配置必須在 512MB 到 16GB 之間"
            },
            "network.download_threads": {
                "type": int,
                "min": 1,
                "max": 32,
                "description": "下載線程數必須在 1 到 32 之間"
            },
            "network.timeout": {
                "type": int,
                "min": 5,
                "max": 300,
                "description": "網路超時必須在 5 到 300 秒之間"
            },
            "launcher.language": {
                "type": str,
                "choices": ["zh-TW", "zh-CN", "en-US", "ja-JP"],
                "description": "語言必須是支援的語言代碼"
            }
        }
    
    def validate_config(self, config: Dict) -> List[str]:
        """驗證配置並返回錯誤列表"""
        errors = []
        
        for path, rule in self.validation_rules.items():
            try:
                value = self._get_nested_value(config, path)
                if value is None:
                    continue  # 可選配置項
                
                error = self._validate_value(path, value, rule)
                if error:
                    errors.append(error)
                    
            except Exception as e:
                errors.append(f"{path}: 驗證過程中發生錯誤 - {e}")
        
        return errors
    
    def _get_nested_value(self, config: Dict, path: str) -> Any:
        """獲取嵌套配置值"""
        keys = path.split(".")
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _validate_value(self, path: str, value: Any, rule: Dict) -> str:
        """驗證單個值"""
        # 檢查類型
        expected_type = rule.get("type")
        if expected_type and not isinstance(value, expected_type):
            return f"{path}: 類型錯誤，期望 {expected_type.__name__}，得到 {type(value).__name__}"
        
        # 檢查範圍
        if "min" in rule and value < rule["min"]:
            return f"{path}: 值過小，最小值為 {rule['min']}"
        
        if "max" in rule and value > rule["max"]:
            return f"{path}: 值過大，最大值為 {rule['max']}"
        
        # 檢查選擇項
        if "choices" in rule and value not in rule["choices"]:
            return f"{path}: 無效選擇，可選值: {rule['choices']}"
        
        return None
    
    async def validate_and_fix_config(self, config_mgr: ConfigManager) -> bool:
        """驗證並嘗試修復配置"""
        errors = self.validate_config(config_mgr.config)
        
        if not errors:
            self.logger.info("✅ 配置驗證通過")
            return True
        
        self.logger.warning(f"⚠️ 發現 {len(errors)} 個配置錯誤:")
        for error in errors:
            self.logger.warning(f"  - {error}")
        
        # 嘗試自動修復
        fixed_count = 0
        for path, rule in self.validation_rules.items():
            value = config_mgr.get(path)
            if value is None:
                continue
            
            fixed_value = self._try_fix_value(value, rule)
            if fixed_value != value:
                await config_mgr.set(path, fixed_value, save=False)
                fixed_count += 1
                self.logger.info(f"✅ 修復配置 {path}: {value} -> {fixed_value}")
        
        if fixed_count > 0:
            await config_mgr.save_config()
            self.logger.info(f"✅ 自動修復了 {fixed_count} 個配置項")
        
        return fixed_count == len(errors)
    
    def _try_fix_value(self, value: Any, rule: Dict) -> Any:
        """嘗試修復配置值"""
        # 修復範圍問題
        if "min" in rule and value < rule["min"]:
            return rule["min"]
        
        if "max" in rule and value > rule["max"]:
            return rule["max"]
        
        # 修復選擇項問題
        if "choices" in rule and value not in rule["choices"]:
            return rule["choices"][0]  # 返回第一個有效選項
        
        return value

# 使用範例
async def config_validation_example():
    # 創建配置管理器
    config_mgr = ConfigManager("test_config.toml")
    await config_mgr.load_config()
    
    # 設置一些有問題的配置
    await config_mgr.set("launcher.memory", 99999)  # 超出範圍
    await config_mgr.set("network.download_threads", 0)  # 低於最小值
    await config_mgr.set("launcher.language", "invalid")  # 無效選擇
    
    # 驗證和修復配置
    validator = ConfigValidator()
    is_valid = await validator.validate_and_fix_config(config_mgr)
    
    if is_valid:
        print("✅ 配置驗證和修復完成")
    else:
        print("❌ 仍有無法自動修復的配置錯誤")

if __name__ == "__main__":
    asyncio.run(config_validation_example())
```

## 📚 總結

async-mc-launcher-core 的配置管理系統提供：

### 🔧 主要功能
1. **TOML 配置文件** - 人類可讀的配置格式
2. **環境變數支援** - 靈活的配置注入
3. **設定檔管理** - 多重遊戲配置
4. **日誌配置** - 完整的日誌記錄系統
5. **配置驗證** - 確保配置正確性

### 🌟 特色
- 支援嵌套配置結構
- 自動合併預設值
- 配置備份和恢復
- Vanilla 啟動器相容性
- 動態配置更新

### 💡 最佳實踐
1. 使用環境變數管理敏感資訊
2. 定期備份重要配置
3. 驗證配置正確性
4. 分類管理不同類型的日誌
5. 使用設定檔管理不同的遊戲配置

---

更多相關資訊請參考：
- [快速開始 - 基本配置](Quick-Start.md#🛠️-基本配置)
- [高級示例 - 配置管理系統](Advanced-Examples.md#🔧-配置管理系統)
- [API 參考 - config 模組](API-Reference.md#config)