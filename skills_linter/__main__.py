"""CLI 入口"""

import sys
import argparse
from pathlib import Path

from .checker import check_all_skills
from .reporter import generate_json_report


def main():
    parser = argparse.ArgumentParser(
        description="Skills Linter - 检查 Skills 是否符合 agent_skills_spec.md 规范"
    )
    parser.add_argument(
        "--path",
        type=str,
        default="skills/",
        help="Skills 目录路径（默认: skills/）"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="并行检查的最大进程数（默认: 4）"
    )

    args = parser.parse_args()

    # 检查所有 Skills
    skills_dir = Path(args.path)
    results = check_all_skills(skills_dir, max_workers=args.max_workers)

    # 生成 JSON 报告
    report = generate_json_report(results)
    print(report)

    # 根据结果返回退出码
    # 0: 所有检查通过
    # 1: 发现 ERROR 级别违规
    # 2: 发现 WARNING 级别违规（但无 ERROR）
    has_error = any(
        issue.level == "ERROR"
        for result in results
        for issue in result.issues
    )
    has_warning = any(
        issue.level == "WARNING"
        for result in results
        for issue in result.issues
    )

    if has_error:
        sys.exit(1)
    elif has_warning:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
