# This is a simple example of how to start a Minecraft game using the launcher-core library.
from launcher_core import command, _types, mojang
import subprocess
from dotenv import dotenv_values

config = dotenv_values(".env")
access_token = config["access_token"]


async def main():
    res = await mojang.get_minecraft_profile(access_token)
    account = _types.Credential(
        access_token=access_token,
        username=res["name"],
        uuid=res["id"],
    )
    # 不要再寫 access_token = account.access_token
    await mojang.have_minecraft(access_token)
    MinecraftOptions: _types.MinecraftOptions = {
        "game_directory": r"C:\Users\Jayden\Desktop\pcl\.minecraft",
        "version": "1.21.1-Fabric 0.16.5",
        "memory": 2048,
        "jvm_args": ["-Xmx2048M", "-Xms1024M"],
        "nativesDirectory": config["nativesDirectory"],
        "assets_root": config["assets_root"],
        "gameDir": r"C:\Users\Jayden\Desktop\pcl\.minecraft\versions\1.21.1-Fabric 0.16.5",
    }
    cmd = await command.get_minecraft_command(
        MinecraftOptions["version"],
        r"C:\Users\Jayden\Desktop\pcl\.minecraft",
        MinecraftOptions,
        Credential=account,
    )
    return subprocess.list2cmdline(cmd)


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(main())
    with open("cmd.txt", "w") as f:
        f.write(result)
    print(result)
