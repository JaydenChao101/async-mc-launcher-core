# minecraft-launcher-lib
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

Using pip:
```bash
pip install async-mc-launcher-core
```

Or using uv (recommended for faster installation):
```bash
uv pip install async-mc-launcher-core
```

## Microsoft Account Login Example

```python
from launcher_core import microsoft_account
from launcher_core._types import AzureApplication, Credential

async def main():
    # refresh my token
    AZURE_APP = AzureApplication(client_id="your_client_id")
    Credential1 = Credential(refresh_token="abc")
    token = await microsoft_account.refresh_minecraft_token(AZURE_APP=AZURE_APP,Credential=Credential1)
    xbl_token = await microsoft_account.Login.get_xbl_token(token["access_token"])
    xsts_token = await microsoft_account.Login.get_xsts_token(xbl_token["Token"])
    minecraft_token = await microsoft_account.Login.get_minecraft_access_token(
        xsts_token["Token"],
        xsts_token["DisplayClaims"]["xui"][0]["uhs"]
    )
    print("Minecraft Access Token:", minecraft_token["access_token"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
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
