# Async MC Launcher Core 🚀
**A modern async Python library for custom Minecraft launchers**
> [中文說明請見 README-Chinese.md](./README-Chinese.md)

[![Test](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/test.yml/badge.svg)](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/test.yml)
[![Build Python Package](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/uv_build.yaml/badge.svg)](https://github.com/JaydenChao101/asyncio-mc-launcher-lib/actions/workflows/uv_build.yaml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JaydenChao101/async-mc-launcher-core)

> This project is a fork of [JakobDev/minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib).

A Python library for building custom Minecraft launchers. Supports installing, launching Minecraft, and interacting with Mojang/Microsoft accounts.

## Features

- Easy installation
- Generate Minecraft launch commands
- Microsoft account login support
- Supports [Forge](https://minecraftforge.net), [Fabric](https://fabricmc.net), [Quilt](https://quiltmc.org), and Liteloader
- Supports alpha/beta and legacy versions
- All functions are type-annotated and documented
- [PyPy](https://www.pypy.org) support
- Full online documentation and tutorials
- Vanilla launcher profiles read/write support
- [mrpack modpacks](https://docs.modrinth.com/docs/modpacks/format_definition) support
- All public APIs are statically typed
- Rich examples
- Open source

## Installation

Install via pip:
```bash
pip install async-mc-launcher-core
```

Or with uv (faster install):
```bash
uv pip install async-mc-launcher-core
```

## Microsoft Account Login Example

```python
import logging
from launcher_core import microsoft_account
import asyncio
from launcher_core.setting import setup_logger
from launcher_core.mojang import have_minecraft

logger = setup_logger(enable_console=False, level=logging.INFO, filename="microsoft_account.log")

async def login_microsoft_account():
    AZURE_APP = microsoft_account.AzureApplication()
    Login = microsoft_account.Login(azure_app=AZURE_APP)
    login_url = await Login.get_login_url()
    print(f"Please open {login_url} in your browser and copy the URL you are redirected into the prompt below.")
    code_url = input()
    code = await microsoft_account.Login.extract_code_from_url(code_url)
    auth_code = await Login.get_ms_token(code)
    print(f"Refresh token: {auth_code['refresh_token']}")
    xbl_token = await microsoft_account.Login.get_xbl_token(auth_code["access_token"])
    xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
    uhs = xbl_token["DisplayClaims"]["xui"][0]["uhs"]
    mc_token = await microsoft_account.Login.get_minecraft_access_token(xsts_token["Token"], uhs)
    await have_minecraft(mc_token["access_token"])
    login_data = {
        "access_token": mc_token["access_token"],
        "refresh_token": auth_code["refresh_token"],
        "expires_in": auth_code["expires_in"],
        "uhs": uhs,
        "xsts_token": xsts_token["Token"],
        "xbl_token": xbl_token["Token"]
    }
    return login_data["access_token"]

if __name__ == "__main__":
    access_token = asyncio.run(login_microsoft_account())
    print(f"Access token: {access_token}")
```

## Documentation & More Examples

- [Online Documentation](https://minecraft-launcher-lib.readthedocs.io)
- [More Examples](https://codeberg.org/JakobDev/minecraft-launcher-lib/src/branch/master/examples)

## Comparison: This Fork vs. [JakobDev/minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib)

| Feature/Design           | This Fork                                             | JakobDev Original                                 |
|-------------------------|-------------------------------------------------------|---------------------------------------------------|
| Python Version Support  | 3.10+, more complete type annotations                 | 3.7+, partial type annotations                    |
| Logging System          | Built-in `setup_logger`, file & console output        | No built-in logging, user must implement          |
| Microsoft Login Flow    | Example & API fully async/await                       | All sync                                          |
| Dependencies            | aiofiles, aiohttp, requests, requests-mock            | requests                                          |
| Documentation           | Primarily in Chinese, tailored for TW/Chinese users   | English                                           |
| Branch Strategy         | main/dev auto-sync (GitHub Actions)                   | Single main branch                                |
| Others                  | Optimized for async/await and type annotations        | Focus on broad compatibility                      |

> Please refer to both the original and this fork to choose the version that best fits your needs!

## Contributing

PRs and issues are welcome!

## Acknowledgements

Thanks to [tomsik68](https://github.com/tomsik68/mclauncher-api/wiki) for documenting Minecraft launcher internals.

Thanks to [JakobDev](https://github.com/JakobDev) for the original code (BSD-2).
