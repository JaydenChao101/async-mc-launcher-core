# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
'''command contains the function for creating the minecraft command'''
import json
import copy
import os
import aiofiles
from ._helper import (
    parse_rule_list,
    inherit_json,
    get_classpath_separator,
    get_library_path,
)
from ._internal_types.shared_types import ClientJson, ClientJsonArgumentRule
from .runtime import get_executable_path
from .exceptions import VersionNotFound
from .utils import get_library_version
from ._types import MinecraftOptions
from ._types import Credential as AuthCredential
from .natives import get_natives

__all__ = ["get_minecraft_command"]


def get_libraries(data: ClientJson, path: str) -> str:
    """
    Returns the argument with all libs that come after -cp
    """
    classpath_seperator = get_classpath_separator()
    libstr = ""
    for i in data["libraries"]:
        if "rules" in i and not parse_rule_list(i["rules"], {}):
            continue

        libstr += get_library_path(i["name"], path) + classpath_seperator
        native = get_natives(i)
        if native != "":
            if "downloads" in i and "path" in i["downloads"]["classifiers"][native]:  # type: ignore
                libstr += os.path.join(
                    path,
                    "libraries",
                    i["downloads"]["classifiers"][native]["path"],  # type: ignore
                ) + classpath_seperator
            else:
                libstr += (
                    get_library_path(i["name"] + "-" + native, path)
                    + classpath_seperator
                )

    if "jar" in data:
        libstr = libstr + os.path.join(
            path, "versions", data["jar"], data["jar"] + ".jar"
        )
    else:
        libstr = libstr + os.path.join(
            path, "versions", data["id"], data["id"] + ".jar"
        )

    return libstr


async def replace_arguments(
    argstr: str,
    version_data: ClientJson,
    path: str,
    options: MinecraftOptions,
    classpath: str,
) -> str:
    arg_replacements = {
        "${natives_directory}": options["nativesDirectory"],
        "${launcher_name}": options.get("launcherName", "minecraft-launcher-lib"),
        "${launcher_version}": options.get(
            "launcherVersion", await get_library_version()
        ),
        "${classpath}": classpath,
        "${auth_player_name}": options.get("username", "{username}"),
        "${version_name}": version_data["id"],
        "${game_directory}": options.get("gameDir", path),
        "${assets_root}": os.path.join(path, "assets"),
        "${assets_index_name}": version_data.get("assets", version_data["id"]),
        "${auth_uuid}": options.get("uuid", "{uuid}"),
        "${auth_access_token}": options.get("token", "{token}"),
        "${user_type}": "msa",
        "${version_type}": version_data["type"],
        "${user_properties}": "{}",
        "${resolution_width}": options.get("resolutionWidth", 854),
        "${resolution_height}": options.get("resolutionHeight", 480),
        "${game_assets}": os.path.join(path, "assets", "virtual", "legacy"),
        "${auth_session}": options.get("token", "{token}"),
        "${library_directory}": os.path.join(path, "libraries"),
        "${classpath_separator}": get_classpath_separator(),
        "${quickPlayPath}": options.get("quickPlayPath") or "{quickPlayPath}",
        "${quickPlaySingleplayer}": options.get("quickPlaySingleplayer")
        or "{quickPlaySingleplayer}",
        "${quickPlayMultiplayer}": options.get("quickPlayMultiplayer")
        or "{quickPlayMultiplayer}",
        "${quickPlayRealms}": options.get("quickPlayRealms") or "{quickPlayRealms}",
    }

    for key, value in arg_replacements.items():
        argstr = argstr.replace(key, str(value))

    return argstr


async def get_arguments_string(
    version_data: ClientJson, path: str, options: MinecraftOptions, classpath: str
) -> list[str]:
    """
    Turns the argument string from the client.json into a list
    """
    arglist: list[str] = []

    for v in version_data["minecraftArguments"].split(" "):
        v = await replace_arguments(v, version_data, path, options, classpath)
        arglist.append(v)

    # Custom resolution is not in the list
    if options.get("customResolution", False):
        arglist.append("--width")
        arglist.append(options.get("resolutionWidth", "854"))
        arglist.append("--height")
        arglist.append(options.get("resolutionHeight", "480"))

    if options.get("demo", False):
        arglist.append("--demo")

    return arglist


async def get_arguments(
    data: list[str | ClientJsonArgumentRule],
    version_data: ClientJson,
    path: str,
    options: MinecraftOptions,
    classpath: str,
) -> list[str]:
    """
    Returns all arguments from the client.json
    """
    arglist: list[str] = []
    for i in data:
        # i could be the argument
        if isinstance(i, str):
            arglist.append(
                await replace_arguments(i, version_data, path, options, classpath)
            )
        else:
            # Rules might has 2 different names in different client.json
            if "compatibilityRules" in i and not parse_rule_list(
                i["compatibilityRules"], options
            ):
                continue

            if "rules" in i and not parse_rule_list(i["rules"], options):
                continue

            # Sometimes  i["value"] is the argument
            if isinstance(i["value"], str):
                arglist.append(
                    await replace_arguments(
                        i["value"], version_data, path, options, classpath
                    )
                )
            # Sometimes i["value"] is a list of arguments
            else:
                for v in i["value"]:
                    v = await replace_arguments(
                        v, version_data, path, options, classpath
                    )
                    arglist.append(v)
    return arglist


