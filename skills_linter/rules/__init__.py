"""规则模块"""

from pathlib import Path
from typing import List, Type
import importlib
import inspect

from .base import Rule


def discover_rules() -> List[Type[Rule]]:
    """自动发现 rules/ 目录下的所有规则类"""
    rules_dir = Path(__file__).parent
    rule_classes = []

    # 遍历 rules/ 目录下的所有 .py 文件
    for py_file in rules_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue

        # 导入模块
        module_name = f"skills_linter.rules.{py_file.stem}"
        try:
            module = importlib.import_module(module_name)

            # 查找继承自 Rule 的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Rule) and obj is not Rule:
                    rule_classes.append(obj)
        except Exception:
            continue

    return rule_classes
