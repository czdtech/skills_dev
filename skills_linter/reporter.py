"""输出格式化"""

import json
from typing import List, Dict, Any

from .models import CheckResult


def generate_json_report(results: List[CheckResult]) -> str:
    """生成 JSON 格式的检查报告"""
    # 计算统计信息
    total_skills = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total_skills - passed

    total_issues = sum(len(r.issues) for r in results)
    errors = sum(1 for r in results for issue in r.issues if issue.level == "ERROR")
    warnings = sum(1 for r in results for issue in r.issues if issue.level == "WARNING")
    infos = sum(1 for r in results for issue in r.issues if issue.level == "INFO")

    # 构建报告结构
    report: Dict[str, Any] = {
        "summary": {
            "total_skills": total_skills,
            "passed": passed,
            "failed": failed,
            "total_issues": total_issues,
            "errors": errors,
            "warnings": warnings,
            "infos": infos
        },
        "results": []
    }

    # 添加每个 Skill 的检查结果
    for result in results:
        report["results"].append({
            "skill_name": result.skill_name,
            "skill_path": result.skill_path,
            "passed": result.passed,
            "issues": [
                {
                    "rule_id": issue.rule_id,
                    "level": issue.level,
                    "message": issue.message,
                    "file_path": issue.file_path,
                    "line": issue.line
                }
                for issue in result.issues
            ]
        })

    return json.dumps(report, indent=2, ensure_ascii=False)
