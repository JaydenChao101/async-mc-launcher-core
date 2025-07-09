# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
"exceptions contains all custom exceptions that can be raised by minecraft_launcher_lib"
from ._types import VanillaLauncherProfile


class VersionNotFound(ValueError):
    """
    The given version does not exists
    """

    def __init__(self, version: str) -> None:
        self.version: str = version
        "The version that caused the exception"

        self.msg: str = f"Version {version} was not found"
        "A message to display"

        ValueError.__init__(self, self.msg)


class UnsupportedVersion(ValueError):
    """
    This Exception is raised when you try to run :func:`~launcher_core.fabric.install_fabric`
    or :func:`~launcher_core.quilt.install_quilt` with a unsupported version
    """

    def __init__(self, version: str) -> None:
        self.version: str = version
        "The version that caused the exception"

        self.msg: str = f"Version {version} is not supported"
        "A message to display"

        ValueError.__init__(self, self.msg)


class ExternalProgramError(Exception):
    """
    This Exception is raised when a external program failed
    """

    def __init__(self, command: list[str], stdout: bytes, stderr: bytes) -> None:
        self.command: list[str] = command
        "The command that caused the error"

        self.stdout: bytes = stdout
        "The stdout of the command"

        self.stderr: bytes = stderr
        "The stderr of the command"


class InvalidRefreshToken(ValueError):
    """
    Raised when
    :func:`~launcher_core.microsoft_account.complete_refresh` is called with a invalid refresh token
    """

    def __init__(self, token: str) -> None:
        self.token: str = token
        "The invalid refresh token"

        super().__init__("Invalid refresh token")


class InvalidVanillaLauncherProfile(ValueError):
    """
    Raised when a function from the
    :doc:`vanilla_launcher` module is called with a invalid vanilla profile
    """

    def __init__(self, profile: VanillaLauncherProfile) -> None:
        self.profile: VanillaLauncherProfile = profile
        "The invalid profile"

        super().__init__("Invalid VanillaLauncherProfile")


class SecurityError(Exception):
    """
    Raised when something security related happens
    """

    def __init__(self, code: str, message: str) -> None:
        self.code: str = code
        "A Code to specify the Error"

        self.message: str = message
        "A Message to display"

        super().__init__(message)


class FileOutsideMinecraftDirectory(SecurityError):
    """
    Raised when a File should be placed outside the given Minecraft directory
    """

    def __init__(self, path: str, minecraft_directory: str) -> None:
        self.path: str = path
        "The Path of the File"

        self.minecraft_directory: str = minecraft_directory
        "The Minecraft directory of the File"

        super().__init__(
            "FileOutsideMinecraftDirectory",
            f"Tried to place {path} outside {minecraft_directory}",
        )


class InvalidChecksum(SecurityError):
    """
    Raised when a File did not match the Checksum
    """

    def __init__(
        self, url: str, path: str, expected_checksum: str, actual_checksum: str
    ) -> None:
        self.url: str = url
        "The URL to the File with the wrong Checksum"

        self.path: str = path
        "The Path to the File with the wrong Checksum"

        self.expected_checksum: str = expected_checksum
        "The expected Checksum"

        self.actual_checksum: str = actual_checksum
        "The actual Checksum"

        super().__init__(
            "InvalidChecksum",
            f"{path} has the wrong Checksum (expected {expected_checksum} got {actual_checksum})",
        )


class AzureAppNotPermitted(Exception):
    """
    Raised when you try to use a Azure App, that don't have the Permission to use the Minecraft API.
    """

    def __init__(self) -> None:
        super().__init__(
            "It looks like your Azure App don't have the Permission to use the Minecraft API."
        )


class PlatformNotSupported(Exception):
    """
    Raised, when the current Platform is not supported by a feature
    """

    def __init__(self) -> None:
        super().__init__("Your Platform is not supported")


class AccountNotOwnMinecraft(Exception):
    """
    Raised by
    :func:`~launcher_core.microsoft_account.complete_login`
    and :func:`~launcher_core.microsoft_account.complete_login`
    when the Account does not own Minecraft
    """

    def __init__(self) -> None:
        super().__init__("This Account does not own Minecraft")


class AccountBanFromXbox(Exception):
    """
    Raised when the Account is banned from Xbox
    """

    def __init__(self) -> None:
        super().__init__("This Account is banned from Xbox")


class AccountNotHaveXbox(Exception):
    """
    Raised when the Account does not have Xbox
    """

    def __init__(self) -> None:
        super().__init__("This Account does not have Xbox")


class XboxLiveNotAvailable(Exception):
    """
    Raised when the Xbox Live Service is not available
    """

    def __init__(self) -> None:
        super().__init__("Xbox Live Service is not available")


class AccountNeedAdultVerification(Exception):
    """
    Raised when the Account needs adult verification
    """

    def __init__(self) -> None:
        super().__init__("This Account needs adult verification")


class NeedAccountInfo(ValueError):
    """
    Raised when the Account needs to be verified
    """

    def __init__(self, message: str = "The Account needs to be verified") -> None:
        super().__init__(message)


class XErrNotFound(ValueError):
    """
    Raised when the XBox Error Code is not found
    """

    def __init__(self, message: str = "The XBox Error Code is not found") -> None:
        super().__init__(message)


class DeviceCodeExpiredError(ValueError):
    """
    Raised when the Device Code is expired
    """

    def __init__(self, message: str = "The Device Code is expired") -> None:
        super().__init__(message)
