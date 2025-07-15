"""
完整的配置模型使用示例
演示如何在不同場景中加載和使用 LauncherConfig
"""

import asyncio
import os
from pathlib import Path

# 從配置模組導入必要的類
from launcher_core.config.load_launcher_config import ConfigManager, LauncherConfig
from launcher_core.pydantic_models import MinecraftOptions


async def basic_config_usage():
    """基本配置使用示例"""
    print("=== 基本配置使用 ===")

    # 1. 創建配置管理器
    config_manager = ConfigManager("launcher_config.toml")

    # 2. 加載配置（第一次會創建默認配置）
    config = await config_manager.load_config()

    # 3. 顯示當前配置
    print(f"啟動器名稱: {config.launcher_name}")
    print(f"啟動器版本: {config.launcher_version}")
    print(f"並發下載數: {config.concurrent_downloads}")

    # 4. 更新配置
    await config_manager.update_config(
        launcher_name="我的自定義啟動器",
        concurrent_downloads=8,
        log_level="DEBUG"
    )

    print("✅ 配置已更新")


async def minecraft_options_usage():
    """使用 MinecraftOptions 的示例"""
    print("\n=== Minecraft 選項配置 ===")

    config_manager = ConfigManager("minecraft_config.toml")

    # 創建 Minecraft 選項
    minecraft_opts = MinecraftOptions(
        username="TestPlayer",
        gameDirectory=str(Path.home() / ".minecraft"),
        jvmArguments=["-Xmx4G", "-Xms2G", "-XX:+UseG1GC"],
        launcherName="MyLauncher",
        launcherVersion="1.0.0"
    )

    # 更新配置以包含 Minecraft 選項
    config = await config_manager.update_config(
        minecraft_options=minecraft_opts,
        auto_refresh_token=True,
        remember_credentials=True
    )

    print(f"Minecraft 用戶名: {config.minecraft_options.username}")
    print(f"遊戲目錄: {config.minecraft_options.gameDirectory}")
    print(f"JVM 參數: {config.minecraft_options.jvmArguments}")


async def environment_variable_example():
    """環境變量配置示例"""
    print("\n=== 環境變量配置 ===")

    # 設置一些環境變量（在實際使用中，這些會在啟動前設置）
    os.environ["MC_LAUNCHER_LAUNCHER_NAME"] = "EnvLauncher"
    os.environ["MC_LAUNCHER_CONCURRENT_DOWNLOADS"] = "12"
    os.environ["MC_LAUNCHER_LOG_LEVEL"] = "WARNING"
    os.environ["MC_LAUNCHER_MINECRAFT_OPTIONS__USERNAME"] = "EnvPlayer"

    # 創建配置（環境變量會自動覆蓋默認值）
    config = LauncherConfig()

    print(f"從環境變量加載的啟動器名稱: {config.launcher_name}")
    print(f"從環境變量加載的並發下載數: {config.concurrent_downloads}")
    print(f"從環境變量加載的日誌級別: {config.log_level}")

    # 清理環境變量
    for key in ["MC_LAUNCHER_LAUNCHER_NAME", "MC_LAUNCHER_CONCURRENT_DOWNLOADS",
                "MC_LAUNCHER_LOG_LEVEL", "MC_LAUNCHER_MINECRAFT_OPTIONS__USERNAME"]:
        os.environ.pop(key, None)


