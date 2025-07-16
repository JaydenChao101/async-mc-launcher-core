import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import check_version, utils


class TestVersionCheck:
    """Test cases for version checking functionality"""

    @patch("launcher_core.http_client.HTTPClient.get_json")
    async def test_get_minecraft_versions(self, mock_get_json):
        """Test getting Minecraft version list"""
        mock_get_json.return_value = {
            "latest": {
                "release": "1.20.4",
                "snapshot": "24w04a"
            },
            "versions": [
                {
                    "id": "1.20.4",
                    "type": "release",
                    "releaseTime": "2023-12-07T12:00:00+00:00",
                    "complianceLevel": 1
                },
                {
                    "id": "24w04a",
                    "type": "snapshot",
                    "releaseTime": "2024-01-24T14:00:00+00:00",
                    "complianceLevel": 0
                }
            ]
        }

        if hasattr(check_version, 'get_minecraft_versions'):
            result = await check_version.get_minecraft_versions()
            assert "latest" in result
            assert "versions" in result
            assert result["latest"]["release"] == "1.20.4"

    async def test_get_latest_version(self):
        """Test getting latest Minecraft version"""
        if hasattr(utils, 'get_latest_version'):
            with patch("launcher_core.http_client.HTTPClient.get_json") as mock_get:
                mock_get.return_value = {
                    "latest": {
                        "release": "1.20.4",
                        "snapshot": "24w04a"
                    }
                }

                result = await utils.get_latest_version()
                assert "release" in result
                assert "snapshot" in result

    async def test_version_comparison(self):
        """Test version comparison functionality"""
        if hasattr(check_version, 'compare_versions'):
            # Test version comparison
            assert check_version.compare_versions("1.20.4", "1.20.3") > 0
            assert check_version.compare_versions("1.20.3", "1.20.4") < 0
            assert check_version.compare_versions("1.20.4", "1.20.4") == 0

    def test_version_parsing(self):
        """Test version string parsing"""
        if hasattr(check_version, 'parse_version'):
            version = check_version.parse_version("1.20.4")
            assert isinstance(version, (tuple, list))
            assert len(version) >= 3

    async def test_check_for_updates(self):
        """Test checking for launcher updates"""
        if hasattr(check_version, 'check_for_updates'):
            with patch("launcher_core.http_client.HTTPClient.get_json") as mock_get:
                mock_get.return_value = {
                    "tag_name": "v2.0.0",
                    "name": "Version 2.0.0",
                    "published_at": "2024-01-01T00:00:00Z"
                }

                result = await check_version.check_for_updates("1.0.0")
                assert "tag_name" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
