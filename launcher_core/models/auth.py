from pydantic.dataclasses import dataclass
from typing import NewType
from uuid import UUID

# 重新定義 MinecraftUUID
MinecraftUUID = NewType("MinecraftUUID", UUID)


@dataclass
class AzureApplication:
    """The Azure Application ID and Secret"""

    # The client ID of the Azure Application
    client_id: str = "00000000402b5328"
    client_secret: str = None
    redirect_uri: str = "https://login.live.com/oauth20_desktop.srf"


@dataclass
class Credential:
    """The credential of the player"""

    access_token: str = None
    username: str = None
    uuid: MinecraftUUID = None
    expires_in: int = None
    refresh_token: str = None
