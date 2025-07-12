# 故障排除

本指南提供 async-mc-launcher-core 使用過程中常見問題的診斷和解決方案，包括安裝問題、認證錯誤、啟動失敗等常見情況。

## 🔧 通用故障排除步驟

### 診斷工具

```python
import asyncio
import sys
import platform
from pathlib import Path
from launcher_core import utils, java_utils, microsoft_account
from launcher_core.setting import setup_logger

class DiagnosticTool:
    """系統診斷工具"""
    
    def __init__(self):
        self.logger = setup_logger(enable_console=True)
        self.issues = []
        self.warnings = []
    
    async def run_full_diagnosis(self) -> dict:
        """運行完整的系統診斷"""
        self.logger.info("🔍 開始系統診斷...")
        
        diagnosis = {
            "system_info": await self._check_system_info(),
            "python_info": self._check_python_info(),
            "dependencies": await self._check_dependencies(),
            "java_environment": await self._check_java_environment(),
            "minecraft_directory": self._check_minecraft_directory(),
            "network_connectivity": await self._check_network_connectivity(),
            "permissions": self._check_file_permissions(),
            "issues": self.issues,
            "warnings": self.warnings
        }
        
        # 生成診斷報告
        await self._generate_report(diagnosis)
        
        return diagnosis
    
    async def _check_system_info(self) -> dict:
        """檢查系統資訊"""
        try:
            return {
                "platform": platform.platform(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "system": platform.system(),
                "release": platform.release()
            }
        except Exception as e:
            self.issues.append(f"無法獲取系統資訊: {e}")
            return {}
    
    def _check_python_info(self) -> dict:
        """檢查 Python 環境"""
        try:
            python_info = {
                "version": sys.version,
                "executable": sys.executable,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro
                }
            }
            
            # 檢查 Python 版本兼容性
            if sys.version_info < (3, 10):
                self.issues.append(
                    f"Python 版本過舊: {sys.version_info.major}.{sys.version_info.minor}，"
                    f"需要 Python 3.10 或更新版本"
                )
            
            return python_info
            
        except Exception as e:
            self.issues.append(f"無法檢查 Python 資訊: {e}")
            return {}
    
    async def _check_dependencies(self) -> dict:
        """檢查依賴項"""
        required_packages = [
            "aiohttp", "aiofiles", "cryptography", 
            "PyJWT", "tomli-w", "requests-mock"
        ]
        
        installed_packages = {}
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                
                # 嘗試獲取版本
                try:
                    import importlib.metadata
                    version = importlib.metadata.version(package)
                    installed_packages[package] = version
                except:
                    installed_packages[package] = "unknown"
                    
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.issues.append(f"缺少必要依賴項: {', '.join(missing_packages)}")
        
        return {
            "installed": installed_packages,
            "missing": missing_packages,
            "total_required": len(required_packages)
        }
    
    async def _check_java_environment(self) -> dict:
        """檢查 Java 環境"""
        try:
            java_versions = await java_utils.find_system_java_versions()
            
            if not java_versions:
                self.warnings.append("未找到 Java 安裝，某些功能（如 Forge）可能無法使用")
                return {"available": False, "versions": []}
            
            java_info = []
            for java_path in java_versions[:3]:  # 檢查前 3 個
                try:
                    info = await java_utils.get_java_information(java_path)
                    java_info.append({
                        "path": java_path,
                        "version": info.version,
                        "architecture": info.architecture
                    })
                except Exception as e:
                    self.warnings.append(f"Java 路徑檢查失敗 {java_path}: {e}")
            
            return {
                "available": True,
                "count": len(java_versions),
                "versions": java_info
            }
            
        except Exception as e:
            self.warnings.append(f"Java 環境檢查失敗: {e}")
            return {"available": False, "error": str(e)}
    
    def _check_minecraft_directory(self) -> dict:
        """檢查 Minecraft 目錄"""
        try:
            mc_dir = utils.get_minecraft_directory()
            mc_path = Path(mc_dir)
            
            info = {
                "path": str(mc_path),
                "exists": mc_path.exists(),
                "writable": False,
                "subdirectories": {}
            }
            
            if mc_path.exists():
                # 檢查寫入權限
                try:
                    test_file = mc_path / "test_write.tmp"
                    test_file.touch()
                    test_file.unlink()
                    info["writable"] = True
                except Exception:
                    self.issues.append(f"Minecraft 目錄沒有寫入權限: {mc_dir}")
                
                # 檢查子目錄
                subdirs = ["versions", "libraries", "assets", "logs"]
                for subdir in subdirs:
                    subpath = mc_path / subdir
                    info["subdirectories"][subdir] = subpath.exists()
            else:
                self.warnings.append(f"Minecraft 目錄不存在: {mc_dir}")
            
            return info
            
        except Exception as e:
            self.issues.append(f"檢查 Minecraft 目錄失敗: {e}")
            return {}
    
    async def _check_network_connectivity(self) -> dict:
        """檢查網路連接"""
        test_urls = [
            "https://launchermeta.mojang.com/mc/game/version_manifest.json",
            "https://meta.fabricmc.net/v2/versions/game",
            "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml",
            "https://login.microsoftonline.com/"
        ]
        
        connectivity_results = {}
        
        for url in test_urls:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        connectivity_results[url] = {
                            "status": response.status,
                            "accessible": response.status == 200,
                            "error": None
                        }
            except Exception as e:
                connectivity_results[url] = {
                    "status": None,
                    "accessible": False,
                    "error": str(e)
                }
                self.warnings.append(f"無法連接到 {url}: {e}")
        
        accessible_count = sum(1 for result in connectivity_results.values() if result["accessible"])
        
        return {
            "total_tested": len(test_urls),
            "accessible_count": accessible_count,
            "results": connectivity_results
        }
    
    def _check_file_permissions(self) -> dict:
        """檢查文件權限"""
        import os
        
        permissions = {
            "current_directory": {
                "path": os.getcwd(),
                "readable": os.access(os.getcwd(), os.R_OK),
                "writable": os.access(os.getcwd(), os.W_OK),
                "executable": os.access(os.getcwd(), os.X_OK)
            }
        }
        
        # 檢查家目錄權限
        home_dir = Path.home()
        permissions["home_directory"] = {
            "path": str(home_dir),
            "readable": os.access(home_dir, os.R_OK),
            "writable": os.access(home_dir, os.W_OK),
            "executable": os.access(home_dir, os.X_OK)
        }
        
        # 檢查權限問題
        for location, perms in permissions.items():
            if not perms["writable"]:
                self.issues.append(f"{location} 沒有寫入權限: {perms['path']}")
        
        return permissions
    
    async def _generate_report(self, diagnosis: dict):
        """生成診斷報告"""
        report_lines = [
            "=== async-mc-launcher-core 診斷報告 ===",
            f"生成時間: {datetime.now()}",
            "",
            "系統資訊:",
            f"  平台: {diagnosis['system_info'].get('platform', 'Unknown')}",
            f"  架構: {diagnosis['system_info'].get('architecture', 'Unknown')}",
            f"  Python: {diagnosis['python_info'].get('version_info', {}).get('major', '?')}.{diagnosis['python_info'].get('version_info', {}).get('minor', '?')}",
            "",
            "依賴項檢查:",
            f"  已安裝: {len(diagnosis['dependencies'].get('installed', {}))}/{diagnosis['dependencies'].get('total_required', 0)}",
            f"  缺少: {len(diagnosis['dependencies'].get('missing', []))}",
            "",
            "Java 環境:",
            f"  可用: {'是' if diagnosis['java_environment'].get('available', False) else '否'}",
            f"  版本數: {diagnosis['java_environment'].get('count', 0)}",
            "",
            "網路連接:",
            f"  測試連接: {diagnosis['network_connectivity'].get('accessible_count', 0)}/{diagnosis['network_connectivity'].get('total_tested', 0)}",
            ""
        ]
        
        if self.issues:
            report_lines.extend([
                "❌ 發現的問題:",
                *[f"  - {issue}" for issue in self.issues],
                ""
            ])
        
        if self.warnings:
            report_lines.extend([
                "⚠️ 警告:",
                *[f"  - {warning}" for warning in self.warnings],
                ""
            ])
        
        if not self.issues and not self.warnings:
            report_lines.append("✅ 沒有發現問題")
        
        report = "\n".join(report_lines)
        
        # 保存報告
        report_file = f"diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        self.logger.info(f"✅ 診斷報告已保存到: {report_file}")
        print(report)

# 使用範例
async def run_diagnosis():
    tool = DiagnosticTool()
    diagnosis = await tool.run_full_diagnosis()
    return diagnosis

if __name__ == "__main__":
    asyncio.run(run_diagnosis())
```

