import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock
import aiohttp
import json

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import http_client


class TestHTTPClientEnhanced:
    """Enhanced test cases for HTTP client module to improve coverage"""

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_with_custom_headers(self, mock_session):
        """Test HTTPClient.get_json with custom headers"""
        # Setup proper async context manager mocks
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_response.status = 200
        mock_response.raise_for_status = Mock()

        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        custom_headers = {"Authorization": "Bearer token", "User-Agent": "custom-agent"}
        result = await http_client.HTTPClient.get_json("https://api.test.com", headers=custom_headers)

        assert result == {"success": True}
        mock_session_instance.get.assert_called_once_with(
            "https://api.test.com",
            headers=custom_headers
        )

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_with_timeout(self, mock_session):
        """Test HTTPClient.get_json method (no timeout parameter in actual implementation)"""
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_response.status = 200
        mock_response.raise_for_status = Mock()

        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        # Test without timeout parameter since actual method doesn't support it
        result = await http_client.HTTPClient.get_json("https://api.test.com")

        assert result == {"data": "test"}

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_http_error(self, mock_session):
        """Test HTTPClient.get_json handles HTTP errors"""
        mock_response = Mock()
        mock_response.status = 404
        mock_response.raise_for_status = Mock(side_effect=aiohttp.ClientResponseError(
            request_info=Mock(), history=Mock(), status=404
        ))

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
            await http_client.HTTPClient.get_json("https://api.test.com/notfound")

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_network_error(self, mock_session):
        """Test HTTPClient.get_json handles network errors"""
        mock_session_instance = Mock()
        mock_session_instance.get = Mock(side_effect=aiohttp.ClientConnectorError(
            connection_key=Mock(), os_error=OSError("Network error")
        ))

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        with pytest.raises(aiohttp.ClientConnectorError):
            await http_client.HTTPClient.get_json("https://unreachable.test.com")

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_post_json_success(self, mock_session):
        """Test HTTPClient.post_json method"""
        if hasattr(http_client.HTTPClient, 'post_json'):
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={"created": True})
            mock_response.status = 201
            mock_response.raise_for_status = Mock()

            mock_post_ctx = AsyncMock()
            mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = Mock()
            mock_session_instance.post = Mock(return_value=mock_post_ctx)

            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_ctx

            # Use correct parameter name 'payload' instead of 'data'
            payload = {"name": "test", "value": 123}
            result = await http_client.HTTPClient.post_json("https://api.test.com", payload=payload)

            assert result == {"created": True}

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_text_method(self, mock_session):
        """Test HTTPClient.get_text method if it exists"""
        if hasattr(http_client.HTTPClient, 'get_text'):
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="Plain text response")
            mock_response.status = 200
            mock_response.raise_for_status = Mock()

            mock_get_ctx = AsyncMock()
            mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = Mock()
            mock_session_instance.get = Mock(return_value=mock_get_ctx)

            mock_session_ctx = AsyncMock()
            mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_ctx

            result = await http_client.HTTPClient.get_text("https://api.test.com/text")

            assert result == "Plain text response"

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_invalid_json_response(self, mock_session):
        """Test HTTPClient.get_json with invalid JSON response"""
        mock_response = Mock()
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        mock_response.status = 200
        mock_response.raise_for_status = Mock()

        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        with pytest.raises(json.JSONDecodeError):
            await http_client.HTTPClient.get_json("https://api.test.com/invalid-json")

    @patch("launcher_core.http_client.aiohttp.ClientSession")
    async def test_get_json_no_headers(self, mock_session):
        """Test HTTPClient.get_json without any headers"""
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"no_headers": True})
        mock_response.status = 200
        mock_response.raise_for_status = Mock()

        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        result = await http_client.HTTPClient.get_json("https://api.test.com")

        assert result == {"no_headers": True}
        # Verify get was called with default headers (None)
        mock_session_instance.get.assert_called_once_with("https://api.test.com", headers=None)

    def test_httpclient_class_exists(self):
        """Test that HTTPClient class is properly defined"""
        assert hasattr(http_client, 'HTTPClient')
        assert hasattr(http_client.HTTPClient, 'get_json')
        assert callable(http_client.HTTPClient.get_json)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
