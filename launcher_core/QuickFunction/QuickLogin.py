from launcher_core.microsoft_account import Login
from launcher_core.models.auth import Credential
import webbrowser

__all__ = ["EasyOpenBrower", "EasyAuth"]


async def EasyOpenBrower() -> str:
    """
    Opens the login URL in the default web browser.
    """
    login_instance = Login()
    # Open the login URL in the default web browser
    login_url = await login_instance.get_login_url()
    webbrowser.open(login_url)
    return login_url

async def EasyAuth(AuthUrl: str) -> Credential:
    """
    Handles the authentication process and returns the credentials.

    Returns:
        Credential: The authenticated user's credentials.
    """
    code = Login.extract_code_from_url(AuthUrl)
    creds = await Login().complete_login(code)
    return creds

if __name__ == '__main__':
    import asyncio
    # Example usage
    async def main():
        login_url = await EasyOpenBrower()
        print(f"Opened browser for login: {login_url}")
        auth_url = input("Please enter the callback URL after login: ")
        creds = await EasyAuth(auth_url)
        print(f"Authenticated successfully: {creds}")

    asyncio.run(main())
