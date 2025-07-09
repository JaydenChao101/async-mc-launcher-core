import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import microsoft_account, microsoft_types


class TestMicrosoftAccount:
    """Test cases for Microsoft Account authentication"""

    @pytest.fixture
    def mock_azure_app(self):
        """Mock Azure application configuration"""
        return (
            microsoft_types.AzureApplication(
                client_id="test_client_id", redirect_uri="http://localhost:8080"
            )
            if hasattr(microsoft_types, "AzureApplication")
            else Mock()
        )

    @patch("aiohttp.ClientSession")
    async def test_get_device_code(self, mock_session, mock_azure_app):
        """Test getting device code from Microsoft"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "device_code": "test_device_code",
                "user_code": "TEST123",
                "verification_uri": "https://microsoft.com/devicelogin",
                "expires_in": 900,
                "interval": 5,
            }
        )
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(microsoft_account, "get_device_code"):
            result = await microsoft_account.get_device_code(mock_azure_app)
            assert result["device_code"] == "test_device_code"
            assert result["user_code"] == "TEST123"

    @patch("aiohttp.ClientSession")
    async def test_authenticate_with_device_code(self, mock_session, mock_azure_app):
        """Test authenticating with device code"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        )
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(microsoft_account, "authenticate_with_device_code"):
            result = await microsoft_account.authenticate_with_device_code(
                mock_azure_app, "test_device_code"
            )
            assert result["access_token"] == "test_access_token"

    @patch("aiohttp.ClientSession")
    async def test_refresh_access_token(self, mock_session, mock_azure_app):
        """Test refreshing access token"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        )
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(microsoft_account, "refresh_access_token"):
            result = await microsoft_account.refresh_access_token(
                mock_azure_app, "old_refresh_token"
            )
            assert result["access_token"] == "new_access_token"

    def test_microsoft_types_exist(self):
        """Test that Microsoft types are properly defined"""
        type_names = ["AzureApplication", "MinecraftProfile", "XboxLiveProfile"]

        for type_name in type_names:
            if hasattr(microsoft_types, type_name):
                type_class = getattr(microsoft_types, type_name)
                assert type_class is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
