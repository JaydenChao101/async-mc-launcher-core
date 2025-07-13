# Modding Examples

This directory contains examples for using different mod loaders with async-mc-launcher-core.

## Examples

### 🔧 forge_launcher.py
Complete Forge mod loader integration example.

**Features:**
- Forge version discovery and validation
- Automatic and manual installation support
- Forge-optimized JVM arguments
- Mod management functionality
- Launch with Forge profiles

**Usage:**
```bash
python forge_launcher.py
```

**Key Capabilities:**
- Browse available Forge versions
- Find recommended versions for Minecraft releases
- Install Forge automatically or manually
- Launch with optimized memory settings
- Manage mods folder

### 🧶 fabric_launcher.py
Fabric mod loader integration with performance optimizations.

**Features:**
- Fabric version support checking
- Loader version management
- Lightweight installation process
- Performance-optimized launch settings
- Fabric-specific mod recommendations

**Usage:**
```bash
python fabric_launcher.py
```

**Key Capabilities:**
- Check Minecraft version support
- Browse Fabric loader versions
- Quick installation process
- Optimized for performance
- Mod compatibility guidance

### 🧵 quilt_launcher.py
Quilt mod loader (Fabric fork) with enhanced features.

**Features:**
- Enhanced modding capabilities
- Fabric mod compatibility
- Community-driven features
- Backward compatibility support
- Quilt vs Fabric comparison

**Usage:**
```bash
python quilt_launcher.py
```

**Key Capabilities:**
- Fabric mod compatibility
- Enhanced mod loading
- Community features
- Detailed comparisons
- Migration guidance

## Mod Loader Comparison

| Feature | Forge | Fabric | Quilt |
|---------|--------|--------|-------|
| **Mod Ecosystem** | 🟢 Largest | 🟡 Growing rapidly | 🟡 Fabric-compatible |
| **Performance** | 🟡 Good | 🟢 Excellent | 🟢 Excellent |
| **Update Speed** | 🟡 Moderate | 🟢 Fast | 🟢 Fast |
| **Stability** | 🟢 Very stable | 🟢 Stable | 🟡 Developing |
| **Memory Usage** | 🟡 Higher | 🟢 Lower | 🟢 Lower |
| **Modding API** | 🟢 Comprehensive | 🟡 Lightweight | 🟢 Enhanced |
| **Installation** | 🟡 Complex | 🟢 Simple | 🟢 Simple |
| **Compatibility** | 🔴 Forge-only | 🟡 Fabric/Quilt | 🟢 Fabric+Quilt |

## Installation Requirements

### Common Requirements
- Python 3.10+
- async-mc-launcher-core
- Java installation
- Internet connection for downloads
- Minecraft directory with appropriate permissions

### Java Versions
- **Java 17+**: Recommended for Minecraft 1.17+
- **Java 8+**: Required for older Minecraft versions
- **Java 21**: Recommended for latest versions

### Memory Recommendations
- **Vanilla/Light mods**: 2-3GB
- **Moderate mods**: 3-6GB
- **Heavy modpacks**: 6-12GB
- **Server hosting**: 8-16GB+

## Getting Started

### Quick Start - Fabric
```bash
# Run the Fabric launcher
python fabric_launcher.py

# Select option 2 to get latest version
# Select option 4 to install Fabric
# Select option 6 to launch
```

### Quick Start - Forge
```bash
# Run the Forge launcher  
python forge_launcher.py

# Select option 2 to find recommended version
# Select option 3 to install
# Select option 5 to launch
```

### Quick Start - Quilt
```bash
# Run the Quilt launcher
python quilt_launcher.py

# Select option 2 to get latest version
# Select option 4 to install Quilt
# Select option 6 to launch
```

## Mod Management

### Mods Folder Structure
```
.minecraft/
├── mods/           # Main mods folder
│   ├── mod1.jar
│   ├── mod2.jar
│   └── disabled/   # Disabled mods (optional)
├── config/         # Mod configuration files
├── saves/          # World saves
└── versions/       # Installed versions
```

### Installing Mods

