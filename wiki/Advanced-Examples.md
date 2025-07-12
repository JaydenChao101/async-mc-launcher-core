# 高級示例

本文檔提供 async-mc-launcher-core 的高級使用場景和複雜功能實現，包括模組包安裝、配置管理、錯誤處理和生產環境最佳實踐。

## 🎮 完整的啟動器應用程式

### 基礎啟動器類

```python
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from launcher_core import (
    microsoft_account, install, command, utils, fabric, forge, quilt,
    _types, mojang, java_utils
)
from launcher_core.setting import setup_logger
from launcher_core.config import read_toml_file, write_toml_file

class MinecraftLauncher:
    """完整的 Minecraft 啟動器類"""
    
    def __init__(self, base_directory: str = "./minecraft_launcher"):
        self.base_dir = Path(base_directory)
        self.minecraft_dir = self.base_dir / "minecraft"
        self.config_file = self.base_dir / "config.toml"
        self.auth_file = self.base_dir / "auth.json"
        
        # 創建必要目錄
        self.base_dir.mkdir(exist_ok=True)
        self.minecraft_dir.mkdir(exist_ok=True)
        
        # 設置日誌
        self.logger = setup_logger(
            enable_console=True,
            level=logging.INFO,
            filename=str(self.base_dir / "launcher.log")
        )
        
        self.config = None
        self.auth_data = None
    
    async def initialize(self):
        """初始化啟動器"""
        await self.load_config()
        await self.load_auth_data()
        self.logger.info("✅ 啟動器初始化完成")
    
    async def load_config(self):
        """載入配置文件"""
        try:
            if self.config_file.exists():
                self.config = await read_toml_file(str(self.config_file))
            else:
                # 創建預設配置
                self.config = {
                    "launcher": {
                        "name": "My Minecraft Launcher",
                        "version": "1.0.0"
                    },
                    "minecraft": {
                        "default_version": "1.21.1",
                        "memory": 2048,
                        "jvm_args": ["-Xmx2048M", "-Xms1024M"]
                    },
                    "mods": {
                        "auto_update": True,
                        "preferred_loader": "fabric"
                    }
                }
                await self.save_config()
            
            self.logger.info("✅ 配置文件載入成功")
            
        except Exception as e:
            self.logger.error(f"❌ 載入配置文件失敗: {e}")
            raise
    
    async def save_config(self):
        """保存配置文件"""
        try:
            await write_toml_file(str(self.config_file), self.config)
            self.logger.info("✅ 配置文件保存成功")
        except Exception as e:
            self.logger.error(f"❌ 保存配置文件失敗: {e}")
            raise
    
    async def load_auth_data(self) -> bool:
        """載入認證資料"""
        try:
            if not self.auth_file.exists():
                return False
            
            with open(self.auth_file, "r", encoding="utf-8") as f:
                self.auth_data = json.load(f)
            
            # 檢查過期時間
            if "expires_at" in self.auth_data:
                expires_at = datetime.fromisoformat(self.auth_data["expires_at"])
                if datetime.now() > expires_at:
                    self.logger.warning("⚠️ 認證資料已過期")
                    return False
            
            self.logger.info("✅ 認證資料載入成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 載入認證資料失敗: {e}")
            return False
    
    async def save_auth_data(self):
        """保存認證資料"""
        if not self.auth_data:
            return
        
        try:
            with open(self.auth_file, "w", encoding="utf-8") as f:
                json.dump(self.auth_data, f, indent=2, ensure_ascii=False)
            
            # 設置檔案權限
            self.auth_file.chmod(0o600)
            self.logger.info("✅ 認證資料保存成功")
            
        except Exception as e:
            self.logger.error(f"❌ 保存認證資料失敗: {e}")
            raise
    
    async def login(self, use_device_code: bool = True) -> str:
        """執行登入流程"""
        try:
            if use_device_code:
                result = await microsoft_account.device_code_login()
                self.auth_data = result
            else:
                # 瀏覽器登入流程
                azure_app = microsoft_account.AzureApplication()
                login = microsoft_account.Login(azure_app=azure_app)
                
                login_url = await login.get_login_url()
                print(f"請在瀏覽器中開啟: {login_url}")
                redirect_url = input("請輸入重定向 URL: ")
                
                code = await microsoft_account.Login.extract_code_from_url(redirect_url)
                auth_response = await login.get_ms_token(code)
                
                # 完整認證流程
                xbl_token = await microsoft_account.Login.get_xbl_token(auth_response["access_token"])
                xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
                uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
                mc_token = await microsoft_account.Login.get_minecraft_access_token(xsts_token["Token"], uhs)
                
                # 獲取玩家資訊
                profile = await mojang.get_minecraft_profile(mc_token["access_token"])
                
                self.auth_data = {
                    "minecraft_access_token": mc_token["access_token"],
                    "refresh_token": auth_response["refresh_token"],
                    "expires_in": auth_response["expires_in"],
                    "player_name": profile["name"],
                    "player_uuid": profile["id"]
                }
            
            # 添加過期時間
            self.auth_data["expires_at"] = (
                datetime.now() + timedelta(seconds=self.auth_data["expires_in"])
            ).isoformat()
            
            await self.save_auth_data()
            self.logger.info(f"✅ 登入成功，玩家: {self.auth_data['player_name']}")
            
            return self.auth_data["minecraft_access_token"]
            
        except Exception as e:
            self.logger.error(f"❌ 登入失敗: {e}")
            raise
    
    async def refresh_token_if_needed(self) -> bool:
        """如果需要則刷新 Token"""
        if not self.auth_data:
            return False
        
        try:
            # 檢查是否需要刷新
            if "expires_at" in self.auth_data:
                expires_at = datetime.fromisoformat(self.auth_data["expires_at"])
                time_left = expires_at - datetime.now()
                
                if time_left.total_seconds() < 600:  # 少於 10 分鐘
                    self.logger.info("🔄 正在刷新 Access Token...")
                    
                    new_tokens = await microsoft_account.refresh_minecraft_token(
                        self.auth_data["refresh_token"]
                    )
                    
                    self.auth_data.update(new_tokens)
                    self.auth_data["expires_at"] = (
                        datetime.now() + timedelta(seconds=new_tokens["expires_in"])
                    ).isoformat()
                    
                    await self.save_auth_data()
                    self.logger.info("✅ Token 刷新成功")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Token 刷新失敗: {e}")
            return False
    
    async def get_valid_access_token(self) -> str:
        """獲取有效的 Access Token"""
        # 嘗試載入現有認證
        if not await self.load_auth_data():
            # 如果沒有有效認證，執行登入
            return await self.login()
        
        # 嘗試刷新 Token
        if not await self.refresh_token_if_needed():
            # 如果刷新失敗，重新登入
            return await self.login()
        
        return self.auth_data["minecraft_access_token"]
    
    async def install_minecraft_version(self, version: str, force: bool = False):
        """安裝 Minecraft 版本"""
        try:
            # 檢查是否已安裝
            if not force and install.is_version_installed(version, str(self.minecraft_dir)):
                self.logger.info(f"✅ 版本 {version} 已安裝")
                return
            
            self.logger.info(f"🔽 開始安裝 Minecraft {version}")
            
            def progress_callback(progress):
                print(f"安裝進度: {progress}%", end="\r")
            
            callback = {
                "setProgress": progress_callback,
                "setStatus": lambda status: self.logger.info(f"狀態: {status}"),
                "setMax": lambda max_val: None
            }
            
            await install.install_minecraft_version(
                version,
                str(self.minecraft_dir),
                callback=callback
            )
            
            print()  # 新行
            self.logger.info(f"✅ Minecraft {version} 安裝完成")
            
        except Exception as e:
            self.logger.error(f"❌ 安裝 Minecraft {version} 失敗: {e}")
            raise
    
    async def install_modloader(self, version: str, loader_type: str, loader_version: str = None):
        """安裝模組載入器"""
        try:
            self.logger.info(f"🔽 開始安裝 {loader_type.title()} 載入器")
            
            if loader_type.lower() == "fabric":
                await fabric.install_fabric(
                    version,
                    str(self.minecraft_dir),
                    loader_version=loader_version
                )
            elif loader_type.lower() == "forge":
                if not loader_version:
                    # 獲取推薦版本
                    forge_versions = await forge.list_forge_versions(version)
                    loader_version = forge_versions[0] if forge_versions else None
                
                if loader_version:
                    await forge.install_forge_version(
                        f"{version}-{loader_version}",
                        str(self.minecraft_dir)
                    )
            elif loader_type.lower() == "quilt":
                await quilt.install_quilt(
                    version,
                    str(self.minecraft_dir),
                    loader_version=loader_version
                )
            else:
                raise ValueError(f"不支援的載入器類型: {loader_type}")
            
            self.logger.info(f"✅ {loader_type.title()} 載入器安裝完成")
            
        except Exception as e:
            self.logger.error(f"❌ 安裝 {loader_type} 載入器失敗: {e}")
            raise
    
    async def launch_minecraft(self, version: str, custom_options: Dict = None) -> asyncio.subprocess.Process:
        """啟動 Minecraft"""
        try:
            # 確保有有效的認證
            access_token = await self.get_valid_access_token()
            
            # 獲取玩家資訊
            profile = await mojang.get_minecraft_profile(access_token)
            
            # 創建認證資訊
            credential = _types.Credential(
                access_token=access_token,
                username=profile["name"],
                uuid=profile["id"]
            )
            
            # 準備啟動選項
            default_options = _types.MinecraftOptions(
                game_directory=str(self.minecraft_dir),
                memory=self.config["minecraft"]["memory"],
                jvm_args=self.config["minecraft"]["jvm_args"]
            )
            
            # 合併自訂選項
            if custom_options:
                default_options.update(custom_options)
            
            # 生成啟動指令
            cmd = await command.get_minecraft_command(
                version,
                str(self.minecraft_dir),
                default_options,
                Credential=credential
            )
            
            self.logger.info(f"🚀 啟動 Minecraft {version}")
            self.logger.debug(f"啟動指令: {' '.join(cmd[:5])}...")
            
            # 啟動遊戲
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.minecraft_dir)
            )
            
            self.logger.info(f"✅ Minecraft 已啟動，PID: {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"❌ 啟動 Minecraft 失敗: {e}")
            raise
    
    async def get_available_versions(self) -> List[str]:
        """獲取可用版本列表"""
        try:
            versions = await utils.get_version_list()
            return [v["id"] for v in versions]
        except Exception as e:
            self.logger.error(f"❌ 獲取版本列表失敗: {e}")
            return []
    
    async def get_java_installations(self) -> List[Dict]:
        """獲取 Java 安裝資訊"""
        try:
            java_versions = await java_utils.find_system_java_versions()
            java_info = []
            
            for java_path in java_versions:
                try:
                    info = await java_utils.get_java_information(java_path)
                    java_info.append({
                        "path": java_path,
                        "version": info.version,
                        "architecture": info.architecture
                    })
                except Exception:
                    continue
            
            return java_info
            
        except Exception as e:
            self.logger.error(f"❌ 獲取 Java 資訊失敗: {e}")
            return []
```

