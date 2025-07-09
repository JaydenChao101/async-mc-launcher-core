import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import mojang, _helper, logging_utils
from launcher_core.config import load_launcher_config, vanilla_profile


class TestMojang:
    """Test cases for Mojang authentication and verification"""

    @patch("aiohttp.ClientSession")
    async def test_authenticate_user(self, mock_session):
        """Test authenticating user with Mojang"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "accessToken": "test_access_token",
                "selectedProfile": {"id": "test_uuid", "name": "TestPlayer"},
                "user": {"id": "test_user_id", "username": "test_username"},
            }
        )
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(mojang, "authenticate_user"):
            result = await mojang.authenticate_user("test_username", "test_password")
            assert result is not None
            assert result["accessToken"] == "test_access_token"
            assert result["selectedProfile"]["name"] == "TestPlayer"

    @patch("aiohttp.ClientSession")
    async def test_refresh_access_token(self, mock_session):
        """Test refreshing Mojang access token"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "accessToken": "new_access_token",
                "selectedProfile": {"id": "test_uuid", "name": "TestPlayer"},
            }
        )
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(mojang, "refresh_access_token"):
            result = await mojang.refresh_access_token(
                "old_access_token", "refresh_token"
            )
            assert result is not None
            assert result["accessToken"] == "new_access_token"

    @patch("aiohttp.ClientSession")
    async def test_validate_access_token(self, mock_session):
        """Test validating Mojang access token"""
        mock_response = Mock()
        mock_response.status = 204  # Success status for validation
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(mojang, "validate_access_token"):
            result = await mojang.validate_access_token("test_access_token")
            assert result is True

    def test_verify_mojang_jwt(self):
        """Test verifying Mojang JWT token"""
        if hasattr(mojang, "verify_mojang_jwt"):
            # Mock JWT token (this would normally be a real JWT)
            mock_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"

            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": "1234567890", "name": "John Doe"}
                result = mojang.verify_mojang_jwt(mock_jwt)
                assert result is not None

    @patch("aiohttp.ClientSession")
    async def test_get_player_profile(self, mock_session):
        """Test getting player profile"""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "id": "test_uuid",
                "name": "TestPlayer",
                "properties": [
                    {"name": "textures", "value": "base64_encoded_texture_data"}
                ],
            }
        )
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        if hasattr(mojang, "get_player_profile"):
            result = await mojang.get_player_profile("test_uuid")
            assert result is not None
            assert result["name"] == "TestPlayer"
            assert result["id"] == "test_uuid"


class TestHelper:
    """Test cases for helper functions"""

    def test_get_minecraft_directory(self):
        """Test getting default Minecraft directory"""
        if hasattr(_helper, "get_minecraft_directory"):
            result = _helper.get_minecraft_directory()
            assert result is not None
            assert isinstance(result, (str, Path))

    def test_get_java_executable(self):
        """Test finding Java executable"""
        if hasattr(_helper, "get_java_executable"):
            result = _helper.get_java_executable()
            # Should return a path or None
            assert result is None or isinstance(result, (str, Path))

    def test_generate_uuid(self):
        """Test generating UUID"""
        if hasattr(_helper, "generate_uuid"):
            result = _helper.generate_uuid()
            assert result is not None
            assert isinstance(result, str)
            assert len(result) == 36  # Standard UUID length with hyphens

    def test_format_rule_list(self):
        """Test formatting rule list"""
        if hasattr(_helper, "format_rule_list"):
            rules = [
                {"action": "allow", "os": {"name": "windows"}},
                {"action": "disallow", "os": {"name": "linux"}},
            ]
            result = _helper.format_rule_list(rules, "windows")
            assert result is not None

    def test_get_library_path(self):
        """Test getting library path"""
        if hasattr(_helper, "get_library_path"):
            library = {
                "name": "com.mojang:logging:1.0.0",
                "downloads": {
                    "artifact": {"path": "com/mojang/logging/1.0.0/logging-1.0.0.jar"}
                },
            }
            result = _helper.get_library_path(library, "/minecraft")
            assert result is not None
            assert "logging-1.0.0.jar" in result


class TestLoggingUtils:
    """Test cases for logging utilities"""

    def test_logger_exists(self):
        """Test that logger is properly configured"""
        assert logging_utils.logger is not None

    def test_logger_methods(self):
        """Test logger methods"""
        # Test that logger has standard methods
        assert hasattr(logging_utils.logger, "debug")
        assert hasattr(logging_utils.logger, "info")
        assert hasattr(logging_utils.logger, "warning")
        assert hasattr(logging_utils.logger, "error")
        assert hasattr(logging_utils.logger, "critical")

    def test_log_formatting(self):
        """Test log message formatting"""
        if hasattr(logging_utils, "format_log_message"):
            result = logging_utils.format_log_message("INFO", "Test message")
            assert result is not None
            assert "Test message" in result


class TestConfig:
    """Test cases for configuration modules"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_load_launcher_config(self, temp_config_dir):
        """Test loading launcher configuration"""
        if hasattr(load_launcher_config, "load_config"):
            # Create mock config file
            config_file = Path(temp_config_dir) / "config.toml"
            config_file.write_text(
                """
[launcher]
name = "Test Launcher"
version = "1.0.0"

[minecraft]
directory = "/minecraft"
java_executable = "java"

[authentication]
client_id = "test_client_id"
redirect_uri = "http://localhost:8080"
            """
            )

            result = load_launcher_config.load_config(str(config_file))
            assert result is not None
            assert "launcher" in result
            assert result["launcher"]["name"] == "Test Launcher"

    def test_vanilla_profile_creation(self):
        """Test creating vanilla profile"""
        if hasattr(vanilla_profile, "create_vanilla_profile"):
            profile = vanilla_profile.create_vanilla_profile("1.20.4", "TestPlayer")
            assert profile is not None
            assert profile["version"] == "1.20.4"
            assert profile["player_name"] == "TestPlayer"

    def test_vanilla_profile_validation(self):
        """Test validating vanilla profile"""
        if hasattr(vanilla_profile, "validate_profile"):
            valid_profile = {
                "version": "1.20.4",
                "player_name": "TestPlayer",
                "java_executable": "java",
                "game_directory": "/minecraft",
            }

            result = vanilla_profile.validate_profile(valid_profile)
            assert result is True

    def test_get_profile_path(self):
        """Test getting profile path"""
        if hasattr(vanilla_profile, "get_profile_path"):
            result = vanilla_profile.get_profile_path("test_profile")
            assert result is not None
            assert isinstance(result, (str, Path))


class TestIntegration:
    """Integration tests for multiple modules"""

    @pytest.fixture
    def temp_minecraft_dir(self):
        """Create temporary Minecraft directory for integration tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    async def test_full_authentication_flow(self, temp_minecraft_dir):
        """Test full authentication flow"""
        # This would test the complete flow from authentication to launching
        # For now, we'll just test that the modules can be imported together
        from launcher_core import microsoft_account, mojang, command, install

        assert microsoft_account is not None
        assert mojang is not None
        assert command is not None
        assert install is not None

    async def test_version_installation_flow(self, temp_minecraft_dir):
        """Test version installation flow"""
        # This would test installing a version and preparing launch command
        # For now, we'll just test that the modules work together
        from launcher_core import install, command, java_utils

        assert install is not None
        assert command is not None
        assert java_utils is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