## 🔐 Microsoft 認證問題

### 常見認證錯誤

#### 1. AccountNotHaveXbox 錯誤

**錯誤訊息**: `AccountNotHaveXbox`
**原因**: Microsoft 帳號沒有 Xbox 資格
**解決方案**:

```python
async def fix_xbox_account_issue():
    """解決 Xbox 帳號問題"""
    print("❌ 您的 Microsoft 帳號沒有 Xbox 資格")
    print("📋 解決步驟:")
    print("1. 前往 https://www.xbox.com/")
    print("2. 使用您的 Microsoft 帳號登入")
    print("3. 完成 Xbox 帳號設置")
    print("4. 確保帳號是免費的 Xbox Live 帳號")
    print("5. 重新嘗試登入")
    
    # 提供自動檢查功能
    input("完成 Xbox 設置後，按 Enter 繼續...")
    
    try:
        from launcher_core import microsoft_account
        result = await microsoft_account.device_code_login()
        print("✅ Xbox 帳號問題已解決")
        return result
    except Exception as e:
        print(f"❌ 仍有問題: {e}")
        raise
```

#### 2. AccountNeedAdultVerification 錯誤

**錯誤訊息**: `AccountNeedAdultVerification`
**原因**: 帳號需要成人驗證
**解決方案**:

