import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import exceptions


class TestExceptions:
    """Test cases for custom exceptions"""

    def test_base_exception_exists(self):
        """Test that base exception class exists"""
        if hasattr(exceptions, 'MinecraftLauncherLibException'):
            exc = exceptions.MinecraftLauncherLibException("Test error")
            assert str(exc) == "Test error"
            assert isinstance(exc, Exception)

    def test_authentication_exception(self):
        """Test authentication exception"""
        if hasattr(exceptions, 'AuthenticationException'):
            exc = exceptions.AuthenticationException("Auth failed")
            assert str(exc) == "Auth failed"
            assert isinstance(exc, Exception)

    def test_installation_exception(self):
        """Test installation exception"""
        if hasattr(exceptions, 'InstallationException'):
            exc = exceptions.InstallationException("Install failed")
            assert str(exc) == "Install failed"

    def test_version_not_found_exception(self):
        """Test version not found exception"""
        if hasattr(exceptions, 'VersionNotFound'):
            exc = exceptions.VersionNotFound("1.20.1")
            assert "1.20.1" in str(exc)

    def test_file_outside_directory_exception(self):
        """Test file outside directory exception"""
        if hasattr(exceptions, 'FileOutsideMinecraftDirectory'):
            exc = exceptions.FileOutsideMinecraftDirectory("/invalid/path", "/minecraft/dir")
            assert "/invalid/path" in str(exc)
            assert "/minecraft/dir" in str(exc)

    def test_invalid_checksum_exception(self):
        """Test invalid checksum exception"""
        if hasattr(exceptions, 'InvalidChecksum'):
            exc = exceptions.InvalidChecksum("http://example.com/file.jar", "/path/to/file.jar", "expected", "actual")
            assert "file.jar" in str(exc)
            assert "expected" in str(exc)
            assert "actual" in str(exc)

    def test_invalid_vanilla_launcher_profile(self):
        """Test invalid vanilla launcher profile exception"""
        if hasattr(exceptions, 'InvalidVanillaLauncherProfile'):
            profile = {"name": "test", "invalid": True}
            exc = exceptions.InvalidVanillaLauncherProfile(profile)
            assert isinstance(exc, Exception)

    def test_network_exception(self):
        """Test network-related exceptions"""
        if hasattr(exceptions, 'NetworkException'):
            exc = exceptions.NetworkException("Connection failed")
            assert str(exc) == "Connection failed"

    def test_java_not_found_exception(self):
        """Test Java not found exception"""
        if hasattr(exceptions, 'JavaNotFound'):
            exc = exceptions.JavaNotFound("Java executable not found")
            assert "Java" in str(exc)

    def test_mod_loader_exception(self):
        """Test mod loader related exceptions"""
        if hasattr(exceptions, 'ModLoaderException'):
            exc = exceptions.ModLoaderException("Fabric installation failed")
            assert "Fabric" in str(exc)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
