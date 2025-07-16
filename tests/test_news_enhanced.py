import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher_core import news


class TestNewsEnhanced:
    """Enhanced test cases for news module to improve coverage"""

    @patch("launcher_core.news.HTTPClient.get_json")
    @patch("launcher_core.news.get_user_agent")
    async def test_get_minecraft_news_with_category_filter(self, mock_get_user_agent, mock_get_json):
        """Test get_minecraft_news with category filtering"""
        mock_get_user_agent.return_value = "test-user-agent"
        mock_get_json.return_value = {
            "entries": [
                {"id": "1", "title": "Update News", "category": "Update", "date": "2024-01-01"},
                {"id": "2", "title": "General News", "category": "General", "date": "2024-01-02"},
                {"id": "3", "title": "Another Update", "category": "Update"},
            ],
            "article_count": 3
        }

        result = await news.get_minecraft_news(category="Update")

        # Should filter to only Update category entries
        assert len(result["entries"]) == 2
        assert result["article_count"] == 2
        assert all(entry.get("category") == "Update" for entry in result["entries"])

        # Check date parsing
        assert result["entries"][0]["date"] == datetime.date(2024, 1, 1)

    @patch("launcher_core.news.HTTPClient.get_json")
    @patch("launcher_core.news.get_user_agent")
    async def test_get_minecraft_news_no_category(self, mock_get_user_agent, mock_get_json):
        """Test get_minecraft_news without category filtering"""
        mock_get_user_agent.return_value = "test-user-agent"
        mock_get_json.return_value = {
            "entries": [
                {"id": "1", "title": "News 1", "date": "2024-01-01"},
                {"id": "2", "title": "News 2", "date": "2024-01-02"},
                {"id": "3", "title": "News 3"},  # No date field
            ],
            "article_count": 3
        }

        result = await news.get_minecraft_news()

        # Should return all entries
        assert len(result["entries"]) == 3
        assert result["article_count"] == 3

        # Check that only entries with date field get parsed
        assert result["entries"][0]["date"] == datetime.date(2024, 1, 1)
        assert result["entries"][1]["date"] == datetime.date(2024, 1, 2)
        assert "date" not in result["entries"][2] or isinstance(result["entries"][2].get("date"), str)

    @patch("launcher_core.news.HTTPClient.get_json")
    @patch("launcher_core.news.get_user_agent")
    async def test_get_minecraft_news_empty_category_filter(self, mock_get_user_agent, mock_get_json):
        """Test get_minecraft_news with category that has no matches"""
        mock_get_user_agent.return_value = "test-user-agent"
        mock_get_json.return_value = {
            "entries": [
                {"id": "1", "title": "News 1", "category": "Update"},
                {"id": "2", "title": "News 2", "category": "General"},
            ],
            "article_count": 2
        }

        result = await news.get_minecraft_news(category="NonExistent")

        # Should return empty entries
        assert len(result["entries"]) == 0
        assert result["article_count"] == 0

    @patch("launcher_core.news.HTTPClient.get_json")
    @patch("launcher_core.news.get_user_agent")
    async def test_get_java_patch_notes(self, mock_get_user_agent, mock_get_json):
        """Test get_java_patch_notes function"""
        mock_get_user_agent.return_value = "test-user-agent"
        expected_patch_notes = {
            "version": "1.20.1",
            "title": "Minecraft Java Edition 1.20.1",
            "body": "Bug fixes and improvements"
        }
        mock_get_json.return_value = expected_patch_notes

        result = await news.get_java_patch_notes()

        assert result == expected_patch_notes
        mock_get_user_agent.assert_called_once()
        mock_get_json.assert_called_once_with(
            "https://launchercontent.mojang.com/javaPatchNotes.json",
            headers={"user-agent": "test-user-agent"}
        )

    @patch("launcher_core.news.HTTPClient.get_json")
    @patch("launcher_core.news.get_user_agent")
    async def test_get_minecraft_news_date_parsing_edge_cases(self, mock_get_user_agent, mock_get_json):
        """Test date parsing with various edge cases"""
        mock_get_user_agent.return_value = "test-user-agent"
        mock_get_json.return_value = {
            "entries": [
                {"id": "1", "title": "Valid date", "date": "2024-12-31"},
                {"id": "2", "title": "No date field"},
                {"id": "3", "title": "Another valid date", "date": "2023-01-01"},
            ],
            "article_count": 3
        }

        result = await news.get_minecraft_news()

        # Check that valid dates are parsed correctly
        assert result["entries"][0]["date"] == datetime.date(2024, 12, 31)
        assert result["entries"][2]["date"] == datetime.date(2023, 1, 1)

        # Entries without date field should remain unchanged
        assert "date" not in result["entries"][1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
