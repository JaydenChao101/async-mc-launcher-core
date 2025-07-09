# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"This module contains some helper functions. It should not be used outside minecraft_launcher_lib"
from typing import Literal, Any, NoReturn
import subprocess
import datetime
import platform
import hashlib
import zipfile
import lzma
import json
import sys
import re
import os
import aiohttp
import aiofiles
from .exceptions import FileOutsideMinecraftDirectory, InvalidChecksum, VersionNotFound
from ._internal_types.shared_types import ClientJson, ClientJsonRule, ClientJsonLibrary
from ._internal_types.helper_types import RequestsResponseCache, MavenMetadata
from ._types import MinecraftOptions, CallbackDict


if os.name == "nt":
    info = subprocess.STARTUPINFO()  # type: ignore
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
    info.wShowWindow = subprocess.SW_HIDE  # type: ignore
    SUBPROCESS_STARTUP_INFO: subprocess.STARTUPINFO | None = info  # type: ignore
else:
    SUBPROCESS_STARTUP_INFO = None


def empty(arg: Any) -> NoReturn:
    """
    This function is just a placeholder
    """
    pass


def check_path_inside_minecraft_directory(
    minecraft_directory: str | os.PathLike, path: str | os.PathLike
) -> None:
    """
    Raises a FileOutsideMinecraftDirectory if the Path is not in the given Directory
    """
    if not os.path.abspath(path).startswith(os.path.abspath(minecraft_directory)):
        raise FileOutsideMinecraftDirectory(
            os.path.abspath(path), os.path.abspath(minecraft_directory)
        )


async def download_file(
    url: str,
    path: str,
    callback: CallbackDict = None,
    sha1: str | None = None,
    lzma_compressed: bool | None = False,
    session: aiohttp.ClientSession | None = None,
    minecraft_directory: str | os.PathLike | None = None,
    overwrite: bool | None = False,
) -> bool:
    """
    Downloads a file into the given path. Check sha1 if given.
    """
    # Check if the Path is outside the given Minecraft Directory
    if minecraft_directory is not None:
        check_path_inside_minecraft_directory(minecraft_directory, path)

    if callback is None:
        callback = {}

    if os.path.isfile(path) and not overwrite:
        if sha1 is None:
            return False
        elif await get_sha1_hash(path) == sha1:
            return False

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass

    callback.get("setStatus", empty)("Download " + os.path.basename(path))

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        headers = {"user-agent": get_user_agent()}
        async with session.get(
            url, headers=headers, timeout=aiohttp.ClientTimeout(total=300)
        ) as r:
            if r.status != 200:
                return False

            async with aiofiles.open(path, "wb") as f:
                if lzma_compressed:
                    content = await r.read()
                    await f.write(lzma.decompress(content))
                else:
                    # Use streaming download with 64KB chunks
                    chunk_size = 65536
                    while True:
                        chunk = await r.content.read(chunk_size)
                        if not chunk:
                            break
                        await f.write(chunk)
                        # Update progress if callback provided
                        if callback.get("setProgress"):
                            callback["setProgress"](r.content_length, f.tell())
    finally:
        if close_session:
            await session.close()

    if sha1 is not None:
        checksum = await get_sha1_hash(path)
        if checksum != sha1:
            raise InvalidChecksum(url, path, sha1, checksum)

    return True


def parse_single_rule(rule: ClientJsonRule, options: MinecraftOptions) -> bool:
    """
    Parse a single rule from the versions.json
    """
    # 1. Handle action and initialize returnvalue
    if rule["action"] == "allow":
        returnvalue = False
    elif rule["action"] == "disallow":
        returnvalue = True
    else:
        raise ValueError(f"Invalid rule action: {rule['action']}")
    # 2. Check OS conditions
    for os_key, os_value in rule.get("os", {}).items():
        if os_key == "name":
            if os_value == "windows" and platform.system() != "Windows":
                return returnvalue
            elif os_value == "osx" and platform.system() != "Darwin":
                return returnvalue
            elif os_value == "linux" and platform.system() != "Linux":
                return returnvalue
        elif os_key == "arch":
            if os_value == "x86" and platform.architecture()[0] != "32bit":
                return returnvalue
        elif os_key == "version":
            if not re.match(os_value, get_os_version()):
                return returnvalue
    # 3. Check features conditions
    for features_key in rule.get("features", {}).keys():
        if features_key == "has_custom_resolution" and not options.get(
            "customResolution", False
        ):
            return returnvalue
        elif features_key == "is_demo_user" and not options.get("demo", False):
            return returnvalue
        elif (
            features_key == "has_quick_plays_support"
            and options.get("quickPlayPath") is None
        ):
            return returnvalue
        elif (
            features_key == "is_quick_play_singleplayer"
            and options.get("quickPlaySingleplayer") is None
        ):
            return returnvalue
        elif (
            features_key == "is_quick_play_multiplayer"
            and options.get("quickPlayMultiplayer") is None
        ):
            return returnvalue
        elif (
            features_key == "is_quick_play_realms"
            and options.get("quickPlayRealms") is None
        ):
            return returnvalue
    # 4. Return opposite value by default
    return not returnvalue


