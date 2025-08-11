"""Simple configuration management utilities used in the tests.

The original project contains a rather feature rich configuration system
which relies on a large number of models.  The tests in this kata only
expect a light‑weight configuration object with a couple of fields and a
manager capable of loading, saving and updating that object asynchronously.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import aiofiles

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Py311 ships tomllib
    import tomli as tomllib

from tomli_w import dumps
from pydantic import BaseModel, Field


class LauncherConfig(BaseModel):
    """Minimal launcher configuration used by the test-suite.

    Only the options that are referenced in the tests are implemented
    here.  Defaults mirror the expectations expressed in the tests.
    """

    launcher_name: str = "AsyncMCLauncher"
    launcher_version: str = "1.0.0"
    username: Optional[str] = None
    version: Optional[str] = None
    concurrent_downloads: int = Field(4, ge=1, le=16)
    download_timeout: int = Field(300, ge=1)
    verify_downloads: bool = True
    auto_refresh_token: bool = True
    log_level: str = "INFO"
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None


class ConfigManager:
    """Load, update and persist :class:`LauncherConfig` instances."""

    def __init__(self, config_path: str | Path = "config.toml") -> None:
        self.config_path = Path(config_path)
        self._config: Optional[LauncherConfig] = None

    async def load_config(self, reload: bool = False) -> LauncherConfig:
        """Load configuration from disk or create a default instance."""

        if self._config is None or reload:
            if self.config_path.exists():
                async with aiofiles.open(self.config_path, "r", encoding="utf-8") as f:
                    data = tomllib.loads(await f.read())
                self._config = LauncherConfig(**data)
            else:
                self._config = LauncherConfig()
        return self._config

    async def save_config(self, config: Optional[LauncherConfig] = None) -> None:
        """Persist configuration to disk."""

        config = config or self._config
        if config is None:  # pragma: no cover - defensive programming
            raise ValueError("No configuration available to save")
        self._config = config

        toml_data = dumps(config.model_dump(exclude_none=True))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.config_path, "w", encoding="utf-8") as f:
            await f.write(toml_data)

    async def update_config(self, **updates: Any) -> LauncherConfig:
        """Update configuration values and persist the changes."""

        config = await self.load_config()
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        await self.save_config(config)
        return config

    def get_config(self) -> Optional[LauncherConfig]:
        """Return the currently loaded configuration, if any."""

        return self._config


async def create_default_config(config_path: str | Path = "config.toml") -> LauncherConfig:
    """Create and persist a default :class:`LauncherConfig` instance."""

    manager = ConfigManager(config_path)
    config = LauncherConfig()
    await manager.save_config(config)
    return config


__all__ = [
    "LauncherConfig",
    "ConfigManager",
    "create_default_config",
]
