import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import exceptions
from launcher_core.utils import sync


class TestUtils:
    """Test cases for utils module"""

    def test_sync_function_success(self):
        """Test sync function with successful async function"""

        async def async_function():
            return "success"

        result = sync(async_function())
        assert result == "success"

    def test_sync_function_with_args(self):
        """Test sync function with arguments"""

        async def async_function_with_args(arg1, arg2):
            return f"{arg1}-{arg2}"

        result = sync(async_function_with_args("hello", "world"))
        assert result == "hello-world"

    def test_sync_function_with_exception(self):
        """Test sync function handles exceptions"""

        async def async_function_with_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            sync(async_function_with_error())


class TestExceptions:
    """Test cases for exceptions module"""

    def test_custom_exceptions_exist(self):
        """Test that custom exceptions are defined"""
        # Check if common exception classes exist
        exception_classes = [
            "MinecraftLauncherLibException",
            "AuthenticationException",
            "InstallationException",
            "VersionNotFoundException",
        ]

        for exc_name in exception_classes:
            if hasattr(exceptions, exc_name):
                exc_class = getattr(exceptions, exc_name)
                assert issubclass(exc_class, Exception)

    def test_exception_inheritance(self):
        """Test exception inheritance"""
        if hasattr(exceptions, "MinecraftLauncherLibException"):
            base_exc = exceptions.MinecraftLauncherLibException("test")
            assert isinstance(base_exc, Exception)
            assert str(base_exc) == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
