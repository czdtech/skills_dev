"""检查必需字段"""

from typing import List
from ..models import Skill, Issue
from .base import Rule


class RequiredFieldsRule(Rule):
    """检查必需字段：name 和 description"""

    @property
    def rule_id(self) -> str:
        return "required-fields"

    @property
    def level(self) -> str:
        return "ERROR"

    def check(self, skill: Skill) -> List[Issue]:
        issues = []

        # 检查 name 字段
        if "name" not in skill.frontmatter or not skill.frontmatter["name"]:
            issues.append(Issue(
                rule_id=self.rule_id,
                level=self.level,
                message="Missing required field: name",
                file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
            ))

        # 检查 description 字段
        if "description" not in skill.frontmatter or not skill.frontmatter["description"]:
            issues.append(Issue(
                rule_id=self.rule_id,
                level=self.level,
                message="Missing required field: description",
                file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
            ))

        return issues
