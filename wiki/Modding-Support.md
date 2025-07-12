# 模組支持

async-mc-launcher-core 提供完整的模組載入器支援，包括 Fabric、Forge 和 Quilt。本指南將詳細介紹如何安裝、配置和管理各種模組載入器。

## 🧵 Fabric 模組載入器

Fabric 是一個輕量級、快速的模組載入器，以其穩定性和快速更新而聞名。

### 基本 Fabric 安裝

```python
import asyncio
from launcher_core import fabric
from launcher_core.setting import setup_logger

async def install_fabric_example():
    """基本 Fabric 安裝示例"""
    logger = setup_logger(enable_console=True)
    
    minecraft_version = "1.21.1"
    minecraft_directory = "./minecraft"
    
    try:
        # 檢查版本支援
        is_supported = await fabric.is_minecraft_version_supported(minecraft_version)
        if not is_supported:
            print(f"❌ Minecraft {minecraft_version} 不支援 Fabric")
            return
        
        print(f"✅ Minecraft {minecraft_version} 支援 Fabric")
        
        # 獲取最新的 Fabric 載入器版本
        latest_loader = await fabric.get_latest_loader_version()
        print(f"最新 Fabric 載入器版本: {latest_loader}")
        
        # 安裝 Fabric
        print("🔽 開始安裝 Fabric...")
        await fabric.install_fabric(
            minecraft_version=minecraft_version,
            minecraft_directory=minecraft_directory
        )
        
        print("✅ Fabric 安裝完成！")
        
    except Exception as e:
        logger.error(f"❌ Fabric 安裝失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(install_fabric_example())
```

### 進階 Fabric 管理

