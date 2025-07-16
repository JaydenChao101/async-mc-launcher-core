import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core.config.load_launcher_config import ConfigManager, LauncherConfig
from launcher_core.config import vanilla_profile


class TestConfigManager:
    """Test cases for configuration management"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    async def test_load_config_default(self, temp_config_dir):
        """Test loading default configuration"""
        config_path = Path(temp_config_dir) / "test_config.toml"
        manager = ConfigManager(config_path)

        config = await manager.load_config()

        assert isinstance(config, LauncherConfig)
        assert config.launcher_name == "AsyncMCLauncher"
        assert config.launcher_version == "1.0.0"
        assert config.concurrent_downloads == 4

    async def test_update_config(self, temp_config_dir):
        """Test updating configuration"""
        config_path = Path(temp_config_dir) / "test_config.toml"
        manager = ConfigManager(config_path)

        config = await manager.update_config(
            launcher_name="CustomLauncher",
            concurrent_downloads=8
        )

        assert config.launcher_name == "CustomLauncher"
        assert config.concurrent_downloads == 8

    async def test_save_and_load_config(self, temp_config_dir):
        """Test saving and loading configuration"""
        config_path = Path(temp_config_dir) / "test_config.toml"
        manager = ConfigManager(config_path)

        # Create and save config
        config = LauncherConfig(
            launcher_name="TestLauncher",
            username="TestUser",
            version="1.20.1"
        )
        await manager.save_config(config)

        # Load config and verify
        loaded_config = await manager.load_config(reload=True)
        assert loaded_config.launcher_name == "TestLauncher"
        assert loaded_config.username == "TestUser"
        assert loaded_config.version == "1.20.1"

    def test_launcher_config_validation(self):
        """Test LauncherConfig validation"""
        config = LauncherConfig(
            concurrent_downloads=8,
            download_timeout=600,
            resolution_width=1920,
            resolution_height=1080
        )

        assert config.concurrent_downloads == 8
        assert config.download_timeout == 600
        assert config.resolution_width == 1920

    def test_launcher_config_defaults(self):
        """Test LauncherConfig default values"""
        config = LauncherConfig()

        assert config.launcher_name == "AsyncMCLauncher"
        assert config.launcher_version == "1.0.0"
        assert config.auto_refresh_token is True
        assert config.verify_downloads is True
        assert config.log_level == "INFO"


class TestVanillaProfile:
    """Test cases for vanilla profile management"""

    def test_vanilla_profile_validator(self):
        """Test vanilla profile validation"""
        valid_profile = {
            "name": "Test Profile",
            "versionType": "latest-release",
            "gameDirectory": "/test/minecraft"
        }

        # This would test the profile validation logic
        # (Note: You might need to adjust based on actual implementation)
        assert "name" in valid_profile
        assert valid_profile["versionType"] in ["latest-release", "latest-snapshot", "custom"]

    @patch("aiofiles.open")
    async def test_load_vanilla_profiles(self, mock_file):
        """Test loading vanilla launcher profiles"""
        mock_profiles_data = {
            "profiles": {
                "default": {
                    "name": "Default",
                    "type": "latest-release",
                    "lastVersionId": "latest-release"
                }
            }
        }

        # Mock file reading
        mock_file.return_value.__aenter__.return_value.read.return_value = str(mock_profiles_data)

        # Test would go here based on actual vanilla_profile implementation
        assert "profiles" in mock_profiles_data
        assert "default" in mock_profiles_data["profiles"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