## 📦 模組包（Modpack）管理

### mrpack 模組包安裝

```python
import asyncio
from pathlib import Path
from launcher_core import mrpack, install
from launcher_core.setting import setup_logger

class ModpackManager:
    """模組包管理器"""
    
    def __init__(self, minecraft_dir: str):
        self.minecraft_dir = Path(minecraft_dir)
        self.logger = setup_logger(enable_console=True)
    
    async def install_mrpack(self, mrpack_path: str, instance_name: str = None):
        """安裝 mrpack 格式的模組包"""
        try:
            if not instance_name:
                instance_name = Path(mrpack_path).stem
            
            instance_dir = self.minecraft_dir / "instances" / instance_name
            instance_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"🔽 開始安裝模組包: {instance_name}")
            
            # 進度回調
            def progress_callback(current, total, status):
                percentage = (current / total) * 100 if total > 0 else 0
                print(f"\r{status}: {percentage:.1f}% ({current}/{total})", end="")
            
            # 安裝模組包
            await mrpack.install_mrpack(
                mrpack_path,
                str(instance_dir),
                callback={
                    "setProgress": lambda x: None,
                    "setStatus": lambda s: progress_callback(0, 0, s),
                    "setMax": lambda x: None
                }
            )
            
            print()  # 新行
            self.logger.info(f"✅ 模組包 {instance_name} 安裝完成")
            
            return str(instance_dir)
            
        except Exception as e:
            self.logger.error(f"❌ 安裝模組包失敗: {e}")
            raise
    
    async def create_custom_modpack(self, name: str, minecraft_version: str, 
                                  loader_type: str, mods: List[Dict]):
        """創建自訂模組包"""
        try:
            instance_dir = self.minecraft_dir / "instances" / name
            instance_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"🔨 創建自訂模組包: {name}")
            
            # 1. 安裝 Minecraft 基礎版本
            await install.install_minecraft_version(
                minecraft_version,
                str(instance_dir)
            )
            
            # 2. 安裝模組載入器
            if loader_type.lower() == "fabric":
                await fabric.install_fabric(
                    minecraft_version,
                    str(instance_dir)
                )
            elif loader_type.lower() == "forge":
                forge_versions = await forge.list_forge_versions(minecraft_version)
                if forge_versions:
                    await forge.install_forge_version(
                        f"{minecraft_version}-{forge_versions[0]}",
                        str(instance_dir)
                    )
            
            # 3. 下載模組
            mods_dir = instance_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            for mod in mods:
                await self._download_mod(mod, str(mods_dir))
            
            # 4. 創建實例配置
            instance_config = {
                "name": name,
                "minecraft_version": minecraft_version,
                "loader_type": loader_type,
                "mods": mods,
                "created_at": datetime.now().isoformat()
            }
            
            config_file = instance_dir / "instance.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(instance_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 自訂模組包 {name} 創建完成")
            return str(instance_dir)
            
        except Exception as e:
            self.logger.error(f"❌ 創建自訂模組包失敗: {e}")
            raise
    
    async def _download_mod(self, mod_info: Dict, mods_dir: str):
        """下載單個模組"""
        # 這裡可以實現從 CurseForge、Modrinth 等平台下載模組的邏輯
        # 簡化示例
        mod_name = mod_info.get("name", "unknown_mod")
        mod_url = mod_info.get("download_url")
        
        if mod_url:
            # 使用 aiohttp 下載模組文件
            import aiohttp
            import aiofiles
            
            async with aiohttp.ClientSession() as session:
                async with session.get(mod_url) as response:
                    if response.status == 200:
                        filename = mod_info.get("filename", f"{mod_name}.jar")
                        file_path = Path(mods_dir) / filename
                        
                        async with aiofiles.open(file_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        self.logger.info(f"✅ 模組下載完成: {filename}")
                    else:
                        self.logger.error(f"❌ 下載模組失敗: {mod_name}")
    
    async def list_instances(self) -> List[Dict]:
        """列出所有模組包實例"""
        instances_dir = self.minecraft_dir / "instances"
        if not instances_dir.exists():
            return []
        
        instances = []
        for instance_dir in instances_dir.iterdir():
            if instance_dir.is_dir():
                config_file = instance_dir / "instance.json"
                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        config["path"] = str(instance_dir)
                        instances.append(config)
                    except Exception as e:
                        self.logger.warning(f"⚠️ 讀取實例配置失敗: {e}")
        
        return instances
    
    async def delete_instance(self, instance_name: str):
        """刪除模組包實例"""
        instance_dir = self.minecraft_dir / "instances" / instance_name
        if instance_dir.exists():
            import shutil
            shutil.rmtree(instance_dir)
            self.logger.info(f"✅ 模組包實例 {instance_name} 已刪除")
        else:
            self.logger.warning(f"⚠️ 找不到實例: {instance_name}")

# 使用範例
async def modpack_example():
    manager = ModpackManager("./minecraft")
    
    # 安裝 mrpack 格式模組包
    await manager.install_mrpack("example_modpack.mrpack", "my_modpack")
    
    # 創建自訂模組包
    custom_mods = [
        {
            "name": "JEI",
            "download_url": "https://example.com/jei.jar",
            "filename": "jei-1.21.1.jar"
        }
    ]
    
    await manager.create_custom_modpack(
        "My Custom Pack",
        "1.21.1",
        "fabric",
        custom_mods
    )
    
    # 列出所有實例
    instances = await manager.list_instances()
    for instance in instances:
        print(f"實例: {instance['name']} - {instance['minecraft_version']}")

if __name__ == "__main__":
    asyncio.run(modpack_example())
```

