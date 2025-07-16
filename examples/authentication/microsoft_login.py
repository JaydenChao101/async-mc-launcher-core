#!/usr/bin/env python3
"""
Microsoft Login Example

This example demonstrates how to authenticate with Microsoft accounts
for Minecraft using the async-mc-launcher-core library. It shows:

1. Complete OAuth2 flow with Microsoft/Azure
2. Token management and refresh
3. Profile retrieval and validation
4. Launching with authenticated Credential

Requirements:
- Python 3.10+
- async-mc-launcher-core
- Microsoft Azure application registration
- Web browser for authentication
"""

import asyncio
import json
import logging
import os
import webbrowser
from pathlib import Path
from typing import Dict, Optional

from launcher_core import microsoft_account, mojang, command, _types
from launcher_core.setting import setup_logger
from launcher_core.exceptions import (
    AccountNotOwnMinecraft,
    InvalidRefreshToken,
    AzureAppNotPermitted,
)


class MicrosoftAuthenticator:
    """Handles Microsoft authentication for Minecraft."""

    def __init__(self, config_file: str = "auth_config.json"):
        """
        Initialize the authenticator.

        Args:
            config_file: Path to configuration file for storing auth data
        """
        self.config_file = Path(config_file)
        self.logger = setup_logger(enable_console=True, level=logging.INFO)
        self.auth_data: Optional[Dict] = None

        # Load existing auth data if available
        self.load_auth_data()

    def load_auth_data(self) -> None:
        """Load authentication data from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.auth_data = json.load(f)
                self.logger.info("Loaded existing authentication data")
            except Exception as e:
                self.logger.warning(f"Failed to load auth data: {e}")
                self.auth_data = None

    def save_auth_data(self, auth_data: Dict) -> None:
        """Save authentication data to config file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(auth_data, f, indent=2)
            self.auth_data = auth_data
            self.logger.info("Saved authentication data")
        except Exception as e:
            self.logger.error(f"Failed to save auth data: {e}")

    async def authenticate_new_user(
        self, azure_app: Optional[_types.AzureApplication] = None
    ) -> Optional[Dict]:
        """
        Authenticate a new user with Microsoft OAuth2 flow.

        Args:
            azure_app: Azure application configuration (uses default if None)

        Returns:
            Authentication data dictionary or None if failed
        """
        try:
            # Use provided Azure app or create default
            if azure_app is None:
                azure_app = microsoft_account.AzureApplication()

            # Create login instance
            login = microsoft_account.Login(azure_app=azure_app)

            # Get the authorization URL
            self.logger.info("Getting authorization URL...")
            auth_url = await login.get_login_url()

            print("\n" + "=" * 60)
            print("MICROSOFT AUTHENTICATION REQUIRED")
            print("=" * 60)
            print(f"Please visit this URL to authorize the application:")
            print(f"{auth_url}")
            print(
                "\nThe page will redirect you to a URL starting with 'http://localhost'"
            )
            print("Copy the ENTIRE redirect URL and paste it below.")
            print("=" * 60)

            # Optionally open browser automatically
            try_open = input("Open browser automatically? (Y/n): ").strip().lower()
            if try_open != "n":
                try:
                    webbrowser.open(auth_url)
                    print(
                        "Browser opened. Complete authentication and copy the redirect URL."
                    )
                except Exception as e:
                    self.logger.warning(f"Could not open browser: {e}")

            # Get the redirect URL from user
            while True:
                redirect_url = input("\nPaste the redirect URL here: ").strip()
                if redirect_url.startswith("http://localhost"):
                    break
                print(
                    "❌ Invalid URL. Please paste the complete redirect URL starting with 'http://localhost'"
                )

            # Extract authorization code
            self.logger.info("Extracting authorization code...")
            code = await microsoft_account.Login.extract_code_from_url(redirect_url)

            # Exchange code for tokens
            self.logger.info("Exchanging code for access token...")
            ms_token_data = await login.get_ms_token(code)

            # Get Xbox Live token
            self.logger.info("Getting Xbox Live token...")
            xbl_token_data = await microsoft_account.Login.get_xbl_token(
                ms_token_data["access_token"]
            )

            # Get XSTS token
            self.logger.info("Getting XSTS token...")
            xsts_token_data = await microsoft_account.Login.get_xsts_token(
                xbl_token_data["Token"]
            )

            # Extract UHS
            uhs = xbl_token_data["DisplayClaims"]["xui"][0]["uhs"]

            # Get Minecraft access token
            self.logger.info("Getting Minecraft access token...")
            mc_token_data = await microsoft_account.Login.get_minecraft_access_token(
                xsts_token_data["Token"], uhs
            )

            # Verify user owns Minecraft
            self.logger.info("Verifying Minecraft ownership...")
            await mojang.have_minecraft(mc_token_data["access_token"])

            # Get player profile
            self.logger.info("Getting player profile...")
            profile = await mojang.get_minecraft_profile(mc_token_data["access_token"])

            # Compile authentication data
            auth_data = {
                "access_token": mc_token_data["access_token"],
                "refresh_token": ms_token_data["refresh_token"],
                "expires_in": ms_token_data["expires_in"],
                "uhs": uhs,
                "xsts_token": xsts_token_data["Token"],
                "xbl_token": xbl_token_data["Token"],
                "profile": profile,
                "authenticated_at": asyncio.get_event_loop().time(),
            }

            # Save auth data
            self.save_auth_data(auth_data)

            self.logger.info(
                f"✅ Successfully authenticated as {profile['name']} ({profile['id']})"
            )
            return auth_data

        except AccountNotOwnMinecraft:
            self.logger.error("❌ This Microsoft account does not own Minecraft")
            return None
        except AzureAppNotPermitted:
            self.logger.error("❌ Azure application not permitted for Minecraft API")
            return None
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            return None

    async def refresh_authentication(self) -> Optional[Dict]:
        """
        Refresh existing authentication using stored refresh token.

        Returns:
            Refreshed authentication data or None if failed
        """
        if not self.auth_data or "refresh_token" not in self.auth_data:
            self.logger.warning("No refresh token available")
            return None

        try:
            self.logger.info("Refreshing authentication...")

            # Use stored refresh token
            refresh_token = self.auth_data["refresh_token"]

            # Create Azure app and login instance
            azure_app = microsoft_account.AzureApplication()
            login = microsoft_account.Login(azure_app=azure_app)

            # Refresh the Microsoft token
            ms_token_data = await login.refresh_ms_token(refresh_token)

            # Get new Xbox Live token
            xbl_token_data = await microsoft_account.Login.get_xbl_token(
                ms_token_data["access_token"]
            )

            # Get new XSTS token
            xsts_token_data = await microsoft_account.Login.get_xsts_token(
                xbl_token_data["Token"]
            )

            # Extract UHS
            uhs = xbl_token_data["DisplayClaims"]["xui"][0]["uhs"]

            # Get new Minecraft access token
            mc_token_data = await microsoft_account.Login.get_minecraft_access_token(
                xsts_token_data["Token"], uhs
            )

            # Verify token still works
            await mojang.have_minecraft(mc_token_data["access_token"])

            # Get updated profile
            profile = await mojang.get_minecraft_profile(mc_token_data["access_token"])

            # Update auth data
            refreshed_auth_data = {
                "access_token": mc_token_data["access_token"],
                "refresh_token": ms_token_data["refresh_token"],
                "expires_in": ms_token_data["expires_in"],
                "uhs": uhs,
                "xsts_token": xsts_token_data["Token"],
                "xbl_token": xbl_token_data["Token"],
                "profile": profile,
                "authenticated_at": asyncio.get_event_loop().time(),
            }

            self.save_auth_data(refreshed_auth_data)

            self.logger.info(
                f"✅ Successfully refreshed authentication for {profile['name']}"
            )
            return refreshed_auth_data

        except InvalidRefreshToken:
            self.logger.error("❌ Refresh token is invalid or expired")
            # Clear stored auth data
            if self.config_file.exists():
                self.config_file.unlink()
            self.auth_data = None
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to refresh authentication: {e}")
            return None

    async def get_valid_Credential(self) -> Optional[_types.Credential]:
        """
        Get valid Minecraft Credential, refreshing if necessary.

        Returns:
            Valid Credential or None if authentication failed
        """
        # Try to refresh existing auth
        if self.auth_data:
            refreshed = await self.refresh_authentication()
            if refreshed:
                self.auth_data = refreshed

        # If no valid auth, authenticate new user
        if not self.auth_data:
            self.auth_data = await self.authenticate_new_user()

        if not self.auth_data:
            return None

        # Create Credential object
        profile = self.auth_data["profile"]
        return _types.Credential(
            access_token=self.auth_data["access_token"],
            username=profile["name"],
            uuid=profile["id"],
        )

    def get_profile_info(self) -> Optional[Dict]:
        """Get stored profile information."""
        if self.auth_data and "profile" in self.auth_data:
            return self.auth_data["profile"]
        return None