```python
import asyncio
from launcher_core import fabric, install
from launcher_core.setting import setup_logger

class FabricManager:
    """Fabric 模組載入器管理器"""
    
    def __init__(self, minecraft_directory: str = "./minecraft"):
        self.minecraft_dir = minecraft_directory
        self.logger = setup_logger(enable_console=True)
    
    async def get_fabric_info(self):
        """獲取 Fabric 相關資訊"""
        try:
            # 獲取支援的 Minecraft 版本
            all_versions = await fabric.get_all_minecraft_versions()
            stable_versions = await fabric.get_stable_minecraft_versions()
            
            # 獲取載入器版本
            loader_versions = await fabric.get_all_loader_versions()
            
            # 獲取最新版本
            latest_mc = await fabric.get_latest_minecraft_version()
            latest_stable_mc = await fabric.get_latest_stable_minecraft_version()
            latest_loader = await fabric.get_latest_loader_version()
            
            info = {
                "total_minecraft_versions": len(all_versions),
                "stable_minecraft_versions": len(stable_versions),
                "total_loader_versions": len(loader_versions),
                "latest_minecraft": latest_mc,
                "latest_stable_minecraft": latest_stable_mc,
                "latest_loader": latest_loader,
                "recent_stable_versions": stable_versions[:10]  # 最近的 10 個穩定版本
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"❌ 獲取 Fabric 資訊失敗: {e}")
            raise
    
    async def install_fabric_with_progress(self, minecraft_version: str, 
                                         loader_version: str = None):
        """帶進度顯示的 Fabric 安裝"""
        try:
            # 檢查版本支援
            if not await fabric.is_minecraft_version_supported(minecraft_version):
                raise ValueError(f"Minecraft {minecraft_version} 不支援 Fabric")
            
            # 如果沒有指定載入器版本，使用最新版本
            if not loader_version:
                loader_version = await fabric.get_latest_loader_version()
            
            self.logger.info(f"🔽 安裝 Fabric {loader_version} for Minecraft {minecraft_version}")
            
            # 進度回調
            def progress_callback(status):
                print(f"狀態: {status}")
            
            callback = {
                "setStatus": progress_callback,
                "setProgress": lambda x: print(f"進度: {x}%"),
                "setMax": lambda x: None
            }
            
            # 確保 Minecraft 基礎版本已安裝
            if not install.is_version_installed(minecraft_version, self.minecraft_dir):
                self.logger.info(f"🔽 先安裝 Minecraft {minecraft_version}")
                await install.install_minecraft_version(
                    minecraft_version, 
                    self.minecraft_dir,
                    callback=callback
                )
            
            # 安裝 Fabric
            await fabric.install_fabric(
                minecraft_version=minecraft_version,
                minecraft_directory=self.minecraft_dir,
                loader_version=loader_version,
                callback=callback
            )
            
            # 生成的版本 ID 通常是 "minecraft_version-fabric-loader_version"
            fabric_version = f"{minecraft_version}-fabric-{loader_version}"
            self.logger.info(f"✅ Fabric 安裝完成，版本 ID: {fabric_version}")
            
            return fabric_version
            
        except Exception as e:
            self.logger.error(f"❌ Fabric 安裝失敗: {e}")
            raise
    
    async def check_fabric_installation(self, minecraft_version: str) -> bool:
        """檢查 Fabric 是否已安裝"""
        try:
            # 檢查可能的 Fabric 版本 ID
            loader_versions = await fabric.get_all_loader_versions()
            
            for loader in loader_versions[:5]:  # 檢查最新的 5 個版本
                fabric_version = f"{minecraft_version}-fabric-{loader['version']}"
                if install.is_version_installed(fabric_version, self.minecraft_dir):
                    self.logger.info(f"✅ 找到已安裝的 Fabric: {fabric_version}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ 檢查 Fabric 安裝狀態失敗: {e}")
            return False

# 使用範例
async def fabric_management_example():
    manager = FabricManager("./minecraft")
    
    # 獲取 Fabric 資訊
    info = await manager.get_fabric_info()
    print("=== Fabric 資訊 ===")
    print(f"支援的 Minecraft 版本數: {info['total_minecraft_versions']}")
    print(f"穩定版本數: {info['stable_minecraft_versions']}")
    print(f"最新 Minecraft 版本: {info['latest_minecraft']}")
    print(f"最新穩定版本: {info['latest_stable_minecraft']}")
    print(f"最新載入器版本: {info['latest_loader']}")
    
    # 安裝 Fabric
    minecraft_version = "1.21.1"
    fabric_version = await manager.install_fabric_with_progress(minecraft_version)
    
    # 檢查安裝狀態
    is_installed = await manager.check_fabric_installation(minecraft_version)
    print(f"Fabric 安裝狀態: {'已安裝' if is_installed else '未安裝'}")

if __name__ == "__main__":
    asyncio.run(fabric_management_example())
```

## 🔨 Forge 模組載入器

Minecraft Forge 是最古老且功能最豐富的模組載入器，支援大量的模組。

### ⚠️ 重要提醒

根據 Forge 開發者的要求：
> 請不要自動化下載和安裝 Forge。我們的工作由下載頁面的廣告支持。如果您必須自動化此操作，請考慮通過 https://www.patreon.com/LexManos/ 支持該專案。

請在使用自動化安裝前考慮支持 Forge 專案。

### 基本 Forge 安裝

