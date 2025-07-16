import pytest
import sys
import os
import platform
import zipfile
import tempfile
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import natives


class TestNativesEnhanced:
    """Enhanced test cases for natives module to improve coverage"""

    def test_get_natives_windows_32bit(self):
        """Test get_natives function on Windows 32-bit"""
        with patch("platform.system", return_value="Windows"):
            with patch("platform.architecture", return_value=("32bit", "")):
                data = {
                    "natives": {
                        "windows": "natives-windows-${arch}"
                    }
                }
                result = natives.get_natives(data)
                assert result == "natives-windows-32"

    def test_get_natives_windows_64bit(self):
        """Test get_natives function on Windows 64-bit"""
        with patch("platform.system", return_value="Windows"):
            with patch("platform.architecture", return_value=("64bit", "")):
                data = {
                    "natives": {
                        "windows": "natives-windows-${arch}"
                    }
                }
                result = natives.get_natives(data)
                assert result == "natives-windows-64"

    def test_get_natives_darwin_64bit(self):
        """Test get_natives function on macOS"""
        with patch("platform.system", return_value="Darwin"):
            with patch("platform.architecture", return_value=("64bit", "")):
                data = {
                    "natives": {
                        "osx": "natives-osx-${arch}"
                    }
                }
                result = natives.get_natives(data)
                assert result == "natives-osx-64"

    def test_get_natives_linux_64bit(self):
        """Test get_natives function on Linux"""
        with patch("platform.system", return_value="Linux"):
            with patch("platform.architecture", return_value=("64bit", "")):
                data = {
                    "natives": {
                        "linux": "natives-linux-${arch}"
                    }
                }
                result = natives.get_natives(data)
                assert result == "natives-linux-64"

    def test_get_natives_no_natives_field(self):
        """Test get_natives function when natives field is missing"""
        data = {
            "name": "some-library",
            "downloads": {}
        }
        result = natives.get_natives(data)
        assert result == ""

    def test_get_natives_missing_platform(self):
        """Test get_natives function when current platform is not in natives"""
        with patch("platform.system", return_value="Windows"):
            data = {
                "natives": {
                    "linux": "natives-linux-${arch}",
                    "osx": "natives-osx-${arch}"
                    # No windows entry
                }
            }
            result = natives.get_natives(data)
            assert result == ""

    def test_get_natives_empty_natives(self):
        """Test get_natives function with empty natives dict"""
        data = {
            "natives": {}
        }
        result = natives.get_natives(data)
        assert result == ""

    @patch("launcher_core.natives.aiofiles.open")
    @patch("launcher_core.natives.zipfile.ZipFile")
    @patch("launcher_core.natives.os.path.isfile")
    @patch("launcher_core.natives.get_library_path")
    async def test_extract_natives_basic(self, mock_get_library_path, mock_isfile, mock_zipfile, mock_aiofiles):
        """Test basic extract_natives functionality"""
        # Mock file system checks
        mock_isfile.return_value = True
        mock_get_library_path.return_value = "/minecraft/libraries/test-natives.jar"

        # Mock zip file
        mock_zip = Mock()
        mock_zip.namelist.return_value = ["native1.dll", "native2.so", "META-INF/file.txt"]
        mock_zip.extract = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        # Mock aiofiles for JSON reading
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"libraries": [{"name": "test-lib", "natives": {"windows": "natives-windows"}}]}'
        mock_aiofiles.return_value.__aenter__.return_value = mock_file

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create version file structure
            versions_dir = Path(temp_dir) / "versions" / "1.20.1"
            versions_dir.mkdir(parents=True)
            version_file = versions_dir / "1.20.1.json"
            version_file.touch()

            extract_dir = Path(temp_dir) / "natives"

            await natives.extract_natives("1.20.1", temp_dir, str(extract_dir))

            # Verify version file check was called
            mock_isfile.assert_called()

    @patch("launcher_core.natives.os.path.isfile")
    async def test_extract_natives_file_not_found(self, mock_isfile):
        """Test extract_natives when version file doesn't exist"""
        mock_isfile.return_value = False

        with tempfile.TemporaryDirectory() as temp_dir:
            extract_dir = Path(temp_dir) / "natives"

            with pytest.raises(natives.VersionNotFound):
                await natives.extract_natives("missing-version", temp_dir, str(extract_dir))

    @patch("launcher_core.natives.aiofiles.open")
    @patch("launcher_core.natives.parse_rule_list")
    @patch("launcher_core.natives.os.path.isfile")
    async def test_extract_natives_with_rules(self, mock_isfile, mock_parse_rule_list, mock_aiofiles):
        """Test extract_natives with rule filtering"""
        mock_isfile.return_value = True
        mock_parse_rule_list.return_value = False  # Rules don't allow this library

        # Mock aiofiles for JSON reading
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"libraries": [{"name": "test-lib", "rules": [{"action": "disallow"}]}]}'
        mock_aiofiles.return_value.__aenter__.return_value = mock_file
        mock_aiofiles.return_value.__aexit__.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create version file structure
            versions_dir = Path(temp_dir) / "versions" / "1.20.1"
            versions_dir.mkdir(parents=True)
            version_file = versions_dir / "1.20.1.json"
            version_file.touch()

            extract_dir = Path(temp_dir) / "natives"

            await natives.extract_natives("1.20.1", temp_dir, str(extract_dir))

            # Should check version file exists and parse rules
            mock_isfile.assert_called()

    @patch("launcher_core.natives.aiofiles.open")
    @patch("launcher_core.natives.os.path.isfile")
    async def test_extract_natives_no_natives_in_library(self, mock_isfile, mock_aiofiles):
        """Test extract_natives when version file exists"""
        mock_isfile.return_value = True

        # Mock aiofiles for JSON reading with valid JSON content
        # Use proper Maven-style library name format that get_library_path expects
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"libraries": [{"name": "org.example:regular-lib:1.0.0", "downloads": {"artifact": {"path": "org/example/regular-lib/1.0.0/regular-lib-1.0.0.jar"}}}]}'
        mock_aiofiles.return_value.__aenter__.return_value = mock_file
        mock_aiofiles.return_value.__aexit__.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create version file structure
            versions_dir = Path(temp_dir) / "versions" / "1.20.1"
            versions_dir.mkdir(parents=True)
            version_file = versions_dir / "1.20.1.json"
            version_file.touch()

            extract_dir = Path(temp_dir) / "natives"

            # Should not raise exception, just process the version
            await natives.extract_natives("1.20.1", temp_dir, str(extract_dir))

    def test_get_natives_all_platforms_coverage(self):
        """Test get_natives function covers all platform branches"""
        platforms = ["Windows", "Darwin", "Linux", "FreeBSD"]

        for platform_name in platforms:
            with patch("platform.system", return_value=platform_name):
                with patch("platform.architecture", return_value=("64bit", "")):
                    data = {
                        "natives": {
                            "windows": "natives-windows-${arch}",
                            "osx": "natives-osx-${arch}",
                            "linux": "natives-linux-${arch}"
                        }
                    }
                    result = natives.get_natives(data)

                    if platform_name == "Windows":
                        assert result == "natives-windows-64"
                    elif platform_name == "Darwin":
                        assert result == "natives-osx-64"
                    elif platform_name == "Linux":
                        assert result == "natives-linux-64"
                    else:
                        # FreeBSD or other platforms should fall back to linux
                        assert result == "natives-linux-64"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
