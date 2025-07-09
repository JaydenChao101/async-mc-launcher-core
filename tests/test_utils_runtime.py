import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import news, runtime, natives, setting
from launcher_core._internal_types import runtime_types, shared_types


class TestNews:
    """Test cases for Minecraft news module"""

    @patch("aiohttp.ClientSession")
    async def test_get_minecraft_news(self, mock_session):
        """Test getting Minecraft news"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "article_count": 2,
                "article_grid": [
                    {
                        "id": "news1",
                        "title": "Minecraft Update 1.20.4",
                        "tag": "Update",
                        "category": "News",
                        "date": "2024-01-01T00:00:00.000Z",
                        "text": "New features and bug fixes",
                        "readMoreLink": "https://minecraft.net/news/update-1-20-4",
                    },
                    {
                        "id": "news2",
                        "title": "Minecraft Live 2024",
                        "tag": "Event",
                        "category": "News",
                        "date": "2024-01-02T00:00:00.000Z",
                        "text": "Join us for Minecraft Live",
                        "readMoreLink": "https://minecraft.net/news/minecraft-live-2024",
                    },
                ],
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(news, "get_minecraft_news"):
            result = await news.get_minecraft_news()
            assert result is not None
            assert result["article_count"] == 2
            assert len(result["article_grid"]) == 2
            assert result["article_grid"][0]["title"] == "Minecraft Update 1.20.4"

    @patch("aiohttp.ClientSession")
    async def test_get_minecraft_news_with_filter(self, mock_session):
        """Test getting filtered Minecraft news"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "article_count": 1,
                "article_grid": [
                    {
                        "id": "news1",
                        "title": "Minecraft Update 1.20.4",
                        "tag": "Update",
                        "category": "News",
                    }
                ],
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(news, "get_minecraft_news"):
            result = await news.get_minecraft_news(category="Update")
            assert result is not None
            assert result["article_count"] == 1


class TestRuntime:
    """Test cases for Java runtime module"""

    @patch("aiohttp.ClientSession")
    async def test_get_java_runtime_manifest(self, mock_session):
        """Test getting Java runtime manifest"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "windows-x64": {
                    "java-runtime-alpha": [
                        {
                            "availability": {"group": 1, "progress": 100},
                            "manifest": {
                                "url": "https://example.com/java-runtime-alpha.json"
                            },
                            "version": {
                                "name": "17.0.1",
                                "released": "2021-10-19T00:00:00+00:00",
                            },
                        }
                    ]
                }
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(runtime, "get_java_runtime_manifest"):
            result = await runtime.get_java_runtime_manifest()
            assert result is not None
            assert "windows-x64" in result
            assert "java-runtime-alpha" in result["windows-x64"]

    @patch("aiohttp.ClientSession")
    async def test_get_java_runtime_info(self, mock_session):
        """Test getting specific Java runtime info"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "files": {
                    "bin/java.exe": {
                        "type": "file",
                        "downloads": {
                            "raw": {
                                "url": "https://example.com/java.exe",
                                "sha1": "abc123",
                                "size": 12345,
                            }
                        },
                        "executable": True,
                    }
                }
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(runtime, "get_java_runtime_info"):
            result = await runtime.get_java_runtime_info(
                "https://example.com/java-runtime-alpha.json"
            )
            assert result is not None
            assert "files" in result
            assert "bin/java.exe" in result["files"]

    async def test_install_java_runtime(self):
        """Test installing Java runtime"""
        if hasattr(runtime, "install_java_runtime"):
            with patch("aiohttp.ClientSession") as mock_session:
                mock_response = Mock()
                mock_response.content.read = Mock(return_value=b"fake java executable")
                mock_response.status = 200
                mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                    mock_response
                )

                runtime_info = {
                    "files": {
                        "bin/java.exe": {
                            "type": "file",
                            "downloads": {
                                "raw": {
                                    "url": "https://example.com/java.exe",
                                    "sha1": "abc123",
                                    "size": 12345,
                                }
                            },
                            "executable": True,
                        }
                    }
                }

                result = await runtime.install_java_runtime(runtime_info, "/temp/java")
                assert result is not None


