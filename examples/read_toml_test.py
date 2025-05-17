import asyncio
import os
from launcher_core.load_config import load_config

async def main():
    
    config = await load_config("config.toml")
    print("用户名:", config["Credential"]["username"])
    print("Access Token:", config["Credential"]["access_token"])
    print("UUID:", config["Credential"]["uuid"])

asyncio.run(main())