## 🔧 配置管理系統

### 高級配置管理

```python
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from launcher_core.config import read_toml_file, write_toml_file
from launcher_core.setting import setup_logger

class ConfigManager:
    """高級配置管理器"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = setup_logger(enable_console=True)
        
        # 配置文件
        self.main_config = self.config_dir / "launcher.toml"
        self.profiles_config = self.config_dir / "profiles.toml"
        self.mods_config = self.config_dir / "mods.toml"
        
        self.config = {}
        self.profiles = {}
        self.mods_config_data = {}
    
    async def initialize(self):
        """初始化配置管理器"""
        await self.load_all_configs()
        await self.ensure_default_configs()
    
    async def load_all_configs(self):
        """載入所有配置文件"""
        try:
            # 載入主配置
            if self.main_config.exists():
                self.config = await read_toml_file(str(self.main_config))
            
            # 載入設定檔配置
            if self.profiles_config.exists():
                self.profiles = await read_toml_file(str(self.profiles_config))
            
            # 載入模組配置
            if self.mods_config.exists():
                self.mods_config_data = await read_toml_file(str(self.mods_config))
            
            self.logger.info("✅ 所有配置文件載入完成")
            
        except Exception as e:
            self.logger.error(f"❌ 載入配置文件失敗: {e}")
            raise
    
    async def ensure_default_configs(self):
        """確保預設配置存在"""
        # 預設主配置
        if not self.config:
            self.config = {
                "launcher": {
                    "name": "Advanced Minecraft Launcher",
                    "version": "2.0.0",
                    "theme": "dark",
                    "language": "zh-TW",
                    "check_updates": True,
                    "close_launcher_on_game_start": False
                },
                "minecraft": {
                    "directory": "./minecraft",
                    "keep_launcher_open": True,
                    "show_snapshots": False,
                    "show_alpha_beta": False,
                    "auto_download_natives": True
                },
                "java": {
                    "auto_detect": True,
                    "memory_min": 1024,
                    "memory_max": 4096,
                    "memory_auto": True,
                    "additional_args": [
                        "-XX:+UseG1GC",
                        "-XX:+UnlockExperimentalVMOptions",
                        "-XX:G1NewSizePercent=20",
                        "-XX:G1ReservePercent=20",
                        "-XX:MaxGCPauseMillis=50",
                        "-XX:G1HeapRegionSize=32M"
                    ]
                },
                "network": {
                    "download_threads": 8,
                    "connection_timeout": 30,
                    "retry_attempts": 3,
                    "use_proxy": False,
                    "proxy_host": "",
                    "proxy_port": 0
                }
            }
            await self.save_main_config()
        
        # 預設設定檔配置
        if not self.profiles:
            self.profiles = {
                "default": {
                    "name": "預設設定檔",
                    "minecraft_version": "latest-release",
                    "modloader": "none",
                    "modloader_version": "",
                    "java_executable": "auto",
                    "memory": 2048,
                    "jvm_args": [],
                    "game_directory": "",
                    "resolution": {
                        "width": 854,
                        "height": 480,
                        "fullscreen": False
                    },
                    "server": {
                        "auto_connect": False,
                        "host": "",
                        "port": 25565
                    }
                }
            }
            await self.save_profiles_config()
        
        # 預設模組配置
        if not self.mods_config_data:
            self.mods_config_data = {
                "repositories": {
                    "curseforge": {
                        "enabled": True,
                        "api_key": ""
                    },
                    "modrinth": {
                        "enabled": True,
                        "api_url": "https://api.modrinth.com/v2"
                    }
                },
                "auto_update": {
                    "enabled": False,
                    "check_interval": 24,  # 小時
                    "notify_only": True
                },
                "mod_sources": []
            }
            await self.save_mods_config()
    
    async def save_main_config(self):
        """保存主配置"""
        try:
            await write_toml_file(str(self.main_config), self.config)
            self.logger.info("✅ 主配置保存成功")
        except Exception as e:
            self.logger.error(f"❌ 保存主配置失敗: {e}")
            raise
    
    async def save_profiles_config(self):
        """保存設定檔配置"""
        try:
            await write_toml_file(str(self.profiles_config), self.profiles)
            self.logger.info("✅ 設定檔配置保存成功")
        except Exception as e:
            self.logger.error(f"❌ 保存設定檔配置失敗: {e}")
            raise
    
    async def save_mods_config(self):
        """保存模組配置"""
        try:
            await write_toml_file(str(self.mods_config), self.mods_config_data)
            self.logger.info("✅ 模組配置保存成功")
        except Exception as e:
            self.logger.error(f"❌ 保存模組配置失敗: {e}")
            raise
    
    def get_config(self, path: str, default: Any = None) -> Any:
        """獲取配置值"""
        keys = path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    async def set_config(self, path: str, value: Any):
        """設置配置值"""
        keys = path.split(".")
        config = self.config
        
        # 導航到最後一層
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 設置值
        config[keys[-1]] = value
        await self.save_main_config()
    
    def create_profile(self, name: str, base_profile: str = "default") -> Dict:
        """創建新的遊戲設定檔"""
        if base_profile in self.profiles:
            new_profile = self.profiles[base_profile].copy()
        else:
            new_profile = self.profiles["default"].copy()
        
        new_profile["name"] = name
        self.profiles[name] = new_profile
        return new_profile
    
    async def save_profile(self, name: str, profile_data: Dict):
        """保存遊戲設定檔"""
        self.profiles[name] = profile_data
        await self.save_profiles_config()
    
    def delete_profile(self, name: str) -> bool:
        """刪除遊戲設定檔"""
        if name == "default":
            return False  # 不能刪除預設設定檔
        
        if name in self.profiles:
            del self.profiles[name]
            return True
        return False
    
    def get_profile(self, name: str) -> Optional[Dict]:
        """獲取遊戲設定檔"""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """列出所有設定檔名稱"""
        return list(self.profiles.keys())
    
    async def export_config(self, export_path: str):
        """匯出完整配置"""
        export_data = {
            "launcher_config": self.config,
            "profiles": self.profiles,
            "mods_config": self.mods_config_data,
            "export_version": "1.0",
            "export_date": datetime.now().isoformat()
        }
        
        await write_toml_file(export_path, export_data)
        self.logger.info(f"✅ 配置已匯出到: {export_path}")
    
    async def import_config(self, import_path: str, merge: bool = True):
        """匯入配置"""
        try:
            imported_data = await read_toml_file(import_path)
            
            if merge:
                # 合併配置
                if "launcher_config" in imported_data:
                    self.config.update(imported_data["launcher_config"])
                if "profiles" in imported_data:
                    self.profiles.update(imported_data["profiles"])
                if "mods_config" in imported_data:
                    self.mods_config_data.update(imported_data["mods_config"])
            else:
                # 完全替換
                if "launcher_config" in imported_data:
                    self.config = imported_data["launcher_config"]
                if "profiles" in imported_data:
                    self.profiles = imported_data["profiles"]
                if "mods_config" in imported_data:
                    self.mods_config_data = imported_data["mods_config"]
            
            # 保存所有配置
            await self.save_main_config()
            await self.save_profiles_config()
            await self.save_mods_config()
            
            self.logger.info(f"✅ 配置已從 {import_path} 匯入")
            
        except Exception as e:
            self.logger.error(f"❌ 匯入配置失敗: {e}")
            raise

# 使用範例
async def config_example():
    config_mgr = ConfigManager("./launcher_config")
    await config_mgr.initialize()
    
    # 修改配置
    await config_mgr.set_config("launcher.theme", "light")
    await config_mgr.set_config("java.memory_max", 8192)
    
    # 創建新設定檔
    profile = config_mgr.create_profile("fabric_1.21.1")
    profile["minecraft_version"] = "1.21.1"
    profile["modloader"] = "fabric"
    profile["memory"] = 4096
    
    await config_mgr.save_profile("fabric_1.21.1", profile)
    
    # 獲取配置值
    theme = config_mgr.get_config("launcher.theme")
    print(f"當前主題: {theme}")
    
    # 匯出配置
    await config_mgr.export_config("./backup_config.toml")

if __name__ == "__main__":
    asyncio.run(config_example())
```

