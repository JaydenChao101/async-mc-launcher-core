# Minecraft 啟動器核心插件系統

這個插件系統允許開發者輕鬆擴展 Minecraft 啟動器核心的功能，而無需修改核心代碼。

## 特點

- **簡單的插件 API**：易於創建和管理插件
- **事件系統**：允許插件之間通信
- **掛鉤機制**：在關鍵點擴展啟動器功能
- **依賴管理**：處理插件之間的依賴關係
- **異步支持**：完全支持 `async/await` 模式

## 快速入門

### 創建插件

要創建一個插件，需要繼承 `LauncherPlugin` 基類：

```python
from launcher_core.plugins.base import LauncherPlugin

class MyPlugin(LauncherPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "我的第一個啟動器插件"

    async def initialize(self) -> None:
        await super().initialize()  # 必須調用父類方法
        print(f"插件 {self.name} 已初始化")

    async def cleanup(self) -> None:
        await super().cleanup()  # 必須調用父類方法
        print(f"插件 {self.name} 已清理資源")
```

### 處理掛鉤

您可以通過在插件類中定義以 `on_` 開頭的方法來處理掛鉤點：

```python
class MyPlugin(LauncherPlugin):
    # ... 其他必要方法 ...

    async def on_pre_command_generation(self, version: str, options: dict, result: dict) -> None:
        """在生成啟動命令前修改選項"""
        print(f"將為版本 {version} 修改啟動選項")

        # 添加更多 JVM 參數
        if "jvmArguments" in result:
            result["jvmArguments"].append("-Xmx4G")
        else:
            result["jvmArguments"] = ["-Xmx4G"]
```

### 訂閱事件

您可以在插件初始化時訂閱事件：

```python
from launcher_core.plugins.events_types import VersionInstallCompleteEvent

class MyPlugin(LauncherPlugin):
    # ... 其他必要方法 ...

    async def initialize(self) -> None:
        await super().initialize()

        # 獲取事件管理器並訂閱事件
        from launcher_core import plugins
        plugins.EVENT_MANAGER.subscribe(VersionInstallCompleteEvent, self.handle_version_install)

    async def handle_version_install(self, event: VersionInstallCompleteEvent) -> None:
        """處理版本安裝完成事件"""
        if event.success:
            print(f"版本 {event.version} 安裝成功！")
        else:
            print(f"版本 {event.version} 安裝失敗")
```

## 加載插件

在您的應用程序中，您可以這樣加載和使用插件：

```python
import asyncio
from launcher_core.plugins import PluginManager

async def main():
    # 創建插件管理器
    plugin_manager = PluginManager()

    # 添加插件目錄
    plugin_manager.add_plugin_directory("/path/to/plugins")

    # 發現和加載插件
    available_plugins = await plugin_manager.discover_plugins()
    for plugin_class in available_plugins:
        await plugin_manager.load_plugin(plugin_class)

    # 初始化所有插件
    await plugin_manager.initialize_plugins()

    # 使用啟動器功能...

    # 最後關閉插件
    await plugin_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## 可用的掛鉤點

啟動器核心提供了以下標準掛鉤點：

- **版本管理**
  - `pre_version_install`: 在版本安裝前調用
  - `post_version_install`: 在版本安裝後調用

- **命令生成**
  - `pre_command_generation`: 在生成命令前修改選項
  - `post_command_generation`: 在生成命令後修改結果

- **配置文件處理**
  - `pre_profile_load`: 在加載配置文件前調用
  - `post_profile_load`: 在加載配置文件後調用
  - `pre_profile_save`: 在保存配置文件前調用

- **遊戲啟動**
  - `pre_game_launch`: 在啟動遊戲前調用
  - `post_game_launch`: 在啟動遊戲後調用

## 標準事件類型

啟動器核心提供了以下標準事件類型：

- **版本事件**
  - `VersionInstallStartEvent`: 版本安裝開始
  - `VersionInstallProgressEvent`: 版本安裝進度更新
  - `VersionInstallCompleteEvent`: 版本安裝完成

- **遊戲啟動事件**
  - `PreLaunchEvent`: 遊戲啟動前
  - `PostLaunchEvent`: 遊戲啟動後
  - `GameExitEvent`: 遊戲退出

- **配置文件事件**
  - `ProfilesLoadedEvent`: 配置文件加載完成
  - `ProfileAddedEvent`: 添加新配置文件
  - `ProfileModifiedEvent`: 配置文件被修改

- **登錄事件**
  - `LoginStartEvent`: 登錄開始
  - `LoginSuccessEvent`: 登錄成功
  - `LoginFailureEvent`: 登錄失敗
  - `LogoutEvent`: 登出

## 最佳實踐

1. **異步優先**：盡可能使用 `async/await` 模式
2. **錯誤處理**：妥善處理異常，避免影響核心功能
3. **資源清理**：在 `cleanup()` 方法中清理所有資源
4. **版本兼容**：檢查依賴的功能版本
5. **文檔**：為您的插件提供完整文檔
