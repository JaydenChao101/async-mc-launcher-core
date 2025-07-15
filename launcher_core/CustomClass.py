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
    一行代碼直接管理帳戶的登入、登出和憑證
    """

    def __init__(self, AuthCredential: AuthCredential = None, MultipleCredentials: MultipleCredentials = None):
        self.credential = AuthCredential
        self.multiple_credentials = MultipleCredentials


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



