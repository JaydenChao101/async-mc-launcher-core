"""
Pydantic 模型使用示例
展示如何在其他代碼中使用 launcher_core.pydantic_models
"""

import asyncio
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# 從 pydantic_models 導入所有模型
from launcher_core.pydantic_models import (
    MinecraftOptions,
    Credential,
    LaunchProfile,
    ServerInfo,
    ModInfo,
    LauncherSettings,
    JavaInformation,
    DownloadInfo,
    LibraryInfo,
    LatestMinecraftVersions,
    MinecraftVersionInfo
)


def create_minecraft_options_example():
    """創建 MinecraftOptions 示例"""
    print("=== MinecraftOptions 使用示例 ===")

    # 創建基本的 Minecraft 選項
    minecraft_opts = MinecraftOptions(
        username="TestPlayer",
        uuid="550e8400-e29b-41d4-a716-446655440000",
        gameDirectory=str(Path.home() / ".minecraft"),
        jvmArguments=["-Xmx4G", "-Xms2G", "-XX:+UseG1GC"],
        launcherName="MyCustomLauncher",
        launcherVersion="2.0.0",
        customResolution=True,
        resolutionWidth=1920,
        resolutionHeight=1080
    )

    print(f"用戶名: {minecraft_opts.username}")
    print(f"遊戲目錄: {minecraft_opts.gameDirectory}")
    print(f"JVM 參數: {minecraft_opts.jvmArguments}")
    print(f"解析度: {minecraft_opts.resolutionWidth}x{minecraft_opts.resolutionHeight}")

    # 轉換為字典
    opts_dict = minecraft_opts.model_dump(exclude_none=True)
    print(f"轉換為字典: {opts_dict}")

    return minecraft_opts


def create_login_Credential_example():
    """創建登入憑證示例"""
    print("\n=== Credential 使用示例 ===")

    Credential = Credential(
        access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        refresh_token="refresh_token_example",
        username="TestPlayer",
        uuid=str(uuid4()),
        expires_in=3600,
        token_type="Bearer"
    )

    print(f"用戶名: {Credential.username}")
    print(f"UUID: {Credential.uuid}")
    print(f"令牌類型: {Credential.token_type}")
    print(f"過期時間: {Credential.expires_in} 秒")

    return Credential


def create_launch_profile_example():
    """創建啟動設定檔示例"""
    print("\n=== LaunchProfile 使用示例 ===")

    # 創建 Minecraft 選項
    minecraft_opts = MinecraftOptions(
        username="ProfileUser",
        gameDirectory=str(Path.home() / "Games" / "Minecraft"),
        jvmArguments=["-Xmx8G", "-Xms4G"]
    )

    # 創建登入憑證
    Credential = Credential(
        access_token="access_token_example",
        username="ProfileUser",
        uuid=str(uuid4())
    )

    # 創建完整的啟動設定檔
    profile = LaunchProfile(
        name="我的遊戲設定檔",
        version="1.20.1",
        game_directory=str(Path.home() / "Games" / "Minecraft"),
        java_executable="/usr/bin/java",
        jvm_arguments=["-Xmx8G", "-Xms4G", "-XX:+UseG1GC"],
        game_arguments=["--demo"],
        Credential=Credential,
        minecraft_options=minecraft_opts
    )

    print(f"設定檔名稱: {profile.name}")
    print(f"Minecraft 版本: {profile.version}")
    print(f"Java 路徑: {profile.java_executable}")
    print(f"用戶名: {profile.Credential.username}")
    print(f"遊戲目錄: {profile.minecraft_options.gameDirectory}")

    return profile