## 🚨 錯誤處理與監控

### 完整的錯誤處理系統

```python
import asyncio
import logging
import traceback
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path

class ErrorHandler:
    """錯誤處理和監控系統"""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 設置日誌
        self.logger = logging.getLogger("ErrorHandler")
        self.logger.setLevel(logging.DEBUG)
        
        # 創建文件處理器
        error_log = self.log_dir / "errors.log"
        file_handler = logging.FileHandler(error_log, encoding="utf-8")
        file_handler.setLevel(logging.ERROR)
        
        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 設置格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 錯誤計數器
        self.error_counts = {}
        self.error_callbacks = []
    
    def add_error_callback(self, callback: Callable[[Dict], None]):
        """添加錯誤回調函數"""
        self.error_callbacks.append(callback)
    
    def handle_error(self, error: Exception, context: str = "", 
                    user_message: str = None, recoverable: bool = True):
        """處理錯誤"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 記錄錯誤
        error_info = {
            "type": error_type,
            "message": error_message,
            "context": context,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
            "recoverable": recoverable,
            "user_message": user_message or f"發生 {error_type} 錯誤"
        }
        
        # 更新錯誤計數
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # 記錄到日誌
        self.logger.error(
            f"{context}: {error_type} - {error_message}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # 調用錯誤回調
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as callback_error:
                self.logger.error(f"錯誤回調函數失敗: {callback_error}")
        
        return error_info
    
    async def handle_async_error(self, coro, context: str = "", 
                                user_message: str = None, 
                                retry_count: int = 0) -> Optional[any]:
        """處理異步操作錯誤，支援重試"""
        for attempt in range(retry_count + 1):
            try:
                if asyncio.iscoroutinefunction(coro):
                    return await coro()
                else:
                    return await coro
                    
            except Exception as e:
                is_last_attempt = attempt == retry_count
                
                if is_last_attempt:
                    self.handle_error(
                        e, 
                        f"{context} (嘗試 {attempt + 1}/{retry_count + 1})",
                        user_message,
                        recoverable=retry_count > 0
                    )
                    raise
                else:
                    self.logger.warning(
                        f"{context} 失敗 (嘗試 {attempt + 1}/{retry_count + 1}): {e}"
                    )
                    await asyncio.sleep(2 ** attempt)  # 指數退避
        
        return None
    
    def get_error_statistics(self) -> Dict:
        """獲取錯誤統計資訊"""
        total_errors = sum(self.error_counts.values())
        return {
            "total_errors": total_errors,
            "error_types": dict(self.error_counts),
            "most_common": max(self.error_counts, key=self.error_counts.get) 
                          if self.error_counts else None
        }
    
    async def generate_error_report(self) -> str:
        """生成錯誤報告"""
        stats = self.get_error_statistics()
        
        report = [
            "=== 錯誤報告 ===",
            f"生成時間: {datetime.now()}",
            f"總錯誤數: {stats['total_errors']}",
            "",
            "錯誤類型統計:"
        ]
        
        for error_type, count in sorted(stats['error_types'].items(), 
                                       key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count}")
        
        if stats['most_common']:
            report.extend([
                "",
                f"最常見錯誤: {stats['most_common']}"
            ])
        
        return "\n".join(report)

# 錯誤處理裝飾器
def handle_errors(error_handler: ErrorHandler, context: str = "", 
                 user_message: str = None, retry_count: int = 0):
    """錯誤處理裝飾器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                return await error_handler.handle_async_error(
                    lambda: func(*args, **kwargs),
                    context=context or func.__name__,
                    user_message=user_message,
                    retry_count=retry_count
                )
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_handler.handle_error(
                        e,
                        context=context or func.__name__,
                        user_message=user_message
                    )
                    raise
            return sync_wrapper
    return decorator

# 使用範例
async def error_handling_example():
    error_handler = ErrorHandler("./logs")
    
    # 添加錯誤回調
    def error_callback(error_info):
        print(f"錯誤通知: {error_info['user_message']}")
    
    error_handler.add_error_callback(error_callback)
    
    # 使用裝飾器
    @handle_errors(error_handler, "下載文件", "文件下載失敗", retry_count=3)
    async def download_file(url):
        # 模擬可能失敗的下載操作
        import random
        if random.random() < 0.7:  # 70% 失敗率
            raise ConnectionError("網路連接失敗")
        return "下載成功"
    
    try:
        result = await download_file("https://example.com/file.jar")
        print(result)
    except Exception as e:
        print(f"最終失敗: {e}")
    
    # 生成錯誤報告
    report = await error_handler.generate_error_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(error_handling_example())
```