```python
import asyncio
from launcher_core import forge
from launcher_core.setting import setup_logger

async def install_forge_example():
    """基本 Forge 安裝示例"""
    logger = setup_logger(enable_console=True)
    
    minecraft_version = "1.21.1"
    minecraft_directory = "./minecraft"
    
    try:
        # 獲取可用的 Forge 版本
        forge_versions = await forge.list_forge_versions(minecraft_version)
        
        if not forge_versions:
            print(f"❌ Minecraft {minecraft_version} 沒有可用的 Forge 版本")
            return
        
        print(f"找到 {len(forge_versions)} 個 Forge 版本")
        print(f"推薦版本: {forge_versions[0]}")
        
        # 使用推薦版本安裝
        recommended_version = forge_versions[0]
        full_version = f"{minecraft_version}-{recommended_version}"
        
        print(f"🔽 開始安裝 Forge {full_version}")
        
        # 進度回調
        def progress_callback(current, total, status):
            if total > 0:
                percentage = (current / total) * 100
                print(f"\r{status}: {percentage:.1f}%", end="")
            else:
                print(f"\r{status}", end="")
        
        callback = {
            "setStatus": lambda status: progress_callback(0, 0, status),
            "setProgress": lambda progress: None,
            "setMax": lambda max_val: None
        }
        
        await forge.install_forge_version(
            version=full_version,
            minecraft_directory=minecraft_directory,
            callback=callback
        )
        
        print("\n✅ Forge 安裝完成！")
        
    except Exception as e:
        logger.error(f"❌ Forge 安裝失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(install_forge_example())
```

### 進階 Forge 管理

```python
import asyncio
from launcher_core import forge, install, java_utils
from launcher_core.setting import setup_logger

class ForgeManager:
    """Forge 模組載入器管理器"""
    
    def __init__(self, minecraft_directory: str = "./minecraft"):
        self.minecraft_dir = minecraft_directory
        self.logger = setup_logger(enable_console=True)
    
    async def get_forge_versions_info(self, minecraft_version: str):
        """獲取 Forge 版本資訊"""
        try:
            versions = await forge.list_forge_versions(minecraft_version)
            
            if not versions:
                return {
                    "minecraft_version": minecraft_version,
                    "forge_versions": [],
                    "total_versions": 0,
                    "recommended": None,
                    "latest": None
                }
            
            # 通常第一個是推薦版本，最後一個是最新版本
            recommended = versions[0]
            latest = versions[-1] if len(versions) > 1 else versions[0]
            
            return {
                "minecraft_version": minecraft_version,
                "forge_versions": versions,
                "total_versions": len(versions),
                "recommended": recommended,
                "latest": latest
            }
            
        except Exception as e:
            self.logger.error(f"❌ 獲取 Forge 版本資訊失敗: {e}")
            raise
    
    async def install_forge_with_java_check(self, minecraft_version: str, 
                                          forge_version: str = None,
                                          java_path: str = None):
        """安裝 Forge 並檢查 Java 環境"""
        try:
            # 獲取版本資訊
            version_info = await self.get_forge_versions_info(minecraft_version)
            
            if not version_info["forge_versions"]:
                raise ValueError(f"Minecraft {minecraft_version} 沒有可用的 Forge 版本")
            
            # 選擇 Forge 版本
            if not forge_version:
                forge_version = version_info["recommended"]
                self.logger.info(f"使用推薦的 Forge 版本: {forge_version}")
            
            full_version = f"{minecraft_version}-{forge_version}"
            
            # 檢查 Java 環境
            if not java_path:
                java_versions = await java_utils.find_system_java_versions()
                if not java_versions:
                    raise RuntimeError("找不到 Java 安裝，Forge 需要 Java 才能運行")
                
                java_path = java_versions[0]
                self.logger.info(f"使用 Java: {java_path}")
            
            # 驗證 Java 版本
            java_info = await java_utils.get_java_information(java_path)
            self.logger.info(f"Java 版本: {java_info.version}")
            
            # 檢查 Java 版本兼容性
            java_major_version = int(java_info.version.split('.')[0])
            if java_major_version < 8:
                self.logger.warning("⚠️ Java 版本可能過舊，建議使用 Java 8 或更新版本")
            
            # 確保基礎 Minecraft 版本已安裝
            if not install.is_version_installed(minecraft_version, self.minecraft_dir):
                self.logger.info(f"🔽 先安裝 Minecraft {minecraft_version}")
                await install.install_minecraft_version(
                    minecraft_version, 
                    self.minecraft_dir
                )
            
            # 安裝 Forge
            self.logger.info(f"🔽 安裝 Forge {full_version}")
            
            await forge.install_forge_version(
                version=full_version,
                minecraft_directory=self.minecraft_dir,
                java=java_path
            )
            
            self.logger.info(f"✅ Forge {full_version} 安裝完成")
            return full_version
            
        except Exception as e:
            self.logger.error(f"❌ Forge 安裝失敗: {e}")
            raise
    
    async def check_forge_installation(self, minecraft_version: str) -> list:
        """檢查已安裝的 Forge 版本"""
        try:
            installed_versions = []
            
            # 獲取可能的 Forge 版本
            available_versions = await forge.list_forge_versions(minecraft_version)
            
            for forge_ver in available_versions:
                full_version = f"{minecraft_version}-{forge_ver}"
                if install.is_version_installed(full_version, self.minecraft_dir):
                    installed_versions.append(full_version)
            
            return installed_versions
            
        except Exception as e:
            self.logger.error(f"❌ 檢查 Forge 安裝狀態失敗: {e}")
            return []
    
    async def run_forge_installer_manually(self, installer_path: str, 
                                         minecraft_version: str,
                                         java_path: str = None):
        """手動運行 Forge 安裝器"""
        try:
            if not java_path:
                java_versions = await java_utils.find_system_java_versions()
                if not java_versions:
                    raise RuntimeError("找不到 Java 安裝")
                java_path = java_versions[0]
            
            # 運行 Forge 安裝器
            await forge.run_forge_installer(
                installer_path=installer_path,
                minecraft_directory=self.minecraft_dir,
                java=java_path
            )
            
            self.logger.info("✅ Forge 安裝器執行完成")
            
        except Exception as e:
            self.logger.error(f"❌ 運行 Forge 安裝器失敗: {e}")
            raise

# 使用範例
async def forge_management_example():
    manager = ForgeManager("./minecraft")
    
    minecraft_version = "1.21.1"
    
    # 獲取版本資訊
    info = await manager.get_forge_versions_info(minecraft_version)
    print("=== Forge 版本資訊 ===")
    print(f"Minecraft 版本: {info['minecraft_version']}")
    print(f"可用 Forge 版本數: {info['total_versions']}")
    if info['recommended']:
        print(f"推薦版本: {info['recommended']}")
    if info['latest']:
        print(f"最新版本: {info['latest']}")
    
    # 檢查已安裝的版本
    installed = await manager.check_forge_installation(minecraft_version)
    if installed:
        print(f"已安裝的 Forge 版本: {installed}")
    else:
        print("未安裝任何 Forge 版本")
    
    # 安裝 Forge
    if not installed:
        forge_version = await manager.install_forge_with_java_check(minecraft_version)
        print(f"✅ 安裝完成: {forge_version}")

if __name__ == "__main__":
    asyncio.run(forge_management_example())
```

