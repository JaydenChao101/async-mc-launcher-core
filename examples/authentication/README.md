# Authentication Examples

This directory contains examples for different authentication methods with async-mc-launcher-core.

## Examples

### 🔐 microsoft_login.py
Complete Microsoft OAuth2 authentication implementation for accessing official Minecraft multiplayer servers.

**Features:**
- Full Microsoft OAuth2 flow
- Token management and refresh
- Profile retrieval and validation  
- Automatic browser opening
- Persistent authentication storage
- Error handling for common issues

**Requirements:**
- Microsoft Azure application registration
- Web browser for authentication
- Internet connection

**Usage:**
```bash
python microsoft_login.py
```

**Setup Steps:**
1. Register application in Azure Portal
2. Configure redirect URI: `http://localhost`
3. Grant Minecraft API permissions
4. Run the example and follow authentication flow

### 🔒 offline_mode.py
Offline mode launcher for playing without Microsoft authentication.

**Features:**
- Custom username support
- Profile management
- Demo mode option
- Custom resolution settings
- Advanced JVM configuration
- No internet required (after version download)

**Usage:**
```bash
python offline_mode.py
```

**What Works:**
- Singleplayer worlds
- LAN multiplayer
- Mods and resource packs
- Custom profiles

## Authentication Methods Comparison

| Feature | Microsoft Login | Offline Mode |
|---------|----------------|--------------|
| **Official Servers** | ✅ Full access | ❌ Not supported |
| **Realms** | ✅ Full access | ❌ Not supported |
| **Singleplayer** | ✅ Full access | ✅ Full access |
| **LAN Multiplayer** | ✅ Full access | ✅ Full access |
| **Skin Support** | ✅ Official skins | ⚠️ Limited/Custom |
| **Username** | 🔒 Fixed to account | ✅ Any username |
| **Internet Required** | 🌐 For auth/refresh | ❌ After download |
| **Setup Complexity** | 🔧 Azure registration | ✅ Simple |

## Microsoft Authentication Setup

### Azure Application Registration

1. **Go to Azure Portal**
   - Visit [portal.azure.com](https://portal.azure.com)
   - Sign in with your Microsoft account

2. **Register Application**
   ```
   App registrations → New registration
   Name: "My Minecraft Launcher"
   Redirect URI: http://localhost
   ```

3. **Configure Permissions**
   ```
   API permissions → Add permission
   Microsoft Graph → Delegated permissions
   Add: XboxLive.signin, User.Read
   ```

4. **Get Client ID**
   - Copy the Application (client) ID
   - Use in your launcher configuration

### Configuration File

Create `auth_config.json` for storing authentication data:
```json
{
  "access_token": "your_minecraft_access_token",
  "refresh_token": "your_refresh_token",
  "expires_in": 3600,
  "profile": {
    "name": "your_minecraft_username",
    "id": "your_minecraft_uuid"
  }
}
```

## Troubleshooting

### Microsoft Authentication Issues

**"Azure App not permitted"**
- Ensure your Azure app has correct permissions
- Grant admin consent for permissions
- Check redirect URI configuration

**"Account does not own Minecraft"**
- Verify the Microsoft account owns Minecraft
- Try logging into minecraft.net to confirm
- Check if account needs migration

**"Invalid refresh token"**
- Delete stored auth data and re-authenticate
- Tokens expire after extended periods
- Network issues can corrupt stored tokens

**Browser doesn't open**
- Manually copy the URL to your browser
- Check firewall settings
- Try different browser

### Offline Mode Issues

**"Version not found"**
- Check spelling of version ID
- Use version manager to see available versions
- Some very old versions may not be available

**"Permission denied"**
- Ensure write access to Minecraft directory
- Close other Minecraft launchers
- Check antivirus software

**Custom skins not working**
- Skin support varies by Minecraft version
- Use resource packs for custom skins
- Some mods add offline skin support

## Security Considerations

### Microsoft Authentication
- Store tokens securely
- Don't share refresh tokens
- Use HTTPS in production applications
- Implement proper token rotation

### Offline Mode
- UUIDs are deterministic (same username = same UUID)
- No verification of username uniqueness
- Local profile data is unencrypted

## Best Practices

### Token Management
```python
# Check token expiry before use
if time.time() > auth_data.get('expires_at', 0):
    auth_data = await refresh_authentication()

# Handle refresh failures gracefully
if not auth_data:
    # Fallback to re-authentication
    auth_data = await authenticate_new_user()
```

### Error Handling
```python
from launcher_core.exceptions import (
    AccountNotOwnMinecraft,
    InvalidRefreshToken,
    AzureAppNotPermitted
)

try:
    result = await authenticate_user()
except AccountNotOwnMinecraft:
    print("This account doesn't own Minecraft")
except InvalidRefreshToken:
    print("Please log in again")
except AzureAppNotPermitted:
    print("Azure app needs Minecraft API permissions")
```

### Offline Profiles
```python
# Create consistent UUIDs for offline users
namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
user_uuid = str(uuid.uuid5(namespace, username.lower()))
```

## Advanced Usage

### Custom Azure Configuration
```python
azure_app = microsoft_account.AzureApplication(
    client_id="your_client_id",
    redirect_uri="your_redirect_uri"
)
login = microsoft_account.Login(azure_app=azure_app)
```

### Hybrid Authentication
```python
# Try Microsoft auth first, fallback to offline
try:
    credentials = await get_microsoft_credentials()
except Exception:
    credentials = create_offline_credentials(username)
```

### Profile Migration
```python
# Convert offline profile to Microsoft account
offline_data = load_offline_profile(username)
microsoft_data = await authenticate_microsoft_account()
migrate_profile_data(offline_data, microsoft_data)
```

## Next Steps

After mastering authentication:

1. **Try Modding Examples** - Launch with mod loaders
2. **Advanced Examples** - Build custom launcher GUIs
3. **Integration** - Combine auth with version management

## Common Integration Patterns

### Launcher with Multiple Auth Methods
```python
class MultiAuthLauncher:
    def __init__(self):
        self.microsoft_auth = MicrosoftAuthenticator()
        self.offline_launcher = OfflineLauncher()
    
    async def launch(self, username, version, use_online=True):
        if use_online:
            credentials = await self.microsoft_auth.get_credentials()
        else:
            credentials = self.offline_launcher.create_credentials(username)
        
        return await self.launch_minecraft(credentials, version)
```

### Persistent Authentication Manager
```python
class AuthManager:
    def __init__(self):
        self.current_auth = None
        self.auth_methods = {
            'microsoft': MicrosoftAuthenticator(),
            'offline': OfflineLauncher()
        }
    
    async def get_credentials(self, method='auto'):
        if method == 'auto':
            # Try Microsoft first, fallback to offline
            pass
        
        return await self.auth_methods[method].get_credentials()
```