```python
async def fix_adult_verification_issue():
    """解決成人驗證問題"""
    print("❌ 您的帳號需要成人驗證")
    print("📋 解決步驟:")
    print("1. 前往 https://account.xbox.com/")
    print("2. 登入您的 Microsoft 帳號")
    print("3. 前往隱私設定")
    print("4. 完成年齡驗證")
    print("5. 如果是未成年帳號，請聯繫監護人")
    print("6. 等待驗證完成（可能需要幾小時）")
```

#### 3. Device Code 過期錯誤

**錯誤訊息**: `DeviceCodeExpiredError`
**原因**: 設備代碼過期（通常 15 分鐘）
**解決方案**:

```python
async def handle_device_code_expiry():
    """處理設備代碼過期"""
    from launcher_core import microsoft_account
    from launcher_core.exceptions import DeviceCodeExpiredError
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 嘗試登入 (第 {attempt + 1} 次)...")
            result = await microsoft_account.device_code_login()
            print("✅ 登入成功")
            return result
            
        except DeviceCodeExpiredError:
            if attempt < max_retries - 1:
                print("⚠️ 設備代碼過期，重新嘗試...")
                await asyncio.sleep(2)
            else:
                print("❌ 多次嘗試後仍然失敗")
                print("💡 建議:")
                print("1. 確保網路連接穩定")
                print("2. 在設備代碼顯示後儘快完成認證")
                print("3. 使用瀏覽器登入方式作為替代")
                raise
```

#### 4. Token 刷新失敗

```python
async def handle_token_refresh_failure(refresh_token: str):
    """處理 Token 刷新失敗"""
    from launcher_core import microsoft_account
    
    try:
        # 嘗試刷新 token
        new_tokens = await microsoft_account.refresh_minecraft_token(refresh_token)
        return new_tokens
        
    except Exception as e:
        print(f"❌ Token 刷新失敗: {e}")
        print("💡 可能的原因:")
        print("1. Refresh Token 已過期")
        print("2. Microsoft 帳號狀態變更")
        print("3. 網路連接問題")
        print("4. Microsoft 服務暫時不可用")
        print("")
        print("🔧 解決方案:")
        print("1. 重新執行完整登入流程")
        print("2. 檢查網路連接")
        print("3. 確認 Microsoft 帳號狀態")
        
        # 提供重新登入選項
        retry = input("是否要重新登入? (y/N): ").lower().strip()
        if retry == 'y':
            return await microsoft_account.device_code_login()
        else:
            raise
```

## ⬇️ 安裝和下載問題

### 網路連接問題

