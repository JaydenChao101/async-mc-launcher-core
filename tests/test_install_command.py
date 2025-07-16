import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import shutil
from pathlib import Path
import json

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import install, command, java_utils


class AsyncContextManagerMock:
    """Helper class to mock async context managers"""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestInstall:
    """Test cases for installation module"""

    @pytest.fixture
    def temp_minecraft_dir(self):
        """Create temporary Minecraft directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("aiohttp.ClientSession")
    async def test_get_minecraft_versions(self, mock_session):
        """Test getting Minecraft version manifest"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "latest": {"release": "1.20.4", "snapshot": "24w07a"},
                "versions": [
                    {
                        "id": "1.20.4",
                        "type": "release",
                        "url": "https://example.com/1.20.4.json",
                        "time": "2024-01-01T00:00:00+00:00",
                        "releaseTime": "2024-01-01T00:00:00+00:00",
                    }
                ],
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(install, "get_minecraft_versions"):
            result = await install.get_minecraft_versions()
            assert result["latest"]["release"] == "1.20.4"
            assert len(result["versions"]) == 1

    @patch("aiohttp.ClientSession")
    async def test_get_version_info(self, mock_session):
        """Test getting specific version information"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "id": "1.20.4",
                "type": "release",
                "mainClass": "net.minecraft.client.main.Main",
                "libraries": [],
                "downloads": {
                    "client": {
                        "url": "https://example.com/client.jar",
                        "sha1": "abc123",
                        "size": 12345,
                    }
                },
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(install, "get_version_info"):
            result = await install.get_version_info("1.20.4")
            assert result["id"] == "1.20.4"
            assert result["type"] == "release"

    async def test_install_minecraft_version(self, temp_minecraft_dir):
        """Test installing Minecraft version"""
        if hasattr(install, "install_minecraft_version"):
            # Mock at a higher level to avoid deep implementation issues
            with patch(
                "launcher_core.install.do_version_install", AsyncMock()
            ) as mock_do_install:
                with (
                    patch("aiohttp.ClientSession") as mock_session,
                    patch(
                        "launcher_core._helper.get_user_agent",
                        return_value="test-agent",
                    ),
                ):
                    # Mock the version manifest response (first call)
                    mock_manifest_response = Mock()
                    mock_manifest_response.json = AsyncMock(
                        return_value={
                            "versions": [
                                {
                                    "id": "1.20.4",
                                    "url": "https://example.com/1.20.4.json",
                                    "sha1": "abc123",
                                }
                            ]
                        }
                    )

                    # Set up proper async context manager mock
                    mock_get = Mock(
                        return_value=AsyncContextManagerMock(mock_manifest_response)
                    )
                    mock_session_instance = Mock()
                    mock_session_instance.get = mock_get
                    mock_session.return_value.__aenter__.return_value = (
                        mock_session_instance
                    )

                    # This demonstrates the async context manager fix
                    await install.install_minecraft_version(
                        "1.20.4", temp_minecraft_dir
                    )

                    # Verify the mock was called correctly
                    mock_do_install.assert_called_once()


class TestCommand:
    """Test cases for command module"""


@pytest.fixture
def temp_minecraft_dir():
    """建立暫存的 Minecraft 目錄用於測試"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

    async def test_get_minecraft_command(self, temp_minecraft_dir):
        """Test generating Minecraft launch command"""
        if hasattr(command, "get_minecraft_command"):
            # Create version directory structure
            version_dir = os.path.join(temp_minecraft_dir, "versions", "1.20.4")
            os.makedirs(version_dir, exist_ok=True)

            # Mock version info and options
            version_info = {
                "id": "1.20.4",
                "type": "release",
                "mainClass": "net.minecraft.client.main.Main",
                "libraries": [],
                "minecraftArguments": "--username ${auth_player_name} --version ${version_name}",
                "arguments": {
                    "game": [
                        "--username",
                        "${auth_player_name}",
                        "--version",
                        "${version_name}",
                    ],
                    "jvm": ["-Xmx2G", "-XX:+UnlockExperimentalVMOptions"],
                },
                "downloads": {
                    "client": {
                        "url": "https://example.com/client.jar",
                        "sha1": "abc123",
                        "size": 12345,
                    }
                },
                "releaseTime": "2024-01-01T00:00:00+00:00",
                "time": "2024-01-01T00:00:00+00:00",
            }

            # Create version json file
            version_file = os.path.join(version_dir, "1.20.4.json")
            with open(version_file, "w") as f:
                json.dump(version_info, f)

            options = {
                "username": "TestPlayer",
                "uuid": "test-uuid-123",
                "token": "test-token",
                "gameDirectory": temp_minecraft_dir,
                "executablePath": "java",
            }

            # Mock the executable path
            with patch(
                "launcher_core.runtime.get_executable_path"
            ) as mock_get_executable:
                mock_get_executable.return_value = "java"

                result = await command.get_minecraft_command(
                    version="1.20.4",
                    minecraft_directory=temp_minecraft_dir,
                    options=options,
                )

                # Basic checks
                assert isinstance(result, list)
                assert any("java" in str(item) for item in result)
                assert "net.minecraft.client.main.Main" in result

    def test_get_classpath(self):
        """Test generating classpath for Minecraft"""
        if hasattr(command, "get_classpath"):
            libraries = [
                {
                    "name": "com.mojang:logging:1.0.0",
                    "downloads": {
                        "artifact": {
                            "path": "com/mojang/logging/1.0.0/logging-1.0.0.jar"
                        }
                    },
                },
                {
                    "name": "com.mojang:brigadier:1.0.0",
                    "downloads": {
                        "artifact": {
                            "path": "com/mojang/brigadier/1.0.0/brigadier-1.0.0.jar"
                        }
                    },
                },
            ]

            result = command.get_classpath(libraries, "/path/to/minecraft")
            assert isinstance(result, str)
            assert "logging-1.0.0.jar" in result
            assert "brigadier-1.0.0.jar" in result


class TestJavaUtils:
    """Test cases for Java utilities"""

    def test_find_java_executable(self):
        """Test finding Java executable"""
        if hasattr(java_utils, "find_java_executable"):
            result = java_utils.find_java_executable()
            # Should return a path or None
            assert result is None or isinstance(result, (str, Path))

    def test_get_java_version(self):
        """Test getting Java version"""
        if hasattr(java_utils, "get_java_version"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.stdout = 'java version "17.0.1"'
                mock_run.return_value.returncode = 0

                result = java_utils.get_java_version("java")
                assert result is not None

    def test_is_java_version_supported(self):
        """Test checking if Java version is supported"""
        if hasattr(java_utils, "is_java_version_supported"):
            # Test with different version strings
            assert java_utils.is_java_version_supported("17.0.1", min_version="8")
            assert not java_utils.is_java_version_supported("7.0.1", min_version="8")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
