print("Hello from async-mc-launcher-core!")

# check version
from .check_version import check_version
from . import __version__
import asyncio

asyncio.run(check_version())
print(f"Current version: {__version__}")