def parse_rule_list(rules: list[ClientJsonRule], options: MinecraftOptions) -> bool:
    """
    Parse a list of rules
    """
    for i in rules:
        if not parse_single_rule(i, options):
            return False

    return True


def _get_lib_name_without_version(lib: ClientJsonLibrary) -> str:
    """
    Returns the library name but without the version part
    e.g. org.ow2.asm:asm:9.7.1 -> org.ow2.asm:asm
    """
    return ":".join(lib["name"].split(":")[:-1])


async def inherit_json(
    original_data: ClientJson, path: str | os.PathLike
) -> ClientJson:
    """
    Implement the inheritsFrom function
    See https://github.com/tomsik68/mclauncher-api/wiki/Version-Inheritance-&-Forge
    """
    inherit_version = original_data["inheritsFrom"]

    file_path = os.path.join(
        path, "versions", inherit_version, inherit_version + ".json"
    )
    async with aiofiles.open(file_path, "r") as f:
        new_data: ClientJson = json.loads(await f.read())

    # Inheriting the libs is a bit special
    # If the lib is already present in the client.json in a different, it can't be inherited
    # So first we need a dict which contains all libs that are already present
    original_libs: dict[str, bool] = {}
    for current_lib in original_data.get("libraries", []):
        lib_name = _get_lib_name_without_version(current_lib)
        original_libs[lib_name] = True

    # Now we can attach all libs from the inherited version that are not already existing
    lib_list = original_data.get("libraries", [])
    for current_lib in new_data["libraries"]:
        lib_name = _get_lib_name_without_version(current_lib)
        if lib_name not in original_libs:
            lib_list.append(current_lib)

    new_data["libraries"] = lib_list

    for key, value in original_data.items():
        if key == "libraries":
            # We already had inherited the libs
            continue

        if isinstance(value, list) and isinstance(new_data.get(key, None), list):
            new_data[key] = value + new_data[key]  # type: ignore
        elif isinstance(value, dict) and isinstance(new_data.get(key, None), dict):
            for a, b in value.items():
                if isinstance(b, list):
                    new_data[key][a] = new_data[key][a] + b  # type: ignore
        else:
            new_data[key] = value  # type: ignore

    return new_data


def get_library_path(name: str, path: str | os.PathLike) -> str:
    """
    Returns the path from a library name
    """
    libpath = os.path.join(path, "libraries")
    parts = name.split(":")
    base_path, libname, version = parts[0:3]
    for i in base_path.split("."):
        libpath = os.path.join(libpath, i)
    try:
        version, fileend = version.split("@")
    except ValueError:
        fileend = "jar"

    # construct a filename with the remaining parts
    filename = (
        f"{libname}-{version}{''.join(map(lambda p: f'-{p}', parts[3:]))}.{fileend}"
    )
    libpath = os.path.join(libpath, libname, version, filename)
    return libpath


async def get_jar_mainclass(path: str) -> str:
    """
    Returns the mainclass of a given jar
    """
    zf = zipfile.ZipFile(path)
    # Parse the MANIFEST.MF
    with zf.open("META-INF/MANIFEST.MF") as f:
        lines = f.read().decode("utf-8").splitlines()
    zf.close()
    content = {}
    for i in lines:
        try:
            key, value = i.split(":")
            content[key] = value[1:]
        except Exception:
            pass
    return content["Main-Class"]


async def get_sha1_hash(path: str) -> str:
    """
    Calculate the sha1 checksum of a file
    Source: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """
    buf_size = 65536
    sha1 = hashlib.sha1()
    async with aiofiles.open(path, "rb") as f:
        while True:
            data = await f.read(buf_size)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def get_os_version() -> str:
    """
    Try to implement System.getProperty("os.version") from Java for use in rules
    This doesn't work on mac yet
    """
    if platform.system() == "Windows":
        ver = sys.getwindowsversion()  # type: ignore
        return f"{ver.major}.{ver.minor}"
    if platform.system() == "Darwin":
        return ""
    else:
        return platform.uname().release


_USER_AGENT_CACHE: str | None = None


