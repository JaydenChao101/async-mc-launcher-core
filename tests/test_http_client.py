import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import http_client


class TestHTTPClient:
    """Test cases for HTTP client module"""

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_success(self, mock_session):
        """Test successful JSON GET request"""
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"test": "data"})
        mock_response.status = 200

        # Create proper async context manager mocks
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        result = await http_client.HTTPClient.get_json("https://api.example.com/data")
        assert result == {"test": "data"}

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_with_headers(self, mock_session):
        """Test JSON GET request with custom headers"""
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_response.status = 200

        # Create proper async context manager mocks
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        headers = {"User-Agent": "Test-Agent"}
        result = await http_client.HTTPClient.get_json("https://api.example.com/data", headers=headers)
        assert result == {"success": True}

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_error_response(self, mock_session):
        """Test handling of HTTP error responses"""
        mock_response = Mock()
        mock_response.status = 404
        mock_response.raise_for_status = Mock(side_effect=aiohttp.ClientResponseError(None, None))

        # Create proper async context manager mocks
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        with pytest.raises(aiohttp.ClientResponseError):
            await http_client.HTTPClient.get_json("https://api.example.com/notfound")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
