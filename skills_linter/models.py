"""核心数据模型"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any


@dataclass
class Skill:
    """表示一个 Skill 的完整信息"""
    path: Path                    # Skill 目录路径
    name: str                     # 目录名
    frontmatter: Dict[str, Any]   # YAML frontmatter 内容
    markdown_body: str            # Markdown 正文
    skill_md_path: Path           # SKILL.md 文件路径


@dataclass
class Issue:
    """表示一个检查问题"""
    rule_id: str                  # 规则 ID（如 "required-fields")
    level: str                    # ERROR / WARNING / INFO
    message: str                  # 错误消息
    file_path: str                # 文件路径（相对于仓库根目录）
    line: Optional[int] = None    # 行号（如果适用）


@dataclass
class CheckResult:
    """表示一个 Skill 的检查结果"""
    skill_name: str               # Skill 名称
    skill_path: str               # Skill 路径
    passed: bool                  # 是否通过（无 ERROR）
    issues: List[Issue] = field(default_factory=list)  # 问题列表