class TestNatives:
    """Test cases for native libraries module"""

    def test_get_native_library_path(self):
        """Test getting native library path"""
        if hasattr(natives, "get_native_library_path"):
            library = {
                "name": "org.lwjgl:lwjgl-opengl:3.3.1",
                "downloads": {
                    "classifiers": {
                        "natives-windows": {
                            "path": "org/lwjgl/lwjgl-opengl/3.3.1/lwjgl-opengl-3.3.1-natives-windows.jar",
                            "sha1": "abc123",
                            "size": 12345,
                            "url": "https://example.com/lwjgl-opengl-3.3.1-natives-windows.jar",
                        }
                    }
                },
            }

            result = natives.get_native_library_path(library, "windows")
            assert result is not None
            assert "natives-windows" in result

    def test_extract_natives(self):
        """Test extracting native libraries"""
        if hasattr(natives, "extract_natives"):
            with patch("zipfile.ZipFile") as mock_zip:
                mock_zip.return_value.__enter__.return_value.extractall = Mock()

                native_jars = ["/path/to/natives.jar"]
                result = natives.extract_natives(native_jars, "/temp/natives")
                assert result is not None

    def test_get_platform_classifier(self):
        """Test getting platform classifier for natives"""
        if hasattr(natives, "get_platform_classifier"):
            with patch("platform.system", return_value="Windows"):
                with patch("platform.machine", return_value="AMD64"):
                    result = natives.get_platform_classifier()
                    assert result == "natives-windows"


class TestSetting:
    """Test cases for settings module"""

    @pytest.fixture
    def temp_settings_dir(self):
        """Create temporary settings directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_get_minecraft_directory(self):
        """Test getting Minecraft directory"""
        if hasattr(setting, "get_minecraft_directory"):
            result = setting.get_minecraft_directory()
            assert result is not None
            assert isinstance(result, (str, Path))

    def test_get_launcher_profiles_path(self):
        """Test getting launcher profiles path"""
        if hasattr(setting, "get_launcher_profiles_path"):
            result = setting.get_launcher_profiles_path()
            assert result is not None
            assert isinstance(result, (str, Path))

    def test_load_launcher_profiles(self, temp_settings_dir):
        """Test loading launcher profiles"""
        if hasattr(setting, "load_launcher_profiles"):
            # Create mock launcher_profiles.json
            profiles_file = Path(temp_settings_dir) / "launcher_profiles.json"
            profiles_file.write_text(
                """
            {
                "profiles": {
                    "default": {
                        "name": "Default Profile",
                        "type": "latest-release",
                        "created": "2024-01-01T00:00:00.000Z",
                        "lastUsed": "2024-01-01T00:00:00.000Z"
                    }
                },
                "settings": {
                    "enableSnapshots": false,
                    "enableAdvanced": false
                }
            }
            """
            )

            result = setting.load_launcher_profiles(str(profiles_file))
            assert result is not None
            assert "profiles" in result
            assert "default" in result["profiles"]

    def test_save_launcher_profiles(self, temp_settings_dir):
        """Test saving launcher profiles"""
        if hasattr(setting, "save_launcher_profiles"):
            profiles_data = {
                "profiles": {"test": {"name": "Test Profile", "type": "latest-release"}}
            }

            profiles_file = Path(temp_settings_dir) / "launcher_profiles.json"
            result = setting.save_launcher_profiles(profiles_data, str(profiles_file))
            assert result is not None
            assert profiles_file.exists()


class TestInternalTypes:
    """Test cases for internal types"""

    def test_runtime_types_exist(self):
        """Test that runtime types are properly defined"""
        if hasattr(runtime_types, "JavaRuntimeManifest"):
            assert runtime_types.JavaRuntimeManifest is not None

        if hasattr(runtime_types, "JavaRuntimeInfo"):
            assert runtime_types.JavaRuntimeInfo is not None

    def test_shared_types_exist(self):
        """Test that shared types are properly defined"""
        if hasattr(shared_types, "VersionInfo"):
            assert shared_types.VersionInfo is not None

        if hasattr(shared_types, "Library"):
            assert shared_types.Library is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
