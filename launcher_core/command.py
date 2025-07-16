# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"""command contains the function for creating the minecraft command"""

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
from .models import MinecraftOptions
from .models import Credential as AuthCredential
from .natives import get_natives

__all__ = ["get_minecraft_command"]


async def get_libraries(data: ClientJson, path: str) -> str:
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
                libstr += (
                    os.path.join(
                        path,
                        "libraries",
                        i["downloads"]["classifiers"][native]["path"],  # type: ignore
                    )
                    + classpath_seperator
                )
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


class MinecraftCommandBuilder:
    """Minecraft命令構建器，負責組裝啟動命令的各个部分"""

    def __init__(
        self, version: str, minecraft_directory: str, options: MinecraftOptions
    ):
        self.version = version
        self.path = str(minecraft_directory)
        self.options = copy.deepcopy(options)
        self.data: ClientJson | None = None
        self.classpath: str = ""
        self.command: list[str] = []

    async def validate_version(self) -> None:
        """驗證版本是否存在"""
        if not os.path.isdir(os.path.join(self.path, "versions", self.version)):
            raise VersionNotFound(self.version)

    def set_credential(self, credential: AuthCredential | None) -> None:
        """設置認證信息"""
        if credential:
            self.options["token"] = credential.access_token
            self.options["username"] = credential.username
            self.options["uuid"] = credential.uuid

    async def load_version_data(self) -> None:
        """加載版本數據"""
        json_path = os.path.join(
            self.path, "versions", self.version, self.version + ".json"
        )
        async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
            self.data = json.loads(await f.read())

        if "inheritsFrom" in self.data:
            self.data = await inherit_json(self.data, self.path)

    def setup_natives_directory(self) -> None:
        """設置natives目錄"""
        if self.data:
            self.options["nativesDirectory"] = self.options.get(
                "nativesDirectory",
                os.path.join(self.path, "versions", self.data["id"], "natives"),
            )

    async def build_classpath(self) -> None:
        """構建類路徑"""
        if self.data:
            self.classpath = await get_libraries(self.data, self.path)

    async def add_java_executable(self) -> None:
        """添加Java可執行文件路徑"""
        if "executablePath" in self.options:
            self.command.append(self.options["executablePath"])
        elif self.data and "javaVersion" in self.data:
            java_path = await get_executable_path(
                self.data["javaVersion"]["component"], self.path
            )
            self.command.append(java_path or "java")
        else:
            self.command.append(self.options.get("defaultExecutablePath", "java"))

    async def add_jvm_arguments(self) -> None:
        """添加JVM參數"""
        # 添加用戶自定義的JVM參數
        if "jvmArguments" in self.options:
            self.command.extend(self.options["jvmArguments"])

        # 添加版本特定的JVM參數
        if (
            self.data
            and isinstance(self.data.get("arguments"), dict)
            and "jvm" in self.data["arguments"]
        ):
            jvm_args = await get_arguments(
                self.data["arguments"]["jvm"],
                self.data,
                self.path,
                self.options,
                self.classpath,
            )
            self.command.extend(jvm_args)
        else:
            # 舊版本的默認JVM參數
            self.command.extend(
                [
                    f"-Djava.library.path={self.options['nativesDirectory']}",
                    "-cp",
                    self.classpath,
                ]
            )

    def add_logging_config(self) -> None:
        """添加日誌配置參數"""
        if not self.options.get("enableLoggingConfig", False) or not self.data:
            return

        logging_config = self.data.get("logging", {})
        if logging_config and "client" in logging_config:
            logger_file = os.path.join(
                self.path,
                "assets",
                "log_configs",
                logging_config["client"]["file"]["id"],
            )
            log_argument = logging_config["client"]["argument"].replace(
                "${path}", logger_file
            )
            self.command.append(log_argument)

    def add_main_class(self) -> None:
        """添加主類"""
        if self.data:
            self.command.append(self.data["mainClass"])

    async def add_game_arguments(self) -> None:
        """添加遊戲參數"""
        if not self.data:
            return

        if "minecraftArguments" in self.data:
            # 舊版本格式
            game_args = await get_arguments_string(
                self.data, self.path, self.options, self.classpath
            )
            self.command.extend(game_args)
        else:
            # 新版本格式
            game_args = await get_arguments(
                self.data["arguments"]["game"],
                self.data,
                self.path,
                self.options,
                self.classpath,
            )
            self.command.extend(game_args)

    def add_server_arguments(self) -> None:
        """添加服務器連接參數"""
        if "server" in self.options:
            self.command.extend(["--server", self.options["server"]])
            if "port" in self.options:
                self.command.extend(["--port", self.options["port"]])

    def add_multiplayer_chat_arguments(self) -> None:
        """添加多人遊戲和聊天禁用參數"""
        if self.options.get("disableMultiplayer", False):
            self.command.append("--disableMultiplayer")

        if self.options.get("disableChat", False):
            self.command.append("--disableChat")

    async def build(self) -> list[str]:
        """構建完整的Minecraft啟動命令"""
        await self.validate_version()
        await self.load_version_data()
        self.setup_natives_directory()
        await self.build_classpath()

        await self.add_java_executable()
        await self.add_jvm_arguments()
        self.add_logging_config()
        self.add_main_class()
        await self.add_game_arguments()
        self.add_server_arguments()
        self.add_multiplayer_chat_arguments()

        return self.command


async def get_minecraft_command(
    version: str,
    minecraft_directory: str | os.PathLike,
    options: MinecraftOptions,
    credential: AuthCredential | None = None,
) -> list[str]:
    """
    Returns the command for running minecraft as list. The given command can be executed with subprocess.
    Use :func:`~launcher_core.utils.get_minecraft_directory` to get the default Minecraft directory.

    :param version: The Minecraft version
    :param minecraft_directory: The path to your Minecraft directory
    :param options: Some Options (see below)
    :param credential: Authentication credential object

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
    builder = MinecraftCommandBuilder(version, minecraft_directory, options)
    builder.set_credential(credential)
    return await builder.build()