```python
async def diagnose_network_issues():
    """診斷網路連接問題"""
    import aiohttp
    
    test_endpoints = {
        "Mojang API": "https://launchermeta.mojang.com/mc/game/version_manifest.json",
        "Fabric API": "https://meta.fabricmc.net/v2/versions/game",
        "Forge Maven": "https://maven.minecraftforge.net/",
        "Microsoft Auth": "https://login.microsoftonline.com/"
    }
    
    print("🔍 診斷網路連接...")
    
    async with aiohttp.ClientSession() as session:
        for service, url in test_endpoints.items():
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print(f"✅ {service}: 連接正常")
                    else:
                        print(f"⚠️ {service}: HTTP {response.status}")
            except asyncio.TimeoutError:
                print(f"❌ {service}: 連接超時")
                print(f"   💡 建議: 檢查防火牆設定或嘗試使用 VPN")
            except Exception as e:
                print(f"❌ {service}: 連接失敗 - {e}")
    
    print("\n🔧 網路問題解決建議:")
    print("1. 檢查網路連接穩定性")
    print("2. 暫時關閉防火牆或防毒軟體")
    print("3. 嘗試使用手機熱點")
    print("4. 配置代理伺服器（如果需要）")
    print("5. 聯繫網路管理員（企業環境）")
```

### 下載中斷問題

```python
async def handle_download_interruption():
    """處理下載中斷問題"""
    from launcher_core import install
    
    async def robust_install_with_retry(version: str, minecraft_dir: str, max_retries: int = 3):
        """帶重試機制的穩定安裝"""
        for attempt in range(max_retries):
            try:
                print(f"🔄 安裝嘗試 {attempt + 1}/{max_retries}")
                
                # 進度回調
                def progress_callback(current, total, status):
                    if total > 0:
                        percentage = (current / total) * 100
                        print(f"\r{status}: {percentage:.1f}%", end="", flush=True)
                    else:
                        print(f"\r{status}", end="", flush=True)
                
                callback = {
                    "setStatus": lambda s: progress_callback(0, 0, s),
                    "setProgress": lambda p: None,
                    "setMax": lambda m: None
                }
                
                await install.install_minecraft_version(
                    version, minecraft_dir, callback=callback
                )
                
                print(f"\n✅ Minecraft {version} 安裝成功")
                return True
                
            except Exception as e:
                print(f"\n❌ 安裝失敗: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指數退避
                    print(f"⏳ 等待 {wait_time} 秒後重試...")
                    await asyncio.sleep(wait_time)
                else:
                    print("❌ 所有重試都失敗了")
                    print("💡 可能的解決方案:")
                    print("1. 檢查磁碟空間是否足夠")
                    print("2. 確認目標目錄有寫入權限")
                    print("3. 暫時關閉防毒軟體")
                    print("4. 手動清理損壞的下載文件")
                    print("5. 使用不同的網路連接")
                    raise
        
        return False

    # 使用範例
    try:
        await robust_install_with_retry("1.21.1", "./minecraft")
    except Exception as e:
        print(f"安裝最終失敗: {e}")
```

### 檔案損壞問題

```python
async def verify_and_repair_files():
    """驗證和修復損壞的檔案"""
    import hashlib
    from pathlib import Path
    
    async def verify_file_integrity(file_path: str, expected_hash: str = None):
        """驗證檔案完整性"""
        if not Path(file_path).exists():
            return False, "檔案不存在"
        
        if expected_hash:
            try:
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha1(f.read()).hexdigest()
                if file_hash != expected_hash:
                    return False, f"雜湊值不匹配: 期望 {expected_hash}, 得到 {file_hash}"
            except Exception as e:
                return False, f"無法計算雜湊值: {e}"
        
        return True, "檔案完整"
    
    async def repair_corrupted_installation(minecraft_dir: str):
        """修復損壞的 Minecraft 安裝"""
        mc_path = Path(minecraft_dir)
        
        print("🔍 檢查 Minecraft 安裝完整性...")
        
        # 檢查關鍵目錄
        critical_dirs = ["versions", "libraries", "assets"]
        for dir_name in critical_dirs:
            dir_path = mc_path / dir_name
            if not dir_path.exists():
                print(f"❌ 缺少目錄: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 已創建目錄: {dir_name}")
        
        # 檢查版本文件
        versions_dir = mc_path / "versions"
        if versions_dir.exists():
            for version_dir in versions_dir.iterdir():
                if version_dir.is_dir():
                    version_name = version_dir.name
                    jar_file = version_dir / f"{version_name}.jar"
                    json_file = version_dir / f"{version_name}.json"
                    
                    if not jar_file.exists():
                        print(f"❌ 缺少 JAR 檔案: {version_name}")
                    
                    if not json_file.exists():
                        print(f"❌ 缺少 JSON 檔案: {version_name}")
        
        print("✅ 檔案完整性檢查完成")

    # 使用範例
    await repair_corrupted_installation("./minecraft")
```