## 🧶 Quilt 模組載入器

Quilt 是 Fabric 的分支，提供額外的功能和改進。

### 基本 Quilt 安裝

```python
import asyncio
from launcher_core import quilt
from launcher_core.setting import setup_logger

async def install_quilt_example():
    """基本 Quilt 安裝示例"""
    logger = setup_logger(enable_console=True)
    
    minecraft_version = "1.21.1"
    minecraft_directory = "./minecraft"
    
    try:
        # 獲取支援的版本
        minecraft_versions = await quilt.get_all_minecraft_versions()
        
        # 檢查版本支援
        supported = any(v["version"] == minecraft_version for v in minecraft_versions)
        if not supported:
            print(f"❌ Minecraft {minecraft_version} 不支援 Quilt")
            return
        
        print(f"✅ Minecraft {minecraft_version} 支援 Quilt")
        
        # 安裝 Quilt
        print("🔽 開始安裝 Quilt...")
        await quilt.install_quilt(
            minecraft_version=minecraft_version,
            minecraft_directory=minecraft_directory
        )
        
        print("✅ Quilt 安裝完成！")
        
    except Exception as e:
        logger.error(f"❌ Quilt 安裝失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(install_quilt_example())
```

### 進階 Quilt 管理

```python
import asyncio
from launcher_core import quilt, install
from launcher_core.setting import setup_logger

class QuiltManager:
    """Quilt 模組載入器管理器"""
    
    def __init__(self, minecraft_directory: str = "./minecraft"):
        self.minecraft_dir = minecraft_directory
        self.logger = setup_logger(enable_console=True)
    
    async def get_quilt_info(self):
        """獲取 Quilt 相關資訊"""
        try:
            minecraft_versions = await quilt.get_all_minecraft_versions()
            
            # 分離穩定版和測試版
            stable_versions = [v for v in minecraft_versions if v.get("stable", False)]
            
            info = {
                "total_minecraft_versions": len(minecraft_versions),
                "stable_versions": len(stable_versions),
                "latest_minecraft": minecraft_versions[0]["version"] if minecraft_versions else None,
                "latest_stable": stable_versions[0]["version"] if stable_versions else None,
                "recent_versions": [v["version"] for v in minecraft_versions[:10]]
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"❌ 獲取 Quilt 資訊失敗: {e}")
            raise
    
    async def install_quilt_with_progress(self, minecraft_version: str, 
                                        loader_version: str = None):
        """帶進度顯示的 Quilt 安裝"""
        try:
            # 檢查版本支援
            minecraft_versions = await quilt.get_all_minecraft_versions()
            supported = any(v["version"] == minecraft_version for v in minecraft_versions)
            
            if not supported:
                raise ValueError(f"Minecraft {minecraft_version} 不支援 Quilt")
            
            self.logger.info(f"🔽 安裝 Quilt for Minecraft {minecraft_version}")
            
            # 進度回調
            def progress_callback(status):
                print(f"狀態: {status}")
            
            callback = {
                "setStatus": progress_callback,
                "setProgress": lambda x: print(f"進度: {x}%"),
                "setMax": lambda x: None
            }
            
            # 確保 Minecraft 基礎版本已安裝
            if not install.is_version_installed(minecraft_version, self.minecraft_dir):
                self.logger.info(f"🔽 先安裝 Minecraft {minecraft_version}")
                await install.install_minecraft_version(
                    minecraft_version, 
                    self.minecraft_dir,
                    callback=callback
                )
            
            # 安裝 Quilt
            await quilt.install_quilt(
                minecraft_version=minecraft_version,
                minecraft_directory=self.minecraft_dir,
                loader_version=loader_version,
                callback=callback
            )
            
            # 生成的版本 ID 通常是 "quilt-loader-version-minecraft_version"
            quilt_version = f"quilt-loader-{loader_version or 'latest'}-{minecraft_version}"
            self.logger.info(f"✅ Quilt 安裝完成，版本 ID: {quilt_version}")
            
            return quilt_version
            
        except Exception as e:
            self.logger.error(f"❌ Quilt 安裝失敗: {e}")
            raise

# 使用範例
async def quilt_management_example():
    manager = QuiltManager("./minecraft")
    
    # 獲取 Quilt 資訊
    info = await manager.get_quilt_info()
    print("=== Quilt 資訊 ===")
    print(f"支援的 Minecraft 版本數: {info['total_minecraft_versions']}")
    print(f"穩定版本數: {info['stable_versions']}")
    print(f"最新版本: {info['latest_minecraft']}")
    print(f"最新穩定版本: {info['latest_stable']}")
    
    # 安裝 Quilt
    minecraft_version = "1.21.1"
    quilt_version = await manager.install_quilt_with_progress(minecraft_version)

if __name__ == "__main__":
    asyncio.run(quilt_management_example())
```