1. **Download mods** from trusted sources:
   - [Modrinth](https://modrinth.com) - Modern, fast
   - [CurseForge](https://curseforge.com) - Largest selection
   - GitHub releases - Direct from developers

2. **Check compatibility**:
   - Minecraft version
   - Mod loader (Forge/Fabric/Quilt)
   - Dependencies (other required mods)

3. **Place in mods folder**:
   ```bash
   cp downloaded_mod.jar ~/.minecraft/mods/
   ```

### Essential Mods by Loader

#### Forge Essentials
- **JEI (Just Enough Items)** - Recipe viewing
- **Optifine** - Graphics and performance
- **Biomes O' Plenty** - World generation
- **Tinkers' Construct** - Tool crafting
- **Applied Energistics 2** - Storage systems

#### Fabric Essentials
- **Fabric API** - Required for most Fabric mods
- **Sodium** - Rendering optimization
- **Lithium** - General optimization
- **Phosphor** - Lighting optimization
- **Mod Menu** - In-game mod configuration

#### Quilt Essentials
- **Quilted Fabric API** - Fabric compatibility
- **Quilt Standard Libraries** - Enhanced APIs
- Most Fabric mods work directly

## Troubleshooting

### Common Issues

**"Mod loader not found"**
- Ensure the mod loader is properly installed
- Check the version name in launcher
- Reinstall if necessary

**"Incompatible mod version"**
- Check mod Minecraft version compatibility
- Update or downgrade mods as needed
- Remove incompatible mods temporarily

**"Out of memory errors"**
- Increase memory allocation in launcher
- Remove unnecessary mods
- Use optimization mods (Sodium, Lithium)

**"Crash on startup"**
- Check crash logs in .minecraft/crash-reports/
- Look for mod conflict indicators
- Try launching with fewer mods

### Debug Mode
Enable debug logging in any launcher:
```python
self.logger = setup_logger(enable_console=True, level=logging.DEBUG)
```

### Log Locations
- **Minecraft logs**: `.minecraft/logs/latest.log`
- **Crash reports**: `.minecraft/crash-reports/`
- **Mod loader logs**: Specific to each loader

## Advanced Configuration

### JVM Arguments by Loader

#### Forge (Heavy)
```bash
-Xmx6G -Xms2G 
-XX:+UnlockExperimentalVMOptions 
-XX:+UseG1GC 
-XX:G1NewSizePercent=20 
-XX:G1ReservePercent=20 
-XX:MaxGCPauseMillis=50 
-XX:G1HeapRegionSize=32M
```

#### Fabric/Quilt (Lightweight)
```bash
-Xmx4G -Xms1G 
-XX:+UnlockExperimentalVMOptions 
-XX:+UseG1GC 
-XX:G1NewSizePercent=20 
-XX:G1ReservePercent=20 
-XX:MaxGCPauseMillis=50 
-XX:G1HeapRegionSize=16M
```

### Custom Launch Options
```python
options = {
    "gameDirectory": minecraft_dir,
    "jvmArguments": custom_jvm_args,
    "nativesDirectory": natives_dir,
    "customResolution": True,
    "resolutionWidth": 1920,
    "resolutionHeight": 1080,
}
```

## Performance Optimization

### Mod Selection Tips
- Choose mods that complement each other
- Avoid duplicate functionality
- Use performance optimization mods
- Regular cleanup of unused mods

### Memory Optimization
- Start with reasonable allocation
- Monitor actual usage with profilers
- Increase gradually if needed
- Consider SSD for better loading

### Graphics Settings
- Use Sodium/Optifine for FPS
- Configure render distance appropriately
- Disable unnecessary visual effects
- Use performance-focused resource packs

## Modpack Development

### Creating Modpacks
1. Choose a base mod loader
2. Select compatible mods
3. Test thoroughly
4. Document requirements
5. Provide installation instructions

### Distribution Methods
- Export instance from launcher
- Use modpack platforms (CurseForge, Modrinth)
- Create custom installers
- Provide manual installation guides

## Community Resources

### Mod Loader Communities
- **Forge**: [MinecraftForge Discord](https://discord.minecraftforge.net/)
- **Fabric**: [Fabric Discord](https://discord.gg/v6v4pMv)
- **Quilt**: [Quilt Community Discord](https://discord.quiltmc.org/)

### Development Resources
- [Fabric Documentation](https://fabricmc.net/wiki/)
- [Forge Documentation](https://docs.minecraftforge.net/)
- [Quilt Documentation](https://quiltmc.org/wiki/)

### Mod Discovery
- [Modrinth](https://modrinth.com) - Modern platform
- [CurseForge](https://curseforge.com) - Established platform
- [GitHub](https://github.com) - Direct from developers
- Community recommendations and lists

## Next Steps

After mastering modded Minecraft:

1. **Try Advanced Examples** - Custom GUIs and profile management
2. **Create Modpacks** - Curate your own mod collections
3. **Mod Development** - Learn to create your own mods
4. **Server Administration** - Host modded servers

## Migration Between Loaders

### Fabric to Quilt
- Most Fabric mods work directly
- Install Quilted Fabric API
- Test thoroughly
- Some performance may vary

### Forge to Fabric/Quilt
- Complete recreation needed
- Find equivalent mods
- World compatibility varies
- Backup everything first

### Version Updates
- Update mod loader first
- Update core mods (APIs)
- Update other mods gradually
- Test stability frequently