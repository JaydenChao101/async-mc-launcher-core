import pytest
import sys
import os
import logging
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import setting


class TestSetting:
    """Test cases for setting module"""

    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        logger = setting.setup_logger("test_logger", logging.DEBUG)

        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 0  # No handlers by default

    def test_setup_logger_with_console(self):
        """Test logger setup with console handler"""
        logger = setting.setup_logger(
            "test_console_logger",
            logging.INFO,
            enable_console=True
        )

        assert logger.name == "test_console_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logger_with_file(self):
        """Test logger setup with file handler"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = setting.setup_logger(
                "test_file_logger",
                logging.WARNING,
                filename=str(log_file)
            )

            assert logger.name == "test_file_logger"
            assert logger.level == logging.WARNING
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_logger_with_both_handlers(self):
        """Test logger setup with both console and file handlers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test_both.log"

            logger = setting.setup_logger(
                "test_both_logger",
                logging.ERROR,
                filename=str(log_file),
                enable_console=True
            )

            assert logger.name == "test_both_logger"
            assert logger.level == logging.ERROR
            assert len(logger.handlers) == 2

            handler_types = [type(h) for h in logger.handlers]
            assert logging.StreamHandler in handler_types
            assert logging.FileHandler in handler_types

    def test_setup_logger_default_parameters(self):
        """Test logger setup with default parameters"""
        logger = setting.setup_logger()

        assert logger.name == "root"
        assert logger.level == logging.INFO
        # Note: pytest may add handlers to root logger, so we just check it's a logger instance
        assert isinstance(logger, logging.Logger)

    def test_logger_formatter(self):
        """Test that logger formatter is properly configured"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "formatter_test.log"

            logger = setting.setup_logger(
                "formatter_test",
                logging.INFO,
                filename=str(log_file),
                enable_console=True
            )

            # Test that both handlers have formatters
            for handler in logger.handlers:
                assert handler.formatter is not None
                formatter = handler.formatter
                assert "%(asctime)s" in formatter._fmt
                assert "%(name)s" in formatter._fmt
                assert "%(levelname)s" in formatter._fmt
                assert "%(message)s" in formatter._fmt

    def teardown_method(self):
        """Clean up loggers after each test"""
        # Remove handlers to avoid interference between tests
        for logger_name in ["test_logger", "test_console_logger", "test_file_logger",
                           "test_both_logger", "formatter_test"]:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
