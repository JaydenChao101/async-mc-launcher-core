# Async MC Launcher Core Examples

This directory contains comprehensive examples for using the `async-mc-launcher-core` library to build custom Minecraft launchers. All examples are designed to work with Python 3.10+ and use modern async/await patterns.

## Quick Start

1. Install the library:
   ```bash
   pip install async-mc-launcher-core
   ```

2. Install example dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start with the [Basic Usage Examples](basic_usage/) to understand core concepts.

## Examples Structure

### 📁 [Basic Usage](basic_usage/)
Essential examples for getting started with the library:
- **Simple Launcher**: Basic Minecraft launching functionality
- **Version Management**: List, download, and manage Minecraft versions

### 🔐 [Authentication](authentication/)
Examples for different authentication methods:
- **Microsoft Login**: Complete Microsoft OAuth2 authentication flow
- **Offline Mode**: Launch Minecraft in offline/demo mode

### 🔧 [Modding](modding/)
Examples for mod loader integration:
- **Forge Launcher**: Launch Minecraft with Forge mod loader
- **Fabric Launcher**: Launch Minecraft with Fabric mod loader  
- **Quilt Launcher**: Launch Minecraft with Quilt mod loader

### 🚀 [Advanced](advanced/)
Advanced usage patterns and custom implementations:
- **Custom GUI Launcher**: Simple GUI launcher using tkinter
- **Profile Management**: Advanced profile and instance management

## Common Patterns

### Async/Await Usage
All examples use proper async/await patterns:

```python
import asyncio
from launcher_core import microsoft_account, install

async def main():
    # Your async code here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling
Examples include comprehensive error handling:

```python
from launcher_core.exceptions import VersionNotFound, MinecraftException

try:
    result = await some_launcher_operation()
except VersionNotFound as e:
    print(f"Version not found: {e}")
except MinecraftException as e:
    print(f"Launcher error: {e}")
```

### Configuration Management
Most examples support configuration files for sensitive data:

```python
# Create a config.json file:
{
    "client_id": "your_azure_app_client_id",
    "minecraft_directory": "/path/to/.minecraft",
    "java_executable": "/path/to/java"
}
```

## Prerequisites

- Python 3.10 or higher
- Microsoft Azure application (for Microsoft authentication examples)
- Java installation (for launching Minecraft)

## Environment Setup

For examples requiring authentication, you'll need:

1. **Microsoft Azure App**: Register an application in Azure Portal for OAuth2
2. **Java**: Install Java 17+ for modern Minecraft versions
3. **Minecraft Directory**: A valid `.minecraft` directory structure

## Running Examples

Each example directory contains detailed README files with specific instructions. Generally:

1. Navigate to the example directory
2. Review the README.md for specific requirements
3. Edit any configuration files as needed
4. Run the example: `python example_name.py`

## Common Issues

### Authentication Errors
- Ensure your Azure application is properly configured
- Check that redirect URIs match your application settings
- Verify your client ID and secret are correct

### Version Download Failures
- Check your internet connection
- Ensure you have write permissions to the Minecraft directory
- Verify the requested version exists

### Launch Failures
- Confirm Java is installed and accessible
- Check that all required libraries are downloaded
- Verify your Minecraft directory structure is correct

## Contributing

Found an issue or want to add an example? Please:
1. Check existing issues and examples
2. Follow the existing code style and patterns
3. Include proper error handling and documentation
4. Test your example thoroughly

## Support

- 📖 [Online Documentation](https://minecraft-launcher-lib.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/JaydenChao101/async-mc-launcher-core/issues)
- 💬 [Discussions](https://github.com/JaydenChao101/async-mc-launcher-core/discussions)

## License

These examples are provided under the same BSD-2-Clause license as the main library.