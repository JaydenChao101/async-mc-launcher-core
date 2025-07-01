async def load_vanilla_launcher_profiles(
    minecraft_directory: Union[str, os.PathLike],
) -> list[VanillaLauncherProfile]:
    """
    Loads profiles from the Vanilla Launcher in the given Minecraft directory.

    Args:
        minecraft_directory: Path to the Minecraft directory

    Returns:
        List of vanilla launcher profiles

    Raises:
        FileNotFoundError: If launcher_profiles.json doesn't exist
        json.JSONDecodeError: If the profiles file contains invalid JSON
    """
    # 調用 pre_profile_load 掛鉤點
    from .plugins.hooks import pre_profile_load
    pre_load_options = await pre_profile_load(minecraft_directory)

    # 檢查掛鉤點返回值，決定是否繼續
    if not pre_load_options.get("allow_load", True):
        return []

    file_handler = ProfileFileHandler(minecraft_directory)
    data = await file_handler.read_profiles()

    profiles = []
    for json_profile in data["profiles"].values():
        profile = ProfileConverter.from_json_profile(json_profile)
        profiles.append(profile)

    # 調用 post_profile_load 掛鉤點，可能修改配置文件列表
    from .plugins.hooks import post_profile_load
    profiles = await post_profile_load(minecraft_directory, profiles)

    # 發布配置文件加載完成事件
    try:
        from .plugins.events_types import ProfilesLoadedEvent
        from . import EVENT_MANAGER
        await EVENT_MANAGER.publish(ProfilesLoadedEvent(minecraft_directory, profiles))
    except (ImportError, AttributeError):
        pass  # 如果事件系統未初始化，忽略

    return profiles