## 🎛️ 統一模組載入器管理

### 通用模組載入器管理器

```python
import asyncio
from typing import List, Dict, Optional
from launcher_core import fabric, forge, quilt, install
from launcher_core.setting import setup_logger

class ModLoaderManager:
    """統一的模組載入器管理器"""
    
    def __init__(self, minecraft_directory: str = "./minecraft"):
        self.minecraft_dir = minecraft_directory
        self.logger = setup_logger(enable_console=True)
        
        # 支援的載入器
        self.supported_loaders = ["fabric", "forge", "quilt"]
    
    async def get_available_loaders(self, minecraft_version: str) -> Dict[str, bool]:
        """檢查指定 Minecraft 版本支援哪些載入器"""
        availability = {}
        
        try:
            # 檢查 Fabric
            fabric_supported = await fabric.is_minecraft_version_supported(minecraft_version)
            availability["fabric"] = fabric_supported
            
            # 檢查 Forge
            forge_versions = await forge.list_forge_versions(minecraft_version)
            availability["forge"] = len(forge_versions) > 0
            
            # 檢查 Quilt
            quilt_versions = await quilt.get_all_minecraft_versions()
            quilt_supported = any(v["version"] == minecraft_version for v in quilt_versions)
            availability["quilt"] = quilt_supported
            
            return availability
            
        except Exception as e:
            self.logger.error(f"❌ 檢查載入器支援狀態失敗: {e}")
            return {loader: False for loader in self.supported_loaders}
    
    async def install_modloader(self, loader_type: str, minecraft_version: str, 
                              loader_version: str = None, 
                              java_path: str = None) -> str:
        """安裝指定的模組載入器"""
        try:
            loader_type = loader_type.lower()
            
            if loader_type not in self.supported_loaders:
                raise ValueError(f"不支援的載入器類型: {loader_type}")
            
            # 檢查支援狀態
            availability = await self.get_available_loaders(minecraft_version)
            if not availability.get(loader_type, False):
                raise ValueError(f"{loader_type.title()} 不支援 Minecraft {minecraft_version}")
            
            self.logger.info(f"🔽 安裝 {loader_type.title()} for Minecraft {minecraft_version}")
            
            # 根據載入器類型執行安裝
            if loader_type == "fabric":
                await fabric.install_fabric(
                    minecraft_version=minecraft_version,
                    minecraft_directory=self.minecraft_dir,
                    loader_version=loader_version
                )
                version_id = f"{minecraft_version}-fabric-{loader_version or 'latest'}"
                
            elif loader_type == "forge":
                if not loader_version:
                    forge_versions = await forge.list_forge_versions(minecraft_version)
                    loader_version = forge_versions[0] if forge_versions else None
                
                if not loader_version:
                    raise ValueError(f"找不到適用於 Minecraft {minecraft_version} 的 Forge 版本")
                
                full_version = f"{minecraft_version}-{loader_version}"
                await forge.install_forge_version(
                    version=full_version,
                    minecraft_directory=self.minecraft_dir,
                    java=java_path
                )
                version_id = full_version
                
            elif loader_type == "quilt":
                await quilt.install_quilt(
                    minecraft_version=minecraft_version,
                    minecraft_directory=self.minecraft_dir,
                    loader_version=loader_version
                )
                version_id = f"quilt-loader-{loader_version or 'latest'}-{minecraft_version}"
            
            self.logger.info(f"✅ {loader_type.title()} 安裝完成，版本 ID: {version_id}")
            return version_id
            
        except Exception as e:
            self.logger.error(f"❌ 安裝 {loader_type} 失敗: {e}")
            raise
    
    async def get_installed_modloaders(self, minecraft_version: str) -> Dict[str, List[str]]:
        """獲取已安裝的模組載入器"""
        installed = {loader: [] for loader in self.supported_loaders}
        
        try:
            # 檢查 Fabric
            fabric_versions = await fabric.get_all_loader_versions()
            for loader in fabric_versions[:10]:  # 檢查最新的 10 個版本
                version_id = f"{minecraft_version}-fabric-{loader['version']}"
                if install.is_version_installed(version_id, self.minecraft_dir):
                    installed["fabric"].append(version_id)
            
            # 檢查 Forge
            forge_versions = await forge.list_forge_versions(minecraft_version)
            for forge_ver in forge_versions[:10]:  # 檢查前 10 個版本
                version_id = f"{minecraft_version}-{forge_ver}"
                if install.is_version_installed(version_id, self.minecraft_dir):
                    installed["forge"].append(version_id)
            
            # 檢查 Quilt（簡化檢查）
            # Quilt 的版本 ID 格式可能因版本而異
            
            return installed
            
        except Exception as e:
            self.logger.error(f"❌ 檢查已安裝的模組載入器失敗: {e}")
            return installed
    
    async def get_loader_recommendations(self, minecraft_version: str) -> Dict[str, str]:
        """獲取載入器推薦版本"""
        recommendations = {}
        
        try:
            availability = await self.get_available_loaders(minecraft_version)
            
            if availability.get("fabric", False):
                latest_fabric = await fabric.get_latest_loader_version()
                recommendations["fabric"] = latest_fabric
            
            if availability.get("forge", False):
                forge_versions = await forge.list_forge_versions(minecraft_version)
                if forge_versions:
                    recommendations["forge"] = forge_versions[0]  # 通常是推薦版本
            
            if availability.get("quilt", False):
                recommendations["quilt"] = "latest"  # Quilt 通常使用最新版本
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ 獲取推薦版本失敗: {e}")
            return {}
    
    def get_loader_comparison(self) -> Dict[str, Dict[str, str]]:
        """獲取載入器比較資訊"""
        return {
            "fabric": {
                "description": "輕量級、快速的模組載入器",
                "advantages": "啟動快速、穩定、更新迅速",
                "disadvantages": "模組生態相對較小",
                "best_for": "輕量化遊戲、快照版本"
            },
            "forge": {
                "description": "功能最豐富的模組載入器",
                "advantages": "模組生態最大、功能強大",
                "disadvantages": "啟動較慢、資源占用較高",
                "best_for": "大型模組包、複雜模組"
            },
            "quilt": {
                "description": "Fabric 的改進版本",
                "advantages": "Fabric 兼容、額外功能",
                "disadvantages": "相對較新、模組較少",
                "best_for": "需要 Fabric 兼容性和額外功能"
            }
        }

# 使用範例
async def modloader_management_example():
    manager = ModLoaderManager("./minecraft")
    
    minecraft_version = "1.21.1"
    
    # 檢查支援的載入器
    availability = await manager.get_available_loaders(minecraft_version)
    print(f"=== Minecraft {minecraft_version} 載入器支援狀況 ===")
    for loader, supported in availability.items():
        status = "✅ 支援" if supported else "❌ 不支援"
        print(f"{loader.title()}: {status}")
    
    # 獲取推薦版本
    recommendations = await manager.get_loader_recommendations(minecraft_version)
    print("\n=== 推薦版本 ===")
    for loader, version in recommendations.items():
        print(f"{loader.title()}: {version}")
    
    # 獲取比較資訊
    comparison = manager.get_loader_comparison()
    print("\n=== 載入器比較 ===")
    for loader, info in comparison.items():
        print(f"{loader.title()}: {info['description']}")
        print(f"  優點: {info['advantages']}")
        print(f"  缺點: {info['disadvantages']}")
        print(f"  適用: {info['best_for']}\n")
    
    # 安裝推薦的載入器（這裡選擇 Fabric）
    if availability.get("fabric", False):
        fabric_version = await manager.install_modloader("fabric", minecraft_version)
        print(f"✅ 安裝完成: {fabric_version}")
    
    # 檢查已安裝的載入器
    installed = await manager.get_installed_modloaders(minecraft_version)
    print("\n=== 已安裝的載入器 ===")
    for loader, versions in installed.items():
        if versions:
            print(f"{loader.title()}: {versions}")

if __name__ == "__main__":
    asyncio.run(modloader_management_example())
```