async def launch_with_microsoft_auth(minecraft_dir: str, version: str = "1.21.1"):
    """
    Example of launching Minecraft with Microsoft authentication.

    Args:
        minecraft_dir: Path to Minecraft directory
        version: Minecraft version to launch
    """
    print("\n=== Launching Minecraft with Microsoft Authentication ===")

    # Create authenticator
    authenticator = MicrosoftAuthenticator()

    # Get valid Credential
    print("\nAuthenticating with Microsoft...")
    Credential = await authenticator.get_valid_Credential()

    if not Credential:
        print("❌ Authentication failed. Cannot launch Minecraft.")
        return False

    # Display profile info
    profile = authenticator.get_profile_info()
    if profile:
        print(f"✅ Authenticated as: {profile['name']}")
        print(f"   UUID: {profile['id']}")
        if "skins" in profile and profile["skins"]:
            print(f"   Skin: {profile['skins'][0].get('url', 'Default')}")

    # Set up launch options
    minecraft_path = Path(minecraft_dir)
    natives_dir = minecraft_path / "natives" / version
    natives_dir.mkdir(parents=True, exist_ok=True)

    options: _types.MinecraftOptions = {
        "gameDirectory": str(minecraft_path),
        "jvmArguments": ["-Xmx2048M", "-Xms1024M"],
        "nativesDirectory": str(natives_dir),
    }

    try:
        print(f"\nGenerating launch command for {version}...")

        # Generate launch command
        minecraft_command = await command.get_minecraft_command(
            version, str(minecraft_path), options, Credential=Credential
        )

        print("✅ Launch command generated successfully!")
        print(f"Command length: {len(minecraft_command)} arguments")

        # Ask user if they want to launch
        launch_choice = input("\nLaunch Minecraft now? (y/N): ").strip().lower()
        if launch_choice == "y":
            print("🚀 Launching Minecraft...")

            import subprocess

            process = subprocess.Popen(
                minecraft_command,
                cwd=str(minecraft_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            print(f"✅ Minecraft launched with PID: {process.pid}")
            print("Game is running. Check the game window.")
            return True
        else:
            print("Launch command ready. Use it when needed.")
            return True

    except Exception as e:
        print(f"❌ Failed to launch Minecraft: {e}")
        return False


async def main():
    """Main example function."""
    print("=== Microsoft Authentication Example ===")
    print("\nThis example demonstrates Microsoft OAuth2 authentication for Minecraft.")
    print("You'll need to complete authentication in your web browser.")

    # Get Minecraft directory
    minecraft_dir = input(
        "\nEnter Minecraft directory (or press Enter for default): "
    ).strip()
    if not minecraft_dir:
        minecraft_dir = os.path.join(os.path.expanduser("~"), ".minecraft")

    print(f"Using directory: {minecraft_dir}")

    # Menu loop
    authenticator = MicrosoftAuthenticator()

    while True:
        print("\n" + "=" * 50)
        print("Microsoft Authentication Options:")
        print("1. Authenticate new user")
        print("2. Refresh existing authentication")
        print("3. Show current profile")
        print("4. Launch Minecraft with auth")
        print("5. Clear stored authentication")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            # New authentication
            auth_data = await authenticator.authenticate_new_user()
            if auth_data:
                profile = auth_data["profile"]
                print(f"✅ Successfully authenticated as {profile['name']}")
            else:
                print("❌ Authentication failed")

        elif choice == "2":
            # Refresh authentication
            if not authenticator.auth_data:
                print("❌ No stored authentication to refresh")
                continue

            refreshed = await authenticator.refresh_authentication()
            if refreshed:
                print("✅ Authentication refreshed successfully")
            else:
                print("❌ Failed to refresh authentication")

        elif choice == "3":
            # Show profile
            profile = authenticator.get_profile_info()
            if profile:
                print(f"\n👤 Current Profile:")
                print(f"   Name: {profile['name']}")
                print(f"   UUID: {profile['id']}")
                if "skins" in profile and profile["skins"]:
                    for i, skin in enumerate(profile["skins"]):
                        print(f"   Skin {i+1}: {skin.get('url', 'Default')}")
                        print(f"            State: {skin.get('state', 'Unknown')}")
            else:
                print("❌ No authenticated profile available")

        elif choice == "4":
            # Launch Minecraft
            version = input("Enter Minecraft version (default: 1.21.1): ").strip()
            if not version:
                version = "1.21.1"

            success = await launch_with_microsoft_auth(minecraft_dir, version)
            if not success:
                print("Launch failed!")

        elif choice == "5":
            # Clear authentication
            if authenticator.config_file.exists():
                authenticator.config_file.unlink()
                authenticator.auth_data = None
                print("✅ Cleared stored authentication")
            else:
                print("No stored authentication to clear")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAuthentication interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in Microsoft authentication")
