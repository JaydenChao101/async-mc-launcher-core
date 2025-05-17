'''
This module is responsible for loading the configuration file for the application.
It handles the loading of the configuration file, including default values and environment variables.
'''
# This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
# SPDX-FileCopyrightText: Copyright (c) 2019-2025 JaydenChao101 <jaydenchao@proton.me> and contributors
# SPDX-License-Identifier: BSD-2-Clause
import os
from os import environ
import aiofiles

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # 降級到 tomli


async def load_config(config_path: str | os.PathLike) -> dict:
    """加载TOML配置，支持环境变量和默认值"""
    read_mode = "rb" if tomllib.__name__ == "tomli" else "r"
    async with aiofiles.open(config_path, mode=read_mode) as f:
        config = tomllib.loads(await f.read())

    def resolve_value(value):
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            var_expr = value[1:-1]
            # 处理带默认值的表达式 {VAR:-default}
            if ":-" in var_expr:
                var_name, default = var_expr.split(":-", 1)
                return environ.get(var_name, default)
            return environ.get(var_expr, value)  # 保持原样如果变量不存在
        return value

    def apply_env_vars(config: dict) -> dict:
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = apply_env_vars(value)
            else:
                config[key] = resolve_value(value)
        return config
    
    return apply_env_vars(config)
