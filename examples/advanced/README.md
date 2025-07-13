# Advanced Examples

This directory contains advanced examples demonstrating sophisticated usage patterns of async-mc-launcher-core.

## Examples

### 🖥️ custom_launcher_gui.py
A complete custom GUI launcher built with tkinter.

**Features:**
- Modern tabbed interface
- Multiple authentication methods
- Profile management with GUI
- Real-time progress updates
- Settings management
- Async operations integration

**Usage:**
```bash
python custom_launcher_gui.py
```

**Key Components:**
- **AsyncTkinterHelper**: Bridges async operations with tkinter
- **MinecraftProfile**: Profile data structure
- **ProfileDialog**: GUI profile editor
- **CustomMinecraftLauncher**: Main launcher class

**GUI Features:**
- Multiple tabs (Launcher, Profiles, Settings)
- Profile selection and switching
- Launch progress tracking
- Directory and Java browsing
- Profile creation and editing

### 📁 profile_management.py
Advanced instance and profile management system.

**Features:**
- Multiple game instances
- Profile templates
- Mod set management
- Instance cloning and export
- Batch operations
- Statistics and analytics

**Usage:**
```bash
python profile_management.py
```

**Key Components:**
- **GameInstance**: Complete game instance representation
- **ProfileTemplate**: Template system for quick setup
- **ModSet**: Mod collection management
- **AdvancedProfileManager**: Main management system

**Management Features:**
- Template-based instance creation
- Instance cloning and migration
- Import/export functionality
- Mod set application
- Statistics and reporting

## Prerequisites

### Required
- Python 3.10 or higher
- async-mc-launcher-core library
- tkinter (usually included with Python)

### Optional
- Additional GUI libraries for enhanced features
- File system permissions for instance management

## Architecture Overview

### Async Integration
Both examples demonstrate proper integration of asyncio with GUI frameworks:

```python
class AsyncTkinterHelper:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.loop = None
        self.thread = None
    
    def run_async(self, coro, callback=None):
        """Run async operation in separate thread"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(callback)
```

### Profile System
Comprehensive profile management with inheritance and templates:

```python
class MinecraftProfile:
    def __init__(self, name, minecraft_version, mod_loader="vanilla", ...):
        self.name = name
        self.minecraft_version = minecraft_version
        self.mod_loader = mod_loader
        # ... additional properties
```

### Instance Management
Isolated game instances with metadata:

```python
class GameInstance:
    def __init__(self, name, directory, minecraft_version, ...):
        self.name = name
        self.directory = Path(directory)
        self.metadata = {}
        # ... instance configuration
```

## GUI Launcher Features

### Main Interface
- **Profile Selection**: Dropdown with current profiles
- **Launch Information**: Real-time profile details
- **Progress Tracking**: Visual progress bar and status
- **Quick Launch**: One-click launching

### Profile Management
- **Profile Editor**: Complete profile configuration
- **Template System**: Pre-configured setups
- **Validation**: Input validation and error handling
- **Persistence**: Automatic saving and loading

### Settings
- **Directory Management**: Minecraft and Java paths
- **Configuration**: Launcher preferences
- **Validation**: Path verification and browsing

## Advanced Profile Management

### Instance Organization
```
minecraft_instances/
├── instances/
│   ├── vanilla_latest/
│   ├── modded_fabric/
│   └── forge_heavy/
├── templates/
├── mod_sets/
└── config/
```

### Template System
Create reusable profile configurations:

```python
template = ProfileTemplate(
    name="Performance Pack",
    minecraft_version="1.21.1",
    mod_loader="fabric",
    memory=4096,
    required_mods=["sodium", "lithium", "phosphor"],
    description="Optimized performance setup"
)
```

### Mod Set Management
Organize mods into reusable collections:

```python
mod_set = ModSet(
    name="Performance Pack",
    mods=["sodium", "lithium", "phosphor"],
    compatible_loaders=["fabric", "quilt"],
    minecraft_versions=["1.21.1", "1.21"]
)
```

## Customization Guide

### Extending the GUI Launcher

#### Adding New Tabs
```python
def create_mods_tab(self):
    """Add a mod management tab"""
    self.mods_frame = ttk.Frame(notebook)
    notebook.add(self.mods_frame, text="Mods")
    # ... implement mod management UI
```

#### Custom Authentication
```python
class CustomAuthenticator:
    async def authenticate(self, method="microsoft"):
        if method == "microsoft":
            return await self.microsoft_auth()
        elif method == "custom":
            return await self.custom_auth()
```

#### Theme Customization
```python
style = ttk.Style()
style.theme_use('clam')  # or 'vista', 'xpnative'
style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
```

