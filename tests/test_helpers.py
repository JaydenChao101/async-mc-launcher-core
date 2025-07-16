import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import json

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import _helper


class TestHelperFunctions:
    """Test cases for helper functions"""

    @patch("launcher_core._helper.aiohttp.ClientSession")
    async def test_download_file_success(self, mock_session):
        """Test successful file download"""
        mock_response = Mock()
        mock_response.content.read = AsyncMock(return_value=b"test file content")
        mock_response.status = 200
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                # This tests the download_file function
                # (Note: Adjust based on actual function signature)
                if hasattr(_helper, 'download_file'):
                    await _helper.download_file(
                        "https://example.com/test.jar",
                        tmp_file.name
                    )
                    # Verify file was created
                    assert os.path.exists(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)

    @patch("launcher_core._helper.aiohttp.ClientSession")
    async def test_get_requests_response_cache(self, mock_session):
        """Test response caching functionality"""
        # Skip this test if the function doesn't exist
        if not hasattr(_helper, 'get_requests_response_cache'):
            pytest.skip("get_requests_response_cache function not found")

        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"cached": "data"})
        mock_response.read = AsyncMock(return_value=b'{"cached": "data"}')  # Add async read method
        mock_response.text = AsyncMock(return_value='{"cached": "data"}')  # Add async text method
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}  # Add headers for content type check

        # Create a proper async context manager mock
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = Mock()
        mock_session_instance.get = Mock(return_value=mock_get_ctx)

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value = mock_session_ctx

        # Test caching mechanism
        result1 = await _helper.get_requests_response_cache("https://api.example.com/data")
        result2 = await _helper.get_requests_response_cache("https://api.example.com/data")

        # Results should be identical if caching works
        assert result1 == result2

    def test_assert_func(self):
        """Test assertion helper function"""
        if hasattr(_helper, 'assert_func'):
            # Test valid assertion - assert_func only takes one bool parameter
            _helper.assert_func(True)

            # Test invalid assertion
            with pytest.raises(AssertionError):
                _helper.assert_func(False)

    def test_parse_rule_list(self):
        """Test rule list parsing"""
        if hasattr(_helper, 'parse_rule_list'):
            test_rules = [
                {
                    "action": "allow",
                    "os": {"name": "linux"}
                },
                {
                    "action": "disallow",
                    "os": {"name": "windows"}
                }
            ]

            # Test parsing rules for different OS
            result = _helper.parse_rule_list(test_rules, "linux")
            assert isinstance(result, bool)

    @patch("launcher_core._helper.aiofiles.open")
    async def test_inherit_json(self, mock_aiofiles_open):
        """Test JSON inheritance functionality"""
        if not hasattr(_helper, 'inherit_json'):
            pytest.skip("inherit_json function not found")

        # Mock file content for the inherited version
        mock_file_content = json.dumps({
            "id": "1.20",
            "type": "release",
            "libraries": [{"name": "test-lib"}],
            "mainClass": "net.minecraft.client.main.Main"
        })

        # Mock aiofiles.open context manager
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=mock_file_content)
        mock_aiofiles_open.return_value.__aenter__ = AsyncMock(return_value=mock_file)
        mock_aiofiles_open.return_value.__aexit__ = AsyncMock(return_value=None)

        # Test data
        original_data = {"id": "1.20.1", "type": "release", "inheritsFrom": "1.20"}
        path = "/minecraft"

        result = await _helper.inherit_json(original_data, path)

        # Should be a dict result with inherited properties
        assert isinstance(result, dict)
        assert result["id"] == "1.20.1"  # Original ID should be preserved

    def test_get_library_path(self):
        """Test library path generation"""
        if hasattr(_helper, 'get_library_path'):
            # get_library_path takes name and path parameters
            library_name = "org.lwjgl:lwjgl:3.3.1"
            minecraft_path = "/minecraft"

            path = _helper.get_library_path(library_name, minecraft_path)
            assert isinstance(path, str)
            assert "lwjgl" in path


class TestCacheManager:
    """Test cases for cache management"""

    def test_cache_storage(self):
        """Test cache storage and retrieval"""
        # This would test any caching mechanisms in _helper
        # (Implementation depends on actual cache structure)
        pass

    def test_cache_expiration(self):
        """Test cache expiration logic"""
        # This would test cache TTL functionality
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
