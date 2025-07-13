# Basic Usage Examples

This directory contains fundamental examples for getting started with the async-mc-launcher-core library.

## Examples

### 📁 simple_launcher.py
A complete example showing how to launch Minecraft with basic configuration.

**Features:**
- Offline mode authentication (no Microsoft account required)
- Automatic version installation
- Interactive configuration
- Memory allocation settings
- Launch command generation

**Usage:**
```bash
python simple_launcher.py
```

**What it does:**
1. Lists available Minecraft versions
2. Allows you to select a version to launch
3. Downloads and installs the version if needed
4. Configures launch settings (username, memory)
5. Generates and optionally executes the launch command

### 📁 version_management.py
Comprehensive version management tool for listing, installing, and managing Minecraft versions.

**Features:**
- List all available versions with filtering
- View detailed version information
- Install specific versions
- Manage locally installed versions
- Uninstall versions

**Usage:**
```bash
python version_management.py
```

**Interactive menu options:**
1. **List available versions** - Browse Mojang's version catalog
2. **List installed versions** - See what's installed locally
3. **Get version details** - View detailed info about any version
4. **Install version** - Download and install a specific version
5. **Uninstall version** - Remove a locally installed version

## Prerequisites

### Required
- Python 3.10 or higher
- async-mc-launcher-core library
- Internet connection (for downloading versions)

### Recommended
- Java 17+ (for launching modern Minecraft versions)
- Java 8+ (for older Minecraft versions)

## Configuration

### Minecraft Directory
The examples will ask for your Minecraft directory. Common locations:

**Windows:**
```
C:\Users\[username]\AppData\Roaming\.minecraft
```

**macOS:**
```
~/Library/Application Support/minecraft
```

**Linux:**
```
~/.minecraft
```

### Memory Allocation
The simple launcher allows you to configure memory allocation:
- **Minimum recommended:** 2GB (2048MB)
- **For modded Minecraft:** 4-8GB (4096-8192MB)
- **For vanilla Minecraft:** 2-4GB (2048-4096MB)

## Common Use Cases

### Quick Launch
Run the simple launcher for a fast setup:
```bash
python simple_launcher.py
```
1. Accept default Minecraft directory
2. Choose a recent release version
3. Use default settings
4. Launch the game

### Version Exploration
Use the version manager to explore available versions:
```bash
python version_management.py
```
1. List available versions filtered by type
2. Get details about interesting versions
3. Install versions you want to try

### Offline Development
Both examples work offline once versions are installed:
- The simple launcher creates offline credentials
- Version manager can list installed versions without internet

## Error Handling

### Common Issues

**"Version not found"**
- Check your spelling of the version ID
- Use the version manager to see available versions
- Some very old versions may not be available

**"Permission denied"**
- Ensure you have write access to the Minecraft directory
- Try running with appropriate permissions
- Check that the directory isn't in use by another program

**"Java not found"**
- Install Java if not present
- The launcher will try to auto-detect Java
- You may need to specify the Java path manually

**"Download failed"**
- Check your internet connection
- Some versions may have temporary download issues
- Try again later or try a different version

### Debug Mode
For more detailed logging, you can modify the examples to use debug level:

```python
self.logger = setup_logger(enable_console=True, level=logging.DEBUG)
```

## Next Steps

After trying these basic examples:

1. **Try Authentication Examples** - Learn Microsoft account login
2. **Explore Modding Examples** - Launch with Forge, Fabric, or Quilt
3. **Advanced Examples** - Build custom GUIs and manage profiles

## Tips

### Performance
- Download versions once and reuse them
- Use appropriate memory allocation for your system
- Close other applications when launching modded Minecraft

### Development
- Start with offline mode for testing
- Use the version manager to prepare test environments
- Check the logs for detailed error information

### Customization
Both examples are designed to be modified:
- Add custom JVM arguments
- Implement different authentication methods
- Integrate with your own launcher interface