## 🚀 啟動問題

### Java 相關問題

```python
async def diagnose_java_issues():
    """診斷 Java 相關問題"""
    from launcher_core import java_utils
    
    print("🔍 診斷 Java 環境...")
    
    try:
        # 尋找 Java 安裝
        java_versions = await java_utils.find_system_java_versions()
        
        if not java_versions:
            print("❌ 沒有找到 Java 安裝")
            print("💡 解決方案:")
            print("1. 下載並安裝 Java:")
            print("   - Oracle JDK: https://www.oracle.com/java/technologies/downloads/")
            print("   - OpenJDK: https://adoptium.net/")
            print("   - Microsoft OpenJDK: https://www.microsoft.com/openjdk")
            print("2. 確保 Java 已添加到 PATH 環境變數")
            print("3. 重新啟動終端或電腦")
            return
        
        print(f"✅ 找到 {len(java_versions)} 個 Java 安裝")
        
        # 檢查每個 Java 版本
        for i, java_path in enumerate(java_versions[:3]):
            try:
                java_info = await java_utils.get_java_information(java_path)
                print(f"Java {i+1}:")
                print(f"  路徑: {java_path}")
                print(f"  版本: {java_info.version}")
                print(f"  架構: {java_info.architecture}")
                
                # 檢查版本兼容性
                major_version = int(java_info.version.split('.')[0])
                if major_version < 8:
                    print(f"  ⚠️ 版本過舊，建議使用 Java 8 或更新版本")
                elif major_version >= 17:
                    print(f"  ✅ 版本兼容，支援最新 Minecraft 版本")
                else:
                    print(f"  ✅ 版本兼容")
                
            except Exception as e:
                print(f"Java {i+1}: ❌ 檢查失敗 - {e}")
    
    except Exception as e:
        print(f"❌ Java 診斷失敗: {e}")

async def fix_java_memory_issues():
    """修復 Java 記憶體問題"""
    print("🔧 Java 記憶體問題診斷")
    print("常見記憶體錯誤及解決方案:")
    print("")
    print("1. OutOfMemoryError: Java heap space")
    print("   解決: 增加 -Xmx 參數 (例如: -Xmx4G)")
    print("")
    print("2. OutOfMemoryError: PermGen space")
    print("   解決: 增加 -XX:MaxPermSize=256m (Java 7 及以下)")
    print("")
    print("3. OutOfMemoryError: Metaspace")
    print("   解決: 增加 -XX:MaxMetaspaceSize=512m (Java 8+)")
    print("")
    print("建議的 JVM 參數配置:")
    
    memory_configs = {
        "輕量級 (2GB)": [
            "-Xmx2G", "-Xms1G",
            "-XX:+UseG1GC",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:G1NewSizePercent=20",
            "-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50"
        ],
        "標準 (4GB)": [
            "-Xmx4G", "-Xms2G",
            "-XX:+UseG1GC",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:G1NewSizePercent=20",
            "-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50",
            "-XX:G1HeapRegionSize=16M"
        ],
        "高效能 (8GB)": [
            "-Xmx8G", "-Xms4G",
            "-XX:+UseG1GC",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:G1NewSizePercent=20",
            "-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50",
            "-XX:G1HeapRegionSize=32M",
            "-XX:+DisableExplicitGC"
        ]
    }
    
    for config_name, jvm_args in memory_configs.items():
        print(f"\n{config_name}:")
        print("  " + " ".join(jvm_args))
```

### 模組載入器啟動問題

