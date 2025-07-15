from . import Credential as AuthCredential
from .exceptions import NeedAccountInfo, AccountNotOwnMinecraft
from .mojang import have_minecraft
from pydantic import BaseModel


class MultipleCredentials(BaseModel):
    """
    用於存儲多個帳戶憑證
    """

    AuthCredentials: list[AuthCredential]


class AccountManager:
    """
    用於管理帳戶的自定義類別
    一行代碼直接管理帳戶的憑證
    """

    @staticmethod
    async def Checker(Credential: AuthCredential) -> bool:
        """
        檢查帳戶憑證是否有效
        """
        if not Credential.access_token:
            raise NeedAccountInfo("帳戶憑證無效或未提供")

        access_token = Credential.access_token
        try:
            await have_minecraft(access_token)
        except AccountNotOwnMinecraft:
            return False
        return True

    @staticmethod
    async def MultipleChecker(MultipleCredentials: MultipleCredentials) -> bool:
        """
        檢查多個帳戶憑證是否有效
        """
        if not MultipleCredentials.AuthCredentials:
            raise NeedAccountInfo("沒有提供任何帳戶憑證")

        for credential in MultipleCredentials.AuthCredentials:
            if not await AccountManager.Checker(credential):
                return False
        return True