def create_server_info_example():
    """創建伺服器信息示例"""
    print("\n=== ServerInfo 使用示例 ===")

    servers = [
        ServerInfo(
            name="Hypixel",
            address="mc.hypixel.net",
            port=25565,
            version="1.8-1.20",
            description="The largest Minecraft server",
            auto_connect=False
        ),
        ServerInfo(
            name="我的私人伺服器",
            address="my.server.com",
            port=25566,
            version="1.20.1",
            description="朋友們的私人伺服器",
            auto_connect=True
        )
    ]

    for server in servers:
        print(f"伺服器: {server.name}")
        print(f"地址: {server.address}:{server.port}")
        print(f"版本: {server.version}")
        print(f"自動連接: {server.auto_connect}")
        print("---")

    return servers


def create_mod_info_example():
    """創建模組信息示例"""
    print("\n=== ModInfo 使用示例 ===")

    mods = [
        ModInfo(
            id="optifine",
            name="OptiFine",
            version="1.20.1_HD_U_I6",
            description="Minecraft 優化模組",
            author="sp614x",
            enabled=True,
            dependencies=[]
        ),
        ModInfo(
            id="jei",
            name="Just Enough Items",
            version="15.2.0.27",
            description="物品查看模組",
            author="mezz",
            enabled=True,
            dependencies=["forge"]
        ),
        ModInfo(
            id="journeymap",
            name="JourneyMap",
            version="5.9.7",
            description="小地圖模組",
            author="techbrew",
            enabled=False,
            dependencies=["forge"]
        )
    ]

    enabled_mods = [mod for mod in mods if mod.enabled]
    print(f"已啟用的模組數量: {len(enabled_mods)}")

    for mod in enabled_mods:
        print(f"模組: {mod.name} v{mod.version}")
        print(f"作者: {mod.author}")
        print(f"依賴: {mod.dependencies}")
        print("---")

    return mods


def create_launcher_settings_example():
    """創建啟動器設定示例"""
    print("\n=== LauncherSettings 使用示例 ===")

    settings = LauncherSettings(
        theme="dark",
        language="zh-TW",
        auto_update=True,
        keep_launcher_open=False,
        show_snapshots=True,
        concurrent_downloads=8,
        memory_allocation=8192
    )

    print(f"主題: {settings.theme}")
    print(f"語言: {settings.language}")
    print(f"自動更新: {settings.auto_update}")
    print(f"並發下載數: {settings.concurrent_downloads}")
    print(f"記憶體分配: {settings.memory_allocation} MB")

    # 驗證設定
    if settings.memory_allocation < 1024:
        print("⚠️ 警告: 記憶體分配過低")
    elif settings.memory_allocation > 16384:
        print("⚠️ 警告: 記憶體分配過高")
    else:
        print("✅ 記憶體分配合理")

    return settings


def create_download_info_example():
    """創建下載信息示例"""
    print("\n=== DownloadInfo 使用示例 ===")

    downloads = [
        DownloadInfo(
            url="https://launcher.mojang.com/v1/objects/abc123/client.jar",
            sha1="abc123def456",
            size=15728640,
            path="versions/1.20.1/1.20.1.jar"
        ),
        DownloadInfo(
            url="https://libraries.minecraft.net/org/lwjgl/lwjgl/3.3.1/lwjgl-3.3.1.jar",
            sha1="def456ghi789",
            size=704512,
            path="libraries/org/lwjgl/lwjgl/3.3.1/lwjgl-3.3.1.jar"
        )
    ]

    total_size = sum(dl.size for dl in downloads if dl.size)
    print(f"總下載大小: {total_size / 1024 / 1024:.2f} MB")

    for dl in downloads:
        filename = Path(dl.path).name if dl.path else "unknown"
        size_mb = dl.size / 1024 / 1024 if dl.size else 0
        print(f"文件: {filename} ({size_mb:.2f} MB)")
        print(f"SHA1: {dl.sha1}")
        print("---")

    return downloads


