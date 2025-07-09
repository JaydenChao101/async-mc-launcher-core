"""
This module handles loading and saving TOML config files with environment variable support.
"""

# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2019-2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
import os
from os import environ
import tomllib
from tomli_w import dumps  # 需要安裝 tomli-w (pip install tomli-w)
import aiofiles


async def load_config(config_path: str | os.PathLike) -> dict:
    """加載 TOML 配置，支持環境變量 {VAR} 和默認值 {VAR:-default}"""
    async with aiofiles.open(config_path, mode="r") as f:
        config = tomllib.loads(await f.read())

    def resolve_value(value):
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            var_expr = value[1:-1]
            if ":-" in var_expr:  # 處理默認值 {VAR:-default}
                var_name, default = var_expr.split(":-", 1)
                return environ.get(var_name, default)
            return environ.get(var_expr, value)  # 無默認值時保持原樣
        return value

    def apply_env_vars(config: dict) -> dict:
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = apply_env_vars(value)
            else:
                config[key] = resolve_value(value)
        return config

    return apply_env_vars(config)


async def save_config(config_path: str | os.PathLike, config: dict) -> None:
    """保存 TOML 配置（自動處理環境變量格式）"""

    def restore_env_vars(value):
        """如果是從環境變量加載的值，恢復為 {VAR} 格式"""
        if isinstance(value, str):
            # 檢查是否來自環境變量（簡單實現，可根據需求改進）
            for var_name, var_value in environ.items():
                if value == var_value:
                    return f"{{{var_name}}}"
        return value

    def process_before_save(config: dict) -> dict:
        """遞歸處理字典，準備寫入"""
        new_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                new_config[key] = process_before_save(value)
            else:
                new_config[key] = restore_env_vars(value)
        return new_config

    # 處理配置後寫入
    toml_str = dumps(process_before_save(config))
    async with aiofiles.open(config_path, mode="w") as f:
        await f.write(toml_str)