```python
async def diagnose_modloader_issues():
    """診斷模組載入器問題"""
    
    print("🔍 診斷模組載入器問題...")
    
    common_issues = {
        "Fabric": {
            "symptoms": ["NoClassDefFoundError", "FabricLoader missing", "Mixin errors"],
            "solutions": [
                "確認 Fabric Loader 版本與 Minecraft 版本兼容",
                "檢查模組是否支援當前 Minecraft 版本",
                "移除不兼容的模組",
                "重新安裝 Fabric Loader"
            ]
        },
        "Forge": {
            "symptoms": ["Forge not loading", "Mod loading errors", "CoreMod issues"],
            "solutions": [
                "確認 Forge 版本與 Minecraft 版本匹配",
                "檢查 Java 版本兼容性",
                "清理 mods 目錄中的舊版本模組",
                "檢查模組依賴關係"
            ]
        },
        "Quilt": {
            "symptoms": ["QuiltLoader missing", "Mod compatibility issues"],
            "solutions": [
                "確認 Quilt 版本正確安裝",
                "檢查模組是否與 Quilt 兼容",
                "驗證 Quilt 配置文件"
            ]
        }
    }
    
    for loader, info in common_issues.items():
        print(f"\n{loader} 常見問題:")
        print("症狀:")
        for symptom in info["symptoms"]:
            print(f"  - {symptom}")
        print("解決方案:")
        for solution in info["solutions"]:
            print(f"  - {solution}")

async def fix_mod_conflicts():
    """解決模組衝突"""
    print("🔧 模組衝突診斷和解決")
    print("")
    print("常見模組衝突類型:")
    print("1. 版本不兼容 - 模組版本與 Minecraft/載入器版本不匹配")
    print("2. 依賴缺失 - 缺少必要的前置模組")
    print("3. ID 衝突 - 多個模組使用相同的 ID")
    print("4. 類別衝突 - 模組修改了相同的遊戲類別")
    print("")
    print("解決步驟:")
    print("1. 檢查最新的 crash 報告")
    print("2. 識別衝突的模組")
    print("3. 更新或移除有問題的模組")
    print("4. 安裝缺失的依賴")
    print("5. 逐個添加模組以找出問題源")
    
    # 提供自動檢查工具
    mods_dir = input("請輸入 mods 目錄路徑 (或按 Enter 跳過): ").strip()
    if mods_dir and Path(mods_dir).exists():
        await analyze_mods_directory(mods_dir)

async def analyze_mods_directory(mods_dir: str):
    """分析模組目錄"""
    from pathlib import Path
    import zipfile
    import json
    
    mods_path = Path(mods_dir)
    mod_files = list(mods_path.glob("*.jar"))
    
    print(f"📦 找到 {len(mod_files)} 個模組文件")
    
    mod_info = []
    for mod_file in mod_files:
        try:
            with zipfile.ZipFile(mod_file, 'r') as zip_file:
                # 嘗試讀取 fabric.mod.json
                if 'fabric.mod.json' in zip_file.namelist():
                    with zip_file.open('fabric.mod.json') as f:
                        fabric_info = json.load(f)
                        mod_info.append({
                            "file": mod_file.name,
                            "type": "fabric",
                            "id": fabric_info.get("id", "unknown"),
                            "version": fabric_info.get("version", "unknown"),
                            "minecraft": fabric_info.get("depends", {}).get("minecraft", "unknown")
                        })
                
                # 嘗試讀取 META-INF/mods.toml (Forge)
                elif 'META-INF/mods.toml' in zip_file.namelist():
                    mod_info.append({
                        "file": mod_file.name,
                        "type": "forge",
                        "id": "unknown",
                        "version": "unknown",
                        "minecraft": "unknown"
                    })
                
        except Exception as e:
            print(f"⚠️ 無法讀取模組資訊: {mod_file.name} - {e}")
    
    # 檢查重複 ID
    id_counts = {}
    for mod in mod_info:
        mod_id = mod["id"]
        if mod_id in id_counts:
            id_counts[mod_id].append(mod["file"])
        else:
            id_counts[mod_id] = [mod["file"]]
    
    duplicates = {id: files for id, files in id_counts.items() if len(files) > 1}
    
    if duplicates:
        print("❌ 發現重複的模組 ID:")
        for mod_id, files in duplicates.items():
            print(f"  {mod_id}: {', '.join(files)}")
    else:
        print("✅ 沒有發現 ID 衝突")
```

## 💾 檔案和權限問題

### 權限問題診斷

