from .logging_utils import logger
from . import __version__


async def check_version():
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://raw.githubusercontent.com/JaydenChao101/async-mc-launcher-core/main/launcher_core/__init__.py"
        ) as response:
            content = await response.text()
            if f'__version__ = "{__version__}"' not in content:
                logger.warning(
                    "Your version of async-mc-launcher-core is outdated. Please update to the latest version."
                )
