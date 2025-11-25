"""检查字段类型"""

from typing import List
from ..models import Skill, Issue
from .base import Rule


class FieldTypesRule(Rule):
    """检查可选字段的类型是否正确"""

    @property
    def rule_id(self) -> str:
        return "field-types"

    @property
    def level(self) -> str:
        return "ERROR"

    def check(self, skill: Skill) -> List[Issue]:
        issues = []

        # 检查 allowed-tools 字段类型
        if "allowed-tools" in skill.frontmatter:
            allowed_tools = skill.frontmatter["allowed-tools"]
            if not isinstance(allowed_tools, list):
                issues.append(Issue(
                    rule_id=self.rule_id,
                    level=self.level,
                    message=f"Invalid type for 'allowed-tools': expected list, got {type(allowed_tools).__name__}",
                    file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
                ))

        # 检查 metadata 字段类型
        if "metadata" in skill.frontmatter:
            metadata = skill.frontmatter["metadata"]
            if not isinstance(metadata, dict):
                issues.append(Issue(
                    rule_id=self.rule_id,
                    level=self.level,
                    message=f"Invalid type for 'metadata': expected dict, got {type(metadata).__name__}",
                    file_path=str(skill.skill_md_path.relative_to(skill.path.parent.parent))
                ))

        return issues
