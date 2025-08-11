"""Minimal Microsoft authentication related types for tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, TypedDict


@dataclass
class AzureApplication:
    """Configuration for an Azure application."""

    client_id: str = ""
    redirect_uri: str = ""
    client_secret: Optional[str] = None


@dataclass
class MinecraftProfile:
    id: str = ""
    name: str = ""


@dataclass
class XboxLiveProfile:
    user_id: str = ""
    gamertag: str = ""


class AuthorizationTokenResponse(TypedDict, total=False):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class XBLResponse(TypedDict, total=False):
    Token: str
    DisplayClaims: Any


class XSTSResponse(TypedDict, total=False):
    Token: str
    DisplayClaims: Any


class MinecraftAuthenticateResponse(TypedDict, total=False):
    access_token: str
    expires_in: int
