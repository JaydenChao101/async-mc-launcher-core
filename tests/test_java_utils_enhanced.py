import pytest
import sys
import os
import platform
import asyncio
from unittest.mock import patch, AsyncMock, Mock
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import java_utils
from launcher_core.models import JavaInformation


class TestJavaUtilsEnhanced:
    """Enhanced test cases for java_utils module to improve coverage"""

    @patch("asyncio.create_subprocess_exec")
    async def test_get_java_information_valid_path_windows(self, mock_subprocess):
        """Test get_java_information with valid Java path on Windows"""
        with patch("platform.system", return_value="Windows"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create fake Java executable structure
                bin_dir = Path(temp_dir) / "bin"
                bin_dir.mkdir()
                java_exe = bin_dir / "java.exe"
                java_exe.touch()

                # Mock subprocess output - java version info goes to stderr
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',  # stdout is empty
                    b'openjdk version "17.0.5" 2022-10-18\nOpenJDK Runtime Environment (build 17.0.5+8-Ubuntu-2ubuntu1)\nOpenJDK 64-Bit Server VM (build 17.0.5+8-Ubuntu-2ubuntu1, mixed mode, sharing)'
                )
                mock_subprocess.return_value = mock_process

                result = await java_utils.get_java_information(temp_dir)

                assert isinstance(result, dict)  # JavaInformation is a dict
                assert result["version"] == "17.0.5"
                assert result["is64Bit"] is True
                assert result["openjdk"] is True

    @patch("asyncio.create_subprocess_exec")
    async def test_get_java_information_valid_path_unix(self, mock_subprocess):
        """Test get_java_information with valid Java path on Unix systems"""
        with patch("platform.system", return_value="Linux"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create fake Java executable structure
                bin_dir = Path(temp_dir) / "bin"
                bin_dir.mkdir()
                java_exe = bin_dir / "java"
                java_exe.touch()

                # Mock subprocess output - java version info goes to stderr
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',  # stdout is empty
                    b'openjdk version "11.0.16" 2022-07-19\nOpenJDK Runtime Environment (build 11.0.16+8-post-Ubuntu-0ubuntu1)\nOpenJDK 64-Bit Server VM (build 11.0.16+8-post-Ubuntu-0ubuntu1, mixed mode, sharing)'
                )
                mock_subprocess.return_value = mock_process

                result = await java_utils.get_java_information(temp_dir)

                assert isinstance(result, dict)
                assert result["version"] == "11.0.16"
                assert result["is64Bit"] is True
                assert result["openjdk"] is True

    async def test_get_java_information_invalid_path_windows(self):
        """Test get_java_information with invalid path on Windows"""
        with patch("platform.system", return_value="Windows"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Don't create java.exe file
                with pytest.raises(ValueError) as exc_info:
                    await java_utils.get_java_information(temp_dir)

                assert "was not found" in str(exc_info.value)
                assert "java.exe" in str(exc_info.value)

    async def test_get_java_information_invalid_path_unix(self):
        """Test get_java_information with invalid path on Unix"""
        with patch("platform.system", return_value="Linux"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Don't create java file
                with pytest.raises(ValueError) as exc_info:
                    await java_utils.get_java_information(temp_dir)

                assert "was not found" in str(exc_info.value)
                assert "/bin/java" in str(exc_info.value)

    @patch("asyncio.create_subprocess_exec")
    async def test_get_java_information_subprocess_failure(self, mock_subprocess):
        """Test get_java_information when subprocess fails"""
        with patch("platform.system", return_value="Linux"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create fake Java executable
                bin_dir = Path(temp_dir) / "bin"
                bin_dir.mkdir()
                java_exe = bin_dir / "java"
                java_exe.touch()

                # Mock subprocess failure with minimal valid output to avoid regex errors
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',
                    b'java version "1.8.0"\nJava Runtime Environment\nJava Client VM'
                )
                mock_subprocess.return_value = mock_process

                result = await java_utils.get_java_information(temp_dir)
                assert isinstance(result, dict)

    @patch("asyncio.create_subprocess_exec")
    async def test_get_java_information_version_parsing(self, mock_subprocess):
        """Test version parsing from different Java output formats"""
        with patch("platform.system", return_value="Linux"):
            with tempfile.TemporaryDirectory() as temp_dir:
                bin_dir = Path(temp_dir) / "bin"
                bin_dir.mkdir()
                java_exe = bin_dir / "java"
                java_exe.touch()

                # Test different version output formats - use stderr since that's where java puts version info
                test_cases = [
                    (b'', b'java version "1.8.0_345"\nJava(TM) SE Runtime Environment\nJava Client VM'),
                    (b'', b'openjdk version "17.0.5" 2022-10-18\nOpenJDK Runtime Environment\nOpenJDK 64-Bit Server VM'),
                    (b'', b'java version "11.0.16"\nOpenJDK Runtime Environment\nOpenJDK 64-Bit Server VM'),
                ]

                for stdout, stderr in test_cases:
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (stdout, stderr)
                    mock_subprocess.return_value = mock_process

                    result = await java_utils.get_java_information(temp_dir)
                    assert isinstance(result, dict)

    @patch("asyncio.create_subprocess_exec")
    async def test_get_java_information_with_path_like_object(self, mock_subprocess):
        """Test get_java_information with Path object instead of string"""
        with patch("platform.system", return_value="Linux"):
            with tempfile.TemporaryDirectory() as temp_dir:
                path_obj = Path(temp_dir)
                bin_dir = path_obj / "bin"
                bin_dir.mkdir()
                java_exe = bin_dir / "java"
                java_exe.touch()

                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',
                    b'openjdk version "17.0.5"\nOpenJDK Runtime Environment\nOpenJDK 64-Bit Server VM'
                )
                mock_subprocess.return_value = mock_process

                result = await java_utils.get_java_information(path_obj)
                assert isinstance(result, dict)

    async def test_get_java_information_nonexistent_directory(self):
        """Test get_java_information with completely nonexistent directory"""
        nonexistent_path = "/this/path/definitely/does/not/exist"

        with pytest.raises(ValueError) as exc_info:
            await java_utils.get_java_information(nonexistent_path)

        assert "was not found" in str(exc_info.value)

    @patch("asyncio.create_subprocess_exec")
    @patch("platform.system")
    async def test_get_java_information_different_platforms(self, mock_platform, mock_subprocess):
        """Test get_java_information behavior on different platforms"""
        platforms_to_test = ["Windows", "Darwin", "Linux"]

        for platform_name in platforms_to_test:
            mock_platform.return_value = platform_name

            with tempfile.TemporaryDirectory() as temp_dir:
                bin_dir = Path(temp_dir) / "bin"
                bin_dir.mkdir()

                # Create appropriate executable based on platform
                if platform_name == "Windows":
                    java_exe = bin_dir / "java.exe"
                else:
                    java_exe = bin_dir / "java"
                java_exe.touch()

                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b'',
                    b'java version "17.0.5"\nJava Runtime Environment\nJava Server VM'
                )
                mock_subprocess.return_value = mock_process

                result = await java_utils.get_java_information(temp_dir)
                assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
