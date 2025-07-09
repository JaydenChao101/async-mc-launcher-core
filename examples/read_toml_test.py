import asyncio
from launcher_core.config.load_launcher_config import load_config


async def main():

    config = await load_config("config.toml")
    print("用户名:", config["Credential"]["username"])
    print("Access Token:", config["Credential"]["access_token"])
    print("UUID:", config["Credential"]["uuid"])


asyncio.run(main())
