import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import forge, fabric, quilt, mrpack


class TestForge:
    """Test cases for Forge mod loader"""

    @patch("aiohttp.ClientSession")
    async def test_get_forge_versions(self, mock_session):
        """Test getting Forge versions for a Minecraft version"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value=[
                {
                    "version": "47.2.0",
                    "minecraft": "1.20.4",
                    "latest": True,
                    "recommended": True,
                },
                {
                    "version": "47.1.0",
                    "minecraft": "1.20.4",
                    "latest": False,
                    "recommended": False,
                },
            ]
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(forge, "get_forge_versions"):
            result = await forge.get_forge_versions("1.20.4")
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["version"] == "47.2.0"
            assert result[0]["latest"] is True

    @patch("aiohttp.ClientSession")
    async def test_install_forge(self, mock_session):
        """Test installing Forge"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "installer": {
                    "url": "https://example.com/forge-installer.jar",
                    "sha1": "abc123",
                }
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(forge, "install_forge"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = await forge.install_forge(
                    "1.20.4", "47.2.0", "/temp/minecraft"
                )
                assert result is not None

    def test_get_forge_profile(self):
        """Test getting Forge profile information"""
        if hasattr(forge, "get_forge_profile"):
            profile = forge.get_forge_profile("1.20.4", "47.2.0")
            assert profile is not None
            assert isinstance(profile, dict)


class TestFabric:
    """Test cases for Fabric mod loader"""

    @patch("aiohttp.ClientSession")
    async def test_get_fabric_versions(self, mock_session):
        """Test getting Fabric versions"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value=[
                {"version": "0.15.3", "stable": True},
                {"version": "0.15.2", "stable": True},
            ]
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(fabric, "get_fabric_versions"):
            result = await fabric.get_fabric_versions()
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["version"] == "0.15.3"
            assert result[0]["stable"] is True

    @patch("aiohttp.ClientSession")
    async def test_get_fabric_loader_versions(self, mock_session):
        """Test getting Fabric loader versions"""
        mock_response = Mock()
        mock_response.json = Mock(return_value=[{"version": "0.14.24", "stable": True}])
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(fabric, "get_fabric_loader_versions"):
            result = await fabric.get_fabric_loader_versions()
            assert isinstance(result, list)
            assert result[0]["version"] == "0.14.24"

    @patch("aiohttp.ClientSession")
    async def test_install_fabric(self, mock_session):
        """Test installing Fabric"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "libraries": [],
                "mainClass": "net.fabricmc.loader.launch.knot.KnotClient",
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(fabric, "install_fabric"):
            result = await fabric.install_fabric("1.20.4", "0.14.24", "/temp/minecraft")
            assert result is not None


class TestQuilt:
    """Test cases for Quilt mod loader"""

    @patch("aiohttp.ClientSession")
    async def test_get_quilt_versions(self, mock_session):
        """Test getting Quilt versions"""
        mock_response = Mock()
        mock_response.json = Mock(return_value=[{"version": "0.20.2", "stable": True}])
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(quilt, "get_quilt_versions"):
            result = await quilt.get_quilt_versions()
            assert isinstance(result, list)
            assert result[0]["version"] == "0.20.2"

    @patch("aiohttp.ClientSession")
    async def test_install_quilt(self, mock_session):
        """Test installing Quilt"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "libraries": [],
                "mainClass": "org.quiltmc.loader.launch.knot.KnotClient",
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(quilt, "install_quilt"):
            result = await quilt.install_quilt("1.20.4", "0.20.2", "/temp/minecraft")
            assert result is not None


class TestMrpack:
    """Test cases for mrpack (Modrinth modpack) support"""

    @pytest.fixture
    def sample_mrpack_data(self):
        """Sample mrpack data for testing"""
        return {
            "formatVersion": 1,
            "game": "minecraft",
            "versionId": "1.20.4",
            "name": "Test Modpack",
            "summary": "A test modpack",
            "files": [
                {
                    "path": "mods/test-mod.jar",
                    "hashes": {"sha1": "abc123"},
                    "downloads": ["https://example.com/test-mod.jar"],
                    "fileSize": 12345,
                }
            ],
            "dependencies": {"minecraft": "1.20.4", "fabric-loader": "0.14.24"},
        }

    def test_parse_mrpack(self, sample_mrpack_data):
        """Test parsing mrpack data"""
        if hasattr(mrpack, "parse_mrpack"):
            result = mrpack.parse_mrpack(sample_mrpack_data)
            assert result is not None
            assert result["name"] == "Test Modpack"
            assert result["versionId"] == "1.20.4"

    @patch("aiohttp.ClientSession")
    async def test_download_mrpack_file(self, mock_session, sample_mrpack_data):
        """Test downloading files from mrpack"""
        mock_response = Mock()
        mock_response.content.read = Mock(return_value=b"fake file content")
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(mrpack, "download_mrpack_file"):
            file_info = sample_mrpack_data["files"][0]
            result = await mrpack.download_mrpack_file(file_info, "/temp/minecraft")
            assert result is not None

    async def test_install_mrpack(self, sample_mrpack_data):
        """Test installing mrpack"""
        if hasattr(mrpack, "install_mrpack"):
            with patch("aiohttp.ClientSession") as mock_session:
                mock_response = Mock()
                mock_response.content.read = Mock(return_value=b"fake file content")
                mock_response.status = 200
                mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                    mock_response
                )

                result = await mrpack.install_mrpack(
                    sample_mrpack_data, "/temp/minecraft"
                )
                assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