## 🔧 模組管理最佳實踐

### 1. 版本兼容性檢查

```python
async def check_mod_compatibility(minecraft_version: str, loader_type: str):
    """檢查模組兼容性"""
    manager = ModLoaderManager()
    
    # 檢查載入器支援
    availability = await manager.get_available_loaders(minecraft_version)
    
    if not availability.get(loader_type, False):
        print(f"❌ {loader_type.title()} 不支援 Minecraft {minecraft_version}")
        
        # 建議替代版本
        all_versions = await utils.get_version_list()
        compatible_versions = []
        
        for version in all_versions[:20]:  # 檢查最近 20 個版本
            version_availability = await manager.get_available_loaders(version["id"])
            if version_availability.get(loader_type, False):
                compatible_versions.append(version["id"])
        
        if compatible_versions:
            print(f"建議使用以下版本:")
            for version in compatible_versions[:5]:
                print(f"  - {version}")
    else:
        print(f"✅ {loader_type.title()} 支援 Minecraft {minecraft_version}")
```

### 2. 自動選擇最佳載入器

```python
async def auto_select_best_loader(minecraft_version: str, 
                                 preferences: List[str] = None) -> str:
    """根據偏好自動選擇最佳載入器"""
    if not preferences:
        preferences = ["fabric", "quilt", "forge"]  # 預設偏好順序
    
    manager = ModLoaderManager()
    availability = await manager.get_available_loaders(minecraft_version)
    
    for preferred_loader in preferences:
        if availability.get(preferred_loader, False):
            print(f"✅ 選擇 {preferred_loader.title()} 作為載入器")
            return preferred_loader
    
    raise ValueError(f"沒有找到適用於 Minecraft {minecraft_version} 的載入器")
```