async def get_minecraft_command(
    version: str,
    minecraft_directory: str | os.PathLike,
    options: MinecraftOptions,
    Credential: AuthCredential | None = None,
) -> list[str]:
    """
    Returns the command for running minecraft as list. The given command can be executed with subprocess. Use :func:`~launcher_core.utils.get_minecraft_directory` to get the default Minecraft directory.

    :param version: The Minecraft version
    :param minecraft_directory: The path to your Minecraft directory
    :param options: Some Options (see below)

    ``options`` is a dict:

    .. code:: python

        options = {
            # This is needed
            "username": The Username,
            "uuid": uuid of the user,
            "token": the accessToken,
            # This is optional
            "executablePath": "java", # The path to the java executable
            "defaultExecutablePath": "java", # The path to the java executable if the client.json has none
            "jvmArguments": [], #The jvmArguments
            "launcherName": "minecraft-launcher-lib", # The name of your launcher
            "launcherVersion": "1.0", # The version of your launcher
            "gameDirectory": "/home/user/.minecraft", # The gameDirectory (default is the path given in arguments)
            "demo": False, # Run Minecraft in demo mode
            "customResolution": False, # Enable custom resolution
            "resolutionWidth": "854", # The resolution width
            "resolutionHeight": "480", # The resolution height
            "server": "example.com", # The IP of a server where Minecraft connect to after start
            "port": "123", # The port of a server where Minecraft connect to after start
            "nativesDirectory": "minecraft_directory/versions/version/natives", # The natives directory
            "enableLoggingConfig": False, # Enable use of the log4j configuration file
            "disableMultiplayer": False, # Disables the multiplayer
            "disableChat": False, # Disables the chat
            "quickPlayPath": None, # The Quick Play Path
            "quickPlaySingleplayer": None, # The Quick Play Singleplayer
            "quickPlayMultiplayer": None, # The Quick Play Multiplayer
            "quickPlayRealms": None, # The Quick Play Realms
        }

    You can use the :doc:`microsoft_account` module to get the needed information.
    For more information about the options take a look at the :doc:`/tutorial/more_launch_options` tutorial.
    """
    path = str(minecraft_directory)

    if Credential:
        token = Credential.access_token if Credential else options.get("token", None)
        username = Credential.username if Credential else options.get("username", None)
        uuid = Credential.uuid if Credential else options.get("uuid", None)
        options["token"] = token
        options["username"] = username
        options["uuid"] = uuid

    if not os.path.isdir(os.path.join(path, "versions", version)):
        raise VersionNotFound(version)

    options = copy.deepcopy(options)

    json_path = os.path.join(path, "versions", version, version + ".json")
    async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
        data: ClientJson = json.loads(await f.read())

    if "inheritsFrom" in data:
        data = await inherit_json(data, path)

    options["nativesDirectory"] = options.get(
        "nativesDirectory", os.path.join(path, "versions", data["id"], "natives")
    )
    classpath = get_libraries(data, path)

    command: list[str] = []
    # Add Java executable
    if "executablePath" in options:
        command.append(options["executablePath"])
    elif "javaVersion" in data:
        javaPath = await get_executable_path(data["javaVersion"]["component"], path)
        if javaPath is None:
            command.append("java")
        else:
            command.append(javaPath)
    else:
        command.append(options.get("defaultExecutablePath", "java"))

    if "jvmArguments" in options:
        command = command + options["jvmArguments"]

    # Newer Versions have jvmArguments in client.json
    if isinstance(data.get("arguments", None), dict):
        if "jvm" in data["arguments"]:
            command = command + await get_arguments(
                data["arguments"]["jvm"], data, path, options, classpath
            )
        else:
            command.append("-Djava.library.path=" + options["nativesDirectory"])
            command.append("-cp")
            command.append(classpath)
    else:
        command.append("-Djava.library.path=" + options["nativesDirectory"])
        command.append("-cp")
        command.append(classpath)

    # The argument for the logger file
    if options.get("enableLoggingConfig", False):
        if "logging" in data:
            if len(data["logging"]) != 0:
                logger_file = os.path.join(
                    path,
                    "assets",
                    "log_configs",
                    data["logging"]["client"]["file"]["id"],
                )
                command.append(
                    data["logging"]["client"]["argument"].replace(
                        "${path}", logger_file
                    )
                )

    command.append(data["mainClass"])

    if "minecraftArguments" in data:
        # For older versions
        command = command + await get_arguments_string(data, path, options, classpath)
    else:
        command = command + await get_arguments(
            data["arguments"]["game"], data, path, options, classpath
        )

    if "server" in options:
        command.append("--server")
        command.append(options["server"])
        if "port" in options:
            command.append("--port")
            command.append(options["port"])

    if options.get("disableMultiplayer", False):
        command.append("--disableMultiplayer")

    if options.get("disableChat", False):
        command.append("--disableChat")

    return command
