"""规则基类"""

from abc import ABC, abstractmethod
from typing import List

from ..models import Skill, Issue


class Rule(ABC):
    """规则基类"""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """规则 ID"""
        pass

    @property
    @abstractmethod
    def level(self) -> str:
        """规则级别：ERROR / WARNING / INFO"""
        pass

    @abstractmethod
    def check(self, skill: Skill) -> List[Issue]:
        """
        检查逻辑，返回问题列表

        Args:
            skill: 要检查的 Skill

        Returns:
            问题列表，如果没有问题则返回空列表
        """
        pass