async def get_user_agent() -> str:
    """
    Returns the user agent of minecraft-launcher-lib
    """
    global _USER_AGENT_CACHE
    if _USER_AGENT_CACHE is not None:
        return _USER_AGENT_CACHE

    file_path = os.path.join(os.path.dirname(__file__), "version.txt")
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        _USER_AGENT_CACHE = "minecraft-launcher-lib/" + (await f.read()).strip()
    return _USER_AGENT_CACHE


def get_classpath_separator() -> Literal[":", ";"]:
    """
    Determines the classpath separator based on the operating system.
    Returns:
        str: The classpath separator (":" for Unix-like systems, ";" for Windows).
    """

    return ";" if platform.system() == "Windows" else ":"


_requests_response_cache: dict[str, RequestsResponseCache] = {}


async def get_requests_response_cache(url: str) -> aiohttp.ClientResponse:
    """
    Caches the result of request.get(). If a request was made to the same URL within the last hour,
    the cache will be used, so you don't need to make a request to a URL each time you call a function.

    Args:
        url: The URL to request or get from cache

    Returns:
        A dictionary containing cached response data
    """
    now = datetime.datetime.now()

    # Return cached response if valid
    if url in _requests_response_cache:
        cache_entry = _requests_response_cache[url]
        if (now - cache_entry["datetime"]).total_seconds() < 3600:  # 1 hour in seconds
            return cache_entry["response"]

    # Make new request if cache expired or missing
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url, headers={"user-agent": await get_user_agent()}
        ) as r:
            if r.status == 200:
                # Copy response data to avoid connection closed issues
                content = await r.read()
                text = await r.text()
                json_data = (
                    await r.json()
                    if "application/json" in r.headers.get("Content-Type", "")
                    else None
                )

                # Create a response cache object
                response_cache = {
                    "status": r.status,
                    "content": content,
                    "text": text,
                    "json_data": json_data,
                    "headers": dict(r.headers),
                }

                # Update cache (with simple size limit)
                if len(_requests_response_cache) > 100:  # Keep max 100 entries
                    _requests_response_cache.clear()

                _requests_response_cache[url] = {
                    "response": response_cache,
                    "datetime": now,
                }
                return response_cache

            # Handle non-200 responses
            return {
                "status": r.status,
                "content": await r.read(),
                "text": await r.text(),
                "json_data": None,
                "headers": dict(r.headers),
            }


async def parse_maven_metadata(url: str) -> MavenMetadata:
    """
    Parses a maven metadata file
    """
    r = await get_requests_response_cache(url)
    # The structure of the metadata file is simple. So you don't need a XML parser. It can be parsed using RegEx.
    text = r["text"]
    return {
        "release": re.search("(?<=<release>).*?(?=</release>)", text, re.MULTILINE).group(),  # type: ignore
        "latest": re.search("(?<=<latest>).*?(?=</latest>)", text, re.MULTILINE).group(),  # type: ignore
        "versions": re.findall("(?<=<version>).*?(?=</version>)", text, re.MULTILINE),
    }


async def extract_file_from_zip(
    handler: zipfile.ZipFile,
    zip_path: str,
    extract_path: str,
    minecraft_directory: str | os.PathLike | None = None,
) -> None:
    """
    Extract a file from a zip handler into the given path
    """
    if minecraft_directory is not None:
        check_path_inside_minecraft_directory(minecraft_directory, extract_path)

    try:
        os.makedirs(os.path.dirname(extract_path), exist_ok=True)
    except Exception:
        pass

    with handler.open(zip_path, "r") as f:
        data = f.read()
        async with aiofiles.open(extract_path, "wb") as w:
            await w.write(data)


def assert_func(expression: bool) -> None:
    """
    The assert keyword is not available when running Python in Optimized Mode.
    This function is a drop-in replacement.
    See https://docs.python.org/3/using/cmdline.html?highlight=pythonoptimize#cmdoption-O
    """
    if not expression:
        raise AssertionError()


async def get_client_json(
    version: str, minecraft_directory: str | os.PathLike
) -> ClientJson:
    """Load the client.json for the given version"""
    local_path = os.path.join(
        minecraft_directory, "versions", version, f"{version}.json"
    )
    if os.path.isfile(local_path):
        async with aiofiles.open(local_path, "r", encoding="utf-8") as f:
            data = json.loads(await f.read())

        if "inheritsFrom" in data:
            data = await inherit_json(data, minecraft_directory)

        return data

    version_list = (
        await get_requests_response_cache(
            "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
        )
    )["json_data"]

    for i in version_list["versions"]:
        if i["id"] == version:
            return (await get_requests_response_cache(i["url"]))["json_data"]

    raise VersionNotFound(version)
