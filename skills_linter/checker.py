"""检查器主逻辑"""

from pathlib import Path
from typing import List
from concurrent.futures import ProcessPoolExecutor, as_completed

from .models import Skill, CheckResult, Issue
from .parser import parse_skill_md, ParseError
from .rules import discover_rules


def scan_skills_directory(skills_dir: Path) -> List[Path]:
    """扫描 skills/ 目录，返回所有 Skill 目录"""
    skill_dirs = []

    if not skills_dir.exists():
        return skill_dirs

    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skill_dirs.append(item)

    return skill_dirs


def check_single_skill(skill_dir: Path, rules: List) -> CheckResult:
    """检查单个 Skill"""
    try:
        skill = parse_skill_md(skill_dir)
    except ParseError as e:
        # 解析失败，返回解析错误
        return CheckResult(
            skill_name=skill_dir.name,
            skill_path=str(skill_dir),
            passed=False,
            issues=[Issue(
                rule_id="parse-error",
                level="ERROR",
                message=str(e),
                file_path=str(skill_dir / "SKILL.md")
            )]
        )

    # 执行所有规则检查
    all_issues = []
    for rule in rules:
        issues = rule.check(skill)
        all_issues.extend(issues)

    # 判断是否通过（无 ERROR 级别问题）
    has_error = any(issue.level == "ERROR" for issue in all_issues)

    return CheckResult(
        skill_name=skill.name,
        skill_path=str(skill.path),
        passed=not has_error,
        issues=all_issues
    )


def check_all_skills(skills_dir: Path, max_workers: int = 4) -> List[CheckResult]:
    """并行检查所有 Skills"""
    # 发现所有规则
    rule_classes = discover_rules()
    rules = [rule_class() for rule_class in rule_classes]

    # 扫描所有 Skill 目录
    skill_dirs = scan_skills_directory(skills_dir)

    if not skill_dirs:
        return []

    # 并行检查
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_single_skill, skill_dir, rules): skill_dir for skill_dir in skill_dirs}
        for future in as_completed(futures):
            results.append(future.result())

    return results
