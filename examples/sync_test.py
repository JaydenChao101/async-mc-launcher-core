from launcher_core import sync, microsoft_account

print(sync(microsoft_account.Login().get_login_url()))