## 🔍 完整的啟動器命令行界面

```python
import asyncio
import argparse
import sys
from pathlib import Path

class LauncherCLI:
    """啟動器命令行界面"""
    
    def __init__(self):
        self.launcher = None
        self.config_manager = None
        self.error_handler = ErrorHandler()
    
    async def initialize(self, base_dir: str = "./minecraft_launcher"):
        """初始化啟動器"""
        self.launcher = MinecraftLauncher(base_dir)
        await self.launcher.initialize()
        
        self.config_manager = ConfigManager(f"{base_dir}/config")
        await self.config_manager.initialize()
    
    def create_parser(self):
        """創建命令行解析器"""
        parser = argparse.ArgumentParser(
            description="Advanced Minecraft Launcher",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # 登入命令
        login_parser = subparsers.add_parser("login", help="Microsoft 帳號登入")
        login_parser.add_argument("--device-code", action="store_true", 
                                help="使用設備代碼登入")
        
        # 安裝命令
        install_parser = subparsers.add_parser("install", help="安裝 Minecraft 版本")
        install_parser.add_argument("version", help="要安裝的版本")
        install_parser.add_argument("--force", action="store_true", 
                                  help="強制重新安裝")
        
        # 啟動命令
        launch_parser = subparsers.add_parser("launch", help="啟動 Minecraft")
        launch_parser.add_argument("version", help="要啟動的版本")
        launch_parser.add_argument("--profile", help="使用的設定檔")
        launch_parser.add_argument("--memory", type=int, help="記憶體大小 (MB)")
        
        # 模組載入器命令
        modloader_parser = subparsers.add_parser("modloader", help="安裝模組載入器")
        modloader_parser.add_argument("type", choices=["fabric", "forge", "quilt"])
        modloader_parser.add_argument("version", help="Minecraft 版本")
        modloader_parser.add_argument("--loader-version", help="載入器版本")
        
        # 設定檔管理
        profile_parser = subparsers.add_parser("profile", help="設定檔管理")
        profile_subparsers = profile_parser.add_subparsers(dest="profile_action")
        
        profile_subparsers.add_parser("list", help="列出所有設定檔")
        
        create_profile = profile_subparsers.add_parser("create", help="創建設定檔")
        create_profile.add_argument("name", help="設定檔名稱")
        create_profile.add_argument("--base", default="default", help="基礎設定檔")
        
        # 版本管理
        version_parser = subparsers.add_parser("versions", help="版本管理")
        version_parser.add_argument("--show-snapshots", action="store_true",
                                  help="顯示快照版本")
        
        return parser
    
    async def cmd_login(self, args):
        """處理登入命令"""
        try:
            access_token = await self.launcher.login(args.device_code)
            print(f"✅ 登入成功！玩家: {self.launcher.auth_data['player_name']}")
        except Exception as e:
            self.error_handler.handle_error(e, "登入", "登入失敗")
            return 1
        return 0
    
    async def cmd_install(self, args):
        """處理安裝命令"""
        try:
            await self.launcher.install_minecraft_version(args.version, args.force)
            print(f"✅ Minecraft {args.version} 安裝完成")
        except Exception as e:
            self.error_handler.handle_error(e, "安裝", f"安裝版本 {args.version} 失敗")
            return 1
        return 0
    
    async def cmd_launch(self, args):
        """處理啟動命令"""
        try:
            custom_options = {}
            
            if args.memory:
                custom_options["memory"] = args.memory
            
            if args.profile:
                profile = self.config_manager.get_profile(args.profile)
                if profile:
                    custom_options.update(profile)
                else:
                    print(f"⚠️ 找不到設定檔: {args.profile}")
            
            process = await self.launcher.launch_minecraft(args.version, custom_options)
            print(f"✅ Minecraft {args.version} 已啟動 (PID: {process.pid})")
            
            # 等待遊戲結束
            await process.wait()
            print("🎮 遊戲已結束")
            
        except Exception as e:
            self.error_handler.handle_error(e, "啟動", f"啟動版本 {args.version} 失敗")
            return 1
        return 0
    
    async def cmd_modloader(self, args):
        """處理模組載入器命令"""
        try:
            await self.launcher.install_modloader(
                args.version, 
                args.type, 
                args.loader_version
            )
            print(f"✅ {args.type.title()} 載入器安裝完成")
        except Exception as e:
            self.error_handler.handle_error(
                e, "模組載入器安裝", 
                f"安裝 {args.type} 載入器失敗"
            )
            return 1
        return 0
    
    async def cmd_profile(self, args):
        """處理設定檔命令"""
        if args.profile_action == "list":
            profiles = self.config_manager.list_profiles()
            print("可用設定檔:")
            for profile_name in profiles:
                profile = self.config_manager.get_profile(profile_name)
                print(f"  {profile_name}: {profile.get('minecraft_version', 'N/A')}")
        
        elif args.profile_action == "create":
            profile = self.config_manager.create_profile(args.name, args.base)
            await self.config_manager.save_profile(args.name, profile)
            print(f"✅ 設定檔 {args.name} 創建完成")
        
        return 0
    
    async def cmd_versions(self, args):
        """處理版本命令"""
        try:
            versions = await self.launcher.get_available_versions()
            
            print("可用的 Minecraft 版本:")
            for version in versions[:20]:  # 只顯示前 20 個
                if "snapshot" in version.lower() and not args.show_snapshots:
                    continue
                print(f"  {version}")
            
            if len(versions) > 20:
                print(f"  ... 還有 {len(versions) - 20} 個版本")
            
        except Exception as e:
            self.error_handler.handle_error(e, "獲取版本", "獲取版本列表失敗")
            return 1
        return 0
    
    async def run(self, args_list=None):
        """運行命令行界面"""
        parser = self.create_parser()
        args = parser.parse_args(args_list)
        
        if not args.command:
            parser.print_help()
            return 0
        
        # 初始化啟動器
        await self.initialize()
        
        # 執行對應命令
        command_map = {
            "login": self.cmd_login,
            "install": self.cmd_install,
            "launch": self.cmd_launch,
            "modloader": self.cmd_modloader,
            "profile": self.cmd_profile,
            "versions": self.cmd_versions,
        }
        
        if args.command in command_map:
            return await command_map[args.command](args)
        else:
            print(f"❌ 未知命令: {args.command}")
            return 1

async def main():
    """主函數"""
    cli = LauncherCLI()
    try:
        exit_code = await cli.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生未預期的錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 使用範例總結

這些高級示例展示了如何使用 async-mc-launcher-core 構建功能完整的 Minecraft 啟動器：

1. **完整的啟動器類** - 包含認證、配置、安裝和啟動功能
2. **模組包管理** - 支援 mrpack 和自訂模組包
3. **高級配置管理** - 多層級配置和設定檔系統
4. **錯誤處理與監控** - 完整的錯誤處理和重試機制
5. **命令行界面** - 專業的 CLI 工具

這些範例可以作為構建您自己的 Minecraft 啟動器的基礎，提供了生產環境所需的功能和最佳實踐。

---

更多詳細資訊請參考：
- [API 參考](API-Reference.md) - 完整的 API 文檔
- [配置管理](Configuration.md) - 配置系統詳解
- [故障排除](Troubleshooting.md) - 常見問題解決