```python
async def diagnose_permission_issues():
    """診斷檔案權限問題"""
    import os
    from pathlib import Path
    
    print("🔍 檢查檔案權限...")
    
    # 檢查關鍵目錄的權限
    critical_paths = [
        os.getcwd(),  # 當前目錄
        Path.home(),  # 家目錄
        utils.get_minecraft_directory(),  # Minecraft 目錄
    ]
    
    for path in critical_paths:
        path_obj = Path(path)
        print(f"\n檢查路徑: {path}")
        
        if not path_obj.exists():
            print("  ❌ 路徑不存在")
            continue
        
        # 檢查讀取權限
        if os.access(path, os.R_OK):
            print("  ✅ 讀取權限: 正常")
        else:
            print("  ❌ 讀取權限: 缺失")
        
        # 檢查寫入權限
        if os.access(path, os.W_OK):
            print("  ✅ 寫入權限: 正常")
        else:
            print("  ❌ 寫入權限: 缺失")
            print("     💡 解決方案:")
            print("       - Windows: 以管理員身份運行")
            print("       - Linux/macOS: 檢查目錄所有者和權限")
            print("       - 嘗試更改到有寫入權限的目錄")
        
        # 檢查執行權限
        if os.access(path, os.X_OK):
            print("  ✅ 執行權限: 正常")
        else:
            print("  ❌ 執行權限: 缺失")

async def fix_permission_issues():
    """修復權限問題"""
    import stat
    from pathlib import Path
    
    minecraft_dir = utils.get_minecraft_directory()
    mc_path = Path(minecraft_dir)
    
    print(f"🔧 修復 Minecraft 目錄權限: {minecraft_dir}")
    
    try:
        # 確保目錄存在
        mc_path.mkdir(parents=True, exist_ok=True)
        
        # 在 Unix 系統上設置權限
        if os.name != 'nt':  # 非 Windows 系統
            # 設置目錄權限為 755 (所有者：讀寫執行，其他：讀執行)
            mc_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # 設置子目錄權限
            for item in mc_path.rglob("*"):
                if item.is_dir():
                    item.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                else:
                    item.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        
        print("✅ 權限修復完成")
        
    except Exception as e:
        print(f"❌ 權限修復失敗: {e}")
        print("💡 手動解決方案:")
        print("1. 使用 sudo/管理員權限運行啟動器")
        print("2. 將 Minecraft 目錄移動到有權限的位置")
        print("3. 使用 chmod 命令修改權限 (Unix 系統)")
```

## 🌐 網路和代理問題

### 代理配置

```python
async def configure_proxy():
    """配置代理設定"""
    import aiohttp
    
    print("🌐 代理配置助手")
    print("如果您在企業網路或需要代理連接，請配置以下設定:")
    
    proxy_type = input("代理類型 (http/socks5) [http]: ").strip() or "http"
    proxy_host = input("代理主機: ").strip()
    proxy_port = input("代理端口: ").strip()
    proxy_user = input("代理用戶名 (可選): ").strip()
    proxy_pass = input("代理密碼 (可選): ").strip()
    
    if not proxy_host or not proxy_port:
        print("❌ 代理配置不完整")
        return
    
    # 構建代理 URL
    proxy_url = f"{proxy_type}://"
    if proxy_user and proxy_pass:
        proxy_url += f"{proxy_user}:{proxy_pass}@"
    proxy_url += f"{proxy_host}:{proxy_port}"
    
    print(f"📡 測試代理連接: {proxy_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://launchermeta.mojang.com/mc/game/version_manifest.json",
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    print("✅ 代理連接測試成功")
                    
                    # 保存代理配置
                    proxy_config = {
                        "use_proxy": True,
                        "proxy_type": proxy_type,
                        "proxy_host": proxy_host,
                        "proxy_port": int(proxy_port),
                        "proxy_user": proxy_user,
                        "proxy_pass": proxy_pass
                    }
                    
                    print("💾 保存代理配置...")
                    # 這裡可以保存到配置文件
                    return proxy_config
                else:
                    print(f"❌ 代理測試失敗: HTTP {response.status}")
    
    except Exception as e:
        print(f"❌ 代理測試失敗: {e}")
        print("💡 請檢查:")
        print("1. 代理服務器地址和端口是否正確")
        print("2. 代理服務器是否正在運行")
        print("3. 用戶名和密碼是否正確")
        print("4. 代理類型是否匹配")

async def test_connectivity_with_retry():
    """帶重試機制的連接測試"""
    test_urls = [
        "https://launchermeta.mojang.com/mc/game/version_manifest.json",
        "https://meta.fabricmc.net/v2/versions/game"
    ]
    
    async def test_url_with_retry(url: str, max_retries: int = 3):
        """測試單個 URL 的連接性"""
        import aiohttp
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return True, f"成功 (嘗試 {attempt + 1})"
                        else:
                            return False, f"HTTP {response.status}"
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False, "連接超時"
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False, str(e)
        
        return False, "所有重試都失敗"
    
    print("🔍 測試網路連接性 (帶重試)...")
    
    for url in test_urls:
        success, message = await test_url_with_retry(url)
        status = "✅" if success else "❌"
        print(f"{status} {url}: {message}")
```

