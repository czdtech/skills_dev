"""YAML frontmatter 和 Markdown 解析器"""

from pathlib import Path
from typing import Optional
import re
import yaml

from .models import Skill


class ParseError(Exception):
    """解析错误"""
    pass


def parse_skill_md(skill_dir: Path) -> Skill:
    """
    解析 Skill 目录中的 SKILL.md 文件

    Args:
        skill_dir: Skill 目录路径

    Returns:
        Skill 对象

    Raises:
        ParseError: 解析失败时抛出
    """
    skill_md_path = skill_dir / "SKILL.md"

    # 检查文件是否存在
    if not skill_md_path.exists():
        raise ParseError(f"SKILL.md not found in {skill_dir}")

    # 读取文件内容
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as e:
        raise ParseError(f"Failed to read {skill_md_path}: {e}")

    # 解析 YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)

    if not frontmatter_match:
        raise ParseError(f"No valid YAML frontmatter found in {skill_md_path}")

    frontmatter_text = frontmatter_match.group(1)
    markdown_body = frontmatter_match.group(2)

    # 解析 YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML syntax in {skill_md_path}: {e}")

    # 创建 Skill 对象
    return Skill(
        path=skill_dir,
        name=skill_dir.name,
        frontmatter=frontmatter,
        markdown_body=markdown_body,
        skill_md_path=skill_md_path
    )
