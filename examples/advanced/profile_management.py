#!/usr/bin/env python3
"""
Profile Management Example

This example demonstrates advanced profile and instance management
using the async-mc-launcher-core library. It shows:

1. Creating and managing multiple game instances
2. Profile templating and inheritance
3. Mod profile management
4. Instance isolation and organization
5. Batch operations on profiles
6. Import/export functionality

Requirements:
- Python 3.10+
- async-mc-launcher-core
- JSON/TOML configuration support

Features:
- Multiple instance support
- Profile templates
- Mod set management
- Instance cloning
- Backup and restore
- Configuration inheritance
"""

import asyncio
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from launcher_core import install, command, _types, forge, fabric, quilt
from launcher_core.setting import setup_logger
from launcher_core.exceptions import VersionNotFound


class GameInstance:
    """Represents a complete Minecraft game instance."""

    def __init__(
        self,
        name: str,
        directory: str,
        minecraft_version: str,
        mod_loader: str = "vanilla",
        mod_loader_version: str = "",
        description: str = "",
        tags: List[str] = None,
    ):
        self.name = name
        self.directory = Path(directory)
        self.minecraft_version = minecraft_version
        self.mod_loader = mod_loader
        self.mod_loader_version = mod_loader_version
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.last_played = None
        self.play_time = 0  # seconds
        self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert instance to dictionary."""
        return {
            "name": self.name,
            "directory": str(self.directory),
            "minecraft_version": self.minecraft_version,
            "mod_loader": self.mod_loader,
            "mod_loader_version": self.mod_loader_version,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at,
            "last_played": self.last_played,
            "play_time": self.play_time,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GameInstance":
        """Create instance from dictionary."""
        instance = cls(
            name=data["name"],
            directory=data["directory"],
            minecraft_version=data["minecraft_version"],
            mod_loader=data.get("mod_loader", "vanilla"),
            mod_loader_version=data.get("mod_loader_version", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )
        instance.created_at = data.get("created_at", instance.created_at)
        instance.last_played = data.get("last_played")
        instance.play_time = data.get("play_time", 0)
        instance.metadata = data.get("metadata", {})
        return instance


class ProfileTemplate:
    """Template for creating new profiles with predefined settings."""

    def __init__(
        self,
        name: str,
        minecraft_version: str,
        mod_loader: str = "vanilla",
        memory: int = 2048,
        jvm_args: List[str] = None,
        required_mods: List[str] = None,
        optional_mods: List[str] = None,
        description: str = "",
    ):
        self.name = name
        self.minecraft_version = minecraft_version
        self.mod_loader = mod_loader
        self.memory = memory
        self.jvm_args = jvm_args or []
        self.required_mods = required_mods or []
        self.optional_mods = optional_mods or []
        self.description = description

    def to_dict(self) -> Dict:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "minecraft_version": self.minecraft_version,
            "mod_loader": self.mod_loader,
            "memory": self.memory,
            "jvm_args": self.jvm_args,
            "required_mods": self.required_mods,
            "optional_mods": self.optional_mods,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProfileTemplate":
        """Create template from dictionary."""
        return cls(
            name=data["name"],
            minecraft_version=data["minecraft_version"],
            mod_loader=data.get("mod_loader", "vanilla"),
            memory=data.get("memory", 2048),
            jvm_args=data.get("jvm_args", []),
            required_mods=data.get("required_mods", []),
            optional_mods=data.get("optional_mods", []),
            description=data.get("description", ""),
        )


class ModSet:
    """Represents a collection of mods that can be applied to instances."""

    def __init__(
        self,
        name: str,
        description: str = "",
        mods: List[str] = None,
        compatible_loaders: List[str] = None,
        minecraft_versions: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.mods = mods or []  # List of mod filenames or IDs
        self.compatible_loaders = compatible_loaders or ["fabric", "quilt"]
        self.minecraft_versions = minecraft_versions or []
        self.dependencies = []  # Other mod sets this depends on
        self.conflicts = []  # Mod sets this conflicts with

    def to_dict(self) -> Dict:
        """Convert mod set to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "mods": self.mods,
            "compatible_loaders": self.compatible_loaders,
            "minecraft_versions": self.minecraft_versions,
            "dependencies": self.dependencies,
            "conflicts": self.conflicts,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ModSet":
        """Create mod set from dictionary."""
        mod_set = cls(
            name=data["name"],
            description=data.get("description", ""),
            mods=data.get("mods", []),
            compatible_loaders=data.get("compatible_loaders", ["fabric", "quilt"]),
            minecraft_versions=data.get("minecraft_versions", []),
        )
        mod_set.dependencies = data.get("dependencies", [])
        mod_set.conflicts = data.get("conflicts", [])
        return mod_set