async def advanced_config_management():
    """高級配置管理示例"""
    print("\n=== 高級配置管理 ===")

    config_manager = ConfigManager("advanced_config.toml")

    # 1. 創建完整的配置
    config = await config_manager.load_config()

    # 2. 批量更新配置
    updates = {
        "launcher_name": "AdvancedLauncher",
        "launcher_version": "2.0.0",
        "concurrent_downloads": 6,
        "download_timeout": 600,
        "verify_downloads": True,
        "auto_refresh_token": True,
        "remember_credentials": True,
        "log_level": "INFO",
        "proxy_host": "proxy.example.com",
        "proxy_port": 8080
    }

    config = await config_manager.update_config(**updates)

    # 3. 創建複雜的 Minecraft 選項
    minecraft_opts = MinecraftOptions(
        username="AdvancedPlayer",
        gameDirectory=str(Path.home() / "Games" / "Minecraft"),
        jvmArguments=[
            "-Xmx8G",
            "-Xms4G",
            "-XX:+UseG1GC",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:G1NewSizePercent=20"
        ],
        launcherName=config.launcher_name,
        launcherVersion=config.launcher_version,
        customResolution=True,
        resolutionWidth=1920,
        resolutionHeight=1080,
        server="mc.example.com",
        port="25565"
    )

    # 4. 更新 Minecraft 選項
    await config_manager.update_config(minecraft_options=minecraft_opts)

    print("✅ 高級配置設置完成")


def sync_config_access():
    """同步配置訪問示例"""
    print("\n=== 同步配置訪問 ===")

    # 直接從環境變量創建配置（同步方法）
    config = LauncherConfig()

    print(f"啟動器名稱: {config.launcher_name}")
    print(f"並發下載數: {config.concurrent_downloads}")
    print(f"日誌級別: {config.log_level}")


class LauncherApplication:
    """示例啟動器應用程式類"""

    def __init__(self, config_path: str = "app_config.toml"):
        self.config_manager = ConfigManager(config_path)
        self.config: LauncherConfig = None

    async def initialize(self):
        """初始化應用程式"""
        print("\n=== 啟動器應用程式初始化 ===")

        # 加載配置
        self.config = await self.config_manager.load_config()

        # 確保必要的目錄存在
        if self.config.config_directory:
            Path(self.config.config_directory).mkdir(parents=True, exist_ok=True)

        if self.config.cache_directory:
            Path(self.config.cache_directory).mkdir(parents=True, exist_ok=True)

        print(f"✅ {self.config.launcher_name} v{self.config.launcher_version} 初始化完成")
        print(f"   配置目錄: {self.config.config_directory}")
        print(f"   緩存目錄: {self.config.cache_directory}")

    async def update_minecraft_profile(self, username: str, game_dir: str):
        """更新 Minecraft 設定檔"""
        minecraft_opts = MinecraftOptions(
            username=username,
            gameDirectory=game_dir,
            jvmArguments=self.config.minecraft_options.jvmArguments if self.config.minecraft_options else ["-Xmx4G"],
            launcherName=self.config.launcher_name,
            launcherVersion=self.config.launcher_version
        )

        await self.config_manager.update_config(minecraft_options=minecraft_opts)
        self.config = await self.config_manager.load_config(reload=True)

        print(f"✅ Minecraft 設定檔已更新: {username} -> {game_dir}")

    def get_launch_options(self) -> dict:
        """獲取啟動選項"""
        if not self.config.minecraft_options:
            return {}

        return self.config.minecraft_options.model_dump(exclude_none=True)


async def application_example():
    """完整的應用程式使用示例"""
    print("\n=== 完整應用程式示例 ===")

    # 創建啟動器應用程式
    app = LauncherApplication("my_launcher.toml")

    # 初始化
    await app.initialize()

    # 設置配置
    await app.config_manager.update_config(
        config_directory=str(Path.home() / ".my_launcher"),
        cache_directory=str(Path.home() / ".my_launcher" / "cache"),
        concurrent_downloads=4,
        auto_refresh_token=True
    )

    # 更新 Minecraft 設定檔
    await app.update_minecraft_profile(
        username="PlayerOne",
        game_dir=str(Path.home() / ".minecraft")
    )

    # 獲取啟動選項
    launch_opts = app.get_launch_options()
    print(f"啟動選項: {launch_opts}")


async def main():
    """主函數 - 運行所有示例"""
    try:
        await basic_config_usage()
        await minecraft_options_usage()
        await environment_variable_example()
        await advanced_config_management()
        sync_config_access()
        await application_example()

        print("\n🎉 所有配置示例運行完成！")

    except Exception as e:
        print(f"❌ 運行示例時出錯: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