def create_java_information_example():
    """創建 Java 信息示例"""
    print("\n=== JavaInformation 使用示例 ===")

    java_installations = [
        JavaInformation(
            path="/usr/lib/jvm/java-8-openjdk",
            name="OpenJDK 8",
            version="1.8.0_352",
            javaPath="/usr/lib/jvm/java-8-openjdk/bin/java",
            javawPath=None,
            is64Bit=True,
            openjdk=True
        ),
        JavaInformation(
            path="/usr/lib/jvm/java-17-openjdk",
            name="OpenJDK 17",
            version="17.0.5",
            javaPath="/usr/lib/jvm/java-17-openjdk/bin/java",
            javawPath=None,
            is64Bit=True,
            openjdk=True
        )
    ]

    # 選擇最適合的 Java 版本
    recommended_java = None
    for java in java_installations:
        if "17" in java.version:
            recommended_java = java
            break

    if not recommended_java:
        recommended_java = java_installations[0] if java_installations else None

    if recommended_java:
        print(f"推薦的 Java: {recommended_java.name}")
        print(f"版本: {recommended_java.version}")
        print(f"路徑: {recommended_java.javaPath}")
        print(f"64 位: {recommended_java.is64Bit}")
        print(f"OpenJDK: {recommended_java.openjdk}")

    return java_installations


class LauncherApplication:
    """示例啟動器應用程式類"""

    def __init__(self):
        self.settings = LauncherSettings()
        self.profiles = []
        self.servers = []
        self.mods = []
        self.java_installations = []

    def add_profile(self, profile: LaunchProfile):
        """添加啟動設定檔"""
        self.profiles.append(profile)
        print(f"✅ 已添加設定檔: {profile.name}")

    def add_server(self, server: ServerInfo):
        """添加伺服器"""
        self.servers.append(server)
        print(f"✅ 已添加伺服器: {server.name}")

    def add_mod(self, mod: ModInfo):
        """添加模組"""
        self.mods.append(mod)
        print(f"✅ 已添加模組: {mod.name}")

    def get_enabled_mods(self) -> list[ModInfo]:
        """獲取已啟用的模組"""
        return [mod for mod in self.mods if mod.enabled]

    def get_auto_connect_servers(self) -> list[ServerInfo]:
        """獲取自動連接的伺服器"""
        return [server for server in self.servers if server.auto_connect]

    def export_config(self) -> dict:
        """導出配置"""
        return {
            "settings": self.settings.model_dump(),
            "profiles": [p.model_dump() for p in self.profiles],
            "servers": [s.model_dump() for s in self.servers],
            "mods": [m.model_dump() for m in self.mods]
        }


def main():
    """主函數 - 運行所有示例"""
    print("🚀 Pydantic 模型使用示例\n")

    # 創建各種模型示例
    minecraft_opts = create_minecraft_options_example()
    Credential = create_login_Credential_example()
    profile = create_launch_profile_example()
    servers = create_server_info_example()
    mods = create_mod_info_example()
    settings = create_launcher_settings_example()
    downloads = create_download_info_example()
    java_info = create_java_information_example()

    # 創建完整的啟動器應用程式示例
    print("\n=== 完整應用程式示例 ===")
    app = LauncherApplication()

    # 設置配置
    app.settings = settings

    # 添加設定檔
    app.add_profile(profile)

    # 添加伺服器
    for server in servers:
        app.add_server(server)

    # 添加模組
    for mod in mods:
        app.add_mod(mod)

    # 顯示統計信息
    print(f"\n📊 應用程式統計:")
    print(f"設定檔數量: {len(app.profiles)}")
    print(f"伺服器數量: {len(app.servers)}")
    print(f"模組數量: {len(app.mods)}")
    print(f"已啟用模組: {len(app.get_enabled_mods())}")
    print(f"自動連接伺服器: {len(app.get_auto_connect_servers())}")

    # 導出配置示例
    config = app.export_config()
    print(f"\n💾 配置導出成功，包含 {len(config)} 個主要配置項")

    print("\n🎉 所有 Pydantic 模型示例運行完成！")


if __name__ == "__main__":
    main()