### 3. 批量安裝管理

```python
async def batch_install_modloaders(configurations: List[Dict]):
    """批量安裝多個載入器配置"""
    manager = ModLoaderManager()
    results = []
    
    for config in configurations:
        try:
            minecraft_version = config["minecraft_version"]
            loader_type = config["loader_type"]
            loader_version = config.get("loader_version")
            
            print(f"🔽 安裝 {loader_type.title()} for {minecraft_version}")
            
            version_id = await manager.install_modloader(
                loader_type, minecraft_version, loader_version
            )
            
            results.append({
                "config": config,
                "success": True,
                "version_id": version_id
            })
            
        except Exception as e:
            print(f"❌ 安裝失敗: {e}")
            results.append({
                "config": config,
                "success": False,
                "error": str(e)
            })
    
    return results

# 使用範例
configurations = [
    {"minecraft_version": "1.21.1", "loader_type": "fabric"},
    {"minecraft_version": "1.20.1", "loader_type": "forge"},
    {"minecraft_version": "1.21.1", "loader_type": "quilt"}
]

# results = await batch_install_modloaders(configurations)
```

## 📚 總結

async-mc-launcher-core 提供了完整的模組載入器支援：

1. **Fabric** - 適合追求效能和快速更新的用戶
2. **Forge** - 適合需要大量模組和複雜功能的用戶  
3. **Quilt** - 適合需要 Fabric 兼容性但想要額外功能的用戶

每種載入器都有其優勢，選擇時應考慮：
- 目標 Minecraft 版本的支援狀況
- 需要的模組生態
- 效能要求
- 更新頻率需求

---

更多相關資訊請參考：
- [API 參考 - fabric/forge/quilt 模組](API-Reference.md)
- [高級示例 - 模組包管理](Advanced-Examples.md#📦-模組包modpack管理)
- [配置管理 - 載入器設定](Configuration.md)