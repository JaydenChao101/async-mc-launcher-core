import pytest
import sys
import os
import logging
from unittest.mock import patch, Mock
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import logging_utils


class TestLoggingUtils:
    """Test cases for logging utilities"""

    def test_logger_creation(self):
        """Test logger creation"""
        if hasattr(logging_utils, 'get_logger'):
            logger = logging_utils.get_logger("test_logger")
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test_logger"

    def test_log_level_setting(self):
        """Test setting log levels"""
        if hasattr(logging_utils, 'set_log_level'):
            logger = logging.getLogger("test_level")
            logging_utils.set_log_level(logger, "DEBUG")
            assert logger.level == logging.DEBUG

    def test_file_handler_creation(self):
        """Test file handler creation"""
        if hasattr(logging_utils, 'add_file_handler'):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                try:
                    logger = logging.getLogger("test_file")
                    logging_utils.add_file_handler(logger, tmp_file.name)

                    # Test that handler was added
                    assert len(logger.handlers) > 0

                    # Test logging to file
                    logger.info("Test message")

                    # Verify file was written
                    with open(tmp_file.name, 'r') as f:
                        content = f.read()
                        assert "Test message" in content
                finally:
                    os.unlink(tmp_file.name)

    def test_console_handler(self):
        """Test console handler creation"""
        if hasattr(logging_utils, 'add_console_handler'):
            logger = logging.getLogger("test_console")
            logging_utils.add_console_handler(logger)

            # Check that console handler was added
            console_handlers = [h for h in logger.handlers
                              if isinstance(h, logging.StreamHandler)]
            assert len(console_handlers) > 0

    def test_log_formatting(self):
        """Test log message formatting"""
        if hasattr(logging_utils, 'get_formatter'):
            formatter = logging_utils.get_formatter()
            assert isinstance(formatter, logging.Formatter)

            # Test formatter with a log record
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="Test message", args=(), exc_info=None
            )
            formatted = formatter.format(record)
            assert "Test message" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
