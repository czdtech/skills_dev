"""检查 name 字段格式"""

import re
from typing import List
from ..models import Skill, Issue
from .base import Rule


class NameFormatRule(Rule):
    """检查 name 字段是否符合 hyphen-case 格式"""

    @property
    def rule_id(self) -> str:
        return "name-format"

    @property
    def level(self) -> str:
        return "ERROR"

    def check(self, skill: Skill) -> List[Issue]:
        issues = []

        name = skill.frontmatter.get("name")
        if not name:
            return issues  # required-fields 规则会处理

        # 检查是否符合 hyphen-case 格式
        # 仅允许小写字母、数字和连字符
        # 不能以连字符开头或结尾
        # 不能有连续连字符
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            issues.append(Issue(
                rule_id=self.rule_id,
                level=self.level,
                message=f"Invalid name format: '{name}'. Must be hyphen-case (lowercase letters, numbers, and hyphens only)",
                file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
            ))

        return issues
