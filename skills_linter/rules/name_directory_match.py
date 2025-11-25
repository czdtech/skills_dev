"""检查 name 字段与目录名是否匹配"""

from typing import List
from ..models import Skill, Issue
from .base import Rule


class NameDirectoryMatchRule(Rule):
    """检查 name 字段是否与目录名完全匹配"""

    @property
    def rule_id(self) -> str:
        return "name-directory-match"

    @property
    def level(self) -> str:
        return "ERROR"

    def check(self, skill: Skill) -> List[Issue]:
        issues = []

        name = skill.frontmatter.get("name")
        if not name:
            return issues  # required-fields 规则会处理

        # 检查 name 是否与目录名匹配
        if name != skill.name:
            issues.append(Issue(
                rule_id=self.rule_id,
                level=self.level,
                message=f"Name mismatch: frontmatter name '{name}' does not match directory name '{skill.name}'",
                file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
            ))

        return issues