### Extending Profile Management

#### Custom Instance Types
```python
class ModpackInstance(GameInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modpack_info = {}
        self.dependencies = []
```

#### Advanced Templates
```python
class SmartTemplate(ProfileTemplate):
    def auto_configure(self, system_specs):
        """Auto-configure based on system capabilities"""
        if system_specs['ram'] >= 16:
            self.memory = 8192
        # ... intelligent configuration
```

#### Plugin System
```python
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def load_plugin(self, plugin_path):
        """Load external plugins"""
        pass
```

## Performance Optimization

### Memory Management
- Use appropriate memory allocation for instances
- Clean up temporary files
- Implement lazy loading for large datasets

### Async Optimization
- Batch async operations where possible
- Use connection pooling for downloads
- Implement proper cancellation handling

### File System
- Use atomic operations for critical files
- Implement proper locking for concurrent access
- Regular cleanup of temporary directories

## Error Handling

### GUI Error Handling
```python
def handle_error(self, error):
    """Handle errors gracefully in GUI"""
    self.root.after(0, lambda: messagebox.showerror(
        "Error", f"Operation failed: {error}"
    ))
```

### Recovery Mechanisms
```python
async def safe_operation(self, operation):
    """Wrapper for safe async operations"""
    try:
        return await operation()
    except Exception as e:
        await self.log_error(e)
        return None
```

### Validation
```python
def validate_profile(self, profile):
    """Validate profile configuration"""
    errors = []
    if not profile.name:
        errors.append("Profile name required")
    if not profile.minecraft_version:
        errors.append("Minecraft version required")
    return errors
```

## Testing and Debugging

### GUI Testing
```python
# Test profile creation
profile = MinecraftProfile("Test", "1.21.1")
assert profile.name == "Test"
assert profile.minecraft_version == "1.21.1"
```

### Debug Mode
```python
# Enable debug logging
self.logger = setup_logger(
    enable_console=True, 
    level=logging.DEBUG
)
```

### Mock Operations
```python
class MockInstaller:
    async def install_version(self, version):
        """Mock installer for testing"""
        await asyncio.sleep(0.1)  # Simulate work
        return True
```

## Deployment Considerations

### Distribution
- Package with PyInstaller or similar
- Include all required dependencies
- Test on target platforms

### Configuration
- Use config files for default settings
- Support command-line arguments
- Implement first-run setup

### Updates
- Implement auto-update checking
- Support configuration migration
- Backup user data before updates

## Integration Examples

### With Other Launchers
```python
def import_vanilla_profiles(self):
    """Import from vanilla launcher"""
    vanilla_path = self.get_vanilla_launcher_path()
    profiles = self.parse_vanilla_profiles(vanilla_path)
    return self.convert_profiles(profiles)
```

### External Tools
```python
def integrate_with_curseforge(self):
    """Integrate with CurseForge API"""
    api = CurseForgeAPI()
    modpacks = api.get_popular_modpacks()
    return self.create_templates_from_modpacks(modpacks)
```

### Cloud Sync
```python
class CloudSync:
    async def sync_profiles(self):
        """Sync profiles with cloud storage"""
        local_profiles = self.get_local_profiles()
        cloud_profiles = await self.get_cloud_profiles()
        return self.merge_profiles(local_profiles, cloud_profiles)
```

## Future Enhancements

### Planned Features
- Web-based interface option
- Plugin architecture
- Cloud profile synchronization
- Advanced mod management
- Automated modpack creation

### Community Integration
- Profile sharing platform
- Community templates
- Mod recommendation system
- Collaborative features

## Troubleshooting

### Common GUI Issues
- **Window not appearing**: Check display settings
- **Async operations freezing**: Verify thread safety
- **Memory leaks**: Proper cleanup in event handlers

### Profile Management Issues
- **Import failures**: Check file formats and permissions
- **Corruption**: Implement backup and recovery
- **Performance**: Optimize large instance collections

### Platform-Specific
- **Windows**: Handle long path names
- **macOS**: Code signing for distribution
- **Linux**: Desktop integration files

## Best Practices

### Code Organization
- Separate GUI from business logic
- Use dependency injection
- Implement proper abstractions

### User Experience
- Provide clear feedback
- Implement undo functionality
- Save state automatically

### Security
- Validate all user inputs
- Secure credential storage
- Implement safe file operations

## Contributing

### Adding Features
1. Follow existing code patterns
2. Add comprehensive error handling
3. Include documentation and examples
4. Test on multiple platforms

### Code Style
- Use type hints consistently
- Follow async/await best practices
- Implement proper logging
- Add docstrings for public APIs