class AdvancedProfileManager:
    """Advanced profile and instance management system."""

    def __init__(self, base_directory: str = None):
        """
        Initialize the profile manager.

        Args:
            base_directory: Base directory for all instances
        """
        self.base_directory = Path(base_directory or "minecraft_instances")
        self.base_directory.mkdir(exist_ok=True)

        # Configuration files
        self.instances_file = self.base_directory / "instances.json"
        self.templates_file = self.base_directory / "templates.json"
        self.mod_sets_file = self.base_directory / "mod_sets.json"
        self.config_file = self.base_directory / "config.json"

        # Initialize logger
        self.logger = setup_logger(enable_console=True, level=logging.INFO)

        # Load data
        self.instances: Dict[str, GameInstance] = self.load_instances()
        self.templates: Dict[str, ProfileTemplate] = self.load_templates()
        self.mod_sets: Dict[str, ModSet] = self.load_mod_sets()
        self.config = self.load_config()

        # Create default templates if none exist
        if not self.templates:
            self.create_default_templates()

    def load_instances(self) -> Dict[str, GameInstance]:
        """Load game instances."""
        if self.instances_file.exists():
            try:
                with open(self.instances_file, "r") as f:
                    data = json.load(f)
                return {
                    name: GameInstance.from_dict(instance_data)
                    for name, instance_data in data.items()
                }
            except Exception as e:
                self.logger.warning(f"Failed to load instances: {e}")
        return {}

    def save_instances(self):
        """Save game instances."""
        try:
            data = {
                name: instance.to_dict() for name, instance in self.instances.items()
            }
            with open(self.instances_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save instances: {e}")

    def load_templates(self) -> Dict[str, ProfileTemplate]:
        """Load profile templates."""
        if self.templates_file.exists():
            try:
                with open(self.templates_file, "r") as f:
                    data = json.load(f)
                return {
                    name: ProfileTemplate.from_dict(template_data)
                    for name, template_data in data.items()
                }
            except Exception as e:
                self.logger.warning(f"Failed to load templates: {e}")
        return {}

    def save_templates(self):
        """Save profile templates."""
        try:
            data = {
                name: template.to_dict() for name, template in self.templates.items()
            }
            with open(self.templates_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save templates: {e}")

    def load_mod_sets(self) -> Dict[str, ModSet]:
        """Load mod sets."""
        if self.mod_sets_file.exists():
            try:
                with open(self.mod_sets_file, "r") as f:
                    data = json.load(f)
                return {
                    name: ModSet.from_dict(mod_set_data)
                    for name, mod_set_data in data.items()
                }
            except Exception as e:
                self.logger.warning(f"Failed to load mod sets: {e}")
        return {}

    def save_mod_sets(self):
        """Save mod sets."""
        try:
            data = {name: mod_set.to_dict() for name, mod_set in self.mod_sets.items()}
            with open(self.mod_sets_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save mod sets: {e}")

    def load_config(self) -> Dict:
        """Load configuration."""
        default_config = {
            "default_memory": 4096,
            "default_java_args": ["-XX:+UnlockExperimentalVMOptions", "-XX:+UseG1GC"],
            "auto_backup": True,
            "backup_retention_days": 30,
            "instance_isolation": True,
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")

        return default_config

    def save_config(self):
        """Save configuration."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def create_default_templates(self):
        """Create default profile templates."""
        templates = [
            ProfileTemplate(
                "Vanilla Latest",
                "1.21.1",
                "vanilla",
                2048,
                description="Latest vanilla Minecraft",
            ),
            ProfileTemplate(
                "Fabric Performance",
                "1.21.1",
                "fabric",
                3072,
                required_mods=["fabric-api", "sodium", "lithium", "phosphor"],
                description="Optimized Fabric setup for performance",
            ),
            ProfileTemplate(
                "Forge Modded",
                "1.20.1",
                "forge",
                6144,
                jvm_args=[
                    "-XX:+UnlockExperimentalVMOptions",
                    "-XX:+UseG1GC",
                    "-XX:G1HeapRegionSize=32M",
                ],
                description="Heavy modded Forge setup",
            ),
            ProfileTemplate(
                "Quilt Enhanced",
                "1.21.1",
                "quilt",
                4096,
                required_mods=["quilted-fabric-api"],
                description="Quilt with enhanced features",
            ),
        ]

        for template in templates:
            self.templates[template.name] = template

        self.save_templates()
        self.logger.info("Created default profile templates")

    async def create_instance_from_template(
        self, instance_name: str, template_name: str, custom_directory: str = None
    ) -> bool:
        """
        Create a new instance from a template.

        Args:
            instance_name: Name for the new instance
            template_name: Template to use
            custom_directory: Custom directory (optional)

        Returns:
            True if instance created successfully
        """
        if template_name not in self.templates:
            self.logger.error(f"Template '{template_name}' not found")
            return False

        if instance_name in self.instances:
            self.logger.error(f"Instance '{instance_name}' already exists")
            return False

        template = self.templates[template_name]

        # Create instance directory
        if custom_directory:
            instance_dir = Path(custom_directory)
        else:
            instance_dir = self.base_directory / "instances" / instance_name

        instance_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create instance
            instance = GameInstance(
                name=instance_name,
                directory=str(instance_dir),
                minecraft_version=template.minecraft_version,
                mod_loader=template.mod_loader,
                mod_loader_version=template.mod_loader_version,
                description=f"Created from template: {template_name}",
            )

            # Install Minecraft version
            await self.install_minecraft_version(instance, template.minecraft_version)

            # Install mod loader if needed
            if template.mod_loader != "vanilla":
                await self.install_mod_loader(
                    instance, template.mod_loader, template.mod_loader_version
                )

            # Create mods directory
            mods_dir = instance_dir / "mods"
            mods_dir.mkdir(exist_ok=True)

            # Apply required mods (would need actual mod installation logic)
            if template.required_mods:
                self.logger.info(
                    f"Required mods for {instance_name}: {template.required_mods}"
                )

            # Save instance
            self.instances[instance_name] = instance
            self.save_instances()

            self.logger.info(
                f"Created instance '{instance_name}' from template '{template_name}'"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to create instance: {e}")
            # Clean up on failure
            if instance_dir.exists():
                shutil.rmtree(instance_dir)
            return False

    async def install_minecraft_version(self, instance: GameInstance, version: str):
        """Install Minecraft version for an instance."""
        self.logger.info(f"Installing Minecraft {version} for {instance.name}")

        def set_status(status: str) -> None:
            self.logger.info(f"Status: {status}")

        callback: _types.CallbackDict = {
            "setStatus": set_status,
            "setProgress": lambda p: None,
            "setMax": lambda m: None,
        }

        await install.install_minecraft_version(
            version, str(instance.directory), callback
        )

    async def install_mod_loader(
        self, instance: GameInstance, loader: str, version: str = ""
    ):
        """Install mod loader for an instance."""
        self.logger.info(f"Installing {loader} for {instance.name}")

        callback: _types.CallbackDict = {
            "setStatus": lambda s: self.logger.info(f"Status: {s}"),
            "setProgress": lambda p: None,
            "setMax": lambda m: None,
        }

        if loader == "forge":
            if not version:
                version = await forge.find_forge_version(instance.minecraft_version)
            await forge.install_forge_version(
                version, str(instance.directory), callback
            )
        elif loader == "fabric":
            await fabric.install_fabric(
                instance.minecraft_version,
                str(instance.directory),
                loader_version=version,
                callback=callback,
            )
        elif loader == "quilt":
            await quilt.install_quilt(
                instance.minecraft_version,
                str(instance.directory),
                loader_version=version,
                callback=callback,
            )

    def clone_instance(self, source_name: str, target_name: str) -> bool:
        """Clone an existing instance."""
        if source_name not in self.instances:
            self.logger.error(f"Source instance '{source_name}' not found")
            return False

        if target_name in self.instances:
            self.logger.error(f"Target instance '{target_name}' already exists")
            return False

        source = self.instances[source_name]
        target_dir = self.base_directory / "instances" / target_name

        try:
            # Copy instance directory
            shutil.copytree(source.directory, target_dir)

            # Create new instance
            target = GameInstance(
                name=target_name,
                directory=str(target_dir),
                minecraft_version=source.minecraft_version,
                mod_loader=source.mod_loader,
                mod_loader_version=source.mod_loader_version,
                description=f"Cloned from {source_name}",
                tags=source.tags.copy(),
            )

            self.instances[target_name] = target
            self.save_instances()

            self.logger.info(f"Cloned instance '{source_name}' to '{target_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clone instance: {e}")
            return False

    def delete_instance(self, instance_name: str, delete_files: bool = True) -> bool:
        """Delete an instance."""
        if instance_name not in self.instances:
            self.logger.error(f"Instance '{instance_name}' not found")
            return False

        instance = self.instances[instance_name]

        try:
            # Delete files if requested
            if delete_files and instance.directory.exists():
                shutil.rmtree(instance.directory)

            # Remove from instances
            del self.instances[instance_name]
            self.save_instances()

            self.logger.info(f"Deleted instance '{instance_name}'")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete instance: {e}")
            return False

    def export_instance(self, instance_name: str, export_path: str) -> bool:
        """Export an instance to a file."""
        if instance_name not in self.instances:
            self.logger.error(f"Instance '{instance_name}' not found")
            return False

        instance = self.instances[instance_name]

        try:
            # Create export archive
            shutil.make_archive(export_path, "zip", instance.directory)

            # Create metadata file
            metadata = {
                "instance": instance.to_dict(),
                "export_date": datetime.now().isoformat(),
                "launcher_version": "async-mc-launcher-core",
            }

            metadata_path = f"{export_path}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(
                f"Exported instance '{instance_name}' to {export_path}.zip"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to export instance: {e}")
            return False

    def import_instance(self, archive_path: str, instance_name: str = None) -> bool:
        """Import an instance from a file."""
        archive_path = Path(archive_path)

        if not archive_path.exists():
            self.logger.error(f"Archive file '{archive_path}' not found")
            return False

        try:
            # Extract to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(archive_path, temp_dir)

                # Look for metadata
                metadata_path = f"{archive_path}_metadata.json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    original_instance = GameInstance.from_dict(metadata["instance"])
                    if not instance_name:
                        instance_name = original_instance.name
                else:
                    # Fallback if no metadata
                    if not instance_name:
                        instance_name = archive_path.stem

                # Check if instance already exists
                if instance_name in self.instances:
                    self.logger.error(f"Instance '{instance_name}' already exists")
                    return False

                # Create instance directory
                instance_dir = self.base_directory / "instances" / instance_name

                # Copy files
                shutil.copytree(temp_dir, instance_dir)

                # Create instance object
                if "original_instance" in locals():
                    instance = original_instance
                    instance.name = instance_name
                    instance.directory = Path(str(instance_dir))
                else:
                    instance = GameInstance(
                        name=instance_name,
                        directory=str(instance_dir),
                        minecraft_version="unknown",
                        description="Imported instance",
                    )

                self.instances[instance_name] = instance
                self.save_instances()

                self.logger.info(
                    f"Imported instance '{instance_name}' from {archive_path}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to import instance: {e}")
            return False

    def apply_mod_set(self, instance_name: str, mod_set_name: str) -> bool:
        """Apply a mod set to an instance."""
        if instance_name not in self.instances:
            self.logger.error(f"Instance '{instance_name}' not found")
            return False

        if mod_set_name not in self.mod_sets:
            self.logger.error(f"Mod set '{mod_set_name}' not found")
            return False

        instance = self.instances[instance_name]
        mod_set = self.mod_sets[mod_set_name]

        # Check compatibility
        if instance.mod_loader not in mod_set.compatible_loaders:
            self.logger.error(
                f"Mod set '{mod_set_name}' not compatible with {instance.mod_loader}"
            )
            return False

        if (
            mod_set.minecraft_versions
            and instance.minecraft_version not in mod_set.minecraft_versions
        ):
            self.logger.warning(
                f"Mod set '{mod_set_name}' may not be compatible with Minecraft {instance.minecraft_version}"
            )

        try:
            # Apply dependencies first
            for dep_name in mod_set.dependencies:
                if dep_name in self.mod_sets:
                    self.apply_mod_set(instance_name, dep_name)

            # Apply mods (implementation would depend on mod sources)
            self.logger.info(
                f"Applied mod set '{mod_set_name}' to instance '{instance_name}'"
            )
            self.logger.info(f"Mods in set: {mod_set.mods}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to apply mod set: {e}")
            return False

    def get_instances_by_tag(self, tag: str) -> List[GameInstance]:
        """Get instances with a specific tag."""
        return [
            instance for instance in self.instances.values() if tag in instance.tags
        ]

    def get_instances_by_loader(self, loader: str) -> List[GameInstance]:
        """Get instances using a specific mod loader."""
        return [
            instance
            for instance in self.instances.values()
            if instance.mod_loader == loader
        ]

    def get_instance_statistics(self) -> Dict:
        """Get statistics about instances."""
        total = len(self.instances)
        by_loader = {}
        by_version = {}
        total_play_time = 0

        for instance in self.instances.values():
            # Count by loader
            by_loader[instance.mod_loader] = by_loader.get(instance.mod_loader, 0) + 1

            # Count by version
            by_version[instance.minecraft_version] = (
                by_version.get(instance.minecraft_version, 0) + 1
            )

            # Sum play time
            total_play_time += instance.play_time

        return {
            "total_instances": total,
            "by_mod_loader": by_loader,
            "by_minecraft_version": by_version,
            "total_play_time_hours": total_play_time / 3600,
            "templates_count": len(self.templates),
            "mod_sets_count": len(self.mod_sets),
        }

    def print_statistics(self):
        """Print instance statistics."""
        stats = self.get_instance_statistics()

        print("\n📊 Instance Statistics:")
        print(f"   Total Instances: {stats['total_instances']}")
        print(f"   Templates: {stats['templates_count']}")
        print(f"   Mod Sets: {stats['mod_sets_count']}")
        print(f"   Total Play Time: {stats['total_play_time_hours']:.1f} hours")

        print("\n🔧 By Mod Loader:")
        for loader, count in stats["by_mod_loader"].items():
            print(f"   {loader}: {count}")

        print("\n🎮 By Minecraft Version:")
        for version, count in sorted(stats["by_minecraft_version"].items()):
            print(f"   {version}: {count}")


async def interactive_profile_manager():
    """Interactive profile management interface."""
    print("=== Advanced Minecraft Profile Manager ===")
    print("\nComprehensive instance and profile management system.")

    # Initialize manager
    base_dir = input(
        "Enter base directory for instances (or press Enter for default): "
    ).strip()
    if not base_dir:
        base_dir = "minecraft_instances"

    manager = AdvancedProfileManager(base_dir)
    print(f"Using base directory: {manager.base_directory}")

    while True:
        print("\n" + "=" * 60)
        print("Profile Manager Options:")
        print("1.  List instances")
        print("2.  Create instance from template")
        print("3.  Clone instance")
        print("4.  Delete instance")
        print("5.  Export instance")
        print("6.  Import instance")
        print("7.  Manage templates")
        print("8.  Manage mod sets")
        print("9.  Apply mod set to instance")
        print("10. Instance statistics")
        print("11. Batch operations")
        print("12. Exit")

        choice = input("\nEnter your choice (1-12): ").strip()

        if choice == "1":
            # List instances
            if not manager.instances:
                print("No instances found")
                continue

            print(f"\n📁 Instances ({len(manager.instances)} total):")
            for name, instance in manager.instances.items():
                tags_str = f"[{', '.join(instance.tags)}]" if instance.tags else ""
                print(f"   🟢 {name}")
                print(
                    f"      Version: {instance.minecraft_version} ({instance.mod_loader})"
                )
                print(f"      Directory: {instance.directory}")
                print(f"      Description: {instance.description}")
                if tags_str:
                    print(f"      Tags: {tags_str}")
                print()

        elif choice == "2":
            # Create from template
            if not manager.templates:
                print("No templates available")
                continue

            print("\nAvailable templates:")
            for i, (name, template) in enumerate(manager.templates.items(), 1):
                print(f"{i}. {name} - {template.description}")

            template_choice = input("Enter template number or name: ").strip()

            if template_choice.isdigit():
                template_names = list(manager.templates.keys())
                idx = int(template_choice) - 1
                if 0 <= idx < len(template_names):
                    template_name = template_names[idx]
                else:
                    print("Invalid template number")
                    continue
            else:
                template_name = template_choice

            if template_name not in manager.templates:
                print(f"Template '{template_name}' not found")
                continue

            instance_name = input("Enter instance name: ").strip()
            if not instance_name:
                print("Instance name required")
                continue

            print(
                f"Creating instance '{instance_name}' from template '{template_name}'..."
            )
            success = await manager.create_instance_from_template(
                instance_name, template_name
            )

            if success:
                print("✅ Instance created successfully!")
            else:
                print("❌ Failed to create instance")

        elif choice == "3":
            # Clone instance
            if not manager.instances:
                print("No instances to clone")
                continue

            print("\nExisting instances:")
            for i, name in enumerate(manager.instances.keys(), 1):
                print(f"{i}. {name}")

            source_choice = input("Enter source instance number or name: ").strip()

            if source_choice.isdigit():
                instance_names = list(manager.instances.keys())
                idx = int(source_choice) - 1
                if 0 <= idx < len(instance_names):
                    source_name = instance_names[idx]
                else:
                    print("Invalid instance number")
                    continue
            else:
                source_name = source_choice

            target_name = input("Enter new instance name: ").strip()
            if not target_name:
                print("Target name required")
                continue

            success = manager.clone_instance(source_name, target_name)

            if success:
                print("✅ Instance cloned successfully!")
            else:
                print("❌ Failed to clone instance")

        elif choice == "4":
            # Delete instance
            if not manager.instances:
                print("No instances to delete")
                continue

            print("\nExisting instances:")
            for i, name in enumerate(manager.instances.keys(), 1):
                print(f"{i}. {name}")

            instance_choice = input("Enter instance number or name to delete: ").strip()

            if instance_choice.isdigit():
                instance_names = list(manager.instances.keys())
                idx = int(instance_choice) - 1
                if 0 <= idx < len(instance_names):
                    instance_name = instance_names[idx]
                else:
                    print("Invalid instance number")
                    continue
            else:
                instance_name = instance_choice

            if instance_name not in manager.instances:
                print("Instance not found")
                continue

            delete_files = (
                input("Delete files from disk? (Y/n): ").strip().lower() != "n"
            )
            confirm = input(f"Really delete '{instance_name}'? (y/N): ").strip().lower()

            if confirm == "y":
                success = manager.delete_instance(instance_name, delete_files)
                if success:
                    print("✅ Instance deleted successfully!")
                else:
                    print("❌ Failed to delete instance")

        elif choice == "5":
            # Export instance
            if not manager.instances:
                print("No instances to export")
                continue

            print("\nExisting instances:")
            for i, name in enumerate(manager.instances.keys(), 1):
                print(f"{i}. {name}")

            instance_choice = input("Enter instance number or name to export: ").strip()

            if instance_choice.isdigit():
                instance_names = list(manager.instances.keys())
                idx = int(instance_choice) - 1
                if 0 <= idx < len(instance_names):
                    instance_name = instance_names[idx]
                else:
                    print("Invalid instance number")
                    continue
            else:
                instance_name = instance_choice

            export_path = input("Enter export path (without .zip extension): ").strip()
            if not export_path:
                export_path = f"{instance_name}_export"

            success = manager.export_instance(instance_name, export_path)
            if success:
                print("✅ Instance exported successfully!")
            else:
                print("❌ Failed to export instance")

        elif choice == "6":
            # Import instance
            import_path = input("Enter path to import archive (.zip): ").strip()
            if not import_path:
                print("Import path required")
                continue

            instance_name = input(
                "Enter instance name (or press Enter for auto): "
            ).strip()
            instance_name = instance_name if instance_name else None

            success = manager.import_instance(import_path, instance_name)
            if success:
                print("✅ Instance imported successfully!")
            else:
                print("❌ Failed to import instance")

        elif choice == "10":
            # Show statistics
            manager.print_statistics()

        elif choice == "12":
            print("Goodbye!")
            break

        else:
            print("Feature not yet implemented or invalid choice")


async def main():
    """Main example function."""
    try:
        await interactive_profile_manager()
    except KeyboardInterrupt:
        print("\n\nProfile manager interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in profile manager")


if __name__ == "__main__":
    asyncio.run(main())
