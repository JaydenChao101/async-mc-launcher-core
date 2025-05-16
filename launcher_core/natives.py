# 標準庫導入
from typing import Literal
import platform
import zipfile
import json
import os

# 第三方庫導入
import aiofiles

# 本地導入
from ._internal_types.shared_types import ClientJson, ClientJsonLibrary
from ._helper import parse_rule_list, inherit_json, get_library_path
from .exceptions import VersionNotFound

__all__ = ["extract_natives"]


def get_natives(data: ClientJsonLibrary) -> str:
    """
    Returns the native part from the json data
    """
    if platform.architecture()[0] == "32bit":
        arch_type = "32"
    else:
        arch_type = "64"

    if "natives" in data:
        if platform.system() == "Windows":
            if "windows" in data["natives"]:
                return data["natives"]["windows"].replace("${arch}", arch_type)
            return ""
        if platform.system() == "Darwin":
            if "osx" in data["natives"]:
                return data["natives"]["osx"].replace("${arch}", arch_type)
            return ""
        if "linux" in data["natives"]:
            return data["natives"]["linux"].replace("${arch}", arch_type)
        return ""
    return ""


async def extract_natives_file(
    filename: str, extract_path: str, extract_data: dict[Literal["exclude"], list[str]]
) -> None:
    """
    Unpack natives
    """
    try:
        os.mkdir(extract_path)
    except (IOError, OSError):
        pass

    with zipfile.ZipFile(filename, "r") as zf:
        for i in zf.namelist():
            for e in extract_data["exclude"]:
                if i.startswith(e):
                    break
            else:
                zf.extract(i, extract_path)


async def extract_natives(
    versionid: str, path: str | os.PathLike, extract_path: str
) -> None:
    """
    Extract all native libraries from a version into the given directory. The directory will be created, if it does not exist.

    :param version: The Minecraft version
    :param minecraft_directory: The path to your Minecraft directory
    :param callback: The same dict as for :func:`~launcher_core.install.install_minecraft_version`
    :raises VersionNotFound: The Minecraft version was not found
    :raises FileOutsideMinecraftDirectory: A File should be placed outside the given Minecraft directory

    The natives are all extracted while installing. So you don't need to use this function in most cases.
    """
    if not os.path.isfile(
        os.path.join(path, "versions", versionid, versionid + ".json")
    ):
        raise VersionNotFound(versionid)

    async with aiofiles.open(
        os.path.join(path, "versions", versionid, versionid + ".json"),
        "r",
        encoding="utf-8",
    ) as f:
        data: ClientJson = json.loads(await f.read())

    if "inheritsFrom" in data:
        data = await inherit_json(data, path)

    for i in data["libraries"]:
        # Check, if the rules allow this lib for the current system
        if "rules" in i and not parse_rule_list(i["rules"], {}):
            continue

        current_path = get_library_path(i["name"], path)
        native = get_natives(i)

        if native == "":
            continue

        lib_path, extension = os.path.splitext(current_path)
        await extract_natives_file(
            f"{lib_path}-{native}{extension}",
            extract_path,
            i.get("extract", {"exclude": []}),
        )