## 📋 常見錯誤代碼及解決方案

### 錯誤代碼對照表

```python
ERROR_SOLUTIONS = {
    "VersionNotFound": {
        "description": "找不到指定的 Minecraft 版本",
        "solutions": [
            "檢查版本 ID 是否正確",
            "確認網路連接正常",
            "嘗試重新獲取版本列表",
            "檢查版本是否為快照版本（需要開啟快照版本選項）"
        ]
    },
    "UnsupportedVersion": {
        "description": "不支援的版本",
        "solutions": [
            "檢查模組載入器是否支援該 Minecraft 版本",
            "嘗試使用相容的版本",
            "等待模組載入器更新支援"
        ]
    },
    "ExternalProgramError": {
        "description": "外部程式執行錯誤",
        "solutions": [
            "檢查 Java 安裝是否正確",
            "確認 Java 版本兼容性",
            "檢查系統權限",
            "暫時關閉防毒軟體"
        ]
    },
    "XErrNotFound": {
        "description": "找不到指定資源",
        "solutions": [
            "檢查網路連接",
            "確認資源 URL 正確",
            "嘗試使用鏡像下載源",
            "檢查防火牆設定"
        ]
    }
}

def get_error_solution(error_name: str):
    """獲取錯誤解決方案"""
    error_info = ERROR_SOLUTIONS.get(error_name)
    
    if error_info:
        print(f"❌ 錯誤: {error_name}")
        print(f"📝 描述: {error_info['description']}")
        print("🔧 解決方案:")
        for i, solution in enumerate(error_info['solutions'], 1):
            print(f"  {i}. {solution}")
    else:
        print(f"❌ 未知錯誤: {error_name}")
        print("💡 通用解決步驟:")
        print("  1. 檢查網路連接")
        print("  2. 重新啟動應用程式")
        print("  3. 檢查日誌文件")
        print("  4. 嘗試重新安裝")
```

## 🆘 獲得幫助

### 收集診斷資訊

```python
async def collect_debug_info():
    """收集調試資訊以供技術支援"""
    import platform
    import sys
    from datetime import datetime
    
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture()[0]
        },
        "launcher_version": "0.3",  # 從配置中獲取
        "error_logs": [],
        "configuration": {}
    }
    
    # 運行診斷
    diagnostic_tool = DiagnosticTool()
    diagnosis = await diagnostic_tool.run_full_diagnosis()
    debug_info["diagnosis"] = diagnosis
    
    # 保存調試資訊
    debug_file = f"debug_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(debug_info, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📋 調試資訊已保存到: {debug_file}")
    print("📨 提交問題時請附上此文件")
    print("🔗 GitHub Issues: https://github.com/JaydenChao101/async-mc-launcher-core/issues")
    
    return debug_file
```

### 問題報告模板

```python
def generate_issue_template():
    """生成問題報告模板"""
    template = """
## 問題描述
請清楚描述您遇到的問題。

## 重現步驟
1. 
2. 
3. 

## 預期行為
描述您期望發生什麼。

## 實際行為
描述實際發生了什麼。

## 環境資訊
- 作業系統: 
- Python 版本: 
- async-mc-launcher-core 版本: 
- Java 版本: 

## 錯誤訊息
```
請在此貼上完整的錯誤訊息或堆疊追蹤
```

## 額外資訊
請附上任何可能有用的額外資訊，如配置文件、日誌文件等。

## 調試資訊
請附上使用 collect_debug_info() 生成的調試資訊文件。
"""
    
    print("📝 問題報告模板:")
    print(template)
    
    # 保存模板
    with open("issue_template.md", "w", encoding="utf-8") as f:
        f.write(template)
    
    print("💾 模板已保存到 issue_template.md")

if __name__ == "__main__":
    generate_issue_template()
```

## 🔗 有用的連結

- **GitHub Issues**: https://github.com/JaydenChao101/async-mc-launcher-core/issues
- **討論區**: https://github.com/JaydenChao101/async-mc-launcher-core/discussions
- **Java 下載**: https://adoptium.net/
- **Microsoft 帳號問題**: https://support.microsoft.com/account
- **Xbox 支援**: https://support.xbox.com/

---

如果本指南沒有解決您的問題，請使用 `collect_debug_info()` 收集診斷資訊並在 GitHub Issues 中報告問題。