"""
Convert TypedDict definitions to Pydantic models
手動轉換 TypedDict 定義為 Pydantic 模型
"""
from pathlib import Path
import ast
import re
from typing import get_type_hints

def convert_typeddict_to_pydantic():
    """
    將 _types.py 中的 TypedDict 轉換為 Pydantic 模型
    """

    # 讀取原始類型文件
    types_file = Path("launcher_core/_types.py")
    if not types_file.exists():
        print(f"錯誤: 找不到文件 {types_file}")
        return

    with open(types_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析 AST
    tree = ast.parse(content)

    # 提取 TypedDict 類定義
    typed_dict_classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.ClassDef):
            # 檢查是否是 TypedDict
            for base in node.bases:
                if (isinstance(base, ast.Name) and base.id == "TypedDict") or \
                   (isinstance(base, ast.Attribute) and base.attr == "TypedDict"):
                    typed_dict_classes.append(node)
                    break

    # 生成 Pydantic 模型代碼
    pydantic_code = generate_pydantic_code(typed_dict_classes, imports)

    # 寫入文件
    output_file = Path("launcher_core/pydantic_models.py")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pydantic_code)

    print(f"✅ 成功生成 Pydantic 模型文件: {output_file}")

def generate_pydantic_code(typed_dict_classes, imports):
    """
    生成 Pydantic 模型代碼
    """

    # 頭部註釋和導入
    header = '''"""
Pydantic Models converted from TypedDict definitions
從 TypedDict 定義轉換而來的 Pydantic 模型

This file is part of async-mc-launcher-core (https://github.com/JaydenChao101/async-mc-launcher-core)
SPDX-FileCopyrightText: Copyright (c) 2025 JaydenChao101 <jaydenchao@proton.me> and contributors
SPDX-License-Identifier: BSD-2-Clause
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, Callable, Union, NewType
import datetime
from uuid import UUID

# 重新定義 MinecraftUUID
MinecraftUUID = NewType("MinecraftUUID", UUID)

'''

    # 轉換每個 TypedDict 類
    model_definitions = []

    for class_node in typed_dict_classes:
        model_code = convert_class_to_pydantic(class_node)
        model_definitions.append(model_code)

    return header + '\n\n'.join(model_definitions)

def convert_class_to_pydantic(class_node):
    """
    將單個 TypedDict 類轉換為 Pydantic 模型
    """
    class_name = class_node.name
    docstring = ast.get_docstring(class_node) or f"Pydantic model for {class_name}"

    # 檢查是否有 total=False
    total_false = False
    for keyword in getattr(class_node, 'keywords', []):
        if keyword.arg == 'total' and isinstance(keyword.value, ast.Constant) and keyword.value.value is False:
            total_false = True
            break

    # 提取字段定義
    fields = []
    for node in class_node.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            field_name = node.target.id
            field_type = ast.unparse(node.annotation)

            # 處理默認值
            default_value = None
            if node.value:
                if isinstance(node.value, ast.Constant):
                    default_value = repr(node.value.value)
                else:
                    default_value = ast.unparse(node.value)

            # 如果是 total=False，所有字段都變為 Optional
            if total_false and not field_type.startswith('Optional'):
                # 檢查是否已經是 Union 類型包含 None
                if '| None' in field_type or 'Union[' in field_type:
                    # 已經是可選類型
                    pass
                else:
                    field_type = f"Optional[{field_type}]"
                    if default_value is None:
                        default_value = "None"

            # 生成字段定義
            if default_value:
                field_def = f"    {field_name}: {field_type} = {default_value}"
            else:
                field_def = f"    {field_name}: {field_type}"

            fields.append(field_def)

    # 生成類定義
    class_code = f'''class {class_name}(BaseModel):
    """{docstring}"""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

{chr(10).join(fields) if fields else "    pass"}'''

    return class_code

if __name__ == "__main__":
    convert_typeddict_to_pydantic()
