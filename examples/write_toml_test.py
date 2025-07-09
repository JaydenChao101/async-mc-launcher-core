import asyncio
from launcher_core.config.load_launcher_config import load_config, save_config


async def main():
    # 加載配置
    config = await load_config("config.toml")
    print("當前用戶名:", config["Credential"]["username"])

    # 修改配置
    config["Credential"]["username"] = "Alex"  # 直接修改
    config["Credential"]["access_token"] = "new_token_123"

    # 保存回文件
    await save_config("config.toml", config)
    print("配置已更新！")


asyncio.run(main())
