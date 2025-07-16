import pytest
import sys
import os
from unittest.mock import patch
from uuid import uuid4
import datetime
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core.models import *


class TestModels:
    """Test cases for Pydantic models"""

    def test_minecraft_options_creation(self):
        """Test MinecraftOptions model creation and validation"""
        options = MinecraftOptions(
            username="TestPlayer",
            uuid="550e8400-e29b-41d4-a716-446655440000",
            jvmArguments=["-Xmx4G", "-Xms2G"],
            customResolution=True,
            resolutionWidth=1920,
            resolutionHeight=1080
        )

        assert options.username == "TestPlayer"
        assert options.uuid == "550e8400-e29b-41d4-a716-446655440000"
        assert options.jvmArguments == ["-Xmx4G", "-Xms2G"]
        assert options.customResolution is True
        assert options.resolutionWidth == 1920
        assert options.resolutionHeight == 1080

    def test_credential_model(self):
        """Test Credential model"""
        credential = Credential(
            access_token="test_token",
            username="TestUser",
            uuid=str(uuid4()),
            refresh_token="refresh_token"
        )

        assert credential.access_token == "test_token"
        assert credential.username == "TestUser"
        assert credential.refresh_token == "refresh_token"

    def test_launch_profile_creation(self):
        """Test LaunchProfile model creation and validation"""
        credential = Credential(
            access_token="test_token",
            username="TestUser",
            uuid=str(uuid4())
        )

        # Use a temporary directory instead of /test/minecraft
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = LaunchProfile(
                name="Test Profile",
                version="1.20.1",
                game_directory=temp_dir,
                java_executable="/usr/bin/java",
                credential=credential
            )

            assert profile.name == "Test Profile"
            assert profile.version == "1.20.1"
            assert profile.credential.username == "TestUser"

    def test_java_information_model(self):
        """Test JavaInformation model"""
        java_info = JavaInformation(
            path="/usr/lib/jvm/java-17",
            name="OpenJDK 17",
            version="17.0.5",
            javaPath="/usr/lib/jvm/java-17/bin/java",
            is64Bit=True,
            openjdk=True
        )

        assert java_info.name == "OpenJDK 17"
        assert java_info.version == "17.0.5"
        assert java_info.is64Bit is True
        assert java_info.openjdk is True

    def test_server_info_model(self):
        """Test ServerInfo model"""
        server = ServerInfo(
            name="Test Server",
            address="mc.example.com",
            port=25565,
            version="1.20.1",
            description="A test server"
        )

        assert server.name == "Test Server"
        assert server.address == "mc.example.com"
        assert server.port == 25565

    def test_launcher_settings_validation(self):
        """Test LauncherSettings with validation"""
        settings = LauncherSettings(
            theme="dark",
            language="zh-TW",
            concurrent_downloads=8,
            memory_allocation=8192
        )

        assert settings.theme == "dark"
        assert settings.language == "zh-TW"
        assert settings.concurrent_downloads == 8
        assert settings.memory_allocation == 8192

    def test_launcher_settings_validation_errors(self):
        """Test LauncherSettings validation errors"""
        with pytest.raises(ValueError):
            LauncherSettings(concurrent_downloads=0)  # Should be >= 1

        with pytest.raises(ValueError):
            LauncherSettings(memory_allocation=256)  # Should be >= 512

    def test_fabric_loader_model(self):
        """Test FabricLoader model"""
        loader = FabricLoader(
            separator=".",
            build=123,
            maven="net.fabricmc:fabric-loader:0.14.21",
            version="0.14.21",
            stable=True
        )

        assert loader.separator == "."
        assert loader.build == 123
        assert loader.stable is True

    def test_mod_info_model(self):
        """Test ModInfo model"""
        mod = ModInfo(
            id="optifine",
            name="OptiFine",
            version="1.20.1_HD_U_I6",
            description="Minecraft optimization mod",
            author="sp614x",
            enabled=True,
            dependencies=[]
        )

        assert mod.id == "optifine"
        assert mod.name == "OptiFine"
        assert mod.enabled is True
        assert mod.dependencies == []

    def test_download_info_model(self):
        """Test DownloadInfo model"""
        download = DownloadInfo(
            url="https://example.com/file.jar",
            sha1="abc123def456",
            size=1024,
            path="libraries/example.jar"
        )

        assert download.url == "https://example.com/file.jar"
        assert download.sha1 == "abc123def456"
        assert download.size == 1024

    def test_minecraft_news_model(self):
        """Test MinecraftNews model"""
        news = MinecraftNews(
            id="news1",
            title="Minecraft Update",
            content="New features added",
            category="Update",
            published_date=datetime.datetime.now(),
            tags=["update", "features"]
        )

        assert news.id == "news1"
        assert news.title == "Minecraft Update"
        assert news.category == "Update"
        assert "update" in